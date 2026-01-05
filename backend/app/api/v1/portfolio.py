"""Portfolio tracking API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Literal
from decimal import Decimal
from datetime import datetime
import logging
import json

from app.models.portfolio_models import (
    PositionCreate,
    PositionUpdate,
    Position,
    PortfolioSummary,
    PortfolioRiskAnalysis
)
from app.models.auth_models import User, UserRiskProfile
from app.api.dependencies import get_current_user, get_user_risk_profile, get_session_context
from app.core.database import get_service_db
from app.core.audit import AuditLogger
from app.core.market_data.factory import ProviderFactory
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/validate-ticker/{ticker}")
async def validate_ticker(ticker: str):
    """Validate if a ticker exists and is tradeable"""
    try:
        ticker = ticker.upper()
        
        # For Indian stocks, must have .NS or .BO suffix
        if not (ticker.endswith('.NS') or ticker.endswith('.BO')):
            return {
                "valid": False,
                "ticker": ticker,
                "message": "Indian stock tickers must end with .NS (NSE) or .BO (BSE). Example: RELIANCE.NS"
            }
        
        provider = ProviderFactory.get_provider(ticker)
        
        # Validate with Yahoo Finance
        from app.core.market_data.indian_provider import IndianMarketDataProvider
        if isinstance(provider, IndianMarketDataProvider):
            is_valid, error_msg = provider.validate_ticker_exists(ticker)
            if not is_valid:
                return {
                    "valid": False,
                    "ticker": ticker,
                    "message": error_msg
                }
            
            return {
                "valid": True,
                "ticker": ticker,
                "message": "Valid stock ticker"
            }
        
        # Fallback for other providers
        return {
            "valid": provider.is_valid_ticker(ticker),
            "ticker": ticker,
            "message": "Valid ticker format"
        }
        
    except Exception as e:
        logger.error(f"Ticker validation error: {e}")
        return {
            "valid": False,
            "ticker": ticker,
            "message": str(e)
        }


@router.get("/historical-price/{ticker}/{date}")
async def get_historical_price(ticker: str, date: str):
    """
    Get the closing price for a stock on a specific date.
    Useful when you remember the date you bought but not the price.
    
    Args:
        ticker: Stock symbol (e.g., RELIANCE.NS)
        date: Date in YYYY-MM-DD format
        
    Returns:
        {"ticker": "RELIANCE.NS", "date": "2024-06-15", "price": 2845.50}
    """
    try:
        ticker = ticker.upper()
        
        # Validate format
        if not (ticker.endswith('.NS') or ticker.endswith('.BO')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Indian stock tickers must end with .NS or .BO"
            )
        
        provider = ProviderFactory.get_provider(ticker)
        
        from app.core.market_data.indian_provider import IndianMarketDataProvider
        if isinstance(provider, IndianMarketDataProvider):
            price = provider.get_historical_price(ticker, date)
            return {
                "ticker": ticker,
                "date": date,
                "price": round(price, 2)
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Historical price lookup only available for Indian stocks"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Historical price lookup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch historical price: {str(e)}"
        )


@router.post("/positions", response_model=Position, status_code=status.HTTP_201_CREATED)
async def add_position(
    position_data: PositionCreate,
    current_user: User = Depends(get_current_user),
    session_ctx: dict = Depends(get_session_context)
):
    """
    Add a new position to portfolio
    
    - Manually track stock holdings
    - Calculates cost basis
    - Validates against risk profile limits
    """
    db = get_service_db()
    
    try:
        # Validate ticker exists
        ticker_upper = position_data.ticker.upper()
        provider = ProviderFactory.get_provider(ticker_upper)
        
        if ticker_upper.endswith('.NS') or ticker_upper.endswith('.BO'):
            from app.core.market_data.indian_provider import IndianMarketDataProvider
            if isinstance(provider, IndianMarketDataProvider):
                is_valid, error_msg = provider.validate_ticker_exists(ticker_upper)
                if not is_valid:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=error_msg
                    )
        
        # Check if position already exists
        existing = db.table("portfolio_positions").select("id").eq("user_id", str(current_user.id)).eq("ticker", ticker_upper).execute()
        
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Position for {ticker_upper} already exists. Use update endpoint to modify."
            )
        
        # Calculate cost basis
        cost_basis = float(position_data.quantity * position_data.entry_price)
        
        # Create position
        position_record = {
            "user_id": str(current_user.id),
            "ticker": ticker_upper,
            "quantity": str(position_data.quantity),
            "entry_price": str(position_data.entry_price),
            "entry_date": position_data.entry_date.isoformat(),
            "notes": position_data.notes,
            "cost_basis": cost_basis
        }
        
        result = db.table("portfolio_positions").insert(position_record).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create position"
            )
        
        position = result.data[0]
        
        # Log to audit trail
        await AuditLogger.log_event(
            event_type="pos_add",
            user_id=session_ctx["user_id"],
            input_data=position_data.model_dump(),
            output_data={"position_id": position["id"], "ticker": position_data.ticker},
            session_id=session_ctx["session_id"],
            ip_address=session_ctx["ip_address"],
            user_agent=session_ctx["user_agent"],
            ticker=position_data.ticker
        )
        
        logger.info(f"Position added: {position['id']} | User: {current_user.id} | Ticker: {position_data.ticker}")
        
        return Position(**position)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add position error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add position"
        )


@router.get("/positions", response_model=List[Position])
async def list_positions(
    current_user: User = Depends(get_current_user)
):
    """
    Get all portfolio positions for current user
    
    Returns list of positions with current values and P&L
    """
    db = get_service_db()
    
    try:
        result = db.table("portfolio_positions").select("*").eq("user_id", str(current_user.id)).order("entry_date", desc=True).execute()
        
        if not result.data:
            return []
        
        positions = []
        for p in result.data:
            # Fetch current price from market data
            ticker = p["ticker"]
            try:
                provider = ProviderFactory.get_provider(ticker)
                quote = provider.get_current_quote(ticker)
                
                # Calculate P&L using the closing price
                current_price = float(quote.close)
                quantity = float(p["quantity"])
                entry_price = float(p["entry_price"])
                cost_basis = float(p["cost_basis"])
                
                current_value = current_price * quantity
                unrealized_pnl = current_value - cost_basis
                unrealized_pnl_percent = (unrealized_pnl / cost_basis) * 100 if cost_basis > 0 else 0
                
                # Update position with current data
                p["current_price"] = str(current_price)
                p["current_value"] = str(current_value)
                p["unrealized_pnl"] = str(unrealized_pnl)
                p["unrealized_pnl_percent"] = str(unrealized_pnl_percent)
                p["last_price_update"] = datetime.utcnow().isoformat()
                
            except Exception as e:
                logger.warning(f"Failed to fetch price for {ticker}: {e}")
                # Keep existing values if price fetch fails
            
            positions.append(Position(**p))
        
        return positions
        
    except Exception as e:
        logger.error(f"List positions error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve positions"
        )


@router.get("/positions/{position_id}", response_model=Position)
async def get_position(
    position_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific position by ID"""
    db = get_service_db()
    
    try:
        result = db.table("portfolio_positions").select("*").eq("id", position_id).eq("user_id", str(current_user.id)).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Position not found"
            )
        
        return Position(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get position error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve position"
        )


