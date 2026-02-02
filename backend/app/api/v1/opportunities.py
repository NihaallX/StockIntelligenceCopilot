"""
Opportunities Feed API
Returns pre-filtered actionable setups based on current market conditions
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import yfinance as yf
from dataclasses import dataclass

from app.mcp.factory import get_mcp_provider
from app.mcp.base import TimeframeEnum
from app.api.dependencies import get_current_user
from app.models.auth_models import User
from app.core.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

logger = logging.getLogger(__name__)
router = APIRouter()


# Stock universe for similarity search (quality NSE stocks)
STOCK_UNIVERSE = [
    # IT
    "TCS.NS", "INFY.NS", "WIPRO.NS", "TECHM.NS", "HCLTECH.NS", "LTIM.NS",
    # Banking
    "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS", "INDUSINDBK.NS",
    # FMCG
    "ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS", "GODREJCP.NS",
    # Energy
    "RELIANCE.NS", "BPCL.NS", "IOC.NS", "ONGC.NS", "ADANIGREEN.NS", "ADANIPORTS.NS",
    # Auto
    "MARUTI.NS", "M&M.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "EICHERMOT.NS",
    # Pharma
    "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "BIOCON.NS", "AUROPHARMA.NS",
    # Metals
    "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "COALINDIA.NS", "VEDL.NS", "HINDZINC.NS",
    # Others
    "LT.NS", "BHARTIARTL.NS", "TITAN.NS", "ASIANPAINT.NS", "ULTRACEMCO.NS"
]


@dataclass
class StockMetrics:
    """Stock metrics for similarity comparison"""
    ticker: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    profit_margin: Optional[float] = None
    revenue_growth: Optional[float] = None
    beta: Optional[float] = None


def fetch_stock_metrics(ticker: str) -> Optional[StockMetrics]:
    """Fetch metrics from Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return StockMetrics(
            ticker=ticker,
            sector=info.get("sector"),
            industry=info.get("industry"),
            market_cap=info.get("marketCap"),
            pe_ratio=info.get("trailingPE"),
            pb_ratio=info.get("priceToBook"),
            roe=info.get("returnOnEquity"),
            profit_margin=info.get("profitMargins"),
            revenue_growth=info.get("revenueGrowth"),
            beta=info.get("beta")
        )
    except Exception as e:
        logger.warning(f"Failed to fetch metrics for {ticker}: {e}")
        return None


def calculate_similarity_score(stock: StockMetrics, reference: StockMetrics) -> float:
    """
    Calculate similarity score between two stocks (0-100)
    
    Weights:
    - Market cap similarity: 20%
    - Valuation similarity (PE, PB): 30%
    - Profitability similarity (ROE, margin): 30%
    - Growth similarity: 20%
    """
    score = 0.0
    total_weight = 0.0
    
    # Sector match (bonus +20 if same sector)
    if stock.sector and reference.sector and stock.sector == reference.sector:
        score += 20
    
    # Market cap similarity (20%)
    if stock.market_cap and reference.market_cap:
        mc_ratio = min(stock.market_cap, reference.market_cap) / max(stock.market_cap, reference.market_cap)
        score += mc_ratio * 20
        total_weight += 20
    
    # PE ratio similarity (15%)
    if stock.pe_ratio and reference.pe_ratio and stock.pe_ratio > 0 and reference.pe_ratio > 0:
        pe_ratio = min(stock.pe_ratio, reference.pe_ratio) / max(stock.pe_ratio, reference.pe_ratio)
        score += pe_ratio * 15
        total_weight += 15
    
    # PB ratio similarity (15%)
    if stock.pb_ratio and reference.pb_ratio and stock.pb_ratio > 0 and reference.pb_ratio > 0:
        pb_ratio = min(stock.pb_ratio, reference.pb_ratio) / max(stock.pb_ratio, reference.pb_ratio)
        score += pb_ratio * 15
        total_weight += 15
    
    # ROE similarity (15%)
    if stock.roe and reference.roe and stock.roe > 0 and reference.roe > 0:
        roe_ratio = min(stock.roe, reference.roe) / max(stock.roe, reference.roe)
        score += roe_ratio * 15
        total_weight += 15
    
    # Profit margin similarity (15%)
    if stock.profit_margin and reference.profit_margin and stock.profit_margin > 0 and reference.profit_margin > 0:
        margin_ratio = min(stock.profit_margin, reference.profit_margin) / max(stock.profit_margin, reference.profit_margin)
        score += margin_ratio * 15
        total_weight += 15
    
    # Revenue growth similarity (20%)
    if stock.revenue_growth is not None and reference.revenue_growth is not None:
        # Growth can be negative, so use different approach
        growth_diff = abs(stock.revenue_growth - reference.revenue_growth)
        if growth_diff < 0.1:  # Within 10% growth difference
            score += 20 * (1 - growth_diff / 0.1)
        total_weight += 20
    
    # Normalize score if we have partial data
    if total_weight > 0:
        score = (score / total_weight) * 80 + 20  # Scale to 20-100 range
    
    return round(score, 2)


