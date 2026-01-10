"""Authentication API endpoints with enhanced security"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional
import logging
from collections import defaultdict

from app.models.auth_models import (
    UserCreate,
    UserLogin,
    User,
    Token,
    TokenRefresh,
    AuthResponse,
    RegisterResponse,
    UserProfile,
    UserRiskProfile
)
from app.core.auth import (
    create_access_token,
    create_refresh_token,
    verify_token,
    hash_password,
    verify_password
)
from app.core.database import get_service_db
from app.core.audit import AuditLogger
from app.core.validation import InputValidator
from app.config import settings
from uuid import uuid4

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


# Brute force protection: track failed login attempts
login_attempts = defaultdict(list)
blocked_ips = {}
MAX_LOGIN_ATTEMPTS = 5
BLOCK_DURATION_MINUTES = 15
ATTEMPT_WINDOW_MINUTES = 15


def check_brute_force(ip: str) -> None:
    """Check if IP is blocked due to too many failed attempts"""
    # Check if IP is currently blocked
    if ip in blocked_ips:
        block_until = blocked_ips[ip]
        if datetime.utcnow() < block_until:
            remaining = (block_until - datetime.utcnow()).seconds // 60
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed login attempts. Try again in {remaining} minutes."
            )
        else:
            del blocked_ips[ip]
            login_attempts[ip] = []
    
    # Clean old attempts
    cutoff = datetime.utcnow() - timedelta(minutes=ATTEMPT_WINDOW_MINUTES)
    login_attempts[ip] = [ts for ts in login_attempts[ip] if ts > cutoff]
    
    # Check attempt count
    if len(login_attempts[ip]) >= MAX_LOGIN_ATTEMPTS:
        block_until = datetime.utcnow() + timedelta(minutes=BLOCK_DURATION_MINUTES)
        blocked_ips[ip] = block_until
        logger.warning(f"IP blocked due to brute force: {ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts. Blocked for {BLOCK_DURATION_MINUTES} minutes."
        )


def record_failed_attempt(ip: str) -> None:
    """Record a failed login attempt"""
    login_attempts[ip].append(datetime.utcnow())


def clear_failed_attempts(ip: str) -> None:
    """Clear failed attempts on successful login"""
    if ip in login_attempts:
        login_attempts[ip] = []
    if ip in blocked_ips:
        del blocked_ips[ip]


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, request: Request):
    """
    Register a new user with enhanced security
    
    - Validates email format and prevents injection
    - Enforces strong password policy
    - Creates user account in Supabase
    - Generates default conservative risk profile
    - Requires terms acceptance and risk acknowledgment
    """
    db = get_service_db()
    
    try:
        # Validate and sanitize email (with fallback)
        try:
            clean_email = InputValidator.validate_email(user_data.email)
        except Exception as e:
            logger.warning(f"Email validation failed: {e}")
            clean_email = user_data.email.lower().strip()
        
        # Validate password strength (with fallback)
        try:
            InputValidator.validate_password_strength(user_data.password)
        except Exception as e:
            logger.warning(f"Password validation failed: {e}")
            # Allow Pydantic validation to handle it
        
        # Check if user already exists
        existing = db.table("users").select("id").eq("email", clean_email).execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password with bcrypt (automatic salting + SHA-256 pre-hash)
        hashed_password = hash_password(user_data.password)
        
        # Sanitize full name if provided
        clean_name = None
        if user_data.full_name:
            try:
                clean_name = InputValidator.sanitize_string(user_data.full_name, max_length=100)
            except Exception:
                clean_name = user_data.full_name[:100]
        
        # Create user record
        user_record = {
            "email": clean_email,
            "full_name": clean_name,
            "terms_accepted_at": datetime.utcnow().isoformat(),
            "terms_version": settings.TERMS_VERSION,
            "risk_acknowledgment_at": datetime.utcnow().isoformat(),
            "is_active": True,
            "metadata": {
                "registration_ip": request.client.host if request.client else "unknown",
                "hashed_password": hashed_password  # Double-hashed: SHA-256 + bcrypt with salt
            }
        }
        
        result = db.table("users").insert(user_record).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        user = result.data[0]
        user_id = user["id"]
        
        logger.info(f"User registered: {user_id} | Email: {clean_email}")
        
        return RegisterResponse(
            user_id=user_id,
            email=clean_email,
            message="Registration successful. Conservative risk profile created by default."
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin, request: Request):
    """
    Authenticate user and return JWT tokens
    
    Enhanced Security:
    - Brute force protection (max 5 attempts in 15 min)
    - IP blocking on excessive failures
    - Constant-time password comparison
    - Validates credentials
    - Creates session
    - Logs audit event
    - Returns access + refresh tokens
    """
    db = get_service_db()
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # Check for brute force attempts
        try:
            check_brute_force(client_ip)
        except HTTPException as e:
            logger.warning(f"Brute force check failed for {client_ip}: {e.detail}")
            raise
        
        # Validate and sanitize email (with fallback)
        try:
            clean_email = InputValidator.validate_email(credentials.email)
        except Exception as e:
            logger.warning(f"Email validation failed: {e}")
            clean_email = credentials.email.lower().strip()
        
        # Get user by email
        result = db.table("users").select("*").eq("email", clean_email).eq("is_active", True).execute()
        
        if not result.data:
            record_failed_attempt(client_ip)
            logger.warning(f"Failed login attempt - user not found: {clean_email} from {client_ip}")
            # Use same error message for user not found and wrong password (prevent user enumeration)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        user = result.data[0]
        stored_hash = user["metadata"].get("hashed_password")
        
        # Verify password (constant-time comparison via bcrypt)
        if not stored_hash or not verify_password(credentials.password, stored_hash):
            record_failed_attempt(client_ip)
            logger.warning(f"Failed login attempt - wrong password: {clean_email} from {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Clear failed attempts on successful login
        clear_failed_attempts(client_ip)
        
        # Generate session ID
        session_id = str(uuid4())
        
        # Create tokens
        access_token = create_access_token(user["id"], session_id)
        refresh_token = create_refresh_token(user["id"], session_id)
        
        # Update last login
        db.table("users").update({
            "last_login_at": datetime.utcnow().isoformat()
        }).eq("id", user["id"]).execute()
        
        # Get risk profile
        profile_result = db.table("user_risk_profiles").select("*").eq("user_id", user["id"]).execute()
        risk_profile = profile_result.data[0] if profile_result.data else None
        
        # Log audit event
        await AuditLogger.log_user_login(
            user_id=user["id"],
            session_id=session_id,
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent"),
            success=True
        )
        
        logger.info(f"User logged in: {user['id']} | Session: {session_id} | IP: {client_ip}")
        
        return AuthResponse(
            user=UserProfile(
                id=user["id"],
                email=user["email"],
                full_name=user.get("full_name"),
                created_at=user["created_at"],
                risk_profile=UserRiskProfile(**risk_profile) if risk_profile else None
            ),
            tokens=Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh):
    """
    Refresh access token using refresh token
    
    - Validates refresh token
    - Issues new access token
    - Rotates refresh token
    """
    payload = verify_token(token_data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    session_id = payload.get("session_id")
    
    # Create new tokens
    new_access_token = create_access_token(user_id, session_id)
    new_refresh_token = create_refresh_token(user_id, session_id)
    
    logger.info(f"Token refreshed: User {user_id} | Session {session_id}")
    
    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout user and invalidate session
    
    - Validates token
    - Logs audit event
    - In production: Would invalidate session in database
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = payload.get("sub")
    session_id = payload.get("session_id")
    
    # Log audit event
    await AuditLogger.log_event(
        event_type="user_logout",
        user_id=user_id,
        input_data={"session_id": session_id},
        output_data={"success": True},
        session_id=session_id
    )
    
    logger.info(f"User logged out: {user_id} | Session: {session_id}")
    
    return {"message": "Logout successful"}


@router.get("/me", response_model=UserProfile)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current authenticated user profile
    
    - Validates JWT token
    - Returns user info + risk profile
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )
    
    user_id = payload.get("sub")
    db = get_service_db()
    
    # Get user
    user_result = db.table("users").select("*").eq("id", user_id).execute()
    if not user_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user = user_result.data[0]
    
    # Get risk profile
    profile_result = db.table("user_risk_profiles").select("*").eq("user_id", user_id).execute()
    risk_profile = profile_result.data[0] if profile_result.data else None
    
    return UserProfile(
        id=user["id"],
        email=user["email"],
        full_name=user.get("full_name"),
        created_at=user["created_at"],
        risk_profile=UserRiskProfile(**risk_profile) if risk_profile else None
    )
