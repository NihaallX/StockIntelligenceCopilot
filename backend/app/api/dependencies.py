"""Authentication dependency for protected endpoints"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from app.core.auth import verify_token
from app.core.database import get_service_db
from app.models.auth_models import User, UserRiskProfile

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency to get current authenticated user
    
    Validates JWT token and returns user object
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
    db = get_service_db()
    result = db.table("users").select("*").eq("id", user_id).eq("is_active", True).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    user_data = result.data[0]
    return User(**user_data)


async def get_user_risk_profile(
    current_user: User = Depends(get_current_user)
) -> UserRiskProfile:
    """
    Dependency to get current user's risk profile
    
    Returns risk profile for authenticated user
    Raises 404 if profile not found
    """
    db = get_service_db()
    result = db.table("user_risk_profiles").select("*").eq("user_id", str(current_user.id)).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk profile not found. Please create one first."
        )
    
    profile_data = result.data[0]
    return UserRiskProfile(**profile_data)


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
