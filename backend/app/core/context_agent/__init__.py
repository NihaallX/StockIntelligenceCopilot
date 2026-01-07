"""Market Regime Context Provider (Intraday-First)

Provides READ-ONLY market regime labels based on:
- Time of day
- Index correlation
- Volume patterns
- Volatility expansion

NO news scraping. NO predictions. NO signal modification.

Usage:
    from app.core.context_agent import MarketRegimeProvider, get_trigger_manager
    
    provider = MarketRegimeProvider()
    trigger_mgr = get_trigger_manager()
    
    if trigger_mgr.should_trigger(ticker, opportunity_type, volatility):
        regime = await provider.get_regime_context(ticker)
"""

from .agent import MarketRegimeProvider, MarketContextAgent
from .models import (
    RegimeContextInput,
    RegimeContextOutput,
    MarketContext,
    ContextEnrichmentInput,
    ContextEnrichmentOutput
)
from .trigger_manager import MCPTriggerManager, get_trigger_manager

__all__ = [
    "MarketRegimeProvider",
    "MarketContextAgent",  # Legacy alias
    "RegimeContextInput",
    "RegimeContextOutput",
    "MarketContext",
    "ContextEnrichmentInput",  # Legacy
    "ContextEnrichmentOutput",  # Legacy
    "MCPTriggerManager",
    "get_trigger_manager"
]
