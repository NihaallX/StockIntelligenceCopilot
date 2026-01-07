"""Enhanced analysis API with fundamental and scenario analysis"""

from fastapi import APIRouter, Depends, HTTPException, status
import logging
from decimal import Decimal
from datetime import datetime

from app.models.portfolio_models import EnhancedInsightRequest, EnhancedInsightResponse
from app.models.schemas import AnalysisRequest
from app.models.auth_models import User, UserRiskProfile
from app.api.dependencies import get_current_user, get_user_risk_profile, get_session_context
from app.core.orchestrator import orchestrator
from app.core.fundamentals import FundamentalProviderCompat as FundamentalProvider
from app.core.scenarios import ScenarioGenerator
from app.core.audit import AuditLogger
from app.mcp.legacy_adapter import get_legacy_adapter
from app.core.context_agent.models import MarketContext

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize new MCP adapter (replaces old MCPContextFetcher)
mcp_adapter = get_legacy_adapter()


@router.post("/enhanced", response_model=EnhancedInsightResponse)
async def enhanced_analysis(
    request: EnhancedInsightRequest,
    current_user: User = Depends(get_current_user),
    user_profile: UserRiskProfile = Depends(get_user_risk_profile),
    session_ctx: dict = Depends(get_session_context)
):
    """
    Enhanced stock analysis combining technical + fundamental + scenario analysis
    
    **Phase 2B Feature:**
    - Technical analysis (existing pipeline)
    - Fundamental scoring (valuation, growth, profitability, financial health)
    - Scenario analysis (best/base/worst case with probability weighting)
    - LLM-enhanced explanations (coming soon)
    
    Provides comprehensive view for informed decision-making.
    """
    
    try:
        # Step 1: Run standard technical analysis
        technical_request = AnalysisRequest(
            ticker=request.ticker,
            time_horizon=request.time_horizon,
            risk_tolerance=request.risk_tolerance,
            lookback_days=request.lookback_days
        )
        
        logger.info(f"Starting enhanced analysis for {request.ticker}")
        
        try:
            technical_result = await orchestrator.analyze_stock(
                request=technical_request,
                user_id=str(current_user.id),
                user_profile=user_profile
            )
            
            if not technical_result.success:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=technical_result.error
                )
            
            technical_insight = technical_result.insight
            logger.info(f"✅ Technical analysis complete for {request.ticker}")
            
        except Exception as e:
            logger.error(f"Technical analysis failed for {request.ticker}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Analysis failed: {str(e)}"
            )
        
        # Step 2: Get fundamental data and score (OPTIONAL - free tier doesn't include this)
        fundamental_data = None
        fundamental_score = None
        
        # For free tier Alpha Vantage, fundamentals are NOT available
        # Only fetch if explicitly requested AND available in database
        if request.include_fundamentals:
            try:
                logger.info(f"Attempting to fetch fundamentals for {request.ticker} from database")
                fundamental_data = await FundamentalProvider.get_fundamentals(request.ticker)
                
                if fundamental_data:
                    fundamental_score = await FundamentalProvider.score_fundamentals(fundamental_data)
                    logger.info(f"✅ Fundamental analysis complete for {request.ticker}")
                else:
                    logger.warning(f"⚠️ No fundamental data in database for {request.ticker} - continuing with technical only")
            except Exception as e:
                logger.warning(f"⚠️ Fundamentals unavailable for {request.ticker}: {e}")
                # Continue without fundamentals - this is expected for free tier
        
        # Step 3: Generate scenario analysis (SEPARATE from fundamentals)
        scenario_analysis = None
        if request.include_scenarios:
            try:
                logger.info(f"Generating scenarios for {request.ticker}")
                # Get indicators and signal from technical insight
                indicators = technical_insight.technical_indicators
                signal = technical_insight.signal
                current_price = Decimal(str(indicators.current_price))
                
                scenario_analysis = await ScenarioGenerator.generate_scenarios(
                    ticker=request.ticker,
                    current_price=current_price,
                    indicators=indicators,
                    signal=signal,
                    fundamentals_score=fundamental_score.overall_score if fundamental_score else None,
                    time_horizon_days=request.scenario_time_horizon or 90
                )
                logger.info(f"✅ Scenario analysis complete for {request.ticker}")
            except Exception as e:
                logger.warning(f"⚠️ Scenario generation failed for {request.ticker}: {e}")
                # Continue without scenarios
        
        # Step 4: Fetch MCP context using new providers (AFTER signal generation)
        market_context = None
        try:
            logger.info(f"Fetching MCP context for {request.ticker}")
            signal = technical_insight.signal
            
            # Use new MCP adapter with legacy format compatibility
            context_dict = await mcp_adapter.fetch_context(
                ticker=request.ticker,
                signal_direction=signal.strength.signal_type.lower()  # "bullish" | "bearish" | "neutral"
            )
            
            # Transform legacy dict to MarketContext model
            if context_dict and context_dict.get("data_source") != "fallback":
                # Build context_summary from legacy fields
                summary_parts = []
                if context_dict.get("market_sentiment") != "neutral":
                    summary_parts.append(f"Market sentiment: {context_dict['market_sentiment']}")
                if context_dict.get("index_trend") != "unavailable":
                    summary_parts.append(f"Index trend: {context_dict['index_trend']}")
                if context_dict.get("volume_analysis") != "unavailable":
                    summary_parts.append(f"Volume: {context_dict['volume_analysis']}")
                
                context_summary = ". ".join(summary_parts) if summary_parts else "Market context available from real-time data providers."
                
                # Create MarketContext model WITHOUT supporting_points (legacy adapter has no citations)
                # This avoids Pydantic validation error for empty sources list
                market_context = MarketContext(
                    context_summary=context_summary,
                    supporting_points=[],  # Empty list is valid - min_length constraint is on sources, not supporting_points
                    data_sources_used=[context_dict["data_source"]],
                    fetch_timestamp=datetime.fromisoformat(context_dict["metadata"]["timestamp"]),
                    mcp_status="success"
                )
                logger.info(f"✅ New MCP context fetched for {request.ticker}: {context_dict.get('data_source')}")
            else:
                logger.warning(f"⚠️ MCP context unavailable for {request.ticker}")
                # Leave market_context as None - EnhancedInsightResponse allows Optional
                
        except Exception as e:
            logger.warning(f"⚠️ MCP context fetch failed for {request.ticker}: {e}")
            # Continue without context - system must work if MCP fails
            market_context = None
        
        # Step 5: Combine insights
        enhanced_response = EnhancedInsightResponse(
            technical_insight=technical_insight,
            fundamental_data=fundamental_data,
            fundamental_score=fundamental_score,
            scenario_analysis=scenario_analysis,
            market_context=market_context,
            combined_score=_calculate_combined_score(
                technical_signal=technical_insight.signal,
                fundamental_score=fundamental_score,
                scenario_analysis=scenario_analysis
            ),
            recommendation=_generate_recommendation(
                technical_insight=technical_insight,
                fundamental_score=fundamental_score,
                scenario_analysis=scenario_analysis,
                user_profile=user_profile
            )
        )
        
        # Step 6: Audit log
        await AuditLogger.log_event(
            event_type="analysis_requested",
            user_id=session_ctx["user_id"],
            input_data={
                "ticker": request.ticker,
                "include_fundamentals": request.include_fundamentals,
                "include_scenarios": request.include_scenarios
            },
            output_data={
                "success": True,
                "combined_score": enhanced_response.combined_score,
                "recommendation": enhanced_response.recommendation
            },
            session_id=session_ctx["session_id"],
            ip_address=session_ctx["ip_address"],
            user_agent=session_ctx["user_agent"],
            ticker=request.ticker
        )
        
        logger.info(f"Enhanced analysis completed: {request.ticker} | User: {current_user.id}")
        
        return enhanced_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enhanced analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Enhanced analysis failed"
        )