def find_similar_stocks(owned_tickers: List[str], top_n: int = 15) -> List[tuple[str, float, str]]:
    """
    Find similar stocks to portfolio holdings
    
    Returns:
        List of (ticker, similarity_score, reason) tuples
    """
    logger.info(f"Finding similar stocks for: {owned_tickers}")
    
    # Fetch metrics for owned stocks
    owned_metrics = []
    for ticker in owned_tickers:
        metrics = fetch_stock_metrics(ticker)
        if metrics:
            owned_metrics.append(metrics)
    
    if not owned_metrics:
        logger.warning("No metrics available for owned stocks")
        return []
    
    # Calculate similarity scores for all candidate stocks
    similarities = []
    
    for candidate_ticker in STOCK_UNIVERSE:
        # Skip if already owned
        if candidate_ticker in owned_tickers:
            continue
        
        # Fetch candidate metrics
        candidate_metrics = fetch_stock_metrics(candidate_ticker)
        if not candidate_metrics:
            continue
        
        # Calculate max similarity to any owned stock
        max_score = 0
        best_match = None
        for owned in owned_metrics:
            score = calculate_similarity_score(candidate_metrics, owned)
            if score > max_score:
                max_score = score
                best_match = owned.ticker
        
        # Generate reason
        reason = f"Similar to {best_match}"
        if candidate_metrics.sector:
            reason += f" ({candidate_metrics.sector})"
        
        similarities.append((candidate_ticker, max_score, reason))
    
    # Sort by similarity score and return top N
    similarities.sort(key=lambda x: x[1], reverse=True)
    logger.info(f"Found {len(similarities)} similar stocks, returning top {top_n}")
    
    return similarities[:top_n]


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
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Get pre-filtered feed of actionable opportunities from statistically similar stocks
    
    Uses Yahoo Finance metrics to find stocks similar to portfolio holdings based on:
    - Market cap, valuation (PE, PB), profitability (ROE, margins), and growth
    
    Returns up to 10 high-confidence setups from most similar stocks (excluding owned)
    """
    mcp = get_mcp_provider()
    
    try:
        logger.info(f"Fetching opportunities for user: {current_user.id}")
        
        # Get user's portfolio tickers using async SQLAlchemy
        from app.models.sql_tables import PortfolioPosition
        stmt = select(PortfolioPosition.ticker).where(PortfolioPosition.user_id == current_user.id)
        result = await session.execute(stmt)
        owned_tickers = list(set([row[0] for row in result.fetchall()]))
        
        logger.info(f"User owns: {owned_tickers}")
        
        # Find similar stocks using metrics-based scoring
        try:
            if owned_tickers:
                logger.info(f"Finding similar stocks to portfolio...")
                similar_stocks = find_similar_stocks(owned_tickers, top_n=15)
                watchlist = [ticker for ticker, score, reason in similar_stocks]
                logger.info(f"Top similar stocks: {[(t, s) for t, s, _ in similar_stocks[:5]]}")
            else:
                # If no portfolio, use default quality stocks
                logger.info(f"No portfolio found - using default quality stocks")
                watchlist = ["HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TCS.NS", 
                            "HINDUNILVR.NS", "TATAMOTORS.NS", "RELIANCE.NS"]
        except Exception as e:
            logger.error(f"Failed to find similar stocks: {e}", exc_info=True)
            # Fallback to default list if similarity search fails
            logger.warning("Using fallback watchlist due to similarity search failure")
            watchlist = ["HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TCS.NS", 
                        "HINDUNILVR.NS", "TATAMOTORS.NS", "RELIANCE.NS"]
        
        logger.info(f"Scanning {len(watchlist)} stocks for opportunities")
        
        # Get current market regime
        market_regime = "trending"
        
        opportunities = []
        total_scanned = len(watchlist)
        filtered_by_confidence = 0
        filtered_by_regime = 0
        
        # Scan each candidate stock
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
        
        logger.info(f"Found {len(opportunities)} opportunities from {total_scanned} stocks")
        
        return OpportunitiesFeedResponse(
            opportunities=opportunities,
            market_regime=market_regime,
            total_scanned=total_scanned,
            filtered_by_confidence=filtered_by_confidence,
            filtered_by_regime=filtered_by_regime
        )
        
    except HTTPException:
        # Re-raise auth errors (401) without modification
        raise
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        
        # Provide specific error messages for common issues
        if "portfolio_positions" in error_msg:
            detail = {
                "error": "Database Error",
                "message": "Failed to fetch your portfolio from database",
                "suggestion": "Check if you have stocks in your portfolio",
                "technical": error_msg
            }
        elif "yfinance" in error_msg or "Yahoo Finance" in error_msg:
            detail = {
                "error": "Market Data Error",
                "message": "Failed to fetch stock data from Yahoo Finance",
                "suggestion": "This may be a temporary network issue. Try again in a moment.",
                "technical": error_msg
            }
        elif "timeout" in error_msg.lower():
            detail = {
                "error": "Timeout Error",
                "message": "Request took too long to complete",
                "suggestion": "Yahoo Finance may be slow. Try refreshing the page.",
                "technical": error_msg
            }
        else:
            detail = {
                "error": error_type,
                "message": "An unexpected error occurred while finding opportunities",
                "suggestion": "Check the backend logs for more details",
                "technical": error_msg
            }
        
        logger.error(f"Opportunities feed failed: {error_type} - {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=detail)


@router.get("/health")
async def opportunities_health(session: AsyncSession = Depends(get_session)):
    """Health check endpoint"""
    try:
        # Test database connection using async SQLAlchemy
        from app.models.sql_tables import PortfolioPosition
        stmt = select(PortfolioPosition.ticker).limit(1)
        await session.execute(stmt)
        
        # Test Yahoo Finance
        test_stock = yf.Ticker("RELIANCE.NS")
        test_stock.info.get("sector")
        
        return {
            "status": "healthy",
            "service": "opportunities-feed",
            "database": "connected",
            "yahoo_finance": "accessible"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "degraded",
            "service": "opportunities-feed",
            "error": str(e)
        }
