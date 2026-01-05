"""FastAPI routes for stock analysis"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict

from app.models.schemas import AnalysisRequest, AnalysisResponse
from app.models.auth_models import User, UserRiskProfile
from app.core.orchestrator import orchestrator
from app.api.dependencies import get_current_user, get_user_risk_profile, get_session_context
from app.core.audit import AuditLogger

router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze a stock",
    description="Generate AI-assisted trading insights for a stock symbol (Authentication required)"
)
async def analyze_stock(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    user_profile: UserRiskProfile = Depends(get_user_risk_profile),
    session_ctx: dict = Depends(get_session_context)
) -> AnalysisResponse:
    """
    Analyze a stock and return insights.
    
    **Phase 2A: Now requires authentication and applies user-specific risk constraints**
    
    This endpoint performs comprehensive technical analysis including:
    - Market data retrieval
    - Technical indicator calculation
    - Signal generation
    - User-specific risk assessment
    - Explanation generation
    - Audit logging
    
    Returns probabilistic insights, NOT guarantees.
    All analysis is logged for compliance.
    """
    response = await orchestrator.analyze_stock(
        request,
        user_id=str(current_user.id),
        user_profile=user_profile
    )
    
    # Log analysis request to audit trail
    await AuditLogger.log_analysis_requested(
        user_id=session_ctx["user_id"],
        ticker=request.ticker,
        input_params=request.model_dump(),
        full_response=response.model_dump(),
        session_id=session_ctx["session_id"],
        ip_address=session_ctx["ip_address"],
        user_agent=session_ctx["user_agent"]
    )
    
    if not response.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response.error
        )
    
    return response


@router.get(
    "/supported-tickers",
    response_model=Dict[str, str],
    summary="Get supported stock tickers",
    description="Returns list of stock tickers supported in MVP (Authentication required)"
)
async def get_supported_tickers(
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Get list of supported tickers for MVP.
    
    **Phase 2A: Now requires authentication**
    
    In production, this would return all available market tickers.
    For MVP, returns only mock data tickers.
    """
    from app.core.market_data.provider import MockMarketDataProvider
    
    return MockMarketDataProvider.MOCK_COMPANIES
