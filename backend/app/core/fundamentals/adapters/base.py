"""Base adapter interface for fundamental data providers"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from enum import Enum


class DataSource(Enum):
    """Data source identifier"""
    FMP = "Financial Modeling Prep"
    EODHD = "EODHD"
    DATABASE = "Database (Cached)"
    UNAVAILABLE = "Unavailable"


@dataclass
class FundamentalDataResult:
    """
    Result from fundamental data fetch
    
    Explicitly tracks data source and completeness.
    Frontend can show "Data from FMP" or "Fundamental data unavailable"
    """
    ticker: str
    source: DataSource
    available: bool
    
    # Valuation metrics
    market_cap: Optional[Decimal] = None
    pe_ratio: Optional[Decimal] = None
    pb_ratio: Optional[Decimal] = None
    dividend_yield: Optional[Decimal] = None
    
    # Growth metrics
    revenue_growth_yoy: Optional[Decimal] = None
    earnings_growth_yoy: Optional[Decimal] = None
    revenue_growth_qoq: Optional[Decimal] = None
    eps: Optional[Decimal] = None
    
    # Profitability metrics
    profit_margin: Optional[Decimal] = None
    operating_margin: Optional[Decimal] = None
    roe: Optional[Decimal] = None
    roa: Optional[Decimal] = None
    
    # Financial health metrics
    debt_to_equity: Optional[Decimal] = None
    current_ratio: Optional[Decimal] = None
    quick_ratio: Optional[Decimal] = None
    
    # Indian market specific
    sector: Optional[str] = None
    industry: Optional[str] = None
    exchange: Optional[str] = None  # NSE, BSE
    
    # Metadata
    company_name: Optional[str] = None
    currency: str = "INR"  # Default to INR for Indian market
    last_updated: Optional[datetime] = None
    data_age_hours: Optional[int] = None
    
    # Partial data tracking
    fields_available: int = 0  # Count of populated fields
    fields_total: int = 16  # Total expected fields
    completeness_percent: float = 0.0
    
    def __post_init__(self):
        """Calculate completeness after initialization"""
        self._calculate_completeness()
    
    def _calculate_completeness(self):
        """Count how many fields are populated"""
        fields = [
            self.market_cap, self.pe_ratio, self.pb_ratio, self.dividend_yield,
            self.revenue_growth_yoy, self.earnings_growth_yoy, self.eps,
            self.profit_margin, self.operating_margin, self.roe, self.roa,
            self.debt_to_equity, self.current_ratio, self.quick_ratio,
            self.sector, self.company_name
        ]
        self.fields_available = sum(1 for f in fields if f is not None)
        self.completeness_percent = (self.fields_available / self.fields_total) * 100
    
    def is_complete(self, threshold: float = 75.0) -> bool:
        """Check if data meets completeness threshold"""
        return self.completeness_percent >= threshold
    
    def missing_fields(self) -> list[str]:
        """List of missing critical fields"""
        missing = []
        if not self.pe_ratio:
            missing.append("PE Ratio")
        if not self.market_cap:
            missing.append("Market Cap")
        if not self.revenue_growth_yoy:
            missing.append("Revenue Growth")
        if not self.roe:
            missing.append("ROE")
        if not self.debt_to_equity:
            missing.append("Debt/Equity")
        return missing


class FundamentalAdapter(ABC):
    """
    Abstract base class for fundamental data adapters
    
    Each provider (FMP, EODHD, etc.) implements this interface.
    """
    
    @abstractmethod
    async def fetch_fundamentals(self, ticker: str) -> FundamentalDataResult:
        """
        Fetch fundamental data for a ticker
        
        Returns FundamentalDataResult with:
        - available=True if ANY data found
        - available=False if provider has no data for this ticker
        - Partial data OK - frontend shows what's available
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if adapter is working (API key valid, network OK)"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return provider name for logging"""
        pass
    
    @abstractmethod
    def supports_market(self, exchange: str) -> bool:
        """Check if this adapter supports given exchange (NSE, BSE, NYSE, etc.)"""
        pass
