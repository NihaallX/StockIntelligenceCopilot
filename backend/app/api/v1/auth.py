"""Authentication API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional
import logging

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
from app.config import settings
from uuid import uuid4

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, request: Request):
    """
    Register a new user
    
    - Creates user account in Supabase
    - Generates default conservative risk profile
    - Requires terms acceptance and risk acknowledgment
    """
    db = get_service_db()
    
    try:
        # Check if user already exists
        existing = db.table("users").select("id").eq("email", user_data.email).execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create user record
        user_record = {
            "email": user_data.email,
            "full_name": user_data.full_name,
            "terms_accepted_at": datetime.utcnow().isoformat(),
            "terms_version": settings.TERMS_VERSION,
            "risk_acknowledgment_at": datetime.utcnow().isoformat(),
            "is_active": True,
            "metadata": {
                "registration_ip": request.client.host,
                "hashed_password": hashed_password  # Store in metadata for now (Phase 2 workaround)
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
        
        logger.info(f"User registered: {user_id} | Email: {user_data.email}")
        
        return RegisterResponse(
            user_id=user_id,
            email=user_data.email,
            message="Registration successful. Conservative risk profile created by default."
        )
        
    except HTTPException:
        raise
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
    
    - Validates credentials
    - Creates session
    - Logs audit event
    - Returns access + refresh tokens
    """
    db = get_service_db()
    
    try:
        # Get user by email
        result = db.table("users").select("*").eq("email", credentials.email).eq("is_active", True).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        user = result.data[0]
        stored_hash = user["metadata"].get("hashed_password")
        
        if not stored_hash or not verify_password(credentials.password, stored_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
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
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            success=True
        )
        
        logger.info(f"User logged in: {user['id']} | Session: {session_id}")
        
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
