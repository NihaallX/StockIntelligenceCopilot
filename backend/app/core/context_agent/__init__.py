"""Market Context Agent - MCP-based context enrichment layer

This module provides READ-ONLY market context to enrich existing opportunities.
It does NOT generate signals, predictions, or recommendations.

Usage:
    from app.core.context_agent import MarketContextAgent, get_trigger_manager
    
    agent = MarketContextAgent()
    trigger_mgr = get_trigger_manager()
    
    if trigger_mgr.should_trigger(ticker, opportunity_type, volatility):
        context = await agent.enrich_opportunity(opportunity_data)
"""

from .agent import MarketContextAgent
from .models import (
    ContextEnrichmentInput,
    ContextEnrichmentOutput,
    SupportingPoint
)
from .trigger_manager import MCPTriggerManager, get_trigger_manager

__all__ = [
    "MarketContextAgent",
    "ContextEnrichmentInput",
    "ContextEnrichmentOutput",
    "SupportingPoint",
    "MCPTriggerManager",
    "get_trigger_manager"
]
