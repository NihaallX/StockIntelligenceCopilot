"""
Market Pulse API
=================

Provides market regime, index bias, and liquidity assessment for intraday trading decisions.

Answers: "Is today even worth trading?"
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import logging

from app.api.dependencies import get_current_user
from app.models.auth_models import User
from app.mcp.factory import get_mcp_provider
from app.mcp.base import TimeframeEnum

logger = logging.getLogger(__name__)
router = APIRouter()


class IndexBias(BaseModel):
    """Index directional bias"""
    name: str = Field(..., description="Index name (NIFTY/BANKNIFTY)")
    bias: str = Field(..., description="Strong/Weak/Neutral")
    change_percent: Optional[float] = None


class MarketPulse(BaseModel):
    """Market pulse summary for the day"""
    regime: str = Field(..., description="choppy/trending/range-bound/low-liquidity")
    index_bias: list[IndexBias] = Field(..., description="NIFTY and BANKNIFTY bias")
    liquidity: str = Field(..., description="low/normal/high")
    summary: str = Field(..., description="Plain English market summary")
    worth_trading: bool = Field(..., description="Whether conditions favor active trading")
    timestamp: str = Field(..., description="Data timestamp")
    session_time: str = Field(..., description="early_open/mid_day/closing/after_hours")


@router.get("/pulse", response_model=MarketPulse)
async def get_market_pulse(
    current_user: User = Depends(get_current_user)
):
    """
    Get today's market pulse - regime, bias, liquidity assessment
    
    **Purpose:** Answer "Is today worth trading?"
    
    **Returns:**
    - Market regime (choppy/trending/range-bound)
    - Index bias (NIFTY/BANKNIFTY direction)
    - Liquidity state (low/normal/high)
    - Plain English summary
    - Whether conditions favor trading
    
    **UX Flow:**
    - This is the FIRST thing users see after login
    - Helps them decide: trade today or stand down
    - No search bar shown until user clicks "View Opportunities"
    """
    try:
        # Get MCP provider for market data
        mcp = get_mcp_provider()
        
        # Fetch regime context for major indices
        # Using NIFTY as proxy for overall market
        # Note: Using NIFTYBEES (ETF) as proxy since ^NSEI not supported by all providers
        nifty_context = await mcp.build_market_regime_context(
            symbol="NIFTYBEES.NS",  # NIFTY ETF as proxy
            timeframe=TimeframeEnum.FIFTEEN_MIN,
            signal_direction=None,
            current_hour=datetime.now().hour
        )
        
        # Determine regime
        regime = _map_regime(nifty_context.trade_environment)
        
        # Get index biases
        index_bias = []
        
        # NIFTY bias
        nifty_bias = _determine_bias(
            nifty_context.index_change_percent,
            nifty_context.volume_state
        )
        index_bias.append(IndexBias(
            name="NIFTY",
            bias=nifty_bias,
            change_percent=nifty_context.index_change_percent
        ))
        
        # Try to get BANKNIFTY (optional)
        try:
            banknifty_context = await mcp.build_market_regime_context(
                symbol="BANKBEES.NS",  # BANKNIFTY ETF as proxy
                timeframe=TimeframeEnum.FIFTEEN_MIN,
                signal_direction=None,
                current_hour=datetime.now().hour
            )
            banknifty_bias = _determine_bias(
                banknifty_context.index_change_percent,
                banknifty_context.volume_state
            )
            index_bias.append(IndexBias(
                name="BANKNIFTY",
                bias=banknifty_bias,
                change_percent=banknifty_context.index_change_percent
            ))
        except Exception as e:
            logger.warning(f"Could not fetch BANKNIFTY data: {e}")
            index_bias.append(IndexBias(name="BANKNIFTY", bias="Unknown"))
        
        # Liquidity assessment
        liquidity = _assess_liquidity(nifty_context.volume_state)
        
        # Generate plain English summary
        summary = _generate_summary(regime, nifty_bias, liquidity)
        
        # Determine if worth trading
        worth_trading = _is_worth_trading(regime, liquidity)
        
        # Session time
        session_time = _get_session_time(datetime.now().hour)
        
        await mcp.cleanup()
        
        return MarketPulse(
            regime=regime,
            index_bias=index_bias,
            liquidity=liquidity,
            summary=summary,
            worth_trading=worth_trading,
            timestamp=datetime.now().isoformat(),
            session_time=session_time
        )
        
    except Exception as e:
        logger.error(f"Market pulse fetch failed: {e}")
        # Return fallback pulse
        return _get_fallback_pulse()


def _map_regime(trade_environment: str) -> str:
    """Map MCP trade environment to regime"""
    mapping = {
        "trending": "trending",
        "choppy": "choppy",
        "stable": "range-bound",
        "volatile": "choppy",
        "illiquid": "low-liquidity"
    }
    return mapping.get(trade_environment, "range-bound")


def _determine_bias(change_percent: Optional[float], volume_state: str) -> str:
    """Determine index bias from change and volume"""
    if change_percent is None:
        return "Neutral"
    
    # Strong bias: >1% move with volume support
    if abs(change_percent) > 1.0 and volume_state == "expansion":
        return "Strong" if change_percent > 0 else "Weak"
    
    # Moderate bias: >0.5% move
    if abs(change_percent) > 0.5:
        return "Moderate" if change_percent > 0 else "Weak"
    
    return "Neutral"


def _assess_liquidity(volume_state: str) -> str:
    """Assess market liquidity"""
    if volume_state == "dry":
        return "low"
    elif volume_state == "expansion":
        return "high"
    return "normal"


def _generate_summary(regime: str, bias: str, liquidity: str) -> str:
    """Generate plain English market summary"""
    
    regime_desc = {
        "trending": "trending with good follow-through",
        "choppy": "choppy with low follow-through",
        "range-bound": "range-bound with limited moves",
        "low-liquidity": "experiencing low liquidity"
    }
    
    liquidity_advice = {
        "low": "Quick exits recommended.",
        "normal": "Normal trading conditions.",
        "high": "Good participation levels."
    }
    
    regime_text = regime_desc.get(regime, "showing mixed behavior")
    liquidity_text = liquidity_advice.get(liquidity, "")
    
    if regime == "choppy" or liquidity == "low":
        return f"Market is {regime_text}. Small moves, {liquidity_text}"
    elif regime == "trending" and liquidity == "high":
        return f"Market is {regime_text}. {liquidity_text} Conditions favor trend following."
    else:
        return f"Market is {regime_text}. {liquidity_text}"


def _is_worth_trading(regime: str, liquidity: str) -> bool:
    """Determine if conditions favor active trading"""
    # Not worth trading if choppy AND low liquidity
    if regime == "choppy" and liquidity == "low":
        return False
    
    # Not worth trading if low liquidity regime
    if regime == "low-liquidity":
        return False
    
    # Worth trading in most other conditions
    return True


def _get_session_time(hour: int) -> str:
    """Get current session time"""
    if 9 <= hour < 11:
        return "early_open"
    elif 11 <= hour < 13:
        return "mid_day"
    elif 13 <= hour < 15:
        return "closing"
    else:
        return "after_hours"


def _get_fallback_pulse() -> MarketPulse:
    """Return fallback pulse when data unavailable"""
    return MarketPulse(
        regime="range-bound",
        index_bias=[
            IndexBias(name="NIFTY", bias="Neutral"),
            IndexBias(name="BANKNIFTY", bias="Neutral")
        ],
        liquidity="normal",
        summary="Market data temporarily unavailable. Proceed with caution.",
        worth_trading=False,
        timestamp=datetime.now().isoformat(),
        session_time=_get_session_time(datetime.now().hour)
    )
