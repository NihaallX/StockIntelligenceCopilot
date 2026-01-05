"""Phase 2A: User and authentication data models"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List, Literal
from uuid import UUID
from enum import Enum


# =====================================================
# USER MODELS
# =====================================================

class UserBase(BaseModel):
    """Base user model"""
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User registration model"""
    password: str = Field(min_length=8, description="Minimum 8 characters")
    terms_accepted: bool = Field(description="Must accept terms to register")
    risk_acknowledged: bool = Field(description="Must acknowledge investment risks")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        """Ensure password meets security requirements"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @field_validator('terms_accepted')
    @classmethod
    def validate_terms(cls, v):
        if not v:
            raise ValueError('Must accept terms and conditions')
        return v
    
    @field_validator('risk_acknowledged')
    @classmethod
    def validate_risk(cls, v):
        if not v:
            raise ValueError('Must acknowledge investment risks')
        return v


class UserLogin(BaseModel):
    """User login credentials"""
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str


class User(UserBase):
    """User database model"""
    id: UUID
    supabase_auth_id: Optional[UUID] = None
    is_active: bool = True
    terms_accepted_at: datetime
    terms_version: str
    risk_acknowledgment_at: datetime
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """Public user profile"""
    id: UUID
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    risk_profile: Optional['UserRiskProfile'] = None


# =====================================================
# RISK PROFILE MODELS
# =====================================================

class RiskTolerance(str, Enum):
    """User risk tolerance levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class TimeHorizonPreference(str, Enum):
    """Investment time horizons"""
    LONG_TERM = "long_term"
    MEDIUM_TERM = "medium_term"


class UserRiskProfileBase(BaseModel):
    """Base risk profile model"""
    risk_tolerance: RiskTolerance = RiskTolerance.CONSERVATIVE
    
    # Position limits
    max_position_size_usd: float = Field(default=10000.00, ge=100, le=1000000)
    max_position_size_percent: float = Field(default=5.00, ge=0.1, le=100)
    
    # Portfolio limits
    max_total_exposure_usd: float = Field(default=100000.00, ge=1000, le=10000000)
    max_capital_at_risk_percent: float = Field(default=2.00, ge=0.1, le=100)
    
    # Drawdown protection
    max_drawdown_percent: float = Field(default=20.00, ge=1, le=100)
    
    # Asset class toggles
    allow_high_volatility_stocks: bool = False
    allow_penny_stocks: bool = False
    allow_international_stocks: bool = True
    
    # Sector preferences
    allowed_sectors: List[str] = Field(default_factory=list)
    excluded_sectors: List[str] = Field(default_factory=list)
    
    # Time horizon
    preferred_time_horizon: TimeHorizonPreference = TimeHorizonPreference.LONG_TERM


class UserRiskProfileCreate(UserRiskProfileBase):
    """Create risk profile"""
    pass


class UserRiskProfileUpdate(UserRiskProfileBase):
    """Update risk profile"""
    pass


class UserRiskProfile(UserRiskProfileBase):
    """Risk profile database model"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    version: int = 1
    
    class Config:
        from_attributes = True


# =====================================================
# AUTHENTICATION MODELS
# =====================================================

class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Refresh token request"""
    refresh_token: str


class TokenPayload(BaseModel):
    """Decoded JWT token payload"""
    sub: str  # user_id
    session_id: str
    jti: str
    type: Literal["access", "refresh"]
    exp: datetime
    iat: datetime


class AuthResponse(BaseModel):
    """Authentication response"""
    user: UserProfile
    tokens: Token
    message: str = "Authentication successful"


class RegisterResponse(BaseModel):
    """Registration response"""
    user_id: UUID
    email: str
    message: str = "Registration successful. Please verify your email."


# =====================================================
# AUDIT LOG MODELS (for querying only - logs are immutable)
# =====================================================

class AuditLogEntry(BaseModel):
    """Audit log entry (read-only)"""
    id: UUID
    event_type: str
    user_id: UUID
    session_id: Optional[UUID] = None
    ip_address: Optional[str] = None
    ticker: Optional[str] = None
    signal_type: Optional[str] = None
    confidence_score: Optional[float] = None
    risk_level: Optional[str] = None
    was_actionable: Optional[bool] = None
    created_at: datetime
    compliance_version: str
    model_version: str
    
    class Config:
        from_attributes = True


# Update forward references
UserProfile.model_rebuild()
