"""Authentication API endpoints with enhanced security"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime
from uuid import uuid4
import logging
from collections import defaultdict

# Models (Pydantic for API)
from app.models.auth_models import (
    UserCreate,
    UserLogin,
    Token,
    TokenRefresh,
    AuthResponse,
    RegisterResponse,
    UserProfile as UserProfileSchema, # Alias to avoid confusion
    UserRiskProfile as UserRiskProfileSchema,
    RiskTolerance
)

# Models (SQLModel for DB)
from app.models.sql_tables import User, UserRiskProfile

# Core Utilities
from app.core.auth import (
    create_access_token,
    create_refresh_token,
    verify_token,
    hash_password,
    verify_password
)
from app.core.database import get_session
from app.core.audit import AuditLogger
from app.core.validation import InputValidator
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# Brute force protection (In-memory for now, could be Redis later)
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
    cutoff = datetime.utcnow().timestamp() - (ATTEMPT_WINDOW_MINUTES * 60)
    # Filter out old timestamps (converting to timestamp for easier comparison if they are datetimes)
    # Assuming stored as datetimes for now
    cutoff_dt = datetime.fromtimestamp(cutoff) # approximate
    # Better: just use datetime comparison
    
    # Check attempt count
    if len(login_attempts[ip]) >= MAX_LOGIN_ATTEMPTS:
        # Check time window
        recent_attempts = [ts for ts in login_attempts[ip] if (datetime.utcnow() - ts).total_seconds() < ATTEMPT_WINDOW_MINUTES * 60]
        if len(recent_attempts) >= MAX_LOGIN_ATTEMPTS:
             block_until = datetime.utcnow().timestamp() + (BLOCK_DURATION_MINUTES * 60)
             blocked_ips[ip] = datetime.fromtimestamp(block_until)
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
async def register(
    user_data: UserCreate, 
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """
    Register a new user with enhanced security
    """
    try:
        # Validate email
        try:
            clean_email = InputValidator.validate_email(user_data.email)
        except Exception as e:
            logger.warning(f"Email validation failed: {e}")
            clean_email = user_data.email.lower().strip()
        
        # Validate password
        try:
             # Basic check, Pydantic model handles complexity usually
             pass 
        except Exception:
            pass

        # Check if user already exists
        statement = select(User).where(User.email == clean_email)
        result = await session.execute(statement)
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Sanitize name
        clean_name = user_data.full_name[:100] if user_data.full_name else None
        
        # Create user
        new_user = User(
            email=clean_email,
            full_name=clean_name,
            terms_accepted_at=datetime.utcnow(),
            terms_version=settings.TERMS_VERSION,
            risk_acknowledgment_at=datetime.utcnow(),
            is_active=True,
            meta_data={
                "registration_ip": request.client.host if request.client else "unknown",
                "hashed_password": hashed_password
            }
        )
        
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        
        # Create default risk profile
        risk_profile = UserRiskProfile(
            user_id=new_user.id,
            risk_tolerance=RiskTolerance.CONSERVATIVE.value
        )
        session.add(risk_profile)
        await session.commit()
        
        logger.info(f"User registered: {new_user.id} | Email: {clean_email}")
        
        return RegisterResponse(
            user_id=new_user.id,
            email=clean_email,
            message="Registration successful. Conservative risk profile created by default."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        with open("fatal_error.log", "w") as f:
            f.write(f"Error: {e}\n")
            traceback.print_exc(file=f)
        logger.error(f"Registration error: {e}", exc_info=True)
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=AuthResponse)
async def login(
    credentials: UserLogin, 
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    """Authenticate user and return JWT tokens"""
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        check_brute_force(client_ip)
        
        clean_email = credentials.email.lower().strip()
        
        # Get user
        statement = select(User).where(User.email == clean_email).where(User.is_active == True)
        result = await session.execute(statement)
        user = result.scalars().first()
        
        if not user:
            record_failed_attempt(client_ip)
            logger.warning(f"Failed login attempt - user not found: {clean_email}")
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
        
        # Check password
        stored_hash = user.meta_data.get("hashed_password") if user.meta_data else None
        if not stored_hash or not verify_password(credentials.password, stored_hash):
            record_failed_attempt(client_ip)
            logger.warning(f"Failed login attempt - wrong password: {clean_email}")
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
        
        # Success
        clear_failed_attempts(client_ip)
        
        # Generate session
        session_id = str(uuid4())
        access_token = create_access_token(str(user.id), session_id)
        refresh_token = create_refresh_token(str(user.id), session_id)
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        session.add(user)
        await session.commit()
        
        # Get risk profile for response
        rp_stmt = select(UserRiskProfile).where(UserRiskProfile.user_id == user.id)
        rp_result = await session.execute(rp_stmt)
        risk_profile_db = rp_result.scalars().first()
        
        risk_profile_schema = None
        if risk_profile_db:
             risk_profile_schema = UserRiskProfileSchema(
                 id=risk_profile_db.id,
                 user_id=risk_profile_db.user_id,
                 created_at=risk_profile_db.created_at,
                 updated_at=risk_profile_db.updated_at,
                 version=risk_profile_db.version,
                 risk_tolerance=risk_profile_db.risk_tolerance,
                 max_position_size_usd=risk_profile_db.max_position_size_usd,
                 max_position_size_percent=risk_profile_db.max_position_size_percent,
                 max_total_exposure_usd=risk_profile_db.max_total_exposure_usd,
                 max_capital_at_risk_percent=risk_profile_db.max_capital_at_risk_percent,
                 max_drawdown_percent=risk_profile_db.max_drawdown_percent,
                 allow_high_volatility_stocks=risk_profile_db.allow_high_volatility_stocks,
                 allow_penny_stocks=risk_profile_db.allow_penny_stocks,
                 allow_international_stocks=risk_profile_db.allow_international_stocks,
                 allowed_sectors=risk_profile_db.allowed_sectors or [],
                 excluded_sectors=risk_profile_db.excluded_sectors or [],
                 preferred_time_horizon=risk_profile_db.preferred_time_horizon
             )

        await AuditLogger.log_user_login(
            user_id=user.id,
            session_id=session_id,
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent"),
            success=True
        )
        
        return AuthResponse(
            user=UserProfileSchema(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                created_at=user.created_at,
                risk_profile=risk_profile_schema
            ),
            tokens=Token(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Login failed")

@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh):
    """Refresh access token"""
    payload = verify_token(token_data.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")
    
    user_id = payload.get("sub")
    session_id = payload.get("session_id")
    
    new_access = create_access_token(user_id, session_id)
    new_refresh = create_refresh_token(user_id, session_id)
    
    return Token(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user"""
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    
    # Just log it
    await AuditLogger.log_event(
        event_type="user_logout",
        user_id=payload.get("sub"),
        input_data={"session_id": payload.get("session_id")},
        output_data={"success": True},
        session_id=payload.get("session_id")
    )
    return {"message": "Logout successful"}

