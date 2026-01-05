"""Scenario analysis generator for probabilistic projections"""

from typing import Dict, Optional
from decimal import Decimal
import logging
from datetime import datetime, timedelta

from app.models.portfolio_models import (
    ScenarioAssumptions,
    ScenarioOutcome,
    ScenarioAnalysis
)
from app.models.schemas import TechnicalIndicators, Signal

logger = logging.getLogger(__name__)


class ScenarioGenerator:
    """Generates best/base/worst case scenarios with probability weighting"""
    
    @staticmethod
    async def generate_scenarios(
        ticker: str,
        current_price: Decimal,
        indicators: TechnicalIndicators,
        signal: Signal,
        fundamentals_score: Optional[int] = None,
        time_horizon_days: int = 90
    ) -> ScenarioAnalysis:
        """
        Generate probabilistic scenarios
        
        Methodology:
        - Base case: Technical target + fundamental alignment
        - Best case: Breakout + positive catalysts (upside deviation)
        - Worst case: Breakdown + risk factors (downside deviation)
        - Probability assignment based on signal strength, volatility, fundamentals
        """
        
        # Calculate volatility multiplier from Bollinger Bands
        bb_width = float(indicators.bollinger_width or 0.10)
        volatility_factor = bb_width * 100  # Convert to percentage
        
        # Base assumptions
        assumptions = ScenarioGenerator._calculate_assumptions(
            signal=signal,
            indicators=indicators,
            fundamentals_score=fundamentals_score,
            volatility_factor=volatility_factor
        )
        
        # Generate three scenarios
        best_case = ScenarioGenerator._generate_best_case(
            current_price=current_price,
            assumptions=assumptions,
            time_horizon_days=time_horizon_days
        )
        
        base_case = ScenarioGenerator._generate_base_case(
            current_price=current_price,
            signal=signal,
            assumptions=assumptions,
            time_horizon_days=time_horizon_days
        )
        
        worst_case = ScenarioGenerator._generate_worst_case(
            current_price=current_price,
            assumptions=assumptions,
            time_horizon_days=time_horizon_days
        )
        
        # Calculate probability-weighted expected return
        expected_return = (
            best_case.probability / 100 * best_case.expected_return_percent +
            base_case.probability / 100 * base_case.expected_return_percent +
            worst_case.probability / 100 * worst_case.expected_return_percent
        )
        
        # Risk/reward ratio
        upside_potential = float(best_case.expected_return_percent)
        downside_risk = abs(float(worst_case.expected_return_percent))
        risk_reward_ratio = upside_potential / downside_risk if downside_risk > 0 else 0
        
        return ScenarioAnalysis(
            ticker=ticker,
            current_price=current_price,
            time_horizon_days=time_horizon_days,
            assumptions=assumptions,
            best_case=best_case,
            base_case=base_case,
            worst_case=worst_case,
            expected_return_weighted=expected_return,
            risk_reward_ratio=Decimal(str(risk_reward_ratio)),
            generated_at=datetime.utcnow()
        )
    
    @staticmethod
    def _calculate_assumptions(
        signal: Signal,
        indicators: TechnicalIndicators,
        fundamentals_score: Optional[int],
        volatility_factor: float
    ) -> ScenarioAssumptions:
        """Calculate scenario assumptions"""
        
        # Market regime
        signal_type = signal.strength.signal_type
        confidence = signal.strength.confidence
        
        if signal_type == "BUY" and confidence > 0.7:
            market_regime = "bullish"
        elif signal_type == "SELL" and confidence > 0.7:
            market_regime = "bearish"
        else:
            market_regime = "neutral"
        
        # Expected volatility (annualized from Bollinger Bands)
        expected_volatility = Decimal(str(volatility_factor * 1.5))  # Scale to reasonable range
        
        # Fundamental catalyst strength
        if fundamentals_score:
            if fundamentals_score >= 80:
                catalyst_strength = "strong"
            elif fundamentals_score >= 60:
                catalyst_strength = "moderate"
            else:
                catalyst_strength = "weak"
        else:
            catalyst_strength = "unknown"
        
        # Technical support/resistance
        support_level = indicators.support_level
        resistance_level = indicators.resistance_level
        
        return ScenarioAssumptions(
            market_regime=market_regime,
            expected_volatility=expected_volatility,
            catalyst_strength=catalyst_strength,
            support_level=support_level,
            resistance_level=resistance_level
        )
    
    @staticmethod
    def _generate_best_case(
        current_price: Decimal,
        assumptions: ScenarioAssumptions,
        time_horizon_days: int
    ) -> ScenarioOutcome:
        """Generate best case scenario (bullish breakout)"""
        
        # Base upside from volatility
        volatility_pct = float(assumptions.expected_volatility)
        base_upside = volatility_pct * 1.5  # 1.5x volatility for best case
        
        # Adjust for resistance level
        if assumptions.resistance_level:
            resistance_pct = (float(assumptions.resistance_level) / float(current_price) - 1) * 100
            upside = max(base_upside, resistance_pct * 1.2)  # Breakout past resistance
        else:
            upside = base_upside
        
        # Catalyst bonus
        if assumptions.catalyst_strength == "strong":
            upside *= 1.3
        elif assumptions.catalyst_strength == "moderate":
            upside *= 1.15
        
        # Cap at reasonable levels
        upside = min(upside, 100)  # Max 100% upside
        
        # Price targets
        target_price_low = current_price * (1 + Decimal(str(upside * 0.7 / 100)))
        target_price_mid = current_price * (1 + Decimal(str(upside / 100)))
        target_price_high = current_price * (1 + Decimal(str(upside * 1.2 / 100)))
        
        # Probability assignment
        if assumptions.market_regime == "bullish":
            probability = Decimal("35")  # 35% in bull market
        elif assumptions.market_regime == "neutral":
            probability = Decimal("20")  # 20% in neutral
        else:
            probability = Decimal("10")  # 10% in bear market
        
        # Key drivers
        drivers = [
            "Technical breakout above resistance",
            "Strong momentum continuation",
        ]
        if assumptions.catalyst_strength == "strong":
            drivers.append("Positive fundamental catalysts")
        
        # Calculate confidence based on market regime and catalyst
        confidence = 0.6  # Base confidence
        if assumptions.market_regime == "bullish":
            confidence += 0.2
        if assumptions.catalyst_strength == "strong":
            confidence += 0.15
        confidence = min(confidence, 0.95)  # Cap at 95%
        
        return ScenarioOutcome(
            scenario_type="best_case",
            probability=probability,
            target_price_low=target_price_low,
            target_price_mid=target_price_mid,
            target_price_high=target_price_high,
            expected_return_percent=Decimal(str(upside)),
            key_drivers=drivers,
            timeline_days=time_horizon_days,
            confidence_level=Decimal(str(confidence))
        )
    
    @staticmethod
    def _generate_base_case(
        current_price: Decimal,
        signal: Signal,
        assumptions: ScenarioAssumptions,
        time_horizon_days: int
    ) -> ScenarioOutcome:
        """Generate base case scenario (expected outcome)"""
        
        # Use signal target if available
        target_price = signal.reasoning.target_price if hasattr(signal.reasoning, 'target_price') else None
        confidence = signal.strength.confidence
        
        if target_price:
            base_return = (float(target_price) / float(current_price) - 1) * 100
        else:
            # Otherwise use moderate volatility
            volatility_pct = float(assumptions.expected_volatility)
            if assumptions.market_regime == "bullish":
                base_return = volatility_pct * 0.5
            elif assumptions.market_regime == "bearish":
                base_return = -volatility_pct * 0.3
            else:
                base_return = 0
        
        # Adjust for confidence
        base_return *= confidence
        
        # Price targets
        target_price_low = current_price * (1 + Decimal(str(base_return * 0.7 / 100)))
        target_price_mid = current_price * (1 + Decimal(str(base_return / 100)))
        target_price_high = current_price * (1 + Decimal(str(base_return * 1.3 / 100)))
        
        # Probability (highest)
        if assumptions.market_regime == "neutral":
            probability = Decimal("60")
        else:
            probability = Decimal("50")
        
        # Key drivers
        drivers = [
            "Technical signals materialize as expected",
            "Market conditions remain stable",
        ]
        
        return ScenarioOutcome(
            scenario_type="base_case",
            probability=probability,
            target_price_low=target_price_low,
            target_price_mid=target_price_mid,
            target_price_high=target_price_high,
            expected_return_percent=Decimal(str(base_return)),
            key_drivers=drivers,
            timeline_days=time_horizon_days,
            confidence_level=Decimal(str(confidence))
        )
    
    @staticmethod
    def _generate_worst_case(
        current_price: Decimal,
        assumptions: ScenarioAssumptions,
        time_horizon_days: int
    ) -> ScenarioOutcome:
        """Generate worst case scenario (bearish breakdown)"""
        
        # Base downside from volatility
        volatility_pct = float(assumptions.expected_volatility)
        base_downside = -volatility_pct * 1.2  # 1.2x volatility for worst case
        
        # Adjust for support level
        if assumptions.support_level:
            support_pct = (float(assumptions.support_level) / float(current_price) - 1) * 100
            downside = min(base_downside, support_pct * 0.8)  # Breakdown below support
        else:
            downside = base_downside
        
        # Market regime penalty
        if assumptions.market_regime == "bearish":
            downside *= 1.4
        elif assumptions.market_regime == "neutral":
            downside *= 1.1
        
        # Cap at reasonable levels
        downside = max(downside, -60)  # Max 60% downside
        
        # Price targets
        target_price_high = current_price * (1 + Decimal(str(downside * 0.7 / 100)))
        target_price_mid = current_price * (1 + Decimal(str(downside / 100)))
        target_price_low = current_price * (1 + Decimal(str(downside * 1.3 / 100)))
        
        # Probability assignment
        if assumptions.market_regime == "bearish":
            probability = Decimal("40")  # 40% in bear market
        elif assumptions.market_regime == "neutral":
            probability = Decimal("20")  # 20% in neutral
        else:
            probability = Decimal("15")  # 15% in bull market
        
        # Key drivers
        drivers = [
            "Technical breakdown below support",
            "Negative market sentiment",
        ]
        if assumptions.catalyst_strength == "weak":
            drivers.append("Weak fundamentals")
        
        return ScenarioOutcome(
            scenario_type="worst_case",
            probability=probability,
            target_price_low=target_price_low,
            target_price_mid=target_price_mid,
            target_price_high=target_price_high,
            expected_return_percent=Decimal(str(downside)),
            key_drivers=drivers,
            timeline_days=time_horizon_days,
            confidence_level=Decimal("0.70")
        )
