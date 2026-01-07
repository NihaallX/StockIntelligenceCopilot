"""Example API endpoint demonstrating Market Context Agent integration

This shows how to integrate the context agent with existing analysis endpoints.
Add this to your router if you want to expose enriched analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
import logging

from app.models.schemas import AnalysisRequest, AnalysisResponse
from app.models.auth_models import User
from app.api.dependencies import get_current_user
from app.core.orchestrator import orchestrator
from app.core.context_agent import (
    MarketContextAgent,
    ContextEnrichmentInput,
    ContextEnrichmentOutput,
    get_trigger_manager
)
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze-with-context", response_model=dict)
async def analyze_with_context(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Enhanced analysis with optional market context enrichment
    
    This endpoint:
    1. Runs standard analysis (existing system)
    2. Optionally enriches with market context (new layer)
    3. Returns both analysis and context
    
    The context layer is OPTIONAL and READ-ONLY.
    If MCP fails or is disabled, the analysis still returns successfully.
    
    **Example Response:**
    ```json
    {
      "success": true,
      "analysis": {
        "signal": { ... },
        "risk_assessment": { ... },
        "recommendation": "BUY - Strong momentum",
        ...
      },
      "market_context": {
        "context_summary": "RELIANCE.NS operates in energy sector...",
        "supporting_points": [
          {
            "claim": "NIFTY declined 2.3% this week",
            "source": "NSE",
            "url": "https://..."
          }
        ],
        "mcp_status": "success"
      }
    }
    ```
    """
    
    try:
        # Step 1: Run standard analysis (existing system)
        logger.info(f"Analyzing {request.ticker} for user {current_user.id}")
        
        analysis_result = await orchestrator.analyze_stock(request)
        
        if not analysis_result.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=analysis_result.error or "Analysis failed"
            )
        
        # Step 2: Optionally enrich with market context (new layer)
        market_context: Optional[ContextEnrichmentOutput] = None
        
        if settings.MCP_ENABLED:
            try:
                # Check if MCP should run (intelligent triggering)
                trigger_mgr = get_trigger_manager(
                    cooldown_minutes=settings.MCP_TRIGGER_COOLDOWN_MINUTES,
                    enabled=True
                )
                
                # Extract opportunity type and volatility for trigger logic
                opportunity_type = analysis_result.insight.get("signal", {}).get("type", "UNKNOWN")
                volatility = analysis_result.insight.get("technical", {}).get("volatility", None)
                
                should_trigger = trigger_mgr.should_trigger(
                    ticker=request.ticker,
                    opportunity_type=opportunity_type,
                    volatility=volatility
                )
                
                if should_trigger:
                    logger.info(f"✅ MCP triggered for {request.ticker} (opportunity: {opportunity_type})")
                    
                    agent = MarketContextAgent(enabled=True)
                    
                    context_input = ContextEnrichmentInput(
                        opportunity=analysis_result.insight.model_dump(),
                        ticker=request.ticker,
                        market="NSE",  # TODO: Detect market from ticker
                        time_horizon=request.time_horizon.upper()
                    )
                    
                    market_context = await agent.enrich_opportunity(context_input)
                    
                    logger.info(
                        f"✅ Context enrichment: {market_context.mcp_status}, "
                        f"{len(market_context.supporting_points)} points"
                    )
                else:
                    logger.debug(
                        f"⏭️ MCP skipped for {request.ticker} (cooldown/no significant change)"
                    )
                
            except Exception as e:
                logger.warning(
                    f"Context enrichment failed (non-fatal): {e}",
                    exc_info=True
                )
                # Continue without context - this is optional
                market_context = None
        else:
            logger.debug("MCP context enrichment disabled")
        
        # Step 3: Return response with optional context
        response = {
            "success": True,
            "analysis": analysis_result.insight.model_dump(),
            "market_context": market_context.model_dump() if market_context else None,
            "disclaimer": settings.DISCLAIMER
        }
        
        logger.info(
            f"✅ Analysis complete for {request.ticker}: "
            f"context={'included' if market_context else 'not included'}"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis with context failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis failed"
        )


@router.get("/context-agent/status")
async def context_agent_status():
    """
    Get Market Context Agent status
    
    Returns:
    ```json
    {
      "mcp_enabled": true,
      "mcp_timeout_seconds": 10,
      "approved_sources": ["Reuters", "NSE", ...],
      "status": "operational"
    }
    ```
    """
    
    from app.mcp.legacy_adapter import get_legacy_adapter
    
    adapter = get_legacy_adapter()
    
    return {
        "mcp_enabled": settings.MCP_ENABLED,
        "mcp_timeout_seconds": settings.MCP_TIMEOUT_SECONDS,
        "approved_sources": ["alpha_vantage", "twelve_data", "yahoo_finance"],
        "mcp_version": "2.0",
        "status": "operational" if settings.MCP_ENABLED else "disabled"
    }
