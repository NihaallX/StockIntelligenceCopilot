"""
Opportunities Feed API
Returns pre-filtered actionable setups based on current market conditions
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

from app.mcp.factory import get_mcp_provider
from app.mcp.base import TimeframeEnum
from app.api.dependencies import get_current_user
from app.models.auth_models import User

router = APIRouter()


# Response Models
class OpportunityMCPContext(BaseModel):
    """Condensed MCP context for opportunity card"""
    price_vs_vwap: str  # "Above", "Below", "At"
    volume_ratio: float  # Current volume / avg volume
    index_alignment: str  # "Aligned", "Diverging", "Neutral"
    regime: str
    news_status: Literal["none", "positive", "negative", "mixed"]


class Opportunity(BaseModel):
    """Single actionable setup"""
    ticker: str
    setup_type: Literal["vwap_bounce", "vwap_rejection", "breakout", "breakdown", "consolidation"]
    confidence: int = Field(ge=0, le=100)
    time_sensitivity: Literal["immediate", "today", "this_week"]
    summary: str  # Plain English: "RELIANCE bouncing off VWAP with strong volume"
    mcp_context: OpportunityMCPContext
    current_price: float
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    bias: Literal["bullish", "bearish", "neutral"]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OpportunitiesFeedResponse(BaseModel):
    """Feed of actionable opportunities"""
    opportunities: List[Opportunity]
    market_regime: str
    total_scanned: int
    filtered_by_confidence: int
    filtered_by_regime: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Helper Functions
def _get_price_vs_vwap(price: float, vwap: float) -> str:
    """Determine price position relative to VWAP"""
    threshold = 0.002  # 0.2%
    if price > vwap * (1 + threshold):
        return "Above"
    elif price < vwap * (1 - threshold):
        return "Below"
    else:
        return "At"


def _calculate_volume_ratio(current_vol: float, avg_vol: float) -> float:
    """Calculate current volume as ratio of average"""
    if avg_vol == 0:
        return 1.0
    return round(current_vol / avg_vol, 2)


def _determine_index_alignment(ticker_change: float, index_change: float) -> str:
    """Check if ticker movement aligns with index"""
    # Both moving in same direction
    if (ticker_change > 0 and index_change > 0) or (ticker_change < 0 and index_change < 0):
        return "Aligned"
    # Significant divergence
    elif abs(ticker_change - index_change) > 1.0:
        return "Diverging"
    else:
        return "Neutral"


def _detect_setup_type(price: float, vwap: float, volume_ratio: float, 
                       trend: str) -> Literal["vwap_bounce", "vwap_rejection", "breakout", "breakdown", "consolidation"]:
    """Detect the type of setup from MCP data"""
    # Price near VWAP with strong volume
    if abs(price - vwap) / vwap < 0.005 and volume_ratio > 1.5:
        if trend == "bullish":
            return "vwap_bounce"
        elif trend == "bearish":
            return "vwap_rejection"
    
    # Strong move away from VWAP
    if price > vwap * 1.01 and volume_ratio > 2.0:
        return "breakout"
    elif price < vwap * 0.99 and volume_ratio > 2.0:
        return "breakdown"
    
    return "consolidation"


def _calculate_confidence(setup_type: str, volume_ratio: float, regime: str, 
                         index_alignment: str) -> int:
    """Calculate confidence score 0-100"""
    base_confidence = {
        "vwap_bounce": 75,
        "vwap_rejection": 75,
        "breakout": 70,
        "breakdown": 70,
        "consolidation": 50
    }
    
    confidence = base_confidence.get(setup_type, 50)
    
    # Volume boost
    if volume_ratio > 2.0:
        confidence += 10
    elif volume_ratio > 1.5:
        confidence += 5
    
    # Regime penalty
    if regime == "choppy":
        confidence -= 15
    elif regime == "low-liquidity":
        confidence -= 25
    
    # Index alignment boost
    if index_alignment == "Aligned":
        confidence += 10
    elif index_alignment == "Diverging":
        confidence -= 5
    
    return max(0, min(100, confidence))


def _determine_time_sensitivity(setup_type: str, volume_ratio: float) -> Literal["immediate", "today", "this_week"]:
    """Determine how time-sensitive the opportunity is"""
    if setup_type in ["breakout", "breakdown"] and volume_ratio > 2.0:
        return "immediate"
    elif setup_type in ["vwap_bounce", "vwap_rejection"]:
        return "today"
    else:
        return "this_week"


def _generate_summary(ticker: str, setup_type: str, price: float, vwap: float, volume_ratio: float) -> str:
    """Generate plain English summary"""
    templates = {
        "vwap_bounce": f"{ticker} bouncing off VWAP ({price:.2f}) with {volume_ratio:.1f}x volume",
        "vwap_rejection": f"{ticker} rejecting at VWAP ({price:.2f}) with {volume_ratio:.1f}x volume",
        "breakout": f"{ticker} breaking above VWAP ({vwap:.2f}) at {price:.2f} with strong volume",
        "breakdown": f"{ticker} breaking below VWAP ({vwap:.2f}) at {price:.2f} with strong volume",
        "consolidation": f"{ticker} consolidating near {price:.2f} (VWAP: {vwap:.2f})"
    }
    return templates.get(setup_type, f"{ticker} at {price:.2f}")


async def _scan_ticker_for_opportunities(
    ticker: str,
    mcp,
    market_regime: str
) -> Optional[Opportunity]:
    """Scan a single ticker and return opportunity if criteria met"""
    try:
        # TODO: Wire actual MCP data - using mock data for now
        # For testing purposes, create a mock opportunity
        import random
        
        setup_types = ["vwap_bounce", "vwap_rejection", "breakout", "breakdown", "consolidation"]
        setup_type = random.choice(setup_types)
        
        current_price = 100.0 + random.uniform(-10, 10)
        vwap = current_price * random.uniform(0.98, 1.02)
        volume_ratio = random.uniform(1.2, 2.5)
        
        # Calculate confidence
        base_confidence = 65 + random.randint(-10, 20)
        confidence = max(60, min(100, base_confidence))
        
        # Only return if confidence > 60%
        if confidence < 60:
            return None
        
        # Build opportunity
        opportunity = Opportunity(
            ticker=ticker,
            setup_type=setup_type,
            confidence=confidence,
            time_sensitivity="today" if setup_type in ["vwap_bounce", "vwap_rejection"] else "immediate",
            summary=_generate_summary(ticker, setup_type, current_price, vwap, volume_ratio),
            mcp_context=OpportunityMCPContext(
                price_vs_vwap=_get_price_vs_vwap(current_price, vwap),
                volume_ratio=volume_ratio,
                index_alignment="Aligned",
                regime=market_regime,
                news_status="none"
            ),
            current_price=current_price,
            target_price=current_price * 1.02 if setup_type in ["vwap_bounce", "breakout"] else current_price * 0.98,
            stop_loss=current_price * 0.98 if setup_type in ["vwap_bounce", "breakout"] else current_price * 1.02,
            bias="bullish" if setup_type in ["vwap_bounce", "breakout"] else "bearish"
        )
        
        return opportunity
        
    except Exception as e:
        print(f"Error scanning {ticker}: {e}")
        return None


@router.get("/feed", response_model=OpportunitiesFeedResponse)
async def get_opportunities_feed(
    current_user: User = Depends(get_current_user)
):
    """
    Get pre-filtered feed of actionable opportunities
    
    Returns up to 10 high-confidence setups that match current market regime
    """
    mcp = get_mcp_provider()
    
    try:
        # Get current market regime (could call market_pulse endpoint)
        # For now, simplified
        market_regime = "trending"
        
        # Scan portfolio tickers (in real implementation, get from user portfolio)
        watchlist = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
        
        opportunities = []
        total_scanned = len(watchlist)
        filtered_by_confidence = 0
        filtered_by_regime = 0
        
        for ticker in watchlist:
            opportunity = await _scan_ticker_for_opportunities(ticker, mcp, market_regime)
            if opportunity:
                opportunities.append(opportunity)
            else:
                filtered_by_confidence += 1
        
        # Sort by confidence descending
        opportunities.sort(key=lambda x: x.confidence, reverse=True)
        
        # Limit to top 10
        opportunities = opportunities[:10]
        
        return OpportunitiesFeedResponse(
            opportunities=opportunities,
            market_regime=market_regime,
            total_scanned=total_scanned,
            filtered_by_confidence=filtered_by_confidence,
            filtered_by_regime=filtered_by_regime
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate opportunities feed: {str(e)}")


@router.get("/health")
async def opportunities_health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "opportunities-feed"}
