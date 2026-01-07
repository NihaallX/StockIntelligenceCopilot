"""
Test script to see ACTUAL data returned by free tier APIs
Run this to understand what we're really getting
"""

import asyncio
import httpx
import yfinance as yf
from datetime import datetime
import json

# Your API keys
ALPHA_VANTAGE_KEY = "MR98NDNBLHNNX0G1"
TWELVE_DATA_KEY = "a13e2ce450204eecbe0106e2e04a2981"
FMP_API_KEY = "qty5ZwSYBANWmtoWHYi1zfE8zDbKXXOV"


async def test_alpha_vantage():
    """Test Alpha Vantage - what do we actually get?"""
    print("\n" + "="*80)
    print("🔍 ALPHA VANTAGE - Testing Real Response")
    print("="*80)
    
    client = httpx.AsyncClient(timeout=30.0)
    
    # Test 1: Intraday OHLCV for RELIANCE
    print("\n📊 Test 1: Intraday OHLCV (RELIANCE.NS)")
    try:
        response = await client.get(
            "https://www.alphavantage.co/query",
            params={
                "function": "TIME_SERIES_INTRADAY",
                "symbol": "RELIANCE",
                "interval": "15min",
                "apikey": ALPHA_VANTAGE_KEY,
                "outputsize": "compact"
            }
        )
        data = response.json()
        
        if "Note" in data:
            print("❌ Rate limit hit!")
        elif "Error Message" in data:
            print(f"❌ Error: {data['Error Message']}")
        elif "Time Series (15min)" in data:
            time_series = data["Time Series (15min)"]
            latest = list(time_series.items())[0]
            print(f"✅ Got data! Latest candle:")
            print(f"   Timestamp: {latest[0]}")
            print(f"   OHLCV: {json.dumps(latest[1], indent=4)}")
            print(f"   Total candles: {len(time_series)}")
        else:
            print(f"❓ Unexpected response: {list(data.keys())}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Index data (^NSEI)
    print("\n📈 Test 2: Index Data (^NSEI)")
    try:
        response = await client.get(
            "https://www.alphavantage.co/query",
            params={
                "function": "GLOBAL_QUOTE",
                "symbol": "^NSEI",
                "apikey": ALPHA_VANTAGE_KEY
            }
        )
        data = response.json()
        
        if "Global Quote" in data and data["Global Quote"]:
            print(f"✅ Got data: {json.dumps(data['Global Quote'], indent=4)}")
        else:
            print(f"❌ No data. Response: {list(data.keys())}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: RSI indicator
    print("\n📊 Test 3: RSI Indicator (RELIANCE)")
    try:
        response = await client.get(
            "https://www.alphavantage.co/query",
            params={
                "function": "RSI",
                "symbol": "RELIANCE",
                "interval": "15min",
                "time_period": 14,
                "series_type": "close",
                "apikey": ALPHA_VANTAGE_KEY
            }
        )
        data = response.json()
        
        if "Technical Analysis: RSI" in data:
            rsi_data = data["Technical Analysis: RSI"]
            latest = list(rsi_data.items())[0]
            print(f"✅ Got RSI: {latest[0]} = {latest[1]['RSI']}")
            print(f"   Total data points: {len(rsi_data)}")
        else:
            print(f"❌ No RSI data. Response: {list(data.keys())}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    await client.aclose()


async def test_twelve_data():
    """Test Twelve Data - what do we actually get?"""
    print("\n" + "="*80)
    print("🔍 TWELVE DATA - Testing Real Response")
    print("="*80)
    
    client = httpx.AsyncClient(timeout=30.0)
    
    # Test 1: Intraday OHLCV
    print("\n📊 Test 1: Intraday OHLCV (RELIANCE)")
    try:
        response = await client.get(
            "https://api.twelvedata.com/time_series",
            params={
                "symbol": "RELIANCE",
                "interval": "15min",
                "outputsize": 10,
                "apikey": TWELVE_DATA_KEY,
                "format": "JSON"
            }
        )
        data = response.json()
        
        if "status" in data and data["status"] == "error":
            print(f"❌ Error: {data.get('message')}")
        elif "values" in data:
            print(f"✅ Got {len(data['values'])} candles")
            if data['values']:
                print(f"   Latest: {json.dumps(data['values'][0], indent=4)}")
                print(f"\n   Meta info: {json.dumps(data.get('meta', {}), indent=4)}")
        else:
            print(f"❓ Unexpected: {list(data.keys())}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Index quote (^NSEI)
    print("\n📈 Test 2: Index Quote (^NSEI)")
    try:
        response = await client.get(
            "https://api.twelvedata.com/quote",
            params={
                "symbol": "^NSEI",
                "apikey": TWELVE_DATA_KEY
            }
        )
        data = response.json()
        
        if "status" in data and data["status"] == "error":
            print(f"❌ Error: {data.get('message')}")
        elif "close" in data:
            print(f"✅ Got quote:")
            print(f"   {json.dumps(data, indent=4)}")
        else:
            print(f"❓ Unexpected: {list(data.keys())}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: RSI
    print("\n📊 Test 3: RSI (RELIANCE)")
    try:
        response = await client.get(
            "https://api.twelvedata.com/rsi",
            params={
                "symbol": "RELIANCE",
                "interval": "15min",
                "time_period": 14,
                "apikey": TWELVE_DATA_KEY
            }
        )
        data = response.json()
        
        if "status" in data and data["status"] == "error":
            print(f"❌ Error: {data.get('message')}")
        elif "values" in data:
            print(f"✅ Got RSI: {len(data['values'])} data points")
            if data['values']:
                print(f"   Latest: {json.dumps(data['values'][0], indent=4)}")
        else:
            print(f"❓ Unexpected: {list(data.keys())}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    await client.aclose()


def test_yahoo_finance():
    """Test Yahoo Finance - what do we actually get?"""
    print("\n" + "="*80)
    print("🔍 YAHOO FINANCE - Testing Real Response")
    print("="*80)
    
    # Test 1: Indian stock fundamentals
    print("\n📊 Test 1: Fundamentals (RELIANCE.NS)")
    try:
        ticker = yf.Ticker("RELIANCE.NS")
        info = ticker.info
        
        if info:
            print("✅ Got fundamentals:")
            important_fields = [
                "marketCap", "trailingPE", "forwardPE", "priceToBook",
                "debtToEquity", "returnOnEquity", "dividendYield",
                "currentPrice", "previousClose", "volume"
            ]
            for field in important_fields:
                if field in info:
                    print(f"   {field}: {info[field]}")
        else:
            print("❌ No data")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Index data (^NSEI)
    print("\n📈 Test 2: Index Data (^NSEI)")
    try:
        ticker = yf.Ticker("^NSEI")
        info = ticker.info
        
        if info:
            print("✅ Got index data:")
            print(f"   Current Price: {info.get('currentPrice') or info.get('regularMarketPrice')}")
            print(f"   Previous Close: {info.get('previousClose')}")
            print(f"   Volume: {info.get('volume')}")
        else:
            print("❌ No data")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 3: Historical intraday (to check if it works)
    print("\n📊 Test 3: Intraday Data (RELIANCE.NS)")
    try:
        ticker = yf.Ticker("RELIANCE.NS")
        intraday = ticker.history(period="1d", interval="15m")
        
        if not intraday.empty:
            print(f"✅ Got {len(intraday)} intraday candles")
            print(f"   Latest:\n{intraday.tail(1)}")
        else:
            print("❌ No intraday data")
    except Exception as e:
        print(f"❌ Exception: {e}")


async def test_fmp():
    """Test FMP - what do we actually get?"""
    print("\n" + "="*80)
    print("🔍 FMP (Financial Modeling Prep) - Testing Real Response")
    print("="*80)
    
    client = httpx.AsyncClient(timeout=30.0)
    
    # Test 1: Company profile
    print("\n📊 Test 1: Company Profile (RELIANCE.NS)")
    try:
        response = await client.get(
            f"https://financialmodelingprep.com/api/v3/profile/RELIANCE.NS",
            params={"apikey": FMP_API_KEY}
        )
        data = response.json()
        
        if response.status_code == 402:
            print("❌ 402 Payment Required - Free tier expired or needs upgrade")
        elif isinstance(data, list) and data:
            print(f"✅ Got profile:")
            print(f"   {json.dumps(data[0], indent=4)}")
        elif isinstance(data, dict) and "Error Message" in data:
            print(f"❌ Error: {data['Error Message']}")
        else:
            print(f"❓ Unexpected: {data}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    # Test 2: Financial ratios
    print("\n📈 Test 2: Financial Ratios (RELIANCE.NS)")
    try:
        response = await client.get(
            f"https://financialmodelingprep.com/api/v3/ratios/RELIANCE.NS",
            params={"apikey": FMP_API_KEY, "limit": 1}
        )
        data = response.json()
        
        if response.status_code == 402:
            print("❌ 402 Payment Required")
        elif isinstance(data, list) and data:
            print(f"✅ Got ratios:")
            print(f"   {json.dumps(data[0], indent=4)}")
        else:
            print(f"❓ Unexpected: {data}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    await client.aclose()


async def main():
    """Run all tests"""
    print("\n" + "🚀"*40)
    print("TESTING FREE TIER APIs - ACTUAL DATA CHECK")
    print(f"Timestamp: {datetime.now()}")
    print("🚀"*40)
    
    # Test all providers
    await test_alpha_vantage()
    await test_twelve_data()
    test_yahoo_finance()
    await test_fmp()
    
    print("\n" + "="*80)
    print("✅ TESTING COMPLETE")
    print("="*80)
    print("\nSUMMARY:")
    print("- Check which APIs worked")
    print("- Note what data fields are actually available")
    print("- See rate limits in action")
    print("- Identify what we can rely on")


if __name__ == "__main__":
    asyncio.run(main())
