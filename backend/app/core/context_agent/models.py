"""Data models for Market Regime Context (Intraday-First)

SIMPLIFIED: No news scraping, no citations.
Only regime labels based on time/index/volume/volatility.
"""

from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import datetime


class RegimeContextInput(BaseModel):
    """Input for market regime detection"""
    
    ticker: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Stock ticker (e.g., RELIANCE.NS)"
    )
    timeframe: Literal["INTRADAY", "DAILY"] = Field(
        default="INTRADAY",
        description="Timeframe for regime detection"
    )


class RegimeContextOutput(BaseModel):
    """Market regime context output (NO NEWS)"""
    
    regime_label: str = Field(
        ...,
        description="Regime label (INDEX_LED_MOVE, LOW_LIQUIDITY_CHOP, etc.)"
    )
    explanation: str = Field(
        ...,
        max_length=300,
        description="Plain-English explanation of current regime"
    )
    index_alignment: str = Field(
        default="neutral",
        description="Stock vs index alignment (aligned, diverging, neutral)"
    )
    volume_state: str = Field(
        default="normal",
        description="Volume state (dry, normal, expansion)"
    )
    volatility_state: str = Field(
        default="normal",
        description="Volatility state (compressed, normal, expanding)"
    )
    time_of_day: str = Field(
        default="open",
        description="Market session (open, lunch, close, after_hours)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When regime was detected"
    )


class MarketContext(BaseModel):
    """Simplified market context (backward compatible)"""
    
    regime_label: str = Field(default="UNKNOWN")
    explanation: str = Field(default="No market context available")
    index_alignment: str = Field(default="neutral")
    volume_state: str = Field(default="normal")
    volatility_state: str = Field(default="normal")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Legacy compatibility (remove after frontend migration)
class ContextEnrichmentInput(BaseModel):
    """DEPRECATED: Use RegimeContextInput"""
    ticker: str
    timeframe: Literal["INTRADAY", "SHORT_TERM", "LONG_TERM"] = "INTRADAY"


class ContextEnrichmentOutput(BaseModel):
    """DEPRECATED: Use RegimeContextOutput"""
    context_summary: str = "No context available"
    enriched_at: datetime = Field(default_factory=datetime.utcnow)
    mcp_status: Literal["success", "disabled"] = "disabled"


class SafeContextOutput(BaseModel):
    """DEPRECATED: Use MarketContext"""
    context_summary: str = "No context available"
    enriched_at: datetime = Field(default_factory=datetime.utcnow)
    mcp_status: Literal["disabled"] = "disabled"
