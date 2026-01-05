"""Abstract base class for market data providers"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from app.models.schemas import StockPrice, StockFundamentals, MarketData


class BaseMarketDataProvider(ABC):
    """
    Abstract interface for market data providers.
    
    All providers (mock, live, hybrid) must implement this interface.
    This ensures drop-in replacement without changing consumers.
    """
    
    @abstractmethod
    def get_stock_data(
        self,
        ticker: str,
        lookback_days: int = 90
    ) -> MarketData:
        """
        Fetch market data for a ticker.
        
        Args:
            ticker: Stock ticker symbol (uppercase)
            lookback_days: Historical days to fetch
            
        Returns:
            MarketData with prices and fundamentals
            
        Raises:
            DataProviderError: If data cannot be fetched
            InvalidTickerError: If ticker is invalid/unsupported
        """
        pass
    
    @abstractmethod
    def is_valid_ticker(self, ticker: str) -> bool:
        """Check if ticker is supported by this provider"""
        pass
    
    @abstractmethod
    def get_provider_info(self) -> dict:
        """
        Return metadata about this provider.
        
        Returns:
            {
                "name": "AlphaVantage" | "Mock" | "Polygon",
                "type": "live" | "demo",
                "rate_limit": "5 requests/minute",
                "cost_per_request": "$0.00" | "$0.01"
            }
        """
        pass


class DataProviderError(Exception):
    """Base exception for data provider errors"""
    pass


class InvalidTickerError(DataProviderError):
    """Ticker is invalid or unsupported"""
    pass


class RateLimitExceededError(DataProviderError):
    """API rate limit exceeded"""
    pass


class StaleDataWarning(Warning):
    """Data is stale but being served from cache"""
    pass
