"""
Seed script for ticker_metadata table.
Populates with US market tickers from Alpha Vantage coverage.
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_db
from app.models.enums import ExchangeEnum, CountryEnum, CurrencyEnum
from app.config.settings import Settings
from supabase import create_client, Client
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# US market tickers (Tech, Finance, Healthcare, Energy, Retail)
US_TICKERS = [
    # Tech Giants
    {"ticker": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ", "sector": "Technology", "industry": "Consumer Electronics"},
    {"ticker": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ", "sector": "Technology", "industry": "Software"},
    {"ticker": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ", "sector": "Technology", "industry": "Internet Services"},
    {"ticker": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ", "sector": "Consumer Cyclical", "industry": "E-Commerce"},
    {"ticker": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ", "sector": "Technology", "industry": "Social Media"},
    {"ticker": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers"},
    
    # Finance
    {"ticker": "JPM", "name": "JPMorgan Chase & Co.", "exchange": "NYSE", "sector": "Financial", "industry": "Banking"},
    {"ticker": "BAC", "name": "Bank of America Corp.", "exchange": "NYSE", "sector": "Financial", "industry": "Banking"},
    {"ticker": "WFC", "name": "Wells Fargo & Co.", "exchange": "NYSE", "sector": "Financial", "industry": "Banking"},
    {"ticker": "GS", "name": "Goldman Sachs Group Inc.", "exchange": "NYSE", "sector": "Financial", "industry": "Investment Banking"},
    {"ticker": "V", "name": "Visa Inc.", "exchange": "NYSE", "sector": "Financial", "industry": "Payment Processing"},
    {"ticker": "MA", "name": "Mastercard Inc.", "exchange": "NYSE", "sector": "Financial", "industry": "Payment Processing"},
    
    # Healthcare
    {"ticker": "JNJ", "name": "Johnson & Johnson", "exchange": "NYSE", "sector": "Healthcare", "industry": "Pharmaceuticals"},
    {"ticker": "UNH", "name": "UnitedHealth Group Inc.", "exchange": "NYSE", "sector": "Healthcare", "industry": "Health Insurance"},
    {"ticker": "PFE", "name": "Pfizer Inc.", "exchange": "NYSE", "sector": "Healthcare", "industry": "Pharmaceuticals"},
    {"ticker": "ABBV", "name": "AbbVie Inc.", "exchange": "NYSE", "sector": "Healthcare", "industry": "Pharmaceuticals"},
    
    # Consumer & Retail
    {"ticker": "WMT", "name": "Walmart Inc.", "exchange": "NYSE", "sector": "Consumer Defensive", "industry": "Discount Stores"},
    {"ticker": "HD", "name": "Home Depot Inc.", "exchange": "NYSE", "sector": "Consumer Cyclical", "industry": "Home Improvement"},
    {"ticker": "NKE", "name": "Nike Inc.", "exchange": "NYSE", "sector": "Consumer Cyclical", "industry": "Footwear & Accessories"},
    {"ticker": "MCD", "name": "McDonald's Corp.", "exchange": "NYSE", "sector": "Consumer Cyclical", "industry": "Restaurants"},
    {"ticker": "SBUX", "name": "Starbucks Corporation", "exchange": "NASDAQ", "sector": "Consumer Cyclical", "industry": "Restaurants"},
    
    # Energy
    {"ticker": "XOM", "name": "Exxon Mobil Corporation", "exchange": "NYSE", "sector": "Energy", "industry": "Oil & Gas"},
    {"ticker": "CVX", "name": "Chevron Corporation", "exchange": "NYSE", "sector": "Energy", "industry": "Oil & Gas"},
    
    # Industrial
    {"ticker": "BA", "name": "Boeing Company", "exchange": "NYSE", "sector": "Industrials", "industry": "Aerospace & Defense"},
    {"ticker": "CAT", "name": "Caterpillar Inc.", "exchange": "NYSE", "sector": "Industrials", "industry": "Construction Equipment"},
    
    # Telecom & Media
    {"ticker": "DIS", "name": "Walt Disney Company", "exchange": "NYSE", "sector": "Communication Services", "industry": "Entertainment"},
    {"ticker": "NFLX", "name": "Netflix Inc.", "exchange": "NASDAQ", "sector": "Communication Services", "industry": "Streaming"},
    {"ticker": "T", "name": "AT&T Inc.", "exchange": "NYSE", "sector": "Communication Services", "industry": "Telecom"},
    
    # Additional Popular
    {"ticker": "INTC", "name": "Intel Corporation", "exchange": "NASDAQ", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "AMD", "name": "Advanced Micro Devices", "exchange": "NASDAQ", "sector": "Technology", "industry": "Semiconductors"},
    {"ticker": "CRM", "name": "Salesforce Inc.", "exchange": "NYSE", "sector": "Technology", "industry": "Software"},
    {"ticker": "ORCL", "name": "Oracle Corporation", "exchange": "NYSE", "sector": "Technology", "industry": "Software"},
    {"ticker": "CSCO", "name": "Cisco Systems Inc.", "exchange": "NASDAQ", "sector": "Technology", "industry": "Networking"},
    {"ticker": "IBM", "name": "IBM Corporation", "exchange": "NYSE", "sector": "Technology", "industry": "IT Services"},
]


def seed_us_tickers():
    """Seed US market tickers into ticker_metadata table"""
    try:
        # Use service role key for admin operations (bypasses RLS)
        settings = Settings()
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", settings.SUPABASE_SERVICE_ROLE_KEY)
        
        if not service_key or service_key == "your-service-role-key-here":
            logger.error("SUPABASE_SERVICE_ROLE_KEY not configured. This is required for seeding.")
            logger.info("Please set SUPABASE_SERVICE_ROLE_KEY in your .env file")
            return 0, 0
        
        db = create_client(settings.SUPABASE_URL, service_key)
        logger.info(f"Seeding {len(US_TICKERS)} US tickers with service role...")
        
        inserted = 0
        skipped = 0
        
        for ticker_data in US_TICKERS:
            try:
                # Check if already exists
                existing = db.table("ticker_metadata").select("id").eq("ticker", ticker_data["ticker"]).eq("exchange", ticker_data["exchange"]).execute()
                
                if existing.data:
                    logger.info(f"Skipping {ticker_data['ticker']} - already exists")
                    skipped += 1
                    continue
                
                # Insert ticker
                row = {
                    "ticker": ticker_data["ticker"],
                    "company_name": ticker_data["name"],
                    "exchange": ticker_data["exchange"],
                    "country": CountryEnum.US.value,
                    "currency": CurrencyEnum.USD.value,
                    "sector": ticker_data.get("sector"),
                    "industry": ticker_data.get("industry"),
                    "ticker_format": ticker_data["ticker"],  # US tickers use as-is
                    "data_provider": "alpha_vantage",
                    "is_active": True,
                    "is_supported": True,
                }
                
                result = db.table("ticker_metadata").insert(row).execute()
                
                if result.data:
                    logger.info(f"Inserted: {ticker_data['ticker']} - {ticker_data['name']}")
                    inserted += 1
                else:
                    logger.warning(f"Failed to insert {ticker_data['ticker']}")
                    
            except Exception as e:
                logger.error(f"Error inserting {ticker_data['ticker']}: {e}")
                continue
        
        logger.info(f"Seeding complete: {inserted} inserted, {skipped} skipped")
        return inserted, skipped
        
    except Exception as e:
        logger.error(f"Seeding failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    logger.info("Starting ticker seeding...")
    inserted, skipped = seed_us_tickers()
    logger.info(f"Done: {inserted} tickers added, {skipped} already existed")
