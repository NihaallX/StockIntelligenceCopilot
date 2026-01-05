"""Insight orchestrator - Coordinates the analysis pipeline"""

import time
from typing import Literal, Optional

from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    Insight,
    TimeHorizon,
)
from app.core.market_data.factory import ProviderFactory

def get_market_data_provider(ticker: Optional[str] = None):
    """Get appropriate market data provider for ticker"""
    return ProviderFactory.get_provider(ticker=ticker)
from app.core.indicators import indicator_calculator
from app.core.signals import signal_generator
from app.core.risk import risk_engine
from app.core.explanation import explanation_generator


class InsightOrchestrator:
    """
    Orchestrates the complete analysis pipeline.
    
    Coordinates all components to transform a stock analysis request
    into a complete insight package.
    
    Pipeline:
    1. Fetch market data
    2. Calculate technical indicators
    3. Generate trading signal
    4. Assess risk (with user-specific constraints in Phase 2A)
    5. Generate explanations
    6. Package insight
    """
    
    async def analyze_stock(
        self,
        request: AnalysisRequest,
        user_id: Optional[str] = None,
        user_profile: Optional[any] = None
    ) -> AnalysisResponse:
        """
        Execute full analysis pipeline for a stock.
        
        Args:
            request: Analysis request with ticker and parameters
            user_id: User ID for audit logging (Phase 2A)
            user_profile: User risk profile for personalized constraints (Phase 2A)
            
        Returns:
            AnalysisResponse with insight or error
        """
        start_time = time.time()
        
        try:
            # Get the provider for this specific ticker
            market_data_provider = get_market_data_provider(ticker=request.ticker)
            
            # Validate ticker
            if not market_data_provider.is_valid_ticker(request.ticker):
                return AnalysisResponse(
                    success=False,
                    error=f"Invalid or unsupported ticker: {request.ticker}",
                    processing_time_ms=0
                )
            
            # Step 1: Fetch market data
            market_data = market_data_provider.get_stock_data(
                ticker=request.ticker,
                lookback_days=request.lookback_days
            )
            
            # Phase 2C: Track data quality
            confidence_penalty = 0.0
            data_warnings = []
            
            if market_data.data_source == "cache_stale":
                confidence_penalty += 0.10  # -10% for stale data
                data_warnings.append(f"⚠️ Data Freshness: {market_data.data_quality_warning}")
            
            elif market_data.data_source == "cache_error_fallback":
                confidence_penalty += 0.15  # -15% for error fallback
                data_warnings.append(f"⚠️ Data Availability: {market_data.data_quality_warning}")
            
            elif market_data.data_source == "demo":
                data_warnings.append("ℹ️ DEMO MODE: Using simulated market data")
            
            if not market_data.prices:
                return AnalysisResponse(
                    success=False,
                    error=f"No market data available for {request.ticker}",
                    processing_time_ms=0
                )
            
            # Step 2: Calculate technical indicators
            indicators = indicator_calculator.calculate_all(
                ticker=request.ticker,
                prices=market_data.prices
            )
            
            if not indicators:
                return AnalysisResponse(
                    success=False,
                    error=f"Insufficient data to calculate indicators (need at least 50 days)",
                    processing_time_ms=0
                )
            
            # Step 3: Generate trading signal
            signal = signal_generator.generate_signal(
                market_data=market_data,
                indicators=indicators,
                time_horizon=request.time_horizon
            )
            
            # Phase 2C: Apply confidence penalty for data quality
            if confidence_penalty > 0:
                original_confidence = signal.strength.confidence
                signal.strength.confidence = max(0.1, original_confidence - confidence_penalty)
                # Log for monitoring
                pass  # Logger would be added in production
            
            # Step 4: Assess risk (with user profile in Phase 2A)
            risk_assessment = risk_engine.assess_risk(
                signal=signal,
                indicators=indicators,
                user_risk_tolerance=request.risk_tolerance,
                user_profile=user_profile  # Phase 2A: Apply user-specific constraints
            )
            
            # Step 5: Generate explanations and package insight
            insight = explanation_generator.generate_insight(
                signal=signal,
                risk_assessment=risk_assessment,
                indicators=indicators,
                time_horizon=request.time_horizon
            )
            
            # Phase 2C: Prepend data quality warnings to key points
            if data_warnings:
                insight.key_points = data_warnings + insight.key_points
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return AnalysisResponse(
                success=True,
                insight=insight,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return AnalysisResponse(
                success=False,
                error=f"Analysis failed: {str(e)}",
                processing_time_ms=processing_time
            )


# Singleton instance
orchestrator = InsightOrchestrator()