def _calculate_combined_score(
    technical_signal,
    fundamental_score,
    scenario_analysis
) -> int:
    """Calculate weighted combined score (0-100)"""
    
    # Technical score from confidence
    tech_score = int(technical_signal.strength.confidence * 100)
    
    # If only technical available
    if not fundamental_score and not scenario_analysis:
        return tech_score
    
    # Weighted combination
    weights = {
        "technical": 0.4,
        "fundamental": 0.35,
        "scenario": 0.25
    }
    
    combined = tech_score * weights["technical"]
    
    if fundamental_score:
        combined += fundamental_score.overall_score * weights["fundamental"]
    else:
        # Redistribute weight
        combined += tech_score * weights["fundamental"]
    
    if scenario_analysis:
        # Score scenarios based on expected return and risk/reward
        scenario_score = 50  # Neutral baseline
        
        expected_return = float(scenario_analysis.expected_return_weighted)
        risk_reward = float(scenario_analysis.risk_reward_ratio)
        
        if expected_return > 15:
            scenario_score += 30
        elif expected_return > 5:
            scenario_score += 15
        elif expected_return < -10:
            scenario_score -= 30
        elif expected_return < -5:
            scenario_score -= 15
        
        if risk_reward > 2:
            scenario_score += 20
        elif risk_reward > 1:
            scenario_score += 10
        
        scenario_score = max(0, min(100, scenario_score))
        combined += scenario_score * weights["scenario"]
    else:
        # Redistribute weight
        combined += tech_score * weights["scenario"]
    
    return int(combined)


