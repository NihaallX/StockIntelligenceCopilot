"""
MCP (Market Context Protocol) Data Adapters
============================================

Clean data integration layer for market context enrichment.

⚠️ CRITICAL: MCP provides DATA ONLY
- NO signal generation
- NO score modification
- NO trade execution
- NO text generation
- NO blocked websites

Approved Sources:
- Alpha Vantage (primary)
- Twelve Data (fallback)
- Yahoo Finance (fundamentals only)
"""

from .base import (
    MCPProvider,
    TimeframeEnum,
    OHLCVData,
    IndicatorData,
    IndexData,
    MCPDataUnavailable,
    MCPRateLimitError
)
from .factory import (
    get_mcp_provider,
    MarketRegimeContext,
    MCPProviderFactory
)

__all__ = [
    # Factory
    "get_mcp_provider",
    "MCPProviderFactory",
    
    # Context
    "MarketRegimeContext",
    
    # Base classes
    "MCPProvider",
    "TimeframeEnum",
    "OHLCVData",
    "IndicatorData",
    "IndexData",
    
    # Exceptions
    "MCPDataUnavailable",
    "MCPRateLimitError"
]
