"""Indian market data provider using Yahoo Finance (yfinance)"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from decimal import Decimal

try:
    import yfinance as yf
except ImportError:
    raise ImportError(
        "yfinance library is required for Indian market data. "
        "Install with: pip install yfinance"
    )

from app.core.market_data.base import (
    BaseMarketDataProvider,
    DataProviderError,
    InvalidTickerError
)
from app.models.schemas import StockPrice, StockFundamentals, MarketData
from app.models.enums import ExchangeEnum, CountryEnum, CurrencyEnum
from app.core.cache import cache_manager

logger = logging.getLogger(__name__)


class IndianMarketDataProvider(BaseMarketDataProvider):
    """
    Indian market data provider using Yahoo Finance (free, unlimited).
    
    Features:
    - NSE/BSE stock data
    - Free, no rate limits
    - Real-time prices (15min delayed)
    - Historical data
    - Ticker format: SYMBOL.NS (NSE) or SYMBOL.BO (BSE)
    """
    
    def __init__(self):
        logger.info("🇮🇳 Indian Market Data Provider initialized (Yahoo Finance)")
    
    def get_stock_data(
        self,
        ticker: str,
        lookback_days: int = 90
    ) -> MarketData:
        """
        Fetch Indian stock data from Yahoo Finance.
        
        Args:
            ticker: Stock symbol (e.g., "RELIANCE.NS", "TCS.BO")
            lookback_days: Historical data period
            
        Returns:
            MarketData with prices and metadata
        """
        ticker = ticker.upper()
        cache_key = f"market_data:indian:{ticker}:{lookback_days}"
        
        # Try cache first
        cached = cache_manager.get(cache_key)
        if cached:
            age_hours = (datetime.now() - cached.last_updated).total_seconds() / 3600
            
            if age_hours < 1:  # Fresh data
                logger.info(f"✅ Cache HIT (fresh): {ticker} - age: {age_hours*60:.1f}min")
                cached.data_source = "cache_fresh"
                return cached
            elif age_hours < 24:  # Stale but usable
                logger.warning(f"⚠️ Cache HIT (stale): {ticker} ({age_hours:.1f}h old)")
                cached.data_source = "cache_stale"
                return cached
        
        logger.info(f"🇮🇳 Fetching Indian stock data: {ticker}")
        
        try:
            prices = self._fetch_prices(ticker, lookback_days)
            
            # Detect exchange from ticker suffix
            if ticker.endswith('.NS'):
                exchange = ExchangeEnum.NSE
                base_ticker = ticker[:-3]
            elif ticker.endswith('.BO'):
                exchange = ExchangeEnum.BSE
                base_ticker = ticker[:-3]
            else:
                raise InvalidTickerError(f"Indian tickers must end with .NS or .BO: {ticker}")
            
            market_data = MarketData(
                ticker=base_ticker,
                exchange=exchange,
                country=CountryEnum.IN,
                currency=CurrencyEnum.INR,
                prices=prices,
                fundamentals=None,  # Not implemented yet
                last_updated=datetime.now(),
                data_source="yahoo_finance"
            )
            
            # Cache for 1 hour
            cache_manager.set(cache_key, market_data, ttl=3600)
            
            return market_data
            
        except Exception as e:
            logger.error(f"Failed to fetch {ticker}: {e}")
            
            # Serve stale cache if available
            if cached:
                logger.warning(f"⚠️ Serving stale cache for {ticker}")
                cached.data_source = "cache_stale_fallback"
                return cached
            
            raise DataProviderError(f"Failed to fetch data for {ticker}: {str(e)}")
    
    def _fetch_prices(self, ticker: str, lookback_days: int) -> List[StockPrice]:
        """Fetch price data from Yahoo Finance"""
        try:
            # Download data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days + 10)  # Buffer for weekends
            
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)
            
            if hist.empty:
                raise InvalidTickerError(f"No data found for {ticker}")
            
            # Convert to StockPrice objects
            prices = []
            for date, row in hist.iterrows():
                try:
                    price = StockPrice(
                        timestamp=date.to_pydatetime(),
                        open=float(row['Open']),
                        high=float(row['High']),
                        low=float(row['Low']),
                        close=float(row['Close']),
                        volume=int(row['Volume'])
                    )
                    
                    # Validation
                    if price.close <= 0 or price.high <= 0 or price.low <= 0:
                        logger.warning(f"⚠️ Invalid price for {ticker} on {date}")
                        continue
                    
                    if price.high < price.low:
                        logger.warning(f"⚠️ High < Low for {ticker} on {date}")
                        continue
                    
                    prices.append(price)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Skipping invalid data for {ticker}: {e}")
                    continue
            
            if len(prices) < 30:
                raise DataProviderError(
                    f"Insufficient data for {ticker}: only {len(prices)} days (need 30+)"
                )
            
            # Keep most recent lookback_days
            prices = prices[-lookback_days:]
            
            logger.info(f"✅ Fetched {len(prices)} price points for {ticker}")
            return prices
            
        except Exception as e:
            raise DataProviderError(f"Yahoo Finance error for {ticker}: {str(e)}")
    
    def is_valid_ticker(self, ticker: str) -> bool:
        """Check if ticker is valid Indian stock"""
        ticker = ticker.upper()
        return ticker.endswith('.NS') or ticker.endswith('.BO')
    
    def validate_ticker_exists(self, ticker: str) -> tuple[bool, str]:
        """
        Validate if ticker exists in Yahoo Finance.
        Returns: (is_valid, error_message)
        """
        ticker = ticker.upper()
        
        # Format check
        if not (ticker.endswith('.NS') or ticker.endswith('.BO')):
            return False, "Indian tickers must end with .NS (NSE) or .BO (BSE)"
        
        try:
            # Try to fetch minimal data with short timeout
            stock = yf.Ticker(ticker)
            
            # Quick check - try to get just 1 day of data
            hist = stock.history(period='1d', timeout=3)
            
            if hist.empty:
                return False, f"Stock '{ticker}' not found. Please check the ticker symbol."
            
            return True, ""
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'no data' in error_msg or 'not found' in error_msg or '404' in error_msg:
                return False, f"Stock '{ticker}' not found. Please verify the ticker symbol."
            elif 'timeout' in error_msg or 'timed out' in error_msg:
                return False, f"Validation timed out. '{ticker}' may not be a valid stock."
            else:
                logger.warning(f"Ticker validation failed for {ticker}: {e}")
                return False, f"Could not validate '{ticker}'. Please check the ticker symbol."
    
    def get_current_quote(self, ticker: str) -> StockPrice:
        """
        Get the most recent price for a ticker.
        
        Args:
            ticker: Stock symbol (e.g., "RELIANCE.NS")
            
        Returns:
            StockPrice with current price data
        """
        ticker = ticker.upper()
        
        try:
            stock = yf.Ticker(ticker)
            
            # Get latest 1-day data
            hist = stock.history(period='1d', timeout=5)
            
            if hist.empty:
                raise DataProviderError(f"No current price data for {ticker}")
            
            # Get the most recent row
            latest = hist.iloc[-1]
            
            return StockPrice(
                timestamp=latest.name.to_pydatetime() if hasattr(latest.name, 'to_pydatetime') else datetime.now(),
                open=float(latest['Open']),
                high=float(latest['High']),
                low=float(latest['Low']),
                close=float(latest['Close']),
                volume=int(latest['Volume'])
            )
            
        except Exception as e:
            logger.error(f"Failed to fetch current quote for {ticker}: {e}")
            raise DataProviderError(f"Could not fetch current price for {ticker}")
    
    def get_historical_price(self, ticker: str, date: str) -> float:
        """
        Get the closing price for a specific date.
        Useful when you remember the date you bought but not the exact price.
        
        Args:
            ticker: Stock symbol (e.g., "RELIANCE.NS")
            date: Date in YYYY-MM-DD format
            
        Returns:
            Closing price on that date (or nearest trading day)
        """
        ticker = ticker.upper()
        
        try:
            stock = yf.Ticker(ticker)
            
            # Parse the date
            target_date = datetime.strptime(date, '%Y-%m-%d')
            
            # Fetch data around that date (±5 days to handle weekends/holidays)
            start_date = target_date - timedelta(days=5)
            end_date = target_date + timedelta(days=5)
            
            hist = stock.history(start=start_date.strftime('%Y-%m-%d'), 
                               end=end_date.strftime('%Y-%m-%d'), 
                               timeout=5)
            
            if hist.empty:
                raise DataProviderError(f"No price data found for {ticker} around {date}")
            
            # Find the closest trading day
            hist.index = hist.index.tz_localize(None)  # Remove timezone
            closest_idx = hist.index.get_indexer([target_date], method='nearest')[0]
            closest_row = hist.iloc[closest_idx]
            
            return float(closest_row['Close'])
            
        except Exception as e:
            logger.error(f"Failed to fetch historical price for {ticker} on {date}: {e}")
            raise DataProviderError(f"Could not fetch price for {ticker} on {date}")
    
    def get_provider_info(self) -> dict:
        """Return provider metadata"""
        return {
            "name": "Yahoo Finance (Indian Markets)",
            "type": "live",
            "rate_limit": "Unlimited (free tier)",
            "cost_per_request": "$0.00 (free)",
            "data_quality": "real-time (15min delayed)",
            "supported_tickers": "NSE/BSE stocks (.NS/.BO suffix)",
            "exchanges": ["NSE", "BSE"],
            "country": "India",
            "currency": "INR"
        }
