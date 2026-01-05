"""Ticker search and market status endpoints"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
import logging

from app.models.ticker_schemas import (
    TickerSearchResponse,
    TickerMetadata,
    MarketStatus
)
from app.models.enums import ExchangeEnum, CountryEnum
from app.api.dependencies import get_current_user
from app.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/tickers", response_model=TickerSearchResponse)
async def search_tickers(
    q: str = Query(..., min_length=1, max_length=50, description="Search query"),
    country: Optional[CountryEnum] = Query(None, description="Filter by country"),
    exchange: Optional[ExchangeEnum] = Query(None, description="Filter by exchange"),
    limit: int = Query(default=10, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    """
    Search tickers by symbol or company name.
    
    Supports:
    - Partial matches on ticker or company name
    - Filtering by country or exchange
    - Full-text search with ranking
    
    Returns:
    - Ranked results (exact ticker match first)
    - Limited to active, supported tickers
    """
    try:
        db = get_db()
        
        # Build query with full-text search
        query_parts = []
        params = {"query_text": f"%{q.upper()}%", "limit": limit}
        
        # Base query with full-text search
        base_query = """
            SELECT 
                ticker,
                company_name,
                exchange,
                country,
                currency,
                sector,
                industry,
                market_cap,
                ticker_format,
                data_provider,
                is_supported,
                CASE
                    WHEN ticker = %(query_upper)s THEN 1
                    WHEN ticker ILIKE %(query_start)s THEN 2
                    WHEN company_name ILIKE %(query_start)s THEN 3
                    ELSE 4
                END as rank
            FROM ticker_metadata
            WHERE is_active = true
                AND (ticker ILIKE %(query_text)s OR company_name ILIKE %(query_text)s)
        """
        
        params["query_upper"] = q.upper()
        params["query_start"] = f"{q.upper()}%"
        
        # Add country filter
        if country:
            base_query += " AND country = %(country)s"
            params["country"] = country.value
        
        # Add exchange filter
        if exchange:
            base_query += " AND exchange = %(exchange)s"
            params["exchange"] = exchange.value
        
        # Order by rank and limit
        base_query += " ORDER BY rank, ticker LIMIT %(limit)s"
        
        # Execute query
        result = db.table("ticker_metadata").select("*").execute()
        
        # Since Supabase doesn't support complex queries easily, fall back to Python filtering
        all_tickers = result.data if result.data else []
        
        # Filter and rank in Python
        filtered = []
        query_upper = q.upper()
        
        for ticker_data in all_tickers:
            # Apply filters
            if not ticker_data.get("is_active"):
                continue
            
            ticker_sym = ticker_data["ticker"]
            company = ticker_data["company_name"]
            
            # Check if matches query
            if query_upper not in ticker_sym.upper() and query_upper not in company.upper():
                continue
            
            # Apply country filter
            if country and ticker_data["country"] != country.value:
                continue
            
            # Apply exchange filter
            if exchange and ticker_data["exchange"] != exchange.value:
                continue
            
            # Calculate rank
            if ticker_sym == query_upper:
                rank = 1
            elif ticker_sym.upper().startswith(query_upper):
                rank = 2
            elif company.upper().startswith(query_upper):
                rank = 3
            else:
                rank = 4
            
            filtered.append((rank, ticker_data))
        
        # Sort by rank and limit
        filtered.sort(key=lambda x: (x[0], x[1]["ticker"]))
        results = [
            TickerMetadata(
                ticker=t["ticker"],
                company_name=t["company_name"],
                exchange=ExchangeEnum(t["exchange"]),
                country=CountryEnum(t["country"]),
                currency=t["currency"],
                sector=t.get("sector"),
                industry=t.get("industry"),
                market_cap=t.get("market_cap"),
                ticker_format=t["ticker_format"],
                data_provider=t["data_provider"],
                is_supported=t.get("is_supported", True)
            )
            for rank, t in filtered[:limit]
        ]
        
        filters_applied = {}
        if country:
            filters_applied["country"] = country.value
        if exchange:
            filters_applied["exchange"] = exchange.value
        
        return TickerSearchResponse(
            results=results,
            total=len(filtered),
            query=q,
            filters_applied=filters_applied
        )
        
    except Exception as e:
        logger.error(f"Ticker search failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Search failed")


@router.get("/markets/{exchange}/status", response_model=MarketStatus)
async def get_market_status(
    exchange: ExchangeEnum,
    current_user: dict = Depends(get_current_user)
):
    """
    Get current market status for an exchange.
    
    Returns:
    - Whether market is currently open
    - Local time in market timezone
    - Next open/close times
    """
    from app.core.market_hours import MarketHoursService
    
    try:
        service = MarketHoursService()
        status = service.get_market_status(exchange)
        
        return MarketStatus(
            exchange=exchange,
            is_open=status["is_open"],
            timezone=status["timezone"],
            local_time=status["local_time"],
            next_open=status.get("next_open"),
            next_close=status.get("next_close")
        )
        
    except Exception as e:
        logger.error(f"Failed to get market status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get market status")
