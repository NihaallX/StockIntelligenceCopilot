"""Market data module"""

from .provider import market_data_provider, MockMarketDataProvider
from .factory import get_market_data_provider, ProviderFactory
from .base import BaseMarketDataProvider, DataProviderError, InvalidTickerError

__all__ = [
    "market_data_provider",  # Legacy - deprecated
    "MockMarketDataProvider",
    "get_market_data_provider",  # NEW - use this
    "ProviderFactory",
    "BaseMarketDataProvider",
    "DataProviderError",
    "InvalidTickerError"
]
