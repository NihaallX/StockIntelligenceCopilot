"""
Database Adapter - Cached fundamental data

Falls back to database when:
- API providers unavailable
- Rate limits exceeded
- Network issues

Cache TTL: 24 hours (configurable)
"""

import logging
from typing import Optional
from decimal import Decimal
from datetime import datetime, timedelta

from .base import FundamentalAdapter, FundamentalDataResult, DataSource
from app.core.database import get_service_db

logger = logging.getLogger(__name__)


class DatabaseAdapter(FundamentalAdapter):
    """
    Database-backed fundamental data adapter
    
    Reads from fundamental_data table (populated by background jobs or admin seeding)
    """
    
    CACHE_TTL_HOURS = 24
    
    async def fetch_fundamentals(self, ticker: str) -> FundamentalDataResult:
        """
        Fetch fundamentals from database
        
        Returns cached data if:
        - Data exists for ticker
        - Data age < 24 hours (or force_stale=True)
        """
        db = get_service_db()
        
        try:
            result = db.table("fundamental_data").select("*").eq("ticker", ticker).execute()
            
            if not result.data or len(result.data) == 0:
                logger.debug(f"No database data for {ticker}")
                return FundamentalDataResult(
                    ticker=ticker,
                    source=DataSource.UNAVAILABLE,
                    available=False
                )
            
            data = result.data[0]
            
            # Check data age
            last_updated = None
            data_age_hours = None
            
            if data.get("last_updated"):
                last_updated = datetime.fromisoformat(data["last_updated"].replace("Z", "+00:00"))
                data_age_hours = int((datetime.utcnow() - last_updated.replace(tzinfo=None)).total_seconds() / 3600)
                
                if data_age_hours > self.CACHE_TTL_HOURS:
                    logger.warning(
                        f"Database data for {ticker} is {data_age_hours}h old "
                        f"(> {self.CACHE_TTL_HOURS}h threshold)"
                    )
            
            # Build result
            fundamental_result = FundamentalDataResult(
                ticker=data["ticker"],
                source=DataSource.DATABASE,
                available=True,
                company_name=data.get("company_name"),
                market_cap=Decimal(str(data["market_cap"])) if data.get("market_cap") else None,
                pe_ratio=Decimal(str(data["pe_ratio"])) if data.get("pe_ratio") else None,
                pb_ratio=Decimal(str(data["pb_ratio"])) if data.get("pb_ratio") else None,
                dividend_yield=Decimal(str(data["dividend_yield"])) if data.get("dividend_yield") else None,
                revenue_growth_yoy=Decimal(str(data["revenue_growth_yoy"])) if data.get("revenue_growth_yoy") else None,
                earnings_growth_yoy=Decimal(str(data["earnings_growth_yoy"])) if data.get("earnings_growth_yoy") else None,
                revenue_growth_qoq=Decimal(str(data["revenue_growth_qoq"])) if data.get("revenue_growth_qoq") else None,
                eps=Decimal(str(data["eps"])) if data.get("eps") else None,
                profit_margin=Decimal(str(data["profit_margin"])) if data.get("profit_margin") else None,
                operating_margin=Decimal(str(data["operating_margin"])) if data.get("operating_margin") else None,
                roe=Decimal(str(data["roe"])) if data.get("roe") else None,
                roa=Decimal(str(data["roa"])) if data.get("roa") else None,
                debt_to_equity=Decimal(str(data["debt_to_equity"])) if data.get("debt_to_equity") else None,
                current_ratio=Decimal(str(data["current_ratio"])) if data.get("current_ratio") else None,
                quick_ratio=Decimal(str(data["quick_ratio"])) if data.get("quick_ratio") else None,
                sector=data.get("sector"),
                industry=data.get("industry"),
                exchange=data.get("exchange"),
                currency=data.get("currency", "INR"),
                last_updated=last_updated,
                data_age_hours=data_age_hours
            )
            
            logger.info(
                f"Database fetch for {ticker}: "
                f"{fundamental_result.completeness_percent:.0f}% complete, "
                f"age={data_age_hours}h"
            )
            
            return fundamental_result
            
        except Exception as e:
            logger.error(f"Database fetch failed for {ticker}: {e}", exc_info=True)
            return FundamentalDataResult(
                ticker=ticker,
                source=DataSource.UNAVAILABLE,
                available=False
            )
    
    async def health_check(self) -> bool:
        """Check if database is accessible"""
        try:
            db = get_service_db()
            result = db.table("fundamental_data").select("count").execute()
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def get_name(self) -> str:
        """Provider name"""
        return "Database (Cached)"
    
    def supports_market(self, exchange: str) -> bool:
        """Database can store any market data"""
        return True
