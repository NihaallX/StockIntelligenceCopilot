"""Tests for signal generation"""

import pytest
from datetime import datetime

from app.core.signals import signal_generator
from app.models.schemas import (
    TechnicalIndicators,
    MarketData,
    StockPrice,
    SignalType,
    TimeHorizon,
)


def test_bullish_signal_generation():
    """Test generation of bullish signal"""
    # Create indicators that should generate bullish signal
    indicators = TechnicalIndicators(
        ticker="TEST",
        timestamp=datetime.now(),
        sma_20=105.0,  # Above sma_50
        sma_50=100.0,
        rsi=25.0,  # Oversold
        macd=0.5,  # Above signal
        macd_signal=0.3,
        macd_histogram=0.2,
        bollinger_upper=110.0,
        bollinger_middle=100.0,
        bollinger_lower=90.0,
        current_price=95.0  # Near lower band
    )
    
    market_data = MarketData(
        ticker="TEST",
        prices=[],
        fundamentals=None
    )
    
    signal = signal_generator.generate_signal(
        market_data=market_data,
        indicators=indicators,
        time_horizon=TimeHorizon.LONG_TERM
    )
    
    assert signal.strength.signal_type == SignalType.BULLISH
    assert 0 <= signal.strength.confidence <= 0.95
    assert len(signal.reasoning.primary_factors) > 0


def test_bearish_signal_generation():
    """Test generation of bearish signal"""
    indicators = TechnicalIndicators(
        ticker="TEST",
        timestamp=datetime.now(),
        sma_20=95.0,  # Below sma_50
        sma_50=100.0,
        rsi=80.0,  # Overbought
        macd=-0.5,  # Below signal
        macd_signal=-0.3,
        macd_histogram=-0.2,
        bollinger_upper=110.0,
        bollinger_middle=100.0,
        bollinger_lower=90.0,
        current_price=112.0  # Above upper band
    )
    
    market_data = MarketData(
        ticker="TEST",
        prices=[],
        fundamentals=None
    )
    
    signal = signal_generator.generate_signal(
        market_data=market_data,
        indicators=indicators,
        time_horizon=TimeHorizon.LONG_TERM
    )
    
    assert signal.strength.signal_type == SignalType.BEARISH
    assert 0 <= signal.strength.confidence <= 0.95


def test_confidence_cap():
    """Test that confidence is capped at 95%"""
    # Extreme bullish indicators
    indicators = TechnicalIndicators(
        ticker="TEST",
        timestamp=datetime.now(),
        sma_20=150.0,
        sma_50=100.0,
        rsi=20.0,
        macd=5.0,
        macd_signal=1.0,
        macd_histogram=4.0,
        bollinger_upper=110.0,
        bollinger_middle=100.0,
        bollinger_lower=90.0,
        current_price=85.0
    )
    
    market_data = MarketData(ticker="TEST", prices=[], fundamentals=None)
    signal = signal_generator.generate_signal(market_data, indicators)
    
    assert signal.strength.confidence <= 0.95
