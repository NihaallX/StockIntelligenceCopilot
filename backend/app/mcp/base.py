"""
Base MCP Provider Interface
============================

Abstract interface all MCP providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class TimeframeEnum(str, Enum):
    """Supported timeframes"""
    ONE_MIN = "1min"
    FIVE_MIN = "5min"
    FIFTEEN_MIN = "15min"
    THIRTY_MIN = "30min"
    SIXTY_MIN = "60min"
    DAILY = "daily"


@dataclass
class OHLCVData:
    """OHLCV candle data"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    source: str  # Which provider returned this data


@dataclass
class IndicatorData:
    """Technical indicator values"""
    timestamp: datetime
    rsi: Optional[float] = None
    vwap: Optional[float] = None
    volume_ratio: Optional[float] = None  # Current vol / avg vol
    source: str = "unknown"


@dataclass
class IndexData:
    """Index/market data"""
    symbol: str  # e.g., "^NSEI" for NIFTY
    price: float
    change_percent: float
    timestamp: datetime
    source: str


class MCPProvider(ABC):
    """Abstract base class for all MCP providers"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.provider_name = self.__class__.__name__
    
    @abstractmethod
    async def fetch_intraday_ohlcv(
        self,
        symbol: str,
        timeframe: TimeframeEnum,
        limit: int = 100
    ) -> List[OHLCVData]:
        """
        Fetch intraday OHLCV data
        
        Args:
            symbol: Stock ticker (e.g., "RELIANCE.BSE")
            timeframe: Candle interval
            limit: Number of candles to fetch
            
        Returns:
            List of OHLCV candles with source tag
            
        Raises:
            MCPDataUnavailable: If data cannot be fetched
        """
        pass
    
    @abstractmethod
    async def fetch_indicators(
        self,
        symbol: str,
        timeframe: TimeframeEnum
    ) -> IndicatorData:
        """
        Fetch technical indicators
        
        Args:
            symbol: Stock ticker
            timeframe: Calculation timeframe
            
        Returns:
            IndicatorData with available metrics
        """
        pass
    
    @abstractmethod
    async def fetch_index_data(
        self,
        index_symbol: str
    ) -> IndexData:
        """
        Fetch index/market data
        
        Args:
            index_symbol: Index ticker (e.g., "^NSEI")
            
        Returns:
            IndexData with current state
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if provider is accessible
        
        Returns:
            True if provider responding, False otherwise
        """
        pass


class MCPDataUnavailable(Exception):
    """Raised when MCP data cannot be fetched"""
    pass


class MCPRateLimitError(Exception):
    """Raised when provider rate limit exceeded"""
    pass
