"""Database schema definitions using SQLModel"""

from typing import Optional, List
from datetime import datetime, date
from uuid import UUID, uuid4
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String, JSON
from app.models.auth_models import RiskTolerance, TimeHorizonPreference

# =====================================================
# USER TABLES
# =====================================================

class UserBase(SQLModel):
    email: str = Field(index=True, unique=True, sa_column_kwargs={"unique": True})
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)
    terms_version: str
    terms_accepted_at: datetime
    risk_acknowledgment_at: datetime
    last_login_at: Optional[datetime] = None
    # We store the hashed password in metadata in the original app
    # For SQL, it's better to have a proper column, but sticking to existing logic for now
    # to minimize refactoring, or we can expose it.
    # The original model used a 'metadata' JSON field.
    meta_data: Optional[dict] = Field(default={}, sa_column=Column("metadata", JSON))

class User(UserBase, table=True):
    __tablename__ = "users"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    risk_profile: Optional["UserRiskProfile"] = Relationship(back_populates="user", sa_relationship_kwargs={"uselist": False})
    positions: List["PortfolioPosition"] = Relationship(back_populates="user")

# =====================================================
# RISK PROFILE TABLES
# =====================================================

class UserRiskProfile(SQLModel, table=True):
    __tablename__ = "user_risk_profiles"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True)
    
    risk_tolerance: str = Field(default=RiskTolerance.CONSERVATIVE.value)
    
    # Position limits
    max_position_size_usd: float = 10000.00
    max_position_size_percent: float = 5.00
    
    # Portfolio limits
    max_total_exposure_usd: float = 100000.00
    max_capital_at_risk_percent: float = 2.00
    
    # Drawdown protection
    max_drawdown_percent: float = 20.00
    
    # Asset class toggles
    allow_high_volatility_stocks: bool = False
    allow_penny_stocks: bool = False
    allow_international_stocks: bool = True
    
    # Sector preferences (Store as JSON)
    allowed_sectors: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    excluded_sectors: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Time horizon
    preferred_time_horizon: str = Field(default=TimeHorizonPreference.LONG_TERM.value)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1)
    
    user: Optional[User] = Relationship(back_populates="risk_profile")

# =====================================================
# PORTFOLIO TABLES
# =====================================================

class PortfolioPosition(SQLModel, table=True):
    __tablename__ = "portfolio_positions"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    
    ticker: str = Field(index=True)
    quantity: Decimal = Field(default=0, max_digits=20, decimal_places=4)
    entry_price: Decimal = Field(default=0, max_digits=20, decimal_places=4)
    entry_date: date
    notes: Optional[str] = Field(None, max_length=500)
    
    # Computed/Cached fields
    cost_basis: Decimal = Field(default=0, max_digits=20, decimal_places=2)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: Optional[User] = Relationship(back_populates="positions")
