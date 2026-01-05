"""Seed Indian stock tickers (NSE/BSE) into ticker_metadata table"""

import os
import sys
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment
load_dotenv()

# Get Supabase credentials
url = os.getenv("SUPABASE_URL")
service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Bypass RLS

if not url or not service_key:
    print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
    sys.exit(1)

# Create Supabase client
supabase: Client = create_client(url, service_key)

# Top 50 Indian stocks (NSE)
INDIAN_STOCKS = [
    # Banking & Financial Services
    {"ticker": "RELIANCE.NS", "name": "Reliance Industries Ltd", "sector": "Energy", "exchange": "NSE"},
    {"ticker": "TCS.NS", "name": "Tata Consultancy Services Ltd", "sector": "Technology", "exchange": "NSE"},
    {"ticker": "HDFCBANK.NS", "name": "HDFC Bank Ltd", "sector": "Banking", "exchange": "NSE"},
    {"ticker": "INFY.NS", "name": "Infosys Ltd", "sector": "Technology", "exchange": "NSE"},
    {"ticker": "ICICIBANK.NS", "name": "ICICI Bank Ltd", "sector": "Banking", "exchange": "NSE"},
    {"ticker": "HINDUNILVR.NS", "name": "Hindustan Unilever Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
    {"ticker": "BHARTIARTL.NS", "name": "Bharti Airtel Ltd", "sector": "Telecom", "exchange": "NSE"},
    {"ticker": "SBIN.NS", "name": "State Bank of India", "sector": "Banking", "exchange": "NSE"},
    {"ticker": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank Ltd", "sector": "Banking", "exchange": "NSE"},
    {"ticker": "LT.NS", "name": "Larsen & Toubro Ltd", "sector": "Construction", "exchange": "NSE"},
    
    # Technology
    {"ticker": "WIPRO.NS", "name": "Wipro Ltd", "sector": "Technology", "exchange": "NSE"},
    {"ticker": "HCLTECH.NS", "name": "HCL Technologies Ltd", "sector": "Technology", "exchange": "NSE"},
    {"ticker": "TECHM.NS", "name": "Tech Mahindra Ltd", "sector": "Technology", "exchange": "NSE"},
    
    # Automobiles
    {"ticker": "MARUTI.NS", "name": "Maruti Suzuki India Ltd", "sector": "Automobile", "exchange": "NSE"},
    {"ticker": "TATAMOTORS.NS", "name": "Tata Motors Ltd", "sector": "Automobile", "exchange": "NSE"},
    {"ticker": "M&M.NS", "name": "Mahindra & Mahindra Ltd", "sector": "Automobile", "exchange": "NSE"},
    {"ticker": "BAJAJ-AUTO.NS", "name": "Bajaj Auto Ltd", "sector": "Automobile", "exchange": "NSE"},
    
    # Pharma
    {"ticker": "SUNPHARMA.NS", "name": "Sun Pharmaceutical Industries Ltd", "sector": "Pharma", "exchange": "NSE"},
    {"ticker": "DRREDDY.NS", "name": "Dr. Reddy's Laboratories Ltd", "sector": "Pharma", "exchange": "NSE"},
    {"ticker": "CIPLA.NS", "name": "Cipla Ltd", "sector": "Pharma", "exchange": "NSE"},
    
    # Consumer
    {"ticker": "ITC.NS", "name": "ITC Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
    {"ticker": "ASIANPAINT.NS", "name": "Asian Paints Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
    {"ticker": "NESTLEIND.NS", "name": "Nestle India Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
    {"ticker": "TITAN.NS", "name": "Titan Company Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
    
    # Energy
    {"ticker": "ONGC.NS", "name": "Oil & Natural Gas Corporation Ltd", "sector": "Energy", "exchange": "NSE"},
    {"ticker": "NTPC.NS", "name": "NTPC Ltd", "sector": "Energy", "exchange": "NSE"},
    {"ticker": "POWERGRID.NS", "name": "Power Grid Corporation of India Ltd", "sector": "Energy", "exchange": "NSE"},
    {"ticker": "BPCL.NS", "name": "Bharat Petroleum Corporation Ltd", "sector": "Energy", "exchange": "NSE"},
    
    # Metals & Mining
    {"ticker": "TATASTEEL.NS", "name": "Tata Steel Ltd", "sector": "Metals", "exchange": "NSE"},
    {"ticker": "HINDALCO.NS", "name": "Hindalco Industries Ltd", "sector": "Metals", "exchange": "NSE"},
    {"ticker": "COALINDIA.NS", "name": "Coal India Ltd", "sector": "Mining", "exchange": "NSE"},
    
    # Financial Services
    {"ticker": "BAJFINANCE.NS", "name": "Bajaj Finance Ltd", "sector": "Finance", "exchange": "NSE"},
    {"ticker": "BAJAJFINSV.NS", "name": "Bajaj Finserv Ltd", "sector": "Finance", "exchange": "NSE"},
    {"ticker": "AXISBANK.NS", "name": "Axis Bank Ltd", "sector": "Banking", "exchange": "NSE"},
    
    # Cement
    {"ticker": "ULTRACEMCO.NS", "name": "UltraTech Cement Ltd", "sector": "Cement", "exchange": "NSE"},
    {"ticker": "GRASIM.NS", "name": "Grasim Industries Ltd", "sector": "Cement", "exchange": "NSE"},
    
    # Others
    {"ticker": "ADANIPORTS.NS", "name": "Adani Ports & SEZ Ltd", "sector": "Infrastructure", "exchange": "NSE"},
    {"ticker": "HEROMOTOCO.NS", "name": "Hero MotoCorp Ltd", "sector": "Automobile", "exchange": "NSE"},
    {"ticker": "BRITANNIA.NS", "name": "Britannia Industries Ltd", "sector": "Consumer Goods", "exchange": "NSE"},
    {"ticker": "DIVISLAB.NS", "name": "Divi's Laboratories Ltd", "sector": "Pharma", "exchange": "NSE"},
    
    # Telecom & Media
    {"ticker": "INDUSINDBK.NS", "name": "IndusInd Bank Ltd", "sector": "Banking", "exchange": "NSE"},
    {"ticker": "EICHERMOT.NS", "name": "Eicher Motors Ltd", "sector": "Automobile", "exchange": "NSE"},
    
    # Selected BSE stocks
    {"ticker": "RELIANCE.BO", "name": "Reliance Industries Ltd", "sector": "Energy", "exchange": "BSE"},
    {"ticker": "TCS.BO", "name": "Tata Consultancy Services Ltd", "sector": "Technology", "exchange": "BSE"},
    {"ticker": "HDFCBANK.BO", "name": "HDFC Bank Ltd", "sector": "Banking", "exchange": "BSE"},
]


def seed_indian_tickers():
    """Insert Indian stocks into ticker_metadata"""
    
    print(f"🇮🇳 Seeding {len(INDIAN_STOCKS)} Indian stocks...")
    
    inserted = 0
    skipped = 0
    
    for stock in INDIAN_STOCKS:
        try:
            data = {
                "ticker": stock["ticker"],
                "company_name": stock["name"],
                "exchange": stock["exchange"],
                "country": "IN",
                "currency": "INR",
                "sector": stock.get("sector"),
                "is_active": True,
                "is_supported": True,
                "data_provider": "yahoo_finance",
                "ticker_format": f"{stock['ticker']}",
            }
            
            # Insert (ON CONFLICT DO NOTHING)
            result = supabase.table("ticker_metadata").upsert(
                data,
                on_conflict="ticker,exchange"
            ).execute()
            
            if result.data:
                print(f"✅ {stock['ticker']:<20} - {stock['name']}")
                inserted += 1
            else:
                print(f"⏭️  {stock['ticker']:<20} - Already exists")
                skipped += 1
                
        except Exception as e:
            print(f"❌ {stock['ticker']:<20} - Error: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Inserted: {inserted}")
    print(f"   Skipped:  {skipped}")
    print(f"   Total:    {len(INDIAN_STOCKS)}")


if __name__ == "__main__":
    seed_indian_tickers()
