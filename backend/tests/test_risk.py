"""Tests for risk engine"""

import pytest
from datetime import datetime

from app.core.risk import risk_engine
from app.models.schemas import (
    Signal,
    SignalType,
    SignalStrength,
    SignalReasoning,
    TimeHorizon,
    TechnicalIndicators,
    RiskLevel,
)


def create_test_signal(
    signal_type: SignalType = SignalType.BULLISH,
    confidence: float = 0.75,
    time_horizon: TimeHorizon = TimeHorizon.LONG_TERM
) -> Signal:
    """Helper to create test signal"""
    return Signal(
        ticker="TEST",
        timestamp=datetime.now(),
        strength=SignalStrength(
            signal_type=signal_type,
            confidence=confidence,
            strength="moderate"
        ),
        reasoning=SignalReasoning(
            primary_factors=["Test factor"],
            supporting_indicators={"RSI": 50.0},
            contradicting_factors=[],
            assumptions=["Test assumption"],
            limitations=["Test limitation"]
        ),
        time_horizon=time_horizon
    )


def create_test_indicators(
    rsi: float = 50.0,
    volatility_high: bool = False
) -> TechnicalIndicators:
    """Helper to create test indicators"""
    if volatility_high:
        bb_width = 0.20  # High volatility
    else:
        bb_width = 0.08  # Normal volatility
    
    return TechnicalIndicators(
        ticker="TEST",
        timestamp=datetime.now(),
        sma_20=100.0,
        sma_50=100.0,
        rsi=rsi,
        macd=0.0,
        macd_signal=0.0,
        macd_histogram=0.0,
        bollinger_upper=100.0 * (1 + bb_width/2),
        bollinger_middle=100.0,
        bollinger_lower=100.0 * (1 - bb_width/2),
        current_price=100.0
    )


def test_high_confidence_signal_passes():
    """Test that high confidence signal with low risk is actionable"""
    signal = create_test_signal(confidence=0.80)
    indicators = create_test_indicators()
    
    assessment = risk_engine.assess_risk(signal, indicators, "moderate")
    
    assert assessment.is_actionable
    assert assessment.overall_risk in [RiskLevel.LOW, RiskLevel.MODERATE]


def test_low_confidence_signal_blocked():
    """Test that low confidence signal is not actionable"""
    signal = create_test_signal(confidence=0.50)  # Below threshold
    indicators = create_test_indicators()
    
    assessment = risk_engine.assess_risk(signal, indicators, "moderate")
    
    assert not assessment.is_actionable


def test_high_volatility_risk():
    """Test that high volatility is flagged as risk"""
    signal = create_test_signal()
    indicators = create_test_indicators(volatility_high=True)
    
    assessment = risk_engine.assess_risk(signal, indicators, "moderate")
    
    risk_names = [rf.name for rf in assessment.risk_factors]
    assert "High Volatility" in risk_names


def test_extreme_rsi_risk():
    """Test that extreme RSI values are flagged"""
    signal = create_test_signal()
    indicators = create_test_indicators(rsi=90.0)  # Extreme overbought
    
    assessment = risk_engine.assess_risk(signal, indicators, "moderate")
    
    risk_names = [rf.name for rf in assessment.risk_factors]
    assert "Extreme Overbought" in risk_names


def test_conservative_user_blocks_high_risk():
    """Test that conservative users don't get high-risk signals"""
    signal = create_test_signal(confidence=0.80)
    indicators = create_test_indicators(volatility_high=True, rsi=85.0)
    
    assessment = risk_engine.assess_risk(signal, indicators, "conservative")
    
    # High risk + conservative = not actionable
    if assessment.overall_risk == RiskLevel.HIGH:
        assert not assessment.is_actionable


def test_neutral_signal_not_actionable():
    """Test that neutral signals are never actionable"""
    signal = create_test_signal(signal_type=SignalType.NEUTRAL, confidence=0.80)
    indicators = create_test_indicators()
    
    assessment = risk_engine.assess_risk(signal, indicators, "aggressive")
    
    assert not assessment.is_actionable
