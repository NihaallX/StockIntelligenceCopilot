"""Notable Signals API - Returns 3-5 most interesting signals for dashboard

This endpoint generates "Today's Situations" - notable signals from user's portfolio
that deserve attention. Uses calm, non-urgent language.

Design Principles:
- Maximum 5 signals (prevent overwhelm)
- Prioritize changed signals (new since yesterday)
- Mix of signal types (not all BUY or all SELL)
- Calm tone (informative, not alarming)
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging

from app.api.dependencies import get_current_user
from app.models.auth_models import User
from app.core.cache import cache_manager
from app.mcp.legacy_adapter import get_legacy_adapter
from app.core.context_agent.models import MarketContext

logger = logging.getLogger(__name__)
mcp_adapter = get_legacy_adapter()

router = APIRouter(prefix="/portfolio/notable-signals", tags=["portfolio"])


class NotableSignalResponse(BaseModel):
    """Response model for a notable signal"""
    ticker: str = Field(..., description="Stock ticker")
    company_name: Optional[str] = Field(None, description="Company name")
    signal_type: str = Field(..., description="BUY, SELL, HOLD, or NEUTRAL")
    signal_strength: str = Field(..., description="STRONG, MODERATE, or WEAK")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    headline: str = Field(..., description="Calm, informative headline")
    summary: str = Field(..., description="2-3 sentence explanation")
    key_reasons: List[str] = Field(..., description="Top 3 reasons for signal")
    timestamp: datetime = Field(..., description="When signal was generated")
    is_new: bool = Field(..., description="True if changed since yesterday")
    market_context: Optional[MarketContext] = Field(None, description="MCP context with citations")


class NotableSignalsResponse(BaseModel):
    """Response containing notable signals"""
    signals: List[NotableSignalResponse] = Field(default_factory=list, max_length=5)
    total_portfolio_stocks: int = Field(..., description="Total stocks in portfolio")
    last_updated: datetime = Field(default_factory=datetime.utcnow)


@router.get("", response_model=NotableSignalsResponse)
async def get_notable_signals(
    current_user: User = Depends(get_current_user),
    max_signals: int = 5
) -> NotableSignalsResponse:
    """
    Get 3-5 notable signals from user's portfolio
    
    Returns signals that:
    - Changed since yesterday (prioritized)
    - Have moderate to high confidence
    - Are diverse (mix of BUY/SELL/NEUTRAL)
    - Use calm, informative language
    
    Cached for 15 minutes to reduce load.
    """
    
    # Check cache first
    cache_key = f"notable_signals:user_{current_user.id}"
    cached = cache_manager.get(cache_key)
    if cached:
        logger.info(f"✅ Notable signals cache HIT for user {current_user.id}")
        return cached
    
    logger.info(f"Fetching notable signals for user {current_user.id}")
    
    try:
        # TODO: Implement actual signal fetching logic
        # For now, return empty response
        # In production, this would:
        # 1. Fetch user's portfolio positions
        # 2. Run analysis on each position
        # 3. Compare with yesterday's signals (detect changes)
        # 4. Score signals by notability (confidence, change, volatility)
        # 5. Select top 3-5 diverse signals
        # 6. Format with calm language
        # 7. Fetch MCP context for each signal (AFTER signal generation)
        
        signals_with_context = []
        # If we had actual signals, we would fetch MCP context for each:
        # for signal in notable_signals:
        #     try:
        #         context = await mcp_fetcher.fetch_context(
        #             ticker=signal.ticker,
        #             market="NSE",
        #             time_horizon="SHORT_TERM",
        #             signal_type=signal.signal_type,
        #             signal_reasons=signal.key_reasons,
        #             confidence=signal.confidence
        #         )
        #         signal.market_context = context
        #     except Exception as e:
        #         logger.warning(f"MCP context failed for {signal.ticker}: {e}")
        #         # Continue without context - system works if MCP fails
        #     signals_with_context.append(signal)
        
        response = NotableSignalsResponse(
            signals=[],
            total_portfolio_stocks=0,
            last_updated=datetime.utcnow()
        )
        
        # Cache for 15 minutes
        cache_manager.set(cache_key, response, ttl=900)
        
        logger.info(f"Returning {len(response.signals)} notable signals")
        return response
        
    except Exception as e:
        logger.error(f"Failed to fetch notable signals: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Unable to fetch notable signals. Please try again later."
        )


def _score_signal_notability(
    signal_type: str,
    confidence: float,
    is_new: bool,
    volatility: float,
    position_size: float
) -> float:
    """
    Score how notable/interesting a signal is
    
    Factors:
    - Is_new (changed since yesterday): +40 points
    - High confidence: +30 points
    - Large position: +15 points
    - High volatility: +15 points
    
    Returns: Score 0-100
    """
    score = 0.0
    
    # Changed signals are most notable
    if is_new:
        score += 40
    
    # High confidence signals
    score += confidence * 30
    
    # Larger positions matter more
    score += min(position_size / 20.0, 1.0) * 15  # Max 15 points if >20% position
    
    # High volatility signals
    score += min(volatility / 0.05, 1.0) * 15  # Max 15 points if >5% volatility
    
    return min(score, 100.0)


def _generate_calm_headline(
    ticker: str,
    signal_type: str,
    signal_strength: str,
    key_reason: str
) -> str:
    """
    Generate calm, informative headline
    
    Examples:
    - "Technical setup suggests potential upside"
    - "Weakness signal detected"
    - "Range-bound activity continues"
    
    NOT:
    - "BUY NOW! Huge opportunity!"
    - "SELL IMMEDIATELY before crash!"
    """
    
    if signal_type == "BUY":
        if signal_strength == "STRONG":
            return "Technical setup suggests potential upside"
        elif signal_strength == "MODERATE":
            return "Support levels holding, conditions improving"
        else:
            return "Minor positive indicators emerging"
    
    elif signal_type == "SELL":
        if signal_strength == "STRONG":
            return "Weakness signal detected"
        elif signal_strength == "MODERATE":
            return "Momentum showing signs of fatigue"
        else:
            return "Minor weakness indicators present"
    
    else:  # NEUTRAL or HOLD
        return "Range-bound activity continues"


def _generate_calm_summary(
    signal_type: str,
    key_reasons: List[str],
    confidence: float
) -> str:
    """
    Generate 2-3 sentence calm summary
    
    Explains why the signal matters without urgency or commands.
    """
    
    # Take first 2 reasons
    reason_text = ". ".join(key_reasons[:2])
    
    if signal_type == "BUY":
        return f"{reason_text}. These factors suggest conditions may favor entry in coming sessions."
    elif signal_type == "SELL":
        return f"{reason_text}. Current setup suggests heightened caution may be warranted."
    else:
        return f"{reason_text}. Price likely to remain rangebound until clearer direction emerges."