def _generate_recommendation(
    technical_insight,
    fundamental_score,
    scenario_analysis,
    user_profile
) -> str:
    """Generate actionable recommendation"""
    
    signal = technical_insight.signal
    risk_level = technical_insight.risk_assessment.overall_risk
    
    # Base recommendation from technical
    signal_type = signal.strength.signal_type
    confidence = signal.strength.confidence
    
    # Adjust based on fundamentals
    if fundamental_score:
        if fundamental_score.overall_assessment == "POOR" and signal_type == "BUY":
            return "HOLD - Technical signals bullish but fundamentals weak. Wait for confirmation."
        elif fundamental_score.overall_assessment == "STRONG" and signal_type == "SELL":
            return "HOLD - Technical signals bearish but fundamentals strong. Consider long-term hold."
    
    # Adjust based on scenarios
    if scenario_analysis:
        risk_reward = float(scenario_analysis.risk_reward_ratio)
        expected_return = float(scenario_analysis.expected_return_weighted)
        
        if risk_reward < 1 and signal_type == "BUY":
            return "CONDITIONS UNFAVORABLE - Risk/reward ratio unattractive. Downside exposure exceeds upside potential."
        
        if expected_return < -5 and signal_type == "BUY":
            return "SETUP NEUTRAL - Probability-weighted scenarios suggest limited return potential."
    
    # Check user profile constraints
    if risk_level == "HIGH" and user_profile.max_risk_level == "conservative":
        return f"RISK ELEVATED - {signal_type} signal present, but volatility exceeds conservative profile parameters."
    
    # Generate recommendation (Option B: Balanced - confident but defensible)
    if signal_type == "BUY":
        base_rec = ""
        if confidence > 0.8 and risk_level in ["LOW", "MEDIUM"]:
            base_rec = "STRONG BUY SIGNAL DETECTED - High-probability entry zone with favorable risk/reward profile."
        elif confidence > 0.6:
            base_rec = "BUY SIGNAL DETECTED - Entry conditions favorable with appropriate position sizing."
        else:
            base_rec = "WEAK BUY SIGNAL - Marginal setup. Wait for stronger confirmation."
        
        # Add price range if scenario analysis available
        if scenario_analysis and confidence > 0.6:
            base_case_return = float(scenario_analysis.base_case.expected_return_percent)
            best_case_return = float(scenario_analysis.best_case.expected_return_percent)
            if base_case_return > 5 or best_case_return > 10:
                base_rec += f" Base scenario suggests {base_case_return:+.1f}% potential with moderate confidence."
        
        return base_rec
    
    elif signal_type == "SELL":
        base_rec = ""
        if confidence > 0.8:
            base_rec = "STRONG CAUTION SIGNAL - High-confidence bearish pattern. Consider reducing exposure."
        elif confidence > 0.6:
            base_rec = "CAUTION SIGNAL DETECTED - Downside risk elevated. Review position sizing recommended."
        else:
            base_rec = "MIXED SIGNALS - No clear direction. Monitor before making changes."
        
        # Add downside risk if scenario analysis available
        if scenario_analysis and confidence > 0.6:
            worst_case_return = float(scenario_analysis.worst_case.expected_return_percent)
            if worst_case_return < -5:
                base_rec += f" Worst-case scenario projects {worst_case_return:.1f}% downside risk."
        
        return base_rec
    
    else:  # HOLD
        return "NEUTRAL - No clear directional bias. Wait for better setup."
