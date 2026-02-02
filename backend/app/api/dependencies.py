"""Authentication dependency for protected endpoints"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
import logging

from app.core.auth import verify_token
from app.core.database import get_session
from app.models.sql_tables import User, UserRiskProfile

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
) -> User:
    """
    Dependency to get current authenticated user
    
    Validates JWT token and returns user object from database
    Raises 401 if token is invalid or user not found
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user from database
    try:
        user = await session.get(User, user_id)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
            
        return user
        
    except Exception as e:
        logger.error(f"Database error in get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )


async def get_user_risk_profile(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> UserRiskProfile:
    """
    Dependency to get current user's risk profile
    
    Returns risk profile for authenticated user
    Raises 404 if profile not found
    """
    try:
        statement = select(UserRiskProfile).where(UserRiskProfile.user_id == current_user.id)
        result = await session.execute(statement)
        profile_data = result.scalars().first()
        
        if not profile_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Risk profile not found. Please create one first."
            )
        
        return profile_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error in get_user_risk_profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch risk profile"
        )


async def get_session_context(
    request: Request,
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Get session context for audit logging
    
    Returns dict with user_id, session_id, ip_address, user_agent
    """
    credentials = await security(request)
    token = credentials.credentials
    payload = verify_token(token)
    
    return {
        "user_id": str(current_user.id),
        "session_id": payload.get("session_id") if payload else None,
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent")
    }
