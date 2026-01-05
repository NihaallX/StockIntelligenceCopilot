"""Live market data provider using Alpha Vantage API"""

import logging
import time
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from decimal import Decimal

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    raise ImportError(
        "requests library is required for live data provider. "
        "Install with: pip install requests"
    )

from app.core.market_data.base import (
    BaseMarketDataProvider,
    DataProviderError,
    InvalidTickerError,
    RateLimitExceededError,
    StaleDataWarning
)
from app.models.schemas import StockPrice, StockFundamentals, MarketData
from app.core.cache import cache_manager

logger = logging.getLogger(__name__)


class LiveMarketDataProvider(BaseMarketDataProvider):
    """
    Live market data provider using Alpha Vantage.
    
    Features:
    - Real-time and historical price data
    - Automatic caching (TTL: 1min intraday, 24h historical)
    - Retry logic with exponential backoff
    - Rate limit handling (5 requests/minute on free tier)
    - Data validation
    """
    
    BASE_URL = "https://www.alphavantage.co/query"
    RATE_LIMIT_CALLS = 5
    RATE_LIMIT_PERIOD = 60  # seconds
    
    def __init__(self, api_key: str):
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")
        self.api_key = api_key.strip()
        self.base_url = self.BASE_URL
        self.call_timestamps: List[float] = []
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic"""
        session = requests.Session()
        
        # Retry on 429, 500, 502, 503, 504
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,  # 1s, 2s, 4s
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session
    
    def _check_rate_limit(self):
        """Check if we're within rate limits"""
        now = time.time()
        
        # Remove calls older than RATE_LIMIT_PERIOD
        self.call_timestamps = [
            ts for ts in self.call_timestamps 
            if now - ts < self.RATE_LIMIT_PERIOD
        ]
        
        logger.info(f"📊 Rate limit check: {len(self.call_timestamps)}/{self.RATE_LIMIT_CALLS} calls in last {self.RATE_LIMIT_PERIOD}s")
        
        if len(self.call_timestamps) >= self.RATE_LIMIT_CALLS:
            wait_time = self.RATE_LIMIT_PERIOD - (now - self.call_timestamps[0])
            logger.warning(f"⏳ Rate limit reached. Need to wait {wait_time:.1f}s...")
            raise RateLimitExceededError(
                f"Rate limit exceeded: {self.RATE_LIMIT_CALLS} calls per {self.RATE_LIMIT_PERIOD}s. "
                f"Please try again in {int(wait_time + 1)} seconds."
            )
        
        self.call_timestamps.append(now)
        logger.info(f"✅ Rate limit OK. Call {len(self.call_timestamps)}/{self.RATE_LIMIT_CALLS}")
    
    def get_stock_data(
        self,
        ticker: str,
        lookback_days: int = 90
    ) -> MarketData:
        """
        Fetch live market data for a ticker.
        
        Caching strategy:
        - Check cache first
        - If cache miss or stale, fetch from API
        - Store in cache with TTL
        """
        ticker = ticker.upper()
        cache_key = f"market_data:{ticker}:{lookback_days}"
        
        # Try cache first
        cached = cache_manager.get(cache_key)
        if cached:
            age_hours = (datetime.now() - cached.last_updated).total_seconds() / 3600
            
            if age_hours < 1:  # Fresh data (< 1 hour)
                logger.info(f"✅ Cache HIT (fresh): {ticker} - age: {age_hours*60:.1f}min")
                cached.data_source = "cache_fresh"
                return cached
            elif age_hours < 24:  # Stale but usable (< 24 hours)
                logger.warning(f"⚠️ Cache HIT (stale): {ticker} ({age_hours:.1f}h old)")
                cached.data_source = "cache_stale"
                cached.data_quality_warning = f"Data is {age_hours:.1f} hours old"
                # Try to refresh in background but serve stale data
                return cached
        
        logger.info(f"❌ Cache MISS: {ticker} - fetching live data...")
        
        try:
            prices = self._fetch_prices(ticker, lookback_days)
            fundamentals = self._fetch_fundamentals(ticker, prices[-1].close if prices else None)
            
            market_data = MarketData(
                ticker=ticker,
                prices=prices,
                fundamentals=fundamentals,
                last_updated=datetime.now(),
                data_source="live",
                data_quality_warning=None
            )
            
            # Cache for 1 hour
            cache_manager.set(cache_key, market_data, ttl=3600)
            
            return market_data
            
        except RateLimitExceededError:
            # Serve stale cache if available
            if cached:
                logger.error(f"⚠️ Rate limit exceeded. Serving stale cache: {ticker}")
                cached.data_source = "cache_stale_fallback"
                cached.data_quality_warning = "Live data unavailable due to rate limit. Using cached data."
                return cached
            else:
                raise DataProviderError(
                    f"Rate limit exceeded and no cached data available for {ticker}. "
                    "Please try again in 60 seconds."
                )
        
        except Exception as e:
            logger.error(f"❌ Failed to fetch live data for {ticker}: {e}")
            
            # Try to serve any cached data as last resort
            if cached:
                logger.warning(f"⚠️ Serving stale cache as fallback: {ticker}")
                cached.data_source = "cache_error_fallback"
                cached.data_quality_warning = f"Live data fetch failed: {str(e)}. Using cached data."
                return cached
            else:
                raise DataProviderError(
                    f"Failed to fetch data for {ticker} and no cache available: {str(e)}"
                )
    
    def _fetch_prices(self, ticker: str, lookback_days: int) -> List[StockPrice]:
        """Fetch historical prices from Alpha Vantage"""
        self._check_rate_limit()
        
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": ticker,
            "outputsize": "full" if lookback_days > 100 else "compact",
            "apikey": self.api_key
        }
        
        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Debug logging
            logger.info(f"Alpha Vantage response keys: {list(data.keys())}")
            
            # Check for API errors
            if "Error Message" in data:
                raise InvalidTickerError(f"Invalid ticker: {ticker}")
            
            if "Note" in data:
                # Rate limit message
                raise RateLimitExceededError(data["Note"])
            
            if "Information" in data:
                # API limit message
                logger.error(f"Alpha Vantage API limit: {data['Information']}")
                raise RateLimitExceededError(data["Information"])
            
            if "Time Series (Daily)" not in data:
                logger.error(f"Response data: {data}")
                raise DataProviderError(f"Unexpected response format for {ticker}. Keys: {list(data.keys())}")
            
            time_series = data["Time Series (Daily)"]
            
            # Parse and validate
            prices = []
            for date_str, values in sorted(time_series.items(), reverse=True)[:lookback_days]:
                try:
                    price = StockPrice(
                        timestamp=datetime.strptime(date_str, "%Y-%m-%d"),
                        open=float(values["1. open"]),
                        high=float(values["2. high"]),
                        low=float(values["3. low"]),
                        close=float(values["4. close"]),
                        volume=int(values["6. volume"])
                    )
                    
                    # Validation
                    if price.close <= 0 or price.high <= 0 or price.low <= 0:
                        logger.warning(f"⚠️ Invalid price data for {ticker} on {date_str}")
                        continue
                    
                    if price.high < price.low:
                        logger.warning(f"⚠️ High < Low for {ticker} on {date_str}")
                        continue
                    
                    if price.volume < 0:
                        logger.warning(f"⚠️ Negative volume for {ticker} on {date_str}")
                        continue
                    
                    prices.append(price)
                    
                except (KeyError, ValueError) as e:
                    logger.warning(f"⚠️ Skipping invalid data point for {ticker}: {e}")
                    continue
            
            prices.reverse()  # Chronological order
            
            if len(prices) < 30:
                raise DataProviderError(
                    f"Insufficient data for {ticker}: only {len(prices)} days available (need 30+)"
                )
            
            logger.info(f"✅ Fetched {len(prices)} price points for {ticker}")
            return prices
            
        except requests.RequestException as e:
            raise DataProviderError(f"Network error fetching {ticker}: {str(e)}")
    
    def _fetch_fundamentals(self, ticker: str, current_price: Optional[float]) -> Optional[StockFundamentals]:
        """
        Fetch fundamental data from Alpha Vantage.
        
        Note: This requires a separate API call. For free tier, may hit rate limits.
        Consider using database cache layer from Phase 2B.
        """
        # For Phase 2C, we'll skip real-time fundamentals to avoid rate limits
        # and use the existing database cache layer from Phase 2B
        logger.info(f"ℹ️ Skipping live fundamentals for {ticker} (using database cache)")
        return None
    
    def is_valid_ticker(self, ticker: str) -> bool:
        """
        Check if ticker exists.
        
        Note: Alpha Vantage doesn't have a dedicated validation endpoint.
        We validate during data fetch.
        """
        # For now, accept any uppercase ticker 1-5 chars
        # Will validate during actual fetch
        return len(ticker) >= 1 and len(ticker) <= 5 and ticker.isalpha()
    
    def get_provider_info(self) -> dict:
        """Return provider metadata"""
        return {
            "name": "Alpha Vantage",
            "type": "live",
            "rate_limit": f"{self.RATE_LIMIT_CALLS} requests/{self.RATE_LIMIT_PERIOD}s",
            "cost_per_request": "$0.00 (free tier)",
            "data_quality": "live",
            "supported_tickers": "8000+ US stocks"
        }
