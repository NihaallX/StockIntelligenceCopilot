"""Phase 2B: Portfolio tracking data models"""

from pydantic import BaseModel, Field, field_validator, field_serializer
from datetime import datetime, date
from typing import Optional, List, Literal, Dict
from uuid import UUID
from decimal import Decimal, ROUND_HALF_UP

from app.models.schemas import Insight
from app.core.context_agent.models import MarketContext


# =====================================================
# PORTFOLIO MODELS
# =====================================================

class PositionBase(BaseModel):
    """Base position model"""
    ticker: str = Field(min_length=1, max_length=20, description="Stock ticker symbol (e.g., RELIANCE.NS)")
    quantity: Decimal = Field(gt=0, description="Number of shares owned")
    entry_price: Decimal = Field(gt=0, description="Average purchase price per share")
    entry_date: date = Field(description="Date of initial purchase")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")


class PositionCreate(PositionBase):
    """Create new position"""
    pass


class PositionUpdate(BaseModel):
    """Update existing position"""
    quantity: Optional[Decimal] = Field(None, gt=0)
    entry_price: Optional[Decimal] = Field(None, gt=0)
    notes: Optional[str] = Field(None, max_length=500)


class Position(PositionBase):
    """Portfolio position database model"""
    id: UUID
    user_id: UUID
    
    # Calculated fields (updated on market data refresh)
    current_price: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    cost_basis: Optional[Decimal] = None
    unrealized_pnl: Optional[Decimal] = None
    unrealized_pnl_percent: Optional[Decimal] = None
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    last_price_update: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PortfolioSummary(BaseModel):
    """Portfolio aggregate statistics"""
    total_positions: int
    total_value: Decimal
    total_cost_basis: Decimal
    total_unrealized_pnl: Decimal
    total_unrealized_pnl_percent: Decimal
    
    # Risk metrics
    largest_position_value: Decimal
    largest_position_ticker: str
    largest_position_percent: Decimal
    
    # Concentration risk
    top_5_concentration: Decimal = Field(description="% of portfolio in top 5 holdings")
    sector_concentration: dict = Field(default_factory=dict, description="% by sector")
    
    @field_serializer('total_unrealized_pnl_percent', 'largest_position_percent', 'top_5_concentration')
    def serialize_percentages(self, value: Decimal) -> str:
        """Round percentages to 2 decimal places"""
        if value is None:
            return "0.00"
        return str(value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    @field_serializer('total_value', 'total_cost_basis', 'total_unrealized_pnl', 'largest_position_value')
    def serialize_currency(self, value: Decimal) -> str:
        """Round currency values to 2 decimal places"""
        if value is None:
            return "0.00"
        return str(value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    # Diversification
    number_of_sectors: int
    average_position_size: Decimal
    
    last_updated: datetime


class PortfolioRiskAnalysis(BaseModel):
    """Portfolio-level risk assessment"""
    overall_risk: Literal["low", "moderate", "high", "critical"]
    risk_factors: List[str]
    warnings: List[str]
    recommendations: List[str]
    
    # Specific checks
    is_over_concentrated: bool
    violates_position_limits: bool
    exceeds_exposure_limit: bool
    exceeds_sector_limits: bool


# =====================================================
# FUNDAMENTAL ANALYSIS MODELS
# =====================================================

class FundamentalData(BaseModel):
    """Fundamental analysis data for a stock"""
    ticker: str
    
    # Valuation metrics
    market_cap: Optional[Decimal] = Field(None, description="Market capitalization")
    pe_ratio: Optional[Decimal] = Field(None, description="Price-to-Earnings ratio")
    pb_ratio: Optional[Decimal] = Field(None, description="Price-to-Book ratio")
    ps_ratio: Optional[Decimal] = Field(None, description="Price-to-Sales ratio")
    peg_ratio: Optional[Decimal] = Field(None, description="Price/Earnings to Growth ratio")
    
    # Growth metrics
    revenue_growth_yoy: Optional[Decimal] = Field(None, description="Year-over-year revenue growth %")
    earnings_growth_yoy: Optional[Decimal] = Field(None, description="Year-over-year earnings growth %")
    eps_growth_3y: Optional[Decimal] = Field(None, description="3-year EPS growth rate %")
    
    # Profitability
    profit_margin: Optional[Decimal] = Field(None, description="Net profit margin %")
    operating_margin: Optional[Decimal] = Field(None, description="Operating margin %")
    roe: Optional[Decimal] = Field(None, description="Return on Equity %")
    roa: Optional[Decimal] = Field(None, description="Return on Assets %")
    
    # Financial health
    debt_to_equity: Optional[Decimal] = Field(None, description="Debt-to-Equity ratio")
    current_ratio: Optional[Decimal] = Field(None, description="Current ratio (liquidity)")
    quick_ratio: Optional[Decimal] = Field(None, description="Quick ratio (liquidity)")
    
    # Dividend
    dividend_yield: Optional[Decimal] = Field(None, description="Annual dividend yield %")
    payout_ratio: Optional[Decimal] = Field(None, description="Dividend payout ratio %")
    
    # Metadata
    last_updated: datetime
    data_quality: Literal["high", "medium", "low"] = "medium"


class FundamentalScore(BaseModel):
    """Fundamental analysis score"""
    ticker: str
    overall_score: int = Field(ge=0, le=100, description="Overall fundamental score (0-100)")
    valuation_score: int = Field(ge=0, le=30, description="Valuation attractiveness")
    growth_score: int = Field(ge=0, le=25, description="Growth potential")
    profitability_score: int = Field(ge=0, le=25, description="Profitability")
    financial_health_score: int = Field(ge=0, le=20, description="Financial health")
    overall_assessment: Literal["STRONG", "MODERATE", "WEAK", "POOR"]
    score_details: Dict[str, float] = Field(default_factory=dict)
    scored_at: datetime


# =====================================================
# SCENARIO ANALYSIS MODELS
# =====================================================

class ScenarioAssumptions(BaseModel):
    """Assumptions for scenario analysis"""
    # Market conditions
    market_regime: Literal["bullish", "neutral", "bearish"]
    expected_volatility: Decimal
    catalyst_strength: Literal["strong", "moderate", "weak", "unknown"]
    
    # Technical levels
    support_level: Optional[Decimal] = None
    resistance_level: Optional[Decimal] = None


class ScenarioOutcome(BaseModel):
    """Single scenario outcome"""
    scenario_type: Literal["best_case", "base_case", "worst_case"]
    probability: Decimal = Field(ge=0, le=100, description="Probability percentage of this scenario")
    
    # Price projections
    target_price_low: Decimal
    target_price_mid: Decimal
    target_price_high: Decimal
    
    # Returns
    expected_return_percent: Decimal
    
    # Key drivers and timeline
    key_drivers: List[str]
    timeline_days: int
    
    # Confidence
    confidence_level: Decimal = Field(ge=0, le=1, description="Confidence in this scenario")


class ScenarioAnalysis(BaseModel):
    """Complete scenario analysis"""
    ticker: str
    current_price: Decimal
    time_horizon_days: int
    
    # Assumptions
    assumptions: ScenarioAssumptions
    
    # Scenarios
    best_case: ScenarioOutcome
    base_case: ScenarioOutcome
    worst_case: ScenarioOutcome
    
    # Risk/Reward
    expected_return_weighted: Decimal = Field(description="Probability-weighted expected return")
    risk_reward_ratio: Decimal = Field(description="Upside potential vs downside risk")
    
    # Metadata
    generated_at: datetime
    disclaimer: str = (
        "Scenario analysis is inherently uncertain and based on assumptions that may not materialize. "
        "These projections are NOT guarantees and should not be relied upon as the sole basis for investment decisions."
    )


# =====================================================
# ENHANCED INSIGHT WITH FUNDAMENTALS + SCENARIOS
# =====================================================

class EnhancedInsightRequest(BaseModel):
    """Request for enhanced analysis with fundamentals and scenarios"""
    ticker: str = Field(pattern=r'^[A-Z0-9]{1,10}(\.[A-Z]{1,3})?$')  # Allows AAPL or RELIANCE.NS
    include_fundamentals: bool = True
    include_scenarios: bool = True
    scenario_assumptions: Optional[ScenarioAssumptions] = None
    time_horizon: Literal["long_term", "medium_term"] = "long_term"
    risk_tolerance: Literal["conservative", "moderate", "aggressive"] = "moderate"
    lookback_days: int = Field(default=90, ge=30, le=365)
    scenario_time_horizon: Optional[int] = Field(default=90, ge=30, le=180)


class EnhancedInsightResponse(BaseModel):
    """Enhanced analysis response"""
    # Core Phase 1 analysis
    technical_insight: Insight
    
    # Phase 2B additions
    fundamental_data: Optional[FundamentalData] = None
    fundamental_score: Optional[FundamentalScore] = None
    scenario_analysis: Optional[ScenarioAnalysis] = None
    
    # MCP Context (Task 3)
    market_context: Optional[MarketContext] = None
    
    # Combined analysis
    combined_score: Decimal = Field(ge=0, le=100, description="Weighted combined score")
    recommendation: str = Field(description="Actionable recommendation text")
    disclaimer: str = (
        "This analysis is for informational purposes only and does not constitute financial advice. "
        "Past performance is not indicative of future results. Always do your own research."
    )
