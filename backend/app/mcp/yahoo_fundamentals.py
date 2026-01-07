"""
Yahoo Finance MCP Provider
===========================

Optional provider for fundamentals snapshot ONLY.
NO intraday dependency.

Features:
- Company fundamentals
- Financial ratios
- Historical daily data (not used for intraday)

No API key required (uses yfinance library).
"""

import yfinance as yf
import logging
from typing import List, Optional
from datetime import datetime
from .base import (
    MCPProvider,
    OHLCVData,
    IndicatorData,
    IndexData,
    TimeframeEnum,
    MCPDataUnavailable
)

logger = logging.getLogger(__name__)


class YahooFinanceMCPProvider(MCPProvider):
    """Yahoo Finance provider - fundamentals only"""
    
    def __init__(self):
        super().__init__(api_key=None)  # No API key needed
    
    async def fetch_intraday_ohlcv(
        self,
        symbol: str,
        timeframe: TimeframeEnum,
        limit: int = 100
    ) -> List[OHLCVData]:
        """
        NOT SUPPORTED for intraday
        Yahoo Finance free tier doesn't provide reliable intraday data
        """
        raise MCPDataUnavailable(
            "Yahoo Finance does not support intraday OHLCV. "
            "Use Alpha Vantage or Twelve Data."
        )
    
    async def fetch_indicators(
        self,
        symbol: str,
        timeframe: TimeframeEnum
    ) -> IndicatorData:
        """NOT SUPPORTED - Use Alpha Vantage or Twelve Data"""
        raise MCPDataUnavailable("Yahoo Finance does not provide technical indicators")
    
    async def fetch_index_data(
        self,
        index_symbol: str
    ) -> IndexData:
        """Fetch index data from Yahoo Finance"""
        
        try:
            ticker = yf.Ticker(index_symbol)
            info = ticker.info
            
            if not info:
                raise MCPDataUnavailable(f"No data for {index_symbol}")
            
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            prev_close = info.get('previousClose', current_price)
            
            change_percent = ((current_price - prev_close) / prev_close) * 100 if prev_close else 0
            
            return IndexData(
                symbol=index_symbol,
                price=current_price,
                change_percent=change_percent,
                timestamp=datetime.now(),
                source="yahoo_finance"
            )
            
        except Exception as e:
            raise MCPDataUnavailable(f"Error fetching index from Yahoo: {e}")
    
    async def health_check(self) -> bool:
        """Check if Yahoo Finance is accessible"""
        try:
            ticker = yf.Ticker("^GSPC")  # S&P 500
            info = ticker.info
            return info is not None and len(info) > 0
        except Exception as e:
            logger.error(f"Yahoo Finance health check failed: {e}")
            return False
    
    async def get_fundamentals(self, symbol: str) -> Optional[dict]:
        """
        Get company fundamentals (async-compatible)
        
        Returns:
            Dict with PE ratio, market cap, etc. or None
        """
        try:
            clean_symbol = symbol.split('.')[0]
            ticker = yf.Ticker(clean_symbol)
            info = ticker.info
            
            if not info:
                return None
            
            return {
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "price_to_book": info.get("priceToBook"),
                "debt_to_equity": info.get("debtToEquity"),
                "roe": info.get("returnOnEquity"),
                "dividend_yield": info.get("dividendYield"),
                "source": "yahoo_finance"
            }
            
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {symbol}: {e}")
            return None
