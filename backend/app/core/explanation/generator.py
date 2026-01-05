"""Explanation layer - Generate human-readable insights"""

from typing import List, Literal

from app.models.schemas import (
    Insight,
    Signal,
    SignalType,
    RiskAssessment,
    RiskLevel,
    TechnicalIndicators,
    TimeHorizon,
)
from app.config import settings


class ExplanationGenerator:
    """
    Generate human-readable explanations for trading insights.
    
    Transforms technical signals into clear, understandable narratives
    suitable for retail investors.
    
    Key principles:
    - Plain language, minimal jargon
    - Emphasis on uncertainty and assumptions
    - Clear action items (or lack thereof)
    - Educational context where helpful
    - Never implies certainty or guarantees
    """
    
    def generate_insight(
        self,
        signal: Signal,
        risk_assessment: RiskAssessment,
        indicators: TechnicalIndicators,
        time_horizon: TimeHorizon
    ) -> Insight:
        """
        Generate complete insight package with explanations.
        
        Args:
            signal: Generated trading signal
            risk_assessment: Risk evaluation results
            indicators: Technical indicators
            time_horizon: Investment time horizon
            
        Returns:
            Complete Insight with summaries and key points
        """
        # Generate summary
        summary = self._generate_summary(signal, risk_assessment, indicators)
        
        # Extract key points
        key_points = self._extract_key_points(signal, risk_assessment, indicators)
        
        # Determine recommendation
        recommendation = self._determine_recommendation(signal, risk_assessment)
        
        # Calculate overall confidence (factoring in risk)
        overall_confidence = self._calculate_overall_confidence(signal, risk_assessment)
        
        return Insight(
            ticker=signal.ticker,
            signal=signal,
            risk_assessment=risk_assessment,
            technical_indicators=indicators,
            analysis_mode=time_horizon,
            recommendation=recommendation,
            summary=summary,
            key_points=key_points,
            disclaimer=settings.DISCLAIMER,
            overall_confidence=overall_confidence
        )
    
    def _generate_summary(
        self,
        signal: Signal,
        risk_assessment: RiskAssessment,
        indicators: TechnicalIndicators
    ) -> str:
        """Generate plain-language summary"""
        
        ticker = signal.ticker
        signal_type = signal.strength.signal_type
        confidence = signal.strength.confidence
        strength = signal.strength.strength
        risk_level = risk_assessment.overall_risk
        is_actionable = risk_assessment.is_actionable
        
        # Build summary based on signal type and actionability
        if signal_type == SignalType.NEUTRAL:
            summary = (
                f"Analysis of {ticker} shows no clear directional signal at this time. "
                f"Technical indicators are mixed or inconclusive, suggesting a wait-and-see approach. "
                f"Current price: ${indicators.current_price:.2f}."
            )
        elif not is_actionable:
            summary = (
                f"While {ticker} shows a {signal_type.value} signal with {strength} strength "
                f"(confidence: {confidence:.1%}), the overall {risk_level.value} risk level "
                f"means this signal does not meet actionability criteria. "
                f"Recommendation: Monitor but do not act at this time."
            )
        else:
            action_word = "buying opportunities" if signal_type == SignalType.BULLISH else "caution or potential selling points"
            summary = (
                f"{ticker} exhibits a {strength} {signal_type.value} signal (confidence: {confidence:.1%}) "
                f"based on technical analysis. This suggests potential {action_word}. "
                f"Risk level: {risk_level.value}. Current price: ${indicators.current_price:.2f}. "
                f"However, this is a probabilistic assessment and should not be treated as certainty."
            )
        
        return summary
    
    def _extract_key_points(
        self,
        signal: Signal,
        risk_assessment: RiskAssessment,
        indicators: TechnicalIndicators
    ) -> List[str]:
        """Extract key bullet points"""
        
        points = []
        
        # 1. Signal information
        signal_emoji = "📈" if signal.strength.signal_type == SignalType.BULLISH else "📉" if signal.strength.signal_type == SignalType.BEARISH else "➡️"
        points.append(
            f"{signal_emoji} Signal: {signal.strength.signal_type.value.upper()} "
            f"({signal.strength.strength}, {signal.strength.confidence:.1%} confidence)"
        )
        
        # 2. Key supporting factors (top 2)
        primary_factors = signal.reasoning.primary_factors[:2]
        for factor in primary_factors:
            points.append(f"✓ {factor}")
        
        # 3. Risk level
        risk_emoji = "🔴" if risk_assessment.overall_risk in [RiskLevel.CRITICAL, RiskLevel.HIGH] else "🟡" if risk_assessment.overall_risk == RiskLevel.MODERATE else "🟢"
        points.append(f"{risk_emoji} Risk Level: {risk_assessment.overall_risk.value.upper()}")
        
        # 4. Key risk factors (top 2)
        top_risks = sorted(
            risk_assessment.risk_factors,
            key=lambda x: {"critical": 4, "high": 3, "moderate": 2, "low": 1}[x.level.value],
            reverse=True
        )[:2]
        for risk in top_risks:
            points.append(f"⚠️ {risk.name}: {risk.description}")
        
        # 5. Actionability
        if risk_assessment.is_actionable:
            points.append("✅ Signal meets minimum actionability criteria")
        else:
            points.append("⛔ Signal does NOT meet actionability criteria - monitoring only")
        
        # 6. Key assumption or limitation
        if signal.reasoning.limitations:
            points.append(f"ℹ️ {signal.reasoning.limitations[0]}")
        
        return points
    
    def _determine_recommendation(
        self,
        signal: Signal,
        risk_assessment: RiskAssessment
    ) -> Literal["consider", "monitor", "avoid", "no_action"]:
        """Determine overall recommendation"""
        
        # Neutral or non-actionable = no action
        if signal.strength.signal_type == SignalType.NEUTRAL:
            return "no_action"
        
        if not risk_assessment.is_actionable:
            return "monitor" if signal.strength.confidence > 0.5 else "avoid"
        
        # Critical or high risk = avoid or monitor only
        if risk_assessment.overall_risk in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            return "avoid"
        
        # Actionable with acceptable risk
        if signal.strength.confidence >= 0.70:
            return "consider"
        else:
            return "monitor"
    
    def _calculate_overall_confidence(
        self,
        signal: Signal,
        risk_assessment: RiskAssessment
    ) -> float:
        """
        Calculate overall confidence factoring in signal confidence and risk.
        Risk reduces confidence.
        """
        base_confidence = signal.strength.confidence
        
        # Risk penalty
        risk_penalty = {
            RiskLevel.LOW: 0.0,
            RiskLevel.MODERATE: 0.1,
            RiskLevel.HIGH: 0.2,
            RiskLevel.CRITICAL: 0.4
        }
        
        penalty = risk_penalty.get(risk_assessment.overall_risk, 0.1)
        adjusted_confidence = max(0.1, base_confidence - penalty)
        
        # Cap at 95%
        return min(adjusted_confidence, 0.95)


# Singleton instance
explanation_generator = ExplanationGenerator()
