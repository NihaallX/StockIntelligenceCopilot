"""Intraday Portfolio Intelligence API Routes

Endpoints for the new intraday system:
- Daily overview ("Today's Watch")
- Stock detail view
- Portfolio monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from app.core.intraday import (
    IntradayDataProvider,
    MethodDetector,
    MarketRegimeContext,
    LanguageFormatter
)
from app.api.dependencies import get_current_user
from app.models.auth_models import User
from app.core.database import get_db

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/intraday", tags=["intraday"])


# Pydantic models for requests/responses

class TodaysWatchResponse(BaseModel):
    """Response for daily overview"""
    ticker: str
    tags: List[str]
    one_line: str
    severity: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "RELIANCE.NS",
                "tags": ["⚠️ Weak vs index", "📊 High exposure"],
                "one_line": "This stock shows weakness and represents large portfolio exposure.",
                "severity": "alert"
            }
        }


class StockDetailResponse(BaseModel):
    """Response for detailed stock view"""
    ticker: str
    explanation: str
    conditional_note: str
    context_badge: dict
    risk_summary: str
    severity: str
    detected_at: str
    
    # Live metrics
    current_price: float
    change_pct: float
    vwap: float
    volume_ratio: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "RELIANCE.NS",
                "explanation": "**Trend Weakness Detected**: RELIANCE.NS is showing signs...",
                "conditional_note": "If price stays below ₹2,850, downside risk may increase.",
                "context_badge": {
                    "labels": ["Index-Led"],
                    "tooltip": "Stock movement driven by index pressure"
                },
                "risk_summary": "🟡 Elevated factors present",
                "severity": "caution",
                "detected_at": "2026-01-06T14:30:00",
                "current_price": 2845.50,
                "change_pct": -1.2,
                "vwap": 2855.30,
                "volume_ratio": 0.8
            }
        }


class PortfolioOverviewRequest(BaseModel):
    """Request for portfolio monitoring"""
    user_id: str = Field(..., description="User identifier")
    tickers: Optional[List[str]] = Field(
        None, 
        description="Specific tickers to monitor (if None, monitors all holdings)"
    )


# Initialize components
data_provider = IntradayDataProvider()
detector = MethodDetector()
regime_context = MarketRegimeContext()
formatter = LanguageFormatter()


@router.get("/todays-watch", response_model=List[TodaysWatchResponse])
async def get_todays_watch(
    tickers: Optional[str] = None,
    min_severity: str = "watch",
    current_user: User = Depends(get_current_user)
):
    """
    Get daily overview of flagged stocks from user's portfolio.
    
    This is the homepage "Today's Watch" feature.
    
    Query params:
    - tickers: Comma-separated list (overrides portfolio)
    - min_severity: Filter level ("watch", "caution", "alert")
    
    Returns list of flagged stocks sorted by severity.
    """
    try:
        # Parse tickers
        if tickers:
            ticker_list = [t.strip() for t in tickers.split(",")]
        else:
            # Get tickers from user's portfolio
            try:
                logger.info(f"Fetching portfolio for user: {current_user.id}")
                db = get_db()
                portfolio_result = db.table("portfolio_positions").select("ticker").eq("user_id", current_user.id).execute()
                
                logger.info(f"Portfolio query result: {portfolio_result.data}")
                
                if portfolio_result.data and len(portfolio_result.data) > 0:
                    # Extract unique tickers from portfolio
                    ticker_list = list(set([p["ticker"] for p in portfolio_result.data]))
                    logger.info(f"User {current_user.id}: Loaded {len(ticker_list)} tickers from portfolio: {ticker_list}")
                else:
                    # Fallback to default watchlist if portfolio is empty
                    ticker_list = [
                        "RELIANCE.NS", "TCS.NS", "INFY.NS", 
                        "HDFCBANK.NS", "ICICIBANK.NS"
                    ]
                    logger.info(f"User {current_user.id}: Using default watchlist (empty portfolio)")
            except Exception as db_error:
                logger.error(f"Portfolio fetch failed: {db_error}", exc_info=True)
                ticker_list = [
                    "RELIANCE.NS", "TCS.NS", "INFY.NS", 
                    "HDFCBANK.NS", "ICICIBANK.NS"
                ]
        
        detections = []
        
        for ticker in ticker_list:
            # Get metrics
            metrics = data_provider.get_intraday_metrics(ticker)
            if not metrics:
                continue
            
            # Count red candles
            red_candles = data_provider.count_red_candles_with_volume(ticker)
            
            # Run detection
            detection = detector.detect_all(
                metrics=metrics,
                red_candles_count=red_candles
            )
            
            # Only include if tags found
            if detection.tags:
                detections.append(detection)
        
        # Filter by severity
        filtered = detector.filter_by_severity(detections, min_severity)
        
        # Format for display
        formatted = formatter.format_batch_overview(filtered)
        
        return formatted
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating daily overview: {str(e)}"
        )


@router.get("/stock/{ticker}", response_model=StockDetailResponse)
async def get_stock_detail(ticker: str):
    """
    Get detailed view for a specific stock.
    
    Includes:
    - Detection explanations
    - Conditional notes
    - Market context
    - Live metrics
    """
    try:
        # Get metrics
        metrics = data_provider.get_intraday_metrics(ticker)
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Could not fetch data for {ticker}"
            )
        
        # Count red candles
        red_candles = data_provider.count_red_candles_with_volume(ticker)
        
        # Run detection
        detection = detector.detect_all(
            metrics=metrics,
            red_candles_count=red_candles
        )
        
        # Get market regime context
        market_context = regime_context.detect_regime(metrics)
        
        # Format detailed view
        formatted = formatter.format_detailed_view(
            detection=detection,
            metrics=metrics,
            market_context=market_context
        )
        
        # Add live metrics
        formatted.update({
            "current_price": metrics.current_price,
            "change_pct": metrics.stock_change_pct,
            "vwap": metrics.vwap,
            "volume_ratio": metrics.volume_ratio
        })
        
        return formatted
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing {ticker}: {str(e)}"
        )


@router.post("/portfolio-monitor")
async def monitor_portfolio(request: PortfolioOverviewRequest):
    """
    Monitor user's portfolio for risks and opportunities.
    
    Returns flagged positions with portfolio-specific context.
    
    TODO: Integrate with database to fetch user positions.
    """
    try:
        # TODO: Fetch user's actual portfolio from database
        # For now, return mock structure
        
        return {
            "user_id": request.user_id,
            "monitored_at": datetime.now().isoformat(),
            "flagged_positions": [],
            "portfolio_summary": {
                "total_positions": 0,
                "flagged_count": 0,
                "alert_count": 0,
                "caution_count": 0
            },
            "note": "Portfolio integration pending. Use /todays-watch for now."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error monitoring portfolio: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check for intraday system"""
    try:
        # Quick test: fetch data for one ticker
        test_metrics = data_provider.get_intraday_metrics("RELIANCE.NS")
        
        return {
            "status": "healthy",
            "data_provider": "operational" if test_metrics else "degraded",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
