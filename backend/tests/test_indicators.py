"""Tests for technical indicators"""

import pytest
import numpy as np
from datetime import datetime, timedelta

from app.core.indicators import indicator_calculator
from app.models.schemas import StockPrice


def generate_test_prices(days: int = 100, base_price: float = 100.0):
    """Helper to generate test price data"""
    prices = []
    current_price = base_price
    end_date = datetime.now()
    
    for i in range(days):
        date = end_date - timedelta(days=days - i - 1)
        if date.weekday() < 5:  # Skip weekends
            daily_change = np.random.normal(0, 0.02)
            current_price *= (1 + daily_change)
            current_price = max(current_price, 1.0)
            
            prices.append(StockPrice(
                timestamp=date,
                open=round(current_price * 1.01, 2),
                high=round(current_price * 1.02, 2),
                low=round(current_price * 0.98, 2),
                close=round(current_price, 2),
                volume=1000000
            ))
    
    return prices


def test_calculate_indicators_success():
    """Test successful indicator calculation"""
    prices = generate_test_prices(100)
    indicators = indicator_calculator.calculate_all("TEST", prices)
    
    assert indicators is not None
    assert indicators.ticker == "TEST"
    assert indicators.sma_20 is not None
    assert indicators.sma_50 is not None
    assert indicators.rsi is not None
    assert 0 <= indicators.rsi <= 100
    assert indicators.macd is not None


def test_calculate_indicators_insufficient_data():
    """Test with insufficient data"""
    prices = generate_test_prices(30)  # Less than 50 days
    indicators = indicator_calculator.calculate_all("TEST", prices)
    
    assert indicators is None


def test_rsi_bounds():
    """Test RSI stays within 0-100 bounds"""
    prices = generate_test_prices(100)
    indicators = indicator_calculator.calculate_all("TEST", prices)
    
    assert indicators is not None
    assert 0 <= indicators.rsi <= 100


def test_bollinger_bands_order():
    """Test Bollinger Bands have correct ordering"""
    prices = generate_test_prices(100)
    indicators = indicator_calculator.calculate_all("TEST", prices)
    
    assert indicators is not None
    assert indicators.bollinger_lower < indicators.bollinger_middle < indicators.bollinger_upper
