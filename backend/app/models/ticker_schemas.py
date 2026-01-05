"""Ticker search schemas for Phase 2D"""

from pydantic import BaseModel, Field
from typing import List, Optional
from app.models.enums import ExchangeEnum, CountryEnum, CurrencyEnum


class TickerMetadata(BaseModel):
    """Ticker metadata for search results"""
    ticker: str
    company_name: str
    exchange: ExchangeEnum
    country: CountryEnum
    currency: CurrencyEnum
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    ticker_format: str
    data_provider: str
    is_supported: bool = True


class TickerSearchRequest(BaseModel):
    """Search request parameters"""
    query: str = Field(..., min_length=1, max_length=50, description="Search query")
    country: Optional[CountryEnum] = Field(None, description="Filter by country")
    exchange: Optional[ExchangeEnum] = Field(None, description="Filter by exchange")
    limit: int = Field(default=10, ge=1, le=50, description="Max results")


class TickerSearchResponse(BaseModel):
    """Search response with results"""
    results: List[TickerMetadata]
    total: int
    query: str
    filters_applied: dict = {}


class MarketStatus(BaseModel):
    """Market operational status"""
    exchange: ExchangeEnum
    is_open: bool
    timezone: str
    local_time: str
    next_open: Optional[str] = None
    next_close: Optional[str] = None