@router.patch("/positions/{position_id}", response_model=Position)
async def update_position(
    position_id: str,
    updates: PositionUpdate,
    current_user: User = Depends(get_current_user),
    session_ctx: dict = Depends(get_session_context)
):
    """Update existing position"""
    db = get_service_db()
    
    try:
        # Get existing position
        existing = db.table("portfolio_positions").select("*").eq("id", position_id).eq("user_id", str(current_user.id)).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Position not found"
            )
        
        # Prepare updates
        update_data = {}
        if updates.quantity is not None:
            update_data["quantity"] = str(updates.quantity)
        if updates.entry_price is not None:
            update_data["entry_price"] = str(updates.entry_price)
        if updates.notes is not None:
            update_data["notes"] = updates.notes
        
        # Recalculate cost basis if needed
        if updates.quantity or updates.entry_price:
            position = existing.data[0]
            quantity = float(updates.quantity) if updates.quantity else float(position["quantity"])
            entry_price = float(updates.entry_price) if updates.entry_price else float(position["entry_price"])
            update_data["cost_basis"] = quantity * entry_price
        
        # Update position
        result = db.table("portfolio_positions").update(update_data).eq("id", position_id).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update position"
            )
        
        logger.info(f"Position updated: {position_id} | User: {current_user.id}")
        
        return Position(**result.data[0])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update position error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update position"
        )


