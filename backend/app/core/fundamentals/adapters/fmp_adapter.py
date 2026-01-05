"""
Financial Modeling Prep (FMP) Adapter

Free tier: 250 calls/day
Supports: Global stocks including Indian markets (NSE/BSE)

API Docs: https://site.financialmodelingprep.com/developer/docs/
"""

import os
import logging
import httpx
from typing import Optional
from decimal import Decimal
from datetime import datetime, timedelta

from .base import FundamentalAdapter, FundamentalDataResult, DataSource

logger = logging.getLogger(__name__)


class FMPAdapter(FundamentalAdapter):
    """
    Financial Modeling Prep API adapter
    
    Endpoints used (NEW /stable API as of Aug 2025):
    - /stable/profile?symbol={ticker} - Company profile, market cap, sector
    - /stable/ratios?symbol={ticker} - Financial ratios (PE, PB, ROE, etc.)
    - /stable/income-statement?symbol={ticker} - Revenue, earnings, margins
    
    Free tier limits: 250 calls/day
    Rate limiting: 3 seconds between calls
    """
    
    BASE_URL = "https://financialmodelingprep.com/stable"
    CACHE_TTL_HOURS = 24
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FMP adapter
        
        Args:
            api_key: FMP API key (from environment or passed directly)
        """
        self.api_key = api_key or os.getenv("FMP_API_KEY")
        if not self.api_key:
            logger.warning("FMP_API_KEY not set - FMP adapter will not work")
        
        self._client = httpx.AsyncClient(timeout=10.0)
        self._last_call_time = None
        self._rate_limit_delay = 3.0  # seconds
    
    async def fetch_fundamentals(self, ticker: str) -> FundamentalDataResult:
        """
        Fetch fundamentals from FMP
        
        Strategy:
        1. Try profile endpoint (basic info)
        2. Try ratios endpoint (valuation, profitability)
        3. Try income statement (growth metrics)
        4. Combine all data
        5. Return partial data if some endpoints fail
        """
        if not self.api_key:
            logger.error("Cannot fetch from FMP - API key not configured")
            return FundamentalDataResult(
                ticker=ticker,
                source=DataSource.UNAVAILABLE,
                available=False
            )
        
        try:
            # Normalize ticker for FMP (RELIANCE.NS → RELIANCE.NS works on FMP)
            # FMP supports .NS and .BO suffixes for Indian stocks
            
            logger.info(f"Fetching fundamentals from FMP for {ticker}")
            
            # Fetch profile (company info, market cap, sector)
            profile_data = await self._fetch_profile(ticker)
            
            # Fetch ratios (PE, PB, ROE, debt ratios)
            ratios_data = await self._fetch_ratios(ticker)
            
            # Fetch income statement (revenue growth, margins)
            income_data = await self._fetch_income_statement(ticker)
            
            # Combine data
            result = self._combine_data(ticker, profile_data, ratios_data, income_data)
            
            logger.info(
                f"FMP fetch complete for {ticker}: "
                f"{result.completeness_percent:.0f}% complete, "
                f"{result.fields_available}/{result.fields_total} fields"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"FMP fetch failed for {ticker}: {e}", exc_info=True)
            return FundamentalDataResult(
                ticker=ticker,
                source=DataSource.FMP,
                available=False
            )
    
    async def _fetch_profile(self, ticker: str) -> Optional[dict]:
        """Fetch company profile"""
        try:
            url = f"{self.BASE_URL}/profile"
            params = {"symbol": ticker, "apikey": self.api_key}
            
            await self._rate_limit()
            response = await self._client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                return data[0]  # Profile returns array
            return None
            
        except Exception as e:
            logger.warning(f"FMP profile fetch failed for {ticker}: {e}")
            return None
    
    async def _fetch_ratios(self, ticker: str) -> Optional[dict]:
        """Fetch financial ratios"""
        try:
            url = f"{self.BASE_URL}/ratios"
            params = {"symbol": ticker, "apikey": self.api_key, "limit": 1}  # Latest only
            
            await self._rate_limit()
            response = await self._client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                return data[0]  # Latest ratios
            return None
            
        except Exception as e:
            logger.warning(f"FMP ratios fetch failed for {ticker}: {e}")
            return None
    
    async def _fetch_income_statement(self, ticker: str) -> Optional[dict]:
        """Fetch income statement for growth metrics"""
        try:
            url = f"{self.BASE_URL}/income-statement"
            params = {"symbol": ticker, "apikey": self.api_key, "limit": 2}  # Latest 2 for YoY growth
            
            await self._rate_limit()
            response = await self._client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) >= 2:
                # Calculate YoY growth from last 2 statements
                current = data[0]
                previous = data[1]
                
                current["revenue_growth_yoy"] = self._calculate_growth(
                    current.get("revenue"),
                    previous.get("revenue")
                )
                current["earnings_growth_yoy"] = self._calculate_growth(
                    current.get("netIncome"),
                    previous.get("netIncome")
                )
                
                return current
            elif data and len(data) == 1:
                return data[0]  # No growth calc, but still useful
            return None
            
        except Exception as e:
            logger.warning(f"FMP income statement fetch failed for {ticker}: {e}")
            return None
    
    def _calculate_growth(self, current: Optional[float], previous: Optional[float]) -> Optional[float]:
        """Calculate YoY growth percentage"""
        if current and previous and previous != 0:
            return ((current - previous) / previous) * 100
        return None
    
    def _combine_data(
        self,
        ticker: str,
        profile: Optional[dict],
        ratios: Optional[dict],
        income: Optional[dict]
    ) -> FundamentalDataResult:
        """Combine data from multiple FMP endpoints"""
        
        # If all failed, return unavailable
        if not profile and not ratios and not income:
            return FundamentalDataResult(
                ticker=ticker,
                source=DataSource.FMP,
                available=False
            )
        
        # Extract data with None fallbacks (partial data OK)
        result = FundamentalDataResult(
            ticker=ticker,
            source=DataSource.FMP,
            available=True,
            last_updated=datetime.utcnow()
        )
        
        # From profile
        if profile:
            result.company_name = profile.get("companyName")
            result.sector = profile.get("sector")
            result.industry = profile.get("industry")
            result.exchange = profile.get("exchangeShortName")  # NSE, BSE, etc.
            result.currency = profile.get("currency", "INR")
            
            if profile.get("mktCap"):
                result.market_cap = Decimal(str(profile["mktCap"]))
        
        # From ratios
        if ratios:
            if ratios.get("priceEarningsRatio"):
                result.pe_ratio = Decimal(str(ratios["priceEarningsRatio"]))
            if ratios.get("priceToBookRatio"):
                result.pb_ratio = Decimal(str(ratios["priceToBookRatio"]))
            if ratios.get("dividendYield"):
                result.dividend_yield = Decimal(str(ratios["dividendYield"])) * 100  # Convert to %
            if ratios.get("returnOnEquity"):
                result.roe = Decimal(str(ratios["returnOnEquity"])) * 100
            if ratios.get("returnOnAssets"):
                result.roa = Decimal(str(ratios["returnOnAssets"])) * 100
            if ratios.get("debtEquityRatio"):
                result.debt_to_equity = Decimal(str(ratios["debtEquityRatio"]))
            if ratios.get("currentRatio"):
                result.current_ratio = Decimal(str(ratios["currentRatio"]))
            if ratios.get("quickRatio"):
                result.quick_ratio = Decimal(str(ratios["quickRatio"]))
        
        # From income statement
        if income:
            if income.get("revenueGrowth"):
                result.revenue_growth_yoy = Decimal(str(income["revenueGrowth"])) * 100
            elif income.get("revenue_growth_yoy"):  # Calculated by us
                result.revenue_growth_yoy = Decimal(str(income["revenue_growth_yoy"]))
            
            if income.get("earnings_growth_yoy"):
                result.earnings_growth_yoy = Decimal(str(income["earnings_growth_yoy"]))
            
            if income.get("netIncomeRatio"):
                result.profit_margin = Decimal(str(income["netIncomeRatio"])) * 100
            if income.get("operatingIncomeRatio"):
                result.operating_margin = Decimal(str(income["operatingIncomeRatio"])) * 100
            if income.get("eps"):
                result.eps = Decimal(str(income["eps"]))
        
        # Calculate completeness (done automatically in __post_init__)
        result._calculate_completeness()
        
        return result
    
    async def _rate_limit(self):
        """Simple rate limiting (3 sec between calls)"""
        if self._last_call_time:
            elapsed = (datetime.now() - self._last_call_time).total_seconds()
            if elapsed < self._rate_limit_delay:
                import asyncio
                await asyncio.sleep(self._rate_limit_delay - elapsed)
        
        self._last_call_time = datetime.now()
    
    async def health_check(self) -> bool:
        """Check if FMP API is accessible"""
        if not self.api_key:
            return False
        
        try:
            url = f"{self.BASE_URL}/profile/AAPL"  # Simple test with well-known ticker
            params = {"apikey": self.api_key}
            
            response = await self._client.get(url, params=params)
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"FMP health check failed: {e}")
            return False
    
    def get_name(self) -> str:
        """Provider name"""
        return "Financial Modeling Prep"
    
    def supports_market(self, exchange: str) -> bool:
        """FMP supports NSE, BSE, and major global exchanges"""
        supported = ["NSE", "BSE", "NYSE", "NASDAQ", "LSE", "TSX"]
        return exchange.upper() in supported
    
    async def close(self):
        """Close HTTP client"""
        await self._client.aclose()