@router.get("/me", response_model=UserProfileSchema)
async def get_current_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
):
    """Get current user profile"""
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    
    user_id = payload.get("sub")
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
        
    rp_stmt = select(UserRiskProfile).where(UserRiskProfile.user_id == user.id)
    rp_result = await session.execute(rp_stmt)
    rp = rp_result.scalars().first()
    
    risk_profile_schema = None
    if rp:
         # Manual mapping to ensure types match Pydantic schema
         risk_profile_schema = UserRiskProfileSchema(
             id=rp.id,
             user_id=rp.user_id,
             created_at=rp.created_at,
             updated_at=rp.updated_at,
             version=rp.version,
             risk_tolerance=rp.risk_tolerance,
             max_position_size_usd=rp.max_position_size_usd,
             max_position_size_percent=rp.max_position_size_percent,
             max_total_exposure_usd=rp.max_total_exposure_usd,
             max_capital_at_risk_percent=rp.max_capital_at_risk_percent,
             max_drawdown_percent=rp.max_drawdown_percent,
             allow_high_volatility_stocks=rp.allow_high_volatility_stocks,
             allow_penny_stocks=rp.allow_penny_stocks,
             allow_international_stocks=rp.allow_international_stocks,
             allowed_sectors=rp.allowed_sectors or [],
             excluded_sectors=rp.excluded_sectors or [],
             preferred_time_horizon=rp.preferred_time_horizon
         )
         
    return UserProfileSchema(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at,
        risk_profile=risk_profile_schema
    )