@router.delete("/positions/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_position(
    position_id: str,
    current_user: User = Depends(get_current_user),
    session_ctx: dict = Depends(get_session_context)
):
    """Remove position from portfolio"""
    db = get_service_db()
    
    try:
        # Get position for audit log
        existing = db.table("portfolio_positions").select("*").eq("id", position_id).eq("user_id", str(current_user.id)).execute()
        
        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Position not found"
            )
        
        position = existing.data[0]
        
        # Delete position
        db.table("portfolio_positions").delete().eq("id", position_id).execute()
        
        # Log to audit trail
        await AuditLogger.log_event(
            event_type="pos_del",
            user_id=session_ctx["user_id"],
            input_data={"position_id": position_id},
            output_data={"ticker": position["ticker"], "removed": True},
            session_id=session_ctx["session_id"],
            ip_address=session_ctx["ip_address"],
            user_agent=session_ctx["user_agent"],
            ticker=position["ticker"]
        )
        
        logger.info(f"Position deleted: {position_id} | User: {current_user.id} | Ticker: {position['ticker']}")
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete position error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete position"
        )


@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(
    current_user: User = Depends(get_current_user),
    user_profile: UserRiskProfile = Depends(get_user_risk_profile)
):
    """
    Get portfolio aggregate statistics
    
    - Total value and P&L
    - Concentration metrics
    - Risk analysis vs user profile
    """
    db = get_service_db()
    
    try:
        # Get all positions
        result = db.table("portfolio_positions").select("*").eq("user_id", str(current_user.id)).execute()
        
        if not result.data:
            return PortfolioSummary(
                total_positions=0,
                total_value=Decimal("0"),
                total_cost_basis=Decimal("0"),
                total_unrealized_pnl=Decimal("0"),
                total_unrealized_pnl_percent=Decimal("0"),
                largest_position_value=Decimal("0"),
                largest_position_ticker="",
                largest_position_percent=Decimal("0"),
                top_5_concentration=Decimal("0"),
                sector_concentration={},
                number_of_sectors=0,
                average_position_size=Decimal("0"),
                last_updated=datetime.utcnow()
            )
        
        positions = result.data
        
        # Calculate totals
        total_value = sum(Decimal(str(p.get("current_value", 0) or 0)) for p in positions)
        total_cost_basis = sum(Decimal(str(p.get("cost_basis", 0) or 0)) for p in positions)
        
        # If no current values, use cost basis as estimate
        if total_value == 0:
            total_value = total_cost_basis
        
        total_pnl = total_value - total_cost_basis
        total_pnl_pct = (total_pnl / total_cost_basis * 100) if total_cost_basis > 0 else Decimal("0")
        
        # Find largest position
        sorted_positions = sorted(positions, key=lambda p: Decimal(str(p.get("current_value", 0) or p.get("cost_basis", 0))), reverse=True)
        largest = sorted_positions[0] if sorted_positions else None
        largest_value = Decimal(str(largest.get("current_value", 0) or largest.get("cost_basis", 0))) if largest else Decimal("0")
        largest_pct = (largest_value / total_value * 100) if total_value > 0 else Decimal("0")
        
        # Top 5 concentration
        top_5_value = sum(Decimal(str(p.get("current_value", 0) or p.get("cost_basis", 0))) for p in sorted_positions[:5])
        top_5_concentration = (top_5_value / total_value * 100) if total_value > 0 else Decimal("0")
        
        # Average position size
        avg_position = total_value / len(positions) if positions else Decimal("0")
        
        return PortfolioSummary(
            total_positions=len(positions),
            total_value=total_value,
            total_cost_basis=total_cost_basis,
            total_unrealized_pnl=total_pnl,
            total_unrealized_pnl_percent=total_pnl_pct,
            largest_position_value=largest_value,
            largest_position_ticker=largest["ticker"] if largest else "",
            largest_position_percent=largest_pct,
            top_5_concentration=top_5_concentration,
            sector_concentration={},  # TODO: Add sector mapping
            number_of_sectors=0,  # TODO: Calculate from fundamentals
            average_position_size=avg_position,
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Portfolio summary error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate portfolio summary"
        )


# =====================================================
# PORTFOLIO AI SUGGESTIONS
# =====================================================

from pydantic import BaseModel, Field
from typing import Literal, Optional
from app.core.orchestrator.pipeline import InsightOrchestrator
from app.models.schemas import AnalysisRequest


class PortfolioPosition(BaseModel):
    """User's current portfolio position"""
    ticker: str = Field(..., description="Stock symbol (e.g., RELIANCE.NS)")
    quantity: int = Field(..., gt=0)
    entry_price: float = Field(..., gt=0)
    current_price: Optional[float] = None


