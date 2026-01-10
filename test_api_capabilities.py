"""Quick test of Yahoo Finance and FMP capabilities for stock similarity"""
import yfinance as yf
import httpx
import asyncio
import json
from datetime import datetime

# Test tickers
TICKERS = ["ITC.NS", "RELIANCE.NS", "TCS.NS"]
FMP_KEY = "qty5ZwSYBANWmtoWHYi1zfE8zDbKXXOV"


def test_yahoo_finance_data():
    """Check what Yahoo Finance gives us for finding similar stocks"""
    print("="*80)
    print("YAHOO FINANCE - Available Data for Stock Comparison")
    print("="*80)
    
    for ticker_symbol in TICKERS:
        print(f"\n📊 {ticker_symbol}")
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            
            # Fields useful for finding similar stocks
            comparison_fields = {
                "Sector": info.get("sector"),
                "Industry": info.get("industry"),
                "Market Cap": info.get("marketCap"),
                "PE Ratio": info.get("trailingPE"),
                "Price/Book": info.get("priceToBook"),
                "ROE": info.get("returnOnEquity"),
                "Profit Margin": info.get("profitMargins"),
                "Revenue Growth": info.get("revenueGrowth"),
                "Beta": info.get("beta"),
                "52W High": info.get("fiftyTwoWeekHigh"),
                "52W Low": info.get("fiftyTwoWeekLow"),
                "Dividend Yield": info.get("dividendYield"),
                "Country": info.get("country"),
                "Exchange": info.get("exchange"),
            }
            
            for field, value in comparison_fields.items():
                if value is not None:
                    print(f"  ✅ {field}: {value}")
                else:
                    print(f"  ❌ {field}: None")
                    
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n" + "="*80)
    print("SUMMARY: Yahoo Finance Capabilities")
    print("="*80)
    print("✅ Sector & Industry classification")
    print("✅ Market Cap, PE, PB, ROE (valuation metrics)")
    print("✅ Beta (volatility comparison)")
    print("✅ Profit margins, revenue growth")
    print("❌ NO direct 'similar stocks' API")
    print("❌ NO screener/filter API")
    print("\nConclusion: We can fetch data for stocks we already know about,")
    print("but Yahoo Finance doesn't offer an API to DISCOVER similar stocks.")


async def test_fmp_capabilities():
    """Check what FMP offers for finding similar stocks"""
    print("\n\n" + "="*80)
    print("FMP (Financial Modeling Prep) - Similar Stock Discovery")
    print("="*80)
    
    client = httpx.AsyncClient(timeout=30.0)
    
    # Test 1: Stock Screener (if available in free tier)
    print("\n📊 Test 1: Stock Screener API")
    try:
        response = await client.get(
            "https://financialmodelingprep.com/api/v3/stock-screener",
            params={
                "marketCapMoreThan": 1000000000,
                "limit": 5,
                "apikey": FMP_KEY
            }
        )
        
        if response.status_code == 402:
            print("❌ 402 Payment Required - Not available in free tier")
        elif response.status_code == 200:
            data = response.json()
            print(f"✅ Screener works! Got {len(data)} results")
            if data:
                print(f"   Sample: {data[0].get('symbol')} - {data[0].get('companyName')}")
        else:
            print(f"❌ Status {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Company Profile (basic data)
    print("\n📊 Test 2: Company Profile (RELIANCE.NS)")
    try:
        response = await client.get(
            "https://financialmodelingprep.com/stable/profile",
            params={"symbol": "RELIANCE.NS", "apikey": FMP_KEY}
        )
        
        if response.status_code == 402:
            print("❌ 402 Payment Required")
        elif response.status_code == 200:
            data = response.json()
            if data:
                profile = data[0]
                print(f"✅ Profile available:")
                print(f"   Sector: {profile.get('sector')}")
                print(f"   Industry: {profile.get('industry')}")
                print(f"   Market Cap: {profile.get('mktCap')}")
                print(f"   PE Ratio: {profile.get('pe')}")
        else:
            print(f"❌ Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Stock List by Exchange
    print("\n📊 Test 3: Stock List by Exchange (NSE)")
    try:
        response = await client.get(
            "https://financialmodelingprep.com/api/v3/symbol/available-nse",
            params={"apikey": FMP_KEY}
        )
        
        if response.status_code == 402:
            print("❌ 402 Payment Required - Not available in free tier")
        elif response.status_code == 200:
            data = response.json()
            print(f"✅ Stock list works! Got {len(data)} NSE stocks")
            print(f"   Can be used to build watchlist for screening")
        else:
            print(f"❌ Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Sector Performance
    print("\n📊 Test 4: Sector Performance")
    try:
        response = await client.get(
            "https://financialmodelingprep.com/api/v3/sector-performance",
            params={"apikey": FMP_KEY}
        )
        
        if response.status_code == 402:
            print("❌ 402 Payment Required")
        elif response.status_code == 200:
            data = response.json()
            print(f"✅ Sector performance available")
            if data:
                for sector in data[:3]:
                    print(f"   {sector.get('sector')}: {sector.get('changesPercentage')}")
        else:
            print(f"❌ Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    await client.aclose()
    
    print("\n" + "="*80)
    print("SUMMARY: FMP Free Tier Capabilities (250 calls/day)")
    print("="*80)
    print("✅ Profile data (sector, industry, market cap, PE)")
    print("❓ Screener API - needs testing (might be premium)")
    print("❓ Stock list by exchange - needs testing")
    print("✅ Sector performance")
    print("\nConclusion: FMP is primarily for fetching known stock data,")
    print("not for discovering similar stocks automatically.")


def show_recommendation():
    """Show our recommendation for implementation"""
    print("\n\n" + "="*80)
    print("RECOMMENDATION FOR SIMILAR STOCK DISCOVERY")
    print("="*80)
    
    print("\n🎯 BEST APPROACH: Manual Sector Mapping + Yahoo Finance Data")
    print("-" * 80)
    print("""
STRATEGY:
1. Fetch user's portfolio from Supabase (ITC.NS, RELIANCE.NS, TCS.NS)
2. For each owned stock, use Yahoo Finance to get sector/industry
3. Use hardcoded sector mapping to find candidate stocks in same sectors
4. Use Yahoo Finance to fetch metrics for all candidates (PE, ROE, market cap, etc.)
5. Score similarity based on:
   - Same sector (50% weight)
   - Similar market cap (20% weight)
   - Similar valuation (PE, PB) (20% weight)
   - Similar profitability (ROE, margins) (10% weight)
6. Return top 10-15 most similar stocks (excluding owned)

ADVANTAGES:
✅ Works with free Yahoo Finance API (no cost)
✅ Real-time data for valuation metrics
✅ Can compare stocks on multiple dimensions
✅ No need for premium API subscriptions
✅ Works for Indian stocks (.NS suffix)

ALTERNATIVE (More Advanced):
- Use FMP for richer fundamental data (PE, ROE, debt ratios)
- Calculate similarity score based on multiple metrics
- Requires 250 API calls/day budget (reasonable for our use)

IMPLEMENTATION:
1. Add scoring algorithm to opportunities.py
2. Fetch metrics via Yahoo Finance for candidate stocks
3. Calculate similarity scores
4. Cache results for 1 hour to save API calls
""")


if __name__ == "__main__":
    # Test Yahoo Finance
    test_yahoo_finance_data()
    
    # Test FMP
    asyncio.run(test_fmp_capabilities())
    
    # Show recommendation
    show_recommendation()
