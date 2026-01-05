"""Technical indicators calculator"""

from typing import List, Optional
import numpy as np
from datetime import datetime

from app.models.schemas import StockPrice, TechnicalIndicators


class IndicatorCalculator:
    """
    Calculate technical indicators from price data.
    
    Implements:
    - Simple Moving Average (SMA)
    - Exponential Moving Average (EMA)
    - Relative Strength Index (RSI)
    - Moving Average Convergence Divergence (MACD)
    - Bollinger Bands
    """
    
    @staticmethod
    def calculate_all(
        ticker: str,
        prices: List[StockPrice]
    ) -> Optional[TechnicalIndicators]:
        """
        Calculate all technical indicators for the given price data.
        
        Args:
            ticker: Stock ticker symbol
            prices: List of price data points
            
        Returns:
            TechnicalIndicators object or None if insufficient data
        """
        if len(prices) < 50:  # Need at least 50 days for reliable indicators
            return None
        
        # Extract close prices and convert to numpy array
        closes = np.array([p.close for p in prices])
        latest_timestamp = prices[-1].timestamp
        current_price = prices[-1].close
        
        # Calculate all indicators
        sma_20 = IndicatorCalculator._sma(closes, 20)
        sma_50 = IndicatorCalculator._sma(closes, 50)
        ema_12 = IndicatorCalculator._ema(closes, 12)
        ema_26 = IndicatorCalculator._ema(closes, 26)
        
        rsi = IndicatorCalculator._rsi(closes, 14)
        
        macd_line, signal_line, histogram = IndicatorCalculator._macd(closes)
        
        bb_upper, bb_middle, bb_lower = IndicatorCalculator._bollinger_bands(closes, 20, 2.0)
        
        return TechnicalIndicators(
            ticker=ticker,
            timestamp=latest_timestamp,
            sma_20=sma_20,
            sma_50=sma_50,
            ema_12=ema_12,
            ema_26=ema_26,
            rsi=rsi,
            macd=macd_line,
            macd_signal=signal_line,
            macd_histogram=histogram,
            bollinger_upper=bb_upper,
            bollinger_middle=bb_middle,
            bollinger_lower=bb_lower,
            current_price=current_price
        )
    
    @staticmethod
    def _sma(data: np.ndarray, period: int) -> Optional[float]:
        """Calculate Simple Moving Average"""
        if len(data) < period:
            return None
        return float(np.mean(data[-period:]))
    
    @staticmethod
    def _ema(data: np.ndarray, period: int) -> Optional[float]:
        """Calculate Exponential Moving Average"""
        if len(data) < period:
            return None
        
        multiplier = 2 / (period + 1)
        ema = data[0]  # Start with first value
        
        for price in data[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return float(ema)
    
    @staticmethod
    def _rsi(data: np.ndarray, period: int = 14) -> Optional[float]:
        """
        Calculate Relative Strength Index (RSI)
        
        RSI = 100 - (100 / (1 + RS))
        where RS = Average Gain / Average Loss
        """
        if len(data) < period + 1:
            return None
        
        # Calculate price changes
        deltas = np.diff(data)
        
        # Separate gains and losses
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Calculate average gains and losses
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0  # No losses = overbought
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi)
    
    @staticmethod
    def _macd(
        data: np.ndarray,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Returns:
            (macd_line, signal_line, histogram)
        """
        if len(data) < slow_period + signal_period:
            return None, None, None
        
        # Calculate EMAs
        ema_fast = IndicatorCalculator._ema(data, fast_period)
        ema_slow = IndicatorCalculator._ema(data, slow_period)
        
        if ema_fast is None or ema_slow is None:
            return None, None, None
        
        # MACD line = EMA(12) - EMA(26)
        macd_line = ema_fast - ema_slow
        
        # Calculate signal line (EMA of MACD line)
        # For simplicity, we'll approximate using recent MACD values
        # In production, you'd maintain the full MACD history
        macd_values = []
        for i in range(max(slow_period, len(data) - 50), len(data)):
            if i < slow_period:
                continue
            ema_f = IndicatorCalculator._ema(data[:i+1], fast_period)
            ema_s = IndicatorCalculator._ema(data[:i+1], slow_period)
            if ema_f and ema_s:
                macd_values.append(ema_f - ema_s)
        
        if len(macd_values) < signal_period:
            signal_line = macd_line  # Fallback
        else:
            signal_line = float(np.mean(macd_values[-signal_period:]))
        
        # Histogram = MACD - Signal
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def _bollinger_bands(
        data: np.ndarray,
        period: int = 20,
        std_dev: float = 2.0
    ) -> tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Calculate Bollinger Bands
        
        Returns:
            (upper_band, middle_band, lower_band)
        """
        if len(data) < period:
            return None, None, None
        
        # Middle band = SMA
        middle = float(np.mean(data[-period:]))
        
        # Standard deviation
        std = float(np.std(data[-period:]))
        
        # Upper and lower bands
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        
        return upper, middle, lower


# Singleton instance
indicator_calculator = IndicatorCalculator()