class PortfolioSuggestion(BaseModel):
    """AI-generated opportunity nudge (non-directive)"""
    nudge: str = Field(..., description="Conditional, non-commanding suggestion")
    context: str = Field(..., description="Risk/reward trade-off explanation")
    priority: Literal["HIGH", "MEDIUM", "LOW"]
    applies_to: List[str] = Field(..., description="Tickers this nudge relates to")


class PortfolioAnalysisRequest(BaseModel):
    """Request to analyze entire portfolio"""
    positions: List[PortfolioPosition] = Field(..., min_length=1, max_length=50)
    risk_tolerance: Literal["conservative", "moderate", "aggressive"] = "moderate"
    time_horizon: Literal["short_term", "medium_term", "long_term"] = "medium_term"


class PortfolioAnalysisResponse(BaseModel):
    """Portfolio analysis with AI suggestions"""
    success: bool
    portfolio_score: int = Field(..., ge=0, le=100)
    portfolio_health: str
    total_value: float
    total_pnl: float
    total_pnl_percent: float
    suggestions: List[PortfolioSuggestion]
    risk_assessment: str
    diversification_score: int = Field(..., ge=0, le=100)
    processing_time_ms: int
    error: Optional[str] = None


@router.post("/ai-suggestions", response_model=PortfolioAnalysisResponse)
async def get_ai_suggestions(
    request: PortfolioAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered portfolio opportunity nudges (NON-DIRECTIVE).
    
    Analyzes portfolio and provides conditional, risk-first suggestions.
    Does NOT command actions - only explains trade-offs.
    """
    import time
    import json
    start_time = time.time()
    
    logger.info(f"🎯 AI suggestions for user {current_user.id}, {len(request.positions)} positions")
    
    try:
        from app.core.fundamentals import FundamentalProvider
        from app.core.scenarios import ScenarioGenerator
        from app.api.v1.enhanced import _calculate_combined_score, _generate_recommendation
        from app.models.auth_models import UserRiskProfile
        
        orchestrator = InsightOrchestrator()
        position_analyses = []
        
        # Simple wrapper to hold combined_score and recommendation
        class AnalysisResult:
            def __init__(self, score, rec):
                self.combined_score = score
                self.recommendation = rec
        
        # Analyze each position with enhanced analysis
        for pos in request.positions:
            try:
                # Get technical analysis
                analysis_request = AnalysisRequest(
                    ticker=pos.ticker,
                    time_horizon=request.time_horizon,
                    lookback_days=90
                )
                analysis = await orchestrator.analyze_stock(analysis_request)
                technical_insight = analysis.insight if analysis.success else None
                
                if not technical_insight:
                    position_analyses.append({"position": pos, "analysis": None})
                    continue
                
                # Get fundamental analysis (optional)
                fundamental_score = None
                try:
                    fundamental_provider = FundamentalProvider()
                    fundamental_data = fundamental_provider.fetch_fundamentals(pos.ticker)
                    if fundamental_data:
                        fundamental_score = fundamental_provider.score_fundamentals(fundamental_data)
                except Exception as fund_err:
                    logger.debug(f"Fundamentals unavailable for {pos.ticker}: {fund_err}")
                
                # Get scenario analysis (optional)
                scenario_analysis = None
                try:
                    scenario_gen = ScenarioGenerator()
                    scenario_analysis = scenario_gen.generate_scenarios(
                        ticker=pos.ticker,
                        signal=technical_insight.signal,
                        fundamentals_score=fundamental_score.overall_score if fundamental_score else None,
                        time_horizon_days=90
                    )
                except Exception as scen_err:
                    logger.debug(f"Scenarios unavailable for {pos.ticker}: {scen_err}")
                
                # Calculate combined score
                combined_score = _calculate_combined_score(
                    technical_insight.signal,
                    fundamental_score,
                    scenario_analysis
                )
                
                # Generate recommendation (using simple approach without full user profile)
                signal_type = technical_insight.signal.strength.signal_type
                confidence = technical_insight.signal.strength.confidence
                
                # Generate recommendation based on signal (Option B: Balanced - confident but defensible)
                if signal_type == "BUY":
                    if confidence > 0.8:
                        recommendation = "STRONG BUY SIGNAL DETECTED - High-probability entry zone identified with favorable risk profile."
                    elif confidence > 0.6:
                        recommendation = "BUY SIGNAL DETECTED - Conditions favor entry with appropriate position sizing."
                    else:
                        recommendation = "WEAK BUY SIGNAL - Marginal setup. Stronger confirmation recommended before entry."
                elif signal_type == "SELL":
                    if confidence > 0.8:
                        recommendation = "STRONG CAUTION SIGNAL - High-confidence bearish pattern detected. Review exposure recommended."
                    elif confidence > 0.6:
                        recommendation = "CAUTION SIGNAL DETECTED - Conditions suggest reducing exposure may lower downside risk."
                    else:
                        recommendation = "MIXED SIGNALS - Uncertain direction. Close monitoring recommended."
                else:
                    recommendation = "NEUTRAL - No clear directional bias. Wait for better setup."
                
                # Adjust based on fundamentals if available
                if fundamental_score:
                    if fundamental_score.overall_assessment == "POOR" and signal_type == "BUY":
                        recommendation = "HOLD - Technical signals positive but fundamentals weak. Waiting for fundamental confirmation may reduce risk."
                    elif fundamental_score.overall_assessment == "STRONG" and signal_type == "SELL":
                        recommendation = "HOLD - Technical caution but fundamentals strong. Long-term holders may consider maintaining position."
                
                position_analyses.append({
                    "position": pos,
                    "analysis": AnalysisResult(combined_score, recommendation)
                })
            except Exception as e:
                logger.error(f"Failed {pos.ticker}: {e}")
                position_analyses.append({"position": pos, "analysis": None})
        
        # Calculate portfolio metrics
        total_value = sum(pos.quantity * (pos.current_price or pos.entry_price) 
                         for pos in request.positions)
        total_cost = sum(pos.quantity * pos.entry_price for pos in request.positions)
        total_pnl = total_value - total_cost
        total_pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0
        
        # Build structured data for LLM
        portfolio_context = {
            "total_positions": len(request.positions),
            "total_value_inr": round(total_value, 2),
            "total_pnl_percent": round(total_pnl_percent, 2),
            "positions": []
        }
        
        scores = []
        for item in position_analyses:
            pos, analysis = item["position"], item["analysis"]
            if not analysis:
                continue
            
            score = int(analysis.combined_score)
            scores.append(score)
            pnl_pct = ((pos.current_price or pos.entry_price) / pos.entry_price - 1) * 100
            position_value = pos.quantity * (pos.current_price or pos.entry_price)
            pct_of_portfolio = (position_value / total_value * 100) if total_value > 0 else 0
            
            portfolio_context["positions"].append({
                "ticker": pos.ticker,
                "score": score,
                "recommendation": analysis.recommendation,
                "pnl_percent": round(pnl_pct, 2),
                "percent_of_portfolio": round(pct_of_portfolio, 2),
                "risk_level": "HIGH" if score < 40 else "MEDIUM" if score < 70 else "LOW"
            })
        
        # Portfolio health
        portfolio_score = int(sum(scores) / len(scores)) if scores else 50
        health = "HEALTHY" if portfolio_score >= 70 else "NEEDS_ATTENTION" if portfolio_score >= 50 else "CRITICAL"
        
        # Risk assessment
        high_risk = sum(1 for s in scores if s < 40)
        risk_pct = high_risk / len(scores) if scores else 0
        if risk_pct > 0.4:
            risk_assessment = "40%+ positions showing weakness"
        elif risk_pct > 0.2:
            risk_assessment = "Some positions need attention"
        else:
            risk_assessment = "Portfolio appears stable"
        
        # Call LLM to generate nudges
        nudges = await _generate_opportunity_nudges(portfolio_context, portfolio_score, risk_assessment)
        
        # Diversification
        div_score = min(100, len(request.positions) * 6)  # 100 at 15+ stocks
        
        processing_time = int((time.time() - start_time) * 1000)
        
        logger.info(f"✅ AI suggestions complete: score={portfolio_score}, {len(nudges)} nudges")
        
        return PortfolioAnalysisResponse(
            success=True,
            portfolio_score=portfolio_score,
            portfolio_health=health,
            total_value=total_value,
            total_pnl=total_pnl,
            total_pnl_percent=total_pnl_percent,
            suggestions=nudges,
            risk_assessment=risk_assessment,
            diversification_score=div_score,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        logger.error(f"❌ AI suggestions failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"AI suggestions failed: {str(e)}"
        )


async def _generate_opportunity_nudges(portfolio_context: dict, portfolio_score: int, risk_assessment: str) -> List[PortfolioSuggestion]:
    """Generate non-directive opportunity nudges using LLM"""
    
    system_prompt = """You are a confident financial analysis assistant providing actionable portfolio insights.

CRITICAL RULES:
- Use CLEAR, CONFIDENT language (Option B: Balanced System)
- Be direct but defensible
- Use signal-based framing: "Signal detected", "Pattern identified", "Conditions favor"
- AVOID absolute commands: "buy now", "sell immediately", "must"
- ALLOWED confident language: "signals suggest", "conditions favor", "pattern detected"

LANGUAGE STYLE:
✅ GOOD (Option B - Confident but Defensible):
- "RELIANCE showing weakness signal. Reducing position size may lower downside exposure."
- "TCS concentration at 35% creates elevated portfolio risk. Diversification signals favor rebalancing."
- "IT sector signals remain strong. Current holdings show favorable momentum."

❌ BAD (Too weak/conditional):
- "If you're worried, you might want to consider..."
- "It could be possible that..."

❌ BAD (Too directive):
- "Sell RELIANCE immediately."
- "You must diversify now."

TONE: Professional analyst providing signal-based insights, not personal commands

OUTPUT FORMAT (JSON):
[
  {
    "nudge": "Clear signal-based suggestion (1-2 sentences)",
    "context": "Evidence supporting the signal (1 sentence)",
    "priority": "HIGH|MEDIUM|LOW",
    "applies_to": ["TICKER.NS"]
  }
]

Be confident and clear. Frame as detected signals and identified patterns, not commands."""

    user_prompt = f"""Portfolio Data:
{json.dumps(portfolio_context, indent=2)}

Portfolio Score: {portfolio_score}/100
Risk: {risk_assessment}

Generate 2-4 simple, beginner-friendly suggestions. Use everyday language."""

    try:
        # Use OpenAI-compatible API
        import openai
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY if hasattr(settings, 'OPENAI_API_KEY') else "")
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        content = response.choices[0].message.content
        
        # Parse JSON response
        nudges_data = json.loads(content)
        
        return [PortfolioSuggestion(**nudge) for nudge in nudges_data]
        
    except Exception as e:
        logger.error(f"LLM nudge generation failed: {e}")
        # Fallback to rule-based nudges
        return _generate_fallback_nudges(portfolio_context, portfolio_score, risk_assessment)


def _generate_fallback_nudges(portfolio_context: dict, portfolio_score: int, risk_assessment: str) -> List[PortfolioSuggestion]:
    """Fallback nudges if LLM fails - Simple beginner-friendly language"""
    nudges = []
    
    # Find weak positions
    weak = [p for p in portfolio_context["positions"] if p["score"] < 40]
    strong = [p for p in portfolio_context["positions"] if p["score"] > 70]
    concentrated = [p for p in portfolio_context["positions"] if p["percent_of_portfolio"] > 25]
    
    if weak:
        tickers = [p["ticker"] for p in weak[:2]]
        nudges.append(PortfolioSuggestion(
            nudge=f"Weakness signal detected in {', '.join(tickers)}. Reducing position size may lower downside exposure.",
            context="Technical indicators show declining momentum. Position reduction could limit losses while allowing recovery potential.",
            priority="HIGH" if len(weak) > 2 else "MEDIUM",
            applies_to=tickers
        ))
    
    if concentrated:
        ticker = concentrated[0]["ticker"]
        pct = concentrated[0]["percent_of_portfolio"]
        nudges.append(PortfolioSuggestion(
            nudge=f"Concentration alert: {ticker} represents {pct:.0f}% of portfolio. Diversification signals favor broader allocation.",
            context="High single-stock concentration creates elevated risk. Multi-stock allocation provides better risk distribution.",
            priority="MEDIUM",
            applies_to=[ticker]
        ))
    
    if strong and portfolio_score > 60:
        tickers = [p["ticker"] for p in strong[:2]]
        nudges.append(PortfolioSuggestion(
            nudge=f"Strong momentum signals in {', '.join(tickers)}. Current positions show favorable pattern continuation.",
            context="Technical strength indicators remain positive. Holding current allocation aligns with momentum strategy.",
            priority="LOW",
            applies_to=tickers
        ))
    
    if not nudges:
        nudges.append(PortfolioSuggestion(
            nudge="Portfolio shows balanced allocation. No high-priority signals detected.",
            context="Current metrics within normal ranges. Continue regular monitoring.",
            priority="LOW",
            applies_to=[]
        ))
    
    return nudges[:4]
