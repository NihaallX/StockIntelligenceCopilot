"""Core data models for Stock Intelligence Copilot"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List, Dict, Literal
from enum import Enum
from app.models.enums import ExchangeEnum, CountryEnum, CurrencyEnum, MarketStatusEnum


# Enums
class SignalType(str, Enum):
    """Signal types"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class TimeHorizon(str, Enum):
    """Investment time horizons"""
    LONG_TERM = "long_term"  # > 1 year
    MEDIUM_TERM = "medium_term"  # 3-12 months
    SHORT_TERM = "short_term"  # < 3 months (restricted in MVP)


# Market Data Models
class StockPrice(BaseModel):
    """Single price data point"""
    timestamp: datetime
    open: float = Field(gt=0, description="Opening price")
    high: float = Field(gt=0, description="Highest price")
    low: float = Field(gt=0, description="Lowest price")
    close: float = Field(gt=0, description="Closing price")
    volume: int = Field(ge=0, description="Trading volume")
    
    @field_validator('high')
    @classmethod
    def validate_high(cls, v, info):
        """Ensure high >= low, open, close"""
        if 'low' in info.data and v < info.data['low']:
            raise ValueError('High must be >= low')
        return v


class StockFundamentals(BaseModel):
    """Fundamental data for a stock"""
    ticker: str
    company_name: str
    market_cap: Optional[float] = Field(None, ge=0)
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = Field(None, ge=0, le=1)
    sector: Optional[str] = None
    industry: Optional[str] = None


class MarketData(BaseModel):
    """Complete market data package"""
    ticker: str
    
    # Phase 2D: Multi-market support
    exchange: ExchangeEnum = Field(default=ExchangeEnum.NASDAQ, description="Stock exchange")
    country: CountryEnum = Field(default=CountryEnum.US, description="Country code")
    currency: CurrencyEnum = Field(default=CurrencyEnum.USD, description="Price currency")
    company_name: Optional[str] = Field(default=None, description="Company name")
    
    prices: List[StockPrice]
    fundamentals: Optional[StockFundamentals] = None
    last_updated: datetime = Field(default_factory=datetime.now)    
    
    # Data quality metadata (Phase 2C)
    data_source: str = Field(
        default="unknown",
        description="Source of data: live, demo, cache_fresh, cache_stale, cache_error_fallback"
    )
    data_quality_warning: Optional[str] = Field(
        default=None,
        description="Warning message if data quality is degraded"
    )

# Technical Indicators Models
class TechnicalIndicators(BaseModel):
    """Calculated technical indicators"""
    ticker: str
    timestamp: datetime
    
    # Trend indicators
    sma_20: Optional[float] = Field(None, description="20-day Simple Moving Average")
    sma_50: Optional[float] = Field(None, description="50-day Simple Moving Average")
    ema_12: Optional[float] = Field(None, description="12-day Exponential Moving Average")
    ema_26: Optional[float] = Field(None, description="26-day Exponential Moving Average")
    
    # Momentum indicators
    rsi: Optional[float] = Field(None, ge=0, le=100, description="Relative Strength Index")
    macd: Optional[float] = Field(None, description="MACD line")
    macd_signal: Optional[float] = Field(None, description="MACD signal line")
    macd_histogram: Optional[float] = Field(None, description="MACD histogram")
    
    # Volatility indicators
    bollinger_upper: Optional[float] = Field(None, description="Upper Bollinger Band")
    bollinger_middle: Optional[float] = Field(None, description="Middle Bollinger Band")
    bollinger_lower: Optional[float] = Field(None, description="Lower Bollinger Band")
    bollinger_width: Optional[float] = Field(None, description="Bollinger Band width (volatility measure)")
    
    # Support/Resistance
    support_level: Optional[float] = Field(None, description="Support level")
    resistance_level: Optional[float] = Field(None, description="Resistance level")
    
    # Price reference
    current_price: float = Field(gt=0, description="Current stock price")


# Signal Models
class SignalStrength(BaseModel):
    """Signal strength and confidence"""
    signal_type: SignalType
    confidence: float = Field(ge=0, le=1, description="Confidence score (0-1)")
    strength: Literal["weak", "moderate", "strong"]
    
    @field_validator('confidence')
    @classmethod
    def cap_confidence(cls, v):
        """Never exceed 95% confidence (epistemic humility)"""
        return min(v, 0.95)


class SignalReasoning(BaseModel):
    """Detailed reasoning for a signal"""
    primary_factors: List[str] = Field(description="Main factors supporting this signal")
    supporting_indicators: Dict[str, float] = Field(description="Indicator values")
    contradicting_factors: List[str] = Field(default_factory=list, description="Factors against this signal")
    assumptions: List[str] = Field(description="Key assumptions made")
    limitations: List[str] = Field(description="Known limitations of this analysis")


class Signal(BaseModel):
    """Generated trading signal"""
    ticker: str
    timestamp: datetime = Field(default_factory=datetime.now)
    strength: SignalStrength
    reasoning: SignalReasoning
    time_horizon: TimeHorizon


# Risk Assessment Models
class RiskFactor(BaseModel):
    """Individual risk factor"""
    name: str
    level: RiskLevel
    description: str
    mitigation: Optional[str] = None


class RiskAssessment(BaseModel):
    """Risk evaluation for a signal"""
    overall_risk: RiskLevel
    risk_factors: List[RiskFactor]
    is_actionable: bool = Field(description="Whether this signal meets minimum safety criteria")
    warnings: List[str] = Field(default_factory=list)
    constraints_applied: List[str] = Field(description="Safety constraints that were enforced")


# Insight Models
class Insight(BaseModel):
    """Complete analysis insight package"""
    ticker: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Core analysis
    signal: Signal
    risk_assessment: RiskAssessment
    technical_indicators: TechnicalIndicators
    
    # Metadata
    analysis_mode: TimeHorizon
    recommendation: Literal["consider", "monitor", "avoid", "no_action"]
    
    # Explanation
    summary: str = Field(description="Human-readable summary")
    key_points: List[str] = Field(description="Bullet points of key insights")
    disclaimer: str = Field(description="Legal/compliance disclaimer")
    
    # Confidence
    overall_confidence: float = Field(ge=0, le=1, description="Overall confidence in this insight")


# Request/Response Models
class AnalysisRequest(BaseModel):
    """Request to analyze a stock"""
    ticker: str = Field(min_length=1, max_length=20, description="Stock ticker symbol (e.g., AAPL or RELIANCE.NS)")
    time_horizon: TimeHorizon = TimeHorizon.LONG_TERM
    risk_tolerance: Literal["conservative", "moderate", "aggressive"] = "moderate"
    lookback_days: int = Field(default=90, ge=30, le=365, description="Days of historical data")


class AnalysisResponse(BaseModel):
    """Response containing analysis results"""
    success: bool
    insight: Optional[Insight] = None
    error: Optional[str] = None
    processing_time_ms: float
