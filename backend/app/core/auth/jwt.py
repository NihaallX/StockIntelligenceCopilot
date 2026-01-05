"""JWT token utilities for authentication"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from app.config import settings
import secrets
import logging

logger = logging.getLogger(__name__)


def create_access_token(
    user_id: str,
    session_id: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token
    
    Args:
        user_id: User UUID
        session_id: Session UUID
        expires_delta: Token expiration time
    
    Returns:
        Encoded JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    jti = secrets.token_urlsafe(32)
    
    to_encode = {
        "sub": user_id,
        "session_id": session_id,
        "jti": jti,
        "type": "access",
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(
    user_id: str,
    session_id: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT refresh token
    
    Args:
        user_id: User UUID
        session_id: Session UUID
        expires_delta: Token expiration time
    
    Returns:
        Encoded JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    expire = datetime.utcnow() + expires_delta
    jti = secrets.token_urlsafe(32)
    
    to_encode = {
        "sub": user_id,
        "session_id": session_id,
        "jti": jti,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        return None


def extract_user_id(token: str) -> Optional[str]:
    """
    Extract user_id from JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        User ID or None if invalid
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None
