"""Risk assessment engine - Rule-based safety constraints"""

from typing import List, Literal, Optional
from datetime import datetime

from app.models.schemas import (
    Signal,
    RiskAssessment,
    RiskLevel,
    RiskFactor,
    SignalType,
    TechnicalIndicators,
)
from app.config import settings


class RiskEngine:
    """
    Deterministic risk assessment engine.
    
    Evaluates signals against predefined safety rules and constraints.
    Primary purpose: prevent harmful recommendations and ensure
    appropriate risk disclosure.
    
    Key principles:
    - Conservative by default
    - Deterministic rules (no ML black box)
    - Multiple risk factors evaluated independently
    - Clear mitigation strategies
    - "No action" is preferred over risky action
    
    Phase 2A: Enhanced with user-specific risk profile enforcement
    """
    
    def assess_risk(
        self,
        signal: Signal,
        indicators: TechnicalIndicators,
        user_risk_tolerance: Literal["conservative", "moderate", "aggressive"] = "moderate",
        user_profile: Optional[any] = None
    ) -> RiskAssessment:
        """
        Assess risk for a given signal.
        
        Args:
            signal: Generated trading signal
            indicators: Technical indicators
            user_risk_tolerance: User's risk tolerance level
            user_profile: User risk profile for Phase 2A personalized checks
            
        Returns:
            RiskAssessment with overall risk, factors, and actionability
        """
        risk_factors = []
        warnings = []
        constraints_applied = []
        
        # 1. Confidence threshold check
        confidence_risk = self._check_confidence_threshold(signal)
        if confidence_risk:
            risk_factors.append(confidence_risk)
        
        # 2. Volatility check
        volatility_risk = self._check_volatility(indicators)
        if volatility_risk:
            risk_factors.append(volatility_risk)
        
        # 3. Extreme indicator values
        extreme_risk = self._check_extreme_indicators(indicators)
        if extreme_risk:
            risk_factors.append(extreme_risk)
        
        # 4. Contradicting signals check
        contradiction_risk = self._check_contradictions(signal)
        if contradiction_risk:
            risk_factors.append(contradiction_risk)
        
        # 5. Time horizon appropriateness
        horizon_risk = self._check_time_horizon(signal)
        if horizon_risk:
            risk_factors.append(horizon_risk)
        
        # 6. Market context (simplified for MVP)
        context_risk = self._check_market_context(indicators)
        if context_risk:
            risk_factors.append(context_risk)
        
        # Phase 2A: User-specific risk checks
        if user_profile:
            user_risk = self._check_user_profile_constraints(signal, indicators, user_profile, warnings)
            if user_risk:
                risk_factors.extend(user_risk)
        
        # Determine overall risk level
        overall_risk = self._aggregate_risk_level(risk_factors)
        
        # Determine if signal is actionable
        is_actionable = self._determine_actionability(
            signal,
            overall_risk,
            user_risk_tolerance,
            warnings
        )
        
        # Apply mandatory constraints
        self._apply_constraints(signal, constraints_applied, warnings)
        
        return RiskAssessment(
            overall_risk=overall_risk,
            risk_factors=risk_factors,
            is_actionable=is_actionable,
            warnings=warnings,
            constraints_applied=constraints_applied
        )
    
    def _check_confidence_threshold(self, signal: Signal) -> RiskFactor | None:
        """Check if confidence is too low for actionable signals"""
        confidence = signal.strength.confidence
        
        if confidence < settings.MIN_ACTIONABLE_CONFIDENCE:
            return RiskFactor(
                name="Low Confidence",
                level=RiskLevel.HIGH,
                description=f"Signal confidence ({confidence:.1%}) below minimum threshold ({settings.MIN_ACTIONABLE_CONFIDENCE:.1%})",
                mitigation="Wait for stronger confirmation before acting"
            )
        elif confidence < 0.70:
            return RiskFactor(
                name="Moderate Confidence",
                level=RiskLevel.MODERATE,
                description=f"Signal confidence ({confidence:.1%}) suggests uncertainty",
                mitigation="Consider this signal as suggestive, not definitive"
            )
        
        return None
    
    def _check_volatility(self, indicators: TechnicalIndicators) -> RiskFactor | None:
        """Check for high volatility conditions"""
        if not all([indicators.bollinger_upper, indicators.bollinger_lower, indicators.bollinger_middle]):
            return None
        
        # Calculate Bollinger Band width as volatility proxy
        bb_width = (indicators.bollinger_upper - indicators.bollinger_lower) / indicators.bollinger_middle
        
        if bb_width > 0.15:  # >15% width indicates high volatility
            return RiskFactor(
                name="High Volatility",
                level=RiskLevel.HIGH,
                description=f"Bollinger Band width ({bb_width:.1%}) indicates elevated volatility",
                mitigation="Reduce position size or wait for volatility to decrease"
            )
        elif bb_width > 0.10:
            return RiskFactor(
                name="Moderate Volatility",
                level=RiskLevel.MODERATE,
                description=f"Bollinger Band width ({bb_width:.1%}) shows moderate volatility",
                mitigation="Be prepared for larger price swings"
            )
        
        return None
    
    def _check_extreme_indicators(self, indicators: TechnicalIndicators) -> RiskFactor | None:
        """Check for extreme overbought/oversold conditions"""
        if indicators.rsi is None:
            return None
        
        if indicators.rsi > 85:
            return RiskFactor(
                name="Extreme Overbought",
                level=RiskLevel.HIGH,
                description=f"RSI at {indicators.rsi:.1f} suggests extreme overbought conditions",
                mitigation="High risk of reversal; consider taking profits if long"
            )
        elif indicators.rsi < 15:
            return RiskFactor(
                name="Extreme Oversold",
                level=RiskLevel.HIGH,
                description=f"RSI at {indicators.rsi:.1f} suggests extreme oversold conditions",
                mitigation="May indicate panic selling; wait for stabilization"
            )
        
        return None
    
    def _check_contradictions(self, signal: Signal) -> RiskFactor | None:
        """Check for contradicting factors in signal reasoning"""
        contradictions = signal.reasoning.contradicting_factors
        
        if len(contradictions) >= 2:
            return RiskFactor(
                name="Mixed Signals",
                level=RiskLevel.MODERATE,
                description=f"Found {len(contradictions)} contradicting indicators",
                mitigation="Wait for clearer alignment before acting"
            )
        
        return None
    
    def _check_time_horizon(self, signal: Signal) -> RiskFactor | None:
        """Check time horizon appropriateness"""
        # MVP: Short-term trading is restricted
        if signal.time_horizon.value == "short_term" and not settings.SHORT_TERM_ENABLED:
            return RiskFactor(
                name="Restricted Time Horizon",
                level=RiskLevel.CRITICAL,
                description="Short-term trading signals are disabled in MVP",
                mitigation="Use long-term analysis mode only"
            )
        
        return None
    
    def _check_market_context(self, indicators: TechnicalIndicators) -> RiskFactor | None:
        """Check broader market context (simplified for MVP)"""
        # In production, this would check:
        # - Market-wide trends (S&P 500, VIX)
        # - Sector performance
        # - Economic indicators
        # - News sentiment
        
        # MVP: Just a placeholder reminder
        return RiskFactor(
            name="Limited Market Context",
            level=RiskLevel.LOW,
            description="Analysis based on individual stock only, not broader market conditions",
            mitigation="Independently verify broader market trends and news"
        )
    
    def _aggregate_risk_level(self, risk_factors: List[RiskFactor]) -> RiskLevel:
        """Aggregate individual risk factors into overall risk level"""
        if not risk_factors:
            return RiskLevel.LOW
        
        # Use highest risk level present
        risk_hierarchy = {
            RiskLevel.CRITICAL: 4,
            RiskLevel.HIGH: 3,
            RiskLevel.MODERATE: 2,
            RiskLevel.LOW: 1
        }
        
        max_risk = max(factor.level for factor in risk_factors)
        return max_risk
    
    def _determine_actionability(
        self,
        signal: Signal,
        overall_risk: RiskLevel,
        user_risk_tolerance: str,
        warnings: List[str]
    ) -> bool:
        """Determine if signal is actionable given risk profile"""
        
        # Never actionable for neutral signals
        if signal.strength.signal_type == SignalType.NEUTRAL:
            warnings.append("Neutral signal: no clear action recommended")
            return False
        
        # Critical risk = never actionable
        if overall_risk == RiskLevel.CRITICAL:
            warnings.append("Critical risk level: signal blocked for safety")
            return False
        
        # High risk = only for aggressive users
        if overall_risk == RiskLevel.HIGH:
            if user_risk_tolerance != "aggressive":
                warnings.append("High risk signal: not suitable for your risk tolerance")
                return False
            else:
                warnings.append("High risk signal: proceed with extreme caution")
                return True
        
        # Moderate risk = not for conservative users
        if overall_risk == RiskLevel.MODERATE:
            if user_risk_tolerance == "conservative":
                warnings.append("Moderate risk signal: not suitable for conservative profile")
                return False
            else:
                warnings.append("Moderate risk signal: careful position sizing recommended")
                return True
        
        # Low risk = actionable for all
        return True
    
    def _apply_constraints(
        self,
        signal: Signal,
        constraints_applied: List[str],
        warnings: List[str]
    ) -> None:
        """Apply mandatory safety constraints"""
        
        # 1. Confidence cap
        if signal.strength.confidence > settings.MAX_CONFIDENCE_THRESHOLD:
            constraints_applied.append(
                f"Confidence capped at {settings.MAX_CONFIDENCE_THRESHOLD:.0%} (was higher)"
            )
        
        # 2. Disclaimer requirement
        constraints_applied.append("Mandatory disclaimer attached to all insights")
        
        # 3. No guarantees
        if signal.strength.confidence > 0.90:
            warnings.append(
                "Even high-confidence signals are probabilistic, not certain"
            )
        
        # 4. Position sizing (reminder)
        constraints_applied.append("Recommended: never risk more than 1-2% per position")
        
        # 5. Independent verification
        constraints_applied.append("Always conduct independent research before investing")
    
    def _check_user_profile_constraints(
        self,
        signal: Signal,
        indicators: TechnicalIndicators,
        user_profile: any,
        warnings: List[str]
    ) -> List[RiskFactor]:
        """
        Phase 2A: Check signal against user-specific risk profile constraints
        
        Args:
            signal: Trading signal
            indicators: Technical indicators
            user_profile: User risk profile
            warnings: List to append warnings to
        
        Returns:
            List of risk factors from user profile violations
        """
        risk_factors = []
        
        # Check volatility tolerance
        if not user_profile.allow_high_volatility_stocks:
            if indicators.bollinger_upper and indicators.bollinger_lower and indicators.bollinger_middle:
                bb_width = (indicators.bollinger_upper - indicators.bollinger_lower) / indicators.bollinger_middle
                if bb_width > 0.15:
                    risk_factors.append(RiskFactor(
                        name="Profile Violation: High Volatility",
                        level=RiskLevel.CRITICAL,
                        description="Stock volatility exceeds your risk profile settings",
                        mitigation="Your profile does not allow high-volatility stocks. Consider skipping this opportunity."
                    ))
                    warnings.append("⚠️ This stock exceeds your volatility tolerance")
        
        # Check penny stock restriction
        if not user_profile.allow_penny_stocks:
            if indicators.current_price < 5.0:
                risk_factors.append(RiskFactor(
                    name="Profile Violation: Penny Stock",
                    level=RiskLevel.CRITICAL,
                    description="Stock price below $5 (penny stock)",
                    mitigation="Your profile prohibits penny stocks due to higher risk."
                ))
                warnings.append("⚠️ Penny stocks are not allowed in your risk profile")
        
        # Add profile-based warning
        if user_profile.risk_tolerance == "conservative":
            warnings.append(
                f"📊 Your conservative risk profile applies strict position limits: "
                f"Max ${user_profile.max_position_size_usd:,.0f} per position, "
                f"{user_profile.max_capital_at_risk_percent}% max capital at risk"
            )
        
        return risk_factors


# Singleton instance
risk_engine = RiskEngine()
