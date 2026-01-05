"""Market data provider - Mock implementation for MVP"""

from datetime import datetime, timedelta
from typing import List, Optional
import random
import math

from app.models.schemas import StockPrice, StockFundamentals, MarketData
from app.core.market_data.base import BaseMarketDataProvider


class MockMarketDataProvider(BaseMarketDataProvider):
    """
    Mock market data provider for MVP testing.
    Generates realistic-looking price data with trends and volatility.
    
    In production, this would be replaced with real market data APIs.
    """
    
    # Mock company database
    MOCK_COMPANIES = {
        "AAPL": {"name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics"},
        "MSFT": {"name": "Microsoft Corporation", "sector": "Technology", "industry": "Software"},
        "GOOGL": {"name": "Alphabet Inc.", "sector": "Technology", "industry": "Internet"},
        "TSLA": {"name": "Tesla, Inc.", "sector": "Automotive", "industry": "Electric Vehicles"},
        "AMZN": {"name": "Amazon.com Inc.", "sector": "Consumer Cyclical", "industry": "E-commerce"},
        "NVDA": {"name": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors"},
        "META": {"name": "Meta Platforms Inc.", "sector": "Technology", "industry": "Social Media"},
        "JPM": {"name": "JPMorgan Chase & Co.", "sector": "Financial", "industry": "Banking"},
        "V": {"name": "Visa Inc.", "sector": "Financial", "industry": "Payment Processing"},
        "WMT": {"name": "Walmart Inc.", "sector": "Consumer Defensive", "industry": "Retail"},
    }
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize with optional seed for reproducibility"""
        if seed is not None:
            random.seed(seed)
    
    def get_stock_data(
        self,
        ticker: str,
        lookback_days: int = 90
    ) -> MarketData:
        """
        Generate mock stock data for the specified ticker.
        
        Args:
            ticker: Stock ticker symbol
            lookback_days: Number of historical days to generate
            
        Returns:
            MarketData object with prices and fundamentals
        """
        ticker = ticker.upper()
        
        # Generate price history
        prices = self._generate_price_history(ticker, lookback_days)
        
        # Generate fundamentals
        fundamentals = self._generate_fundamentals(ticker, prices[-1].close if prices else 100.0)
        
        return MarketData(
            ticker=ticker,
            prices=prices,
            fundamentals=fundamentals,
            last_updated=datetime.now()
        )
    
    def _generate_price_history(
        self,
        ticker: str,
        days: int
    ) -> List[StockPrice]:
        """Generate realistic price history with trends and volatility"""
        
        # Seed based on ticker for consistency
        ticker_seed = sum(ord(c) for c in ticker)
        random.seed(ticker_seed)
        
        # Starting price (varies by ticker)
        base_price = 50 + (ticker_seed % 200)
        
        # Trend and volatility parameters
        trend = random.uniform(-0.001, 0.002)  # Daily drift
        volatility = random.uniform(0.015, 0.035)  # Daily volatility (1.5% - 3.5%)
        
        prices: List[StockPrice] = []
        current_price = base_price
        
        end_date = datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)
        
        for i in range(days):
            date = end_date - timedelta(days=days - i - 1)
            
            # Skip weekends (simplified - doesn't account for holidays)
            if date.weekday() >= 5:
                continue
            
            # Generate daily return with trend and random walk
            daily_return = trend + volatility * random.gauss(0, 1)
            current_price *= (1 + daily_return)
            
            # Ensure price stays positive
            current_price = max(current_price, 1.0)
            
            # Generate OHLC with realistic relationships
            open_price = current_price * (1 + random.uniform(-0.005, 0.005))
            close_price = current_price
            
            daily_range = abs(random.gauss(0.015, 0.005))  # ~1.5% average range
            high_price = max(open_price, close_price) * (1 + daily_range * random.random())
            low_price = min(open_price, close_price) * (1 - daily_range * random.random())
            
            # Ensure high >= low
            high_price = max(high_price, low_price + 0.01)
            
            # Generate volume (higher volume on bigger price moves)
            base_volume = 1_000_000 + random.randint(0, 5_000_000)
            volatility_multiplier = 1 + abs(daily_return) * 10
            volume = int(base_volume * volatility_multiplier)
            
            prices.append(StockPrice(
                timestamp=date,
                open=round(open_price, 2),
                high=round(high_price, 2),
                low=round(low_price, 2),
                close=round(close_price, 2),
                volume=volume
            ))
        
        return prices
    
    def _generate_fundamentals(
        self,
        ticker: str,
        current_price: float
    ) -> StockFundamentals:
        """Generate mock fundamental data"""
        
        company_info = self.MOCK_COMPANIES.get(
            ticker,
            {"name": f"{ticker} Corporation", "sector": "Unknown", "industry": "Unknown"}
        )
        
        # Generate realistic-ish fundamentals based on ticker
        ticker_seed = sum(ord(c) for c in ticker)
        random.seed(ticker_seed)
        
        # Shares outstanding varies by company size
        shares_outstanding = random.randint(500_000_000, 10_000_000_000)
        market_cap = current_price * shares_outstanding
        
        # P/E ratio varies by sector (tech tends higher)
        if company_info["sector"] == "Technology":
            pe_ratio = random.uniform(20, 45)
        elif company_info["sector"] == "Financial":
            pe_ratio = random.uniform(10, 18)
        else:
            pe_ratio = random.uniform(12, 25)
        
        # Dividend yield (tech companies often lower)
        if company_info["sector"] == "Technology":
            dividend_yield = random.uniform(0, 0.015)  # 0-1.5%
        else:
            dividend_yield = random.uniform(0.01, 0.04)  # 1-4%
        
        return StockFundamentals(
            ticker=ticker,
            company_name=company_info["name"],
            market_cap=round(market_cap, 2),
            pe_ratio=round(pe_ratio, 2),
            dividend_yield=round(dividend_yield, 4),
            sector=company_info["sector"],
            industry=company_info["industry"]
        )
    
    def is_valid_ticker(self, ticker: str) -> bool:
        """Check if ticker is in our mock database (for MVP)"""
        return ticker.upper() in self.MOCK_COMPANIES
    
    def get_provider_info(self) -> dict:
        """Return provider metadata"""
        return {
            "name": "Mock Market Data Provider",
            "source": "Synthetic/Demo Data",
            "description": "Generates realistic-looking market data for demonstration purposes",
            "data_quality": "demo",
            "update_frequency": "deterministic (not real-time)"
        }


# Singleton instance
market_data_provider = MockMarketDataProvider()
