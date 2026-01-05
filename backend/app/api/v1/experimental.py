"""
EXPERIMENTAL MODE API ROUTES
=============================

⚠️ WARNING: Personal use only. Not SEBI compliant.
"""

import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime

from app.core.experimental.trading_agent import ExperimentalTradingAgent, TradingThesis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/experimental", tags=["experimental"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class AnalysisRequest(BaseModel):
    """Request for experimental analysis"""
    ticker: str
    current_price: float
    ohlcv: Dict[str, Any]
    indicators: Dict[str, Any]
    portfolio_context: Optional[Dict[str, Any]] = None
    index_context: Optional[Dict[str, Any]] = None
    time_of_day: Optional[str] = None


class FeedbackRequest(BaseModel):
    """User feedback on analysis"""
    analysis_id: str
    ticker: str
    feedback: str  # "helpful" or "wrong"
    user_note: Optional[str] = None
    timestamp: datetime = None
    
    def __init__(self, **data):
        if data.get('timestamp') is None:
            data['timestamp'] = datetime.now()
        super().__init__(**data)


class AnalysisResponse(BaseModel):
    """Response with trading thesis"""
    success: bool
    thesis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    warning: str = "⚠️ EXPERIMENTAL - Personal use only. Not financial advice."


class FeedbackResponse(BaseModel):
    """Confirmation of feedback logged"""
    success: bool
    message: str


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_experimental_agent() -> ExperimentalTradingAgent:
    """Get experimental agent instance"""
    return ExperimentalTradingAgent(enabled=True)


# ============================================================================
# ROUTES
# ============================================================================

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_setup(
    request: AnalysisRequest,
    agent: ExperimentalTradingAgent = Depends(get_experimental_agent)
) -> AnalysisResponse:
    """
    Generate experimental trading thesis
    
    ⚠️ WARNING: Personal use only. Not SEBI compliant.
    """
    try:
        thesis = agent.analyze_setup(
            ticker=request.ticker,
            current_price=request.current_price,
            ohlcv=request.ohlcv,
            indicators=request.indicators,
            portfolio_context=request.portfolio_context,
            index_context=request.index_context,
            time_of_day=request.time_of_day
        )
        
        if thesis is None:
            return AnalysisResponse(
                success=False,
                error="Experimental agent disabled or analysis unavailable"
            )
        
        # Convert to dict
        thesis_dict = {
            "ticker": thesis.ticker,
            "thesis": thesis.thesis,
            "bias": thesis.bias,
            "confidence": thesis.confidence,
            "regime": thesis.regime,
            "price_range_low": thesis.price_range_low,
            "price_range_high": thesis.price_range_high,
            "entry_timing": thesis.entry_timing,
            "time_horizon": thesis.time_horizon,
            "invalidation_reason": thesis.invalidation_reason,
            "volume_analysis": thesis.volume_analysis,
            "risk_notes": thesis.risk_notes,
            "confidence_adjustments": thesis.confidence_adjustments,
            "index_alignment": thesis.index_alignment,
            "signal_age_minutes": thesis.signal_age_minutes,
            "analysis_id": thesis.analysis_id
        }
        
        return AnalysisResponse(
            success=True,
            thesis=thesis_dict
        )
    
    except Exception as e:
        logger.error(f"Error in experimental analysis: {e}", exc_info=True)
        return AnalysisResponse(
            success=False,
            error=f"Analysis failed: {str(e)}"
        )


@router.post("/feedback", response_model=FeedbackResponse)
async def log_feedback(
    feedback: FeedbackRequest
) -> FeedbackResponse:
    """
    Log user feedback on analysis
    
    This creates a learning loop where user can mark:
    - 👍 "helpful" - Analysis was accurate/useful
    - 👎 "wrong" - Analysis was incorrect
    """
    try:
        # Log to file for review
        feedback_entry = {
            "analysis_id": feedback.analysis_id,
            "ticker": feedback.ticker,
            "feedback": feedback.feedback,
            "user_note": feedback.user_note,
            "timestamp": feedback.timestamp.isoformat()
        }
        
        logger.warning(
            f"📊 EXPERIMENTAL FEEDBACK - {feedback.ticker}\n"
            f"   Analysis ID: {feedback.analysis_id}\n"
            f"   Feedback: {feedback.feedback}\n"
            f"   Note: {feedback.user_note or 'None'}"
        )
        
        # TODO: Store in database for ML training
        # For now, just log it
        
        return FeedbackResponse(
            success=True,
            message="Feedback logged successfully"
        )
    
    except Exception as e:
        logger.error(f"Error logging feedback: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log feedback: {str(e)}"
        )


@router.get("/health")
async def health_check(
    agent: ExperimentalTradingAgent = Depends(get_experimental_agent)
) -> Dict[str, Any]:
    """Check if experimental mode is enabled"""
    return {
        "enabled": agent.enabled,
        "mode": "experimental",
        "warning": "⚠️ Personal use only. Not SEBI compliant."
    }
