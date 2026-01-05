"""Factory for selecting market data provider"""

import os
import logging
from typing import Optional

from app.core.market_data.base import BaseMarketDataProvider
from app.core.market_data.provider import MockMarketDataProvider

logger = logging.getLogger(__name__)


class ProviderFactory:
    """
    Factory for creating market data providers.
    
    Routes based on ticker format:
    - .NS/.BO → Indian provider (Yahoo Finance)
    - Others → US provider (Alpha Vantage or Mock)
    """
    
    _us_provider: Optional[BaseMarketDataProvider] = None
    _indian_provider: Optional[BaseMarketDataProvider] = None
    
    @classmethod
    def get_provider(cls, ticker: Optional[str] = None) -> BaseMarketDataProvider:
        """
        Get appropriate market data provider based on ticker.
        
        Args:
            ticker: Stock symbol (e.g., "RELIANCE.NS", "AAPL")
            
        Returns:
            Provider instance (US or Indian)
        """
        # Route to Indian provider for .NS/.BO tickers
        if ticker and (ticker.upper().endswith('.NS') or ticker.upper().endswith('.BO')):
            return cls._get_indian_provider()
        
        # Otherwise use US provider
        return cls._get_us_provider()
    
    @classmethod
    def _get_us_provider(cls) -> BaseMarketDataProvider:
        """Get US market provider (Alpha Vantage or Mock)"""
        if cls._us_provider is not None:
            return cls._us_provider
        
        provider_type = os.getenv("DATA_PROVIDER", "mock").lower()
        
        if provider_type == "mock":
            logger.info("MOCK market data provider (demo mode)")
            cls._us_provider = MockMarketDataProvider()
            
        elif provider_type == "live":
            logger.info("LIVE market data provider (US/Alpha Vantage)")
            
            # Validate required API keys
            api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "").strip()
            if not api_key or api_key == "your_api_key_here":
                logger.critical("ALPHA_VANTAGE_API_KEY not set! Cannot use live provider.")
                logger.critical("Set DATA_PROVIDER=mock explicitly or provide API key.")
                raise ValueError(
                    "Live data provider requested but ALPHA_VANTAGE_API_KEY not configured. "
                    "Set DATA_PROVIDER=mock to use demo mode."
                )
            
            # Import here to avoid dependency issues
            from app.core.market_data.live_provider import LiveMarketDataProvider
            cls._us_provider = LiveMarketDataProvider(api_key=api_key)
            
        else:
            raise ValueError(
                f"Invalid DATA_PROVIDER: {provider_type}. Must be 'mock' or 'live'."
            )
        
        return cls._us_provider
    
    @classmethod
    def _get_indian_provider(cls) -> BaseMarketDataProvider:
        """Get Indian market provider (Yahoo Finance)"""
        if cls._indian_provider is None:
            logger.info("🇮🇳 Initializing Indian market provider (Yahoo Finance)")
            from app.core.market_data.indian_provider import IndianMarketDataProvider
            cls._indian_provider = IndianMarketDataProvider()
        
        return cls._indian_provider
    
    @classmethod
    def reset(cls):
        """Reset singletons (for testing)"""
        cls._us_provider = None
        cls._indian_provider = None


# Singleton accessor
def get_market_data_provider(ticker: Optional[str] = None) -> BaseMarketDataProvider:
    """
    Get appropriate market data provider for ticker.
    
    Args:
        ticker: Stock symbol (e.g., "RELIANCE.NS", "AAPL"). If None, returns US provider.
        
    Returns:
        Provider instance
    """
    return ProviderFactory.get_provider(ticker=ticker)
