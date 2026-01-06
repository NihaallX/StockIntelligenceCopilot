"""Data Layer - Truth Only

Provides real-time and historical data without opinions.
Only numbers, no interpretations.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import yfinance as yf
import pandas as pd
import numpy as np


@dataclass
class IntradayMetrics:
    """Single source of truth for intraday stock data"""
    ticker: str
    timestamp: datetime
    
    # Price data
    current_price: float
    vwap: float
    open_price: float
    high: float
    low: float
    
    # Volume data
    current_volume: int
    avg_volume_20d: float
    volume_ratio: float  # current / average
    
    # Moving averages
    sma_20: float
    sma_50: float
    
    # Technical indicators
    rsi_14: float
    
    # Index comparison
    index_price: float
    index_change_pct: float
    stock_change_pct: float
    relative_performance: float  # stock % - index %
    
    # Sector data (optional)
    sector_change_pct: Optional[float] = None
    
    # Support/Resistance (calculated)
    recent_high_20d: float = 0.0
    recent_low_20d: float = 0.0


@dataclass
class PortfolioPosition:
    """User's holdings data"""
    ticker: str
    quantity: float
    entry_price: float
    current_price: float
    portfolio_weight_pct: float
    daily_pnl: float
    total_pnl: float


class IntradayDataProvider:
    """Fetches real-time and historical data for intraday analysis"""
    
    def __init__(self):
        self.index_ticker = "^NSEI"  # NIFTY 50
        self.banknifty_ticker = "^NSEBANK"
    
    def get_intraday_metrics(
        self, 
        ticker: str, 
        interval: str = "5m"
    ) -> Optional[IntradayMetrics]:
        """
        Fetch all required intraday metrics for a ticker.
        
        Args:
            ticker: Stock symbol (e.g., "RELIANCE.NS")
            interval: Candle interval (1m, 5m, 15m)
            
        Returns:
            IntradayMetrics object or None if data unavailable
        """
        try:
            stock = yf.Ticker(ticker)
            
            # Get intraday data (last 5 days for context)
            intraday_df = stock.history(period="5d", interval=interval)
            if intraday_df.empty:
                return None
            
            # Get daily data for averages
            daily_df = stock.history(period="60d", interval="1d")
            if daily_df.empty:
                return None
            
            # Get index data
            index_ticker = self._get_index_for_ticker(ticker)
            index = yf.Ticker(index_ticker)
            index_intraday = index.history(period="1d", interval=interval)
            
            # Calculate metrics
            current_price = float(intraday_df['Close'].iloc[-1])
            current_volume = int(intraday_df['Volume'].iloc[-1])
            
            # VWAP calculation (today only)
            today_data = intraday_df[intraday_df.index.date == intraday_df.index[-1].date()]
            vwap = self._calculate_vwap(today_data)
            
            # Volume average
            avg_volume_20d = float(daily_df['Volume'].tail(20).mean())
            
            # Moving averages (from daily data)
            sma_20 = float(daily_df['Close'].tail(20).mean())
            sma_50 = float(daily_df['Close'].tail(50).mean())
            
            # RSI
            rsi_14 = self._calculate_rsi(daily_df['Close'], period=14)
            
            # Index comparison
            if not index_intraday.empty:
                index_price = float(index_intraday['Close'].iloc[-1])
                index_open = float(index_intraday['Open'].iloc[0])
                index_change_pct = ((index_price - index_open) / index_open) * 100
            else:
                index_price = 0.0
                index_change_pct = 0.0
            
            # Stock change
            stock_open = float(intraday_df[intraday_df.index.date == intraday_df.index[-1].date()]['Open'].iloc[0])
            stock_change_pct = ((current_price - stock_open) / stock_open) * 100
            
            # Relative performance
            relative_performance = stock_change_pct - index_change_pct
            
            # Support/Resistance
            recent_high_20d = float(daily_df['High'].tail(20).max())
            recent_low_20d = float(daily_df['Low'].tail(20).min())
            
            return IntradayMetrics(
                ticker=ticker,
                timestamp=datetime.now(),
                current_price=current_price,
                vwap=vwap,
                open_price=stock_open,
                high=float(today_data['High'].max()),
                low=float(today_data['Low'].min()),
                current_volume=current_volume,
                avg_volume_20d=avg_volume_20d,
                volume_ratio=current_volume / avg_volume_20d if avg_volume_20d > 0 else 0,
                sma_20=sma_20,
                sma_50=sma_50,
                rsi_14=rsi_14,
                index_price=index_price,
                index_change_pct=index_change_pct,
                stock_change_pct=stock_change_pct,
                relative_performance=relative_performance,
                recent_high_20d=recent_high_20d,
                recent_low_20d=recent_low_20d,
            )
            
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None
    
    def _calculate_vwap(self, df: pd.DataFrame) -> float:
        """Calculate Volume Weighted Average Price"""
        if df.empty:
            return 0.0
        
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        vwap = (typical_price * df['Volume']).sum() / df['Volume'].sum()
        return float(vwap)
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0  # Neutral if insufficient data
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
    
    def _get_index_for_ticker(self, ticker: str) -> str:
        """Determine appropriate index for ticker"""
        # Simple logic: use NIFTY for Indian stocks
        if ticker.endswith('.NS') or ticker.endswith('.BO'):
            return self.index_ticker
        return "^GSPC"  # S&P 500 for US stocks
    
    def get_portfolio_positions(
        self, 
        user_id: str,
        db_connection
    ) -> List[PortfolioPosition]:
        """
        Fetch user's portfolio positions with current prices.
        
        Args:
            user_id: User identifier
            db_connection: Database connection object
            
        Returns:
            List of PortfolioPosition objects
        """
        # This will integrate with existing portfolio database
        # Placeholder for now
        positions = []
        
        # TODO: Query database for user positions
        # For each position, fetch current price and calculate metrics
        
        return positions
    
    def count_red_candles_with_volume(
        self, 
        ticker: str, 
        lookback_candles: int = 5
    ) -> int:
        """
        Count recent red candles that had above-average volume.
        Used for trend stress detection.
        """
        try:
            stock = yf.Ticker(ticker)
            intraday_df = stock.history(period="1d", interval="5m")
            
            if len(intraday_df) < lookback_candles:
                return 0
            
            recent = intraday_df.tail(lookback_candles)
            avg_volume = recent['Volume'].mean()
            
            red_with_volume = 0
            for _, candle in recent.iterrows():
                is_red = candle['Close'] < candle['Open']
                has_volume = candle['Volume'] > avg_volume
                if is_red and has_volume:
                    red_with_volume += 1
            
            return red_with_volume
            
        except Exception:
            return 0
