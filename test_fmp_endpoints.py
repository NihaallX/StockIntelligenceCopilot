"""Test FMP fundamentals endpoints"""
import asyncio
import httpx

async def test_fmp_endpoints():
    """Test all FMP endpoints we use"""
    
    API_KEY = "qty5ZwSYBANWmtoWHYi1zfE8zDbKXXOV"
    BASE_URL = "https://financialmodelingprep.com/stable"
    SYMBOL = "RELIANCE.NS"
    
    client = httpx.AsyncClient(timeout=30.0)
    
    print("="*80)
    print("TESTING FMP ENDPOINTS")
    print("="*80)
    
    # Test 1: Profile
    print("\n1. Testing /stable/profile")
    response = await client.get(
        f"{BASE_URL}/profile",
        params={"symbol": SYMBOL, "apikey": API_KEY}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Got profile data: {data[0]['companyName'] if data else 'None'}")
    else:
        print(f"❌ Error: {response.text[:200]}")
    
    # Test 2: Ratios
    print("\n2. Testing /stable/ratios")
    response = await client.get(
        f"{BASE_URL}/ratios",
        params={"symbol": SYMBOL, "apikey": API_KEY, "limit": 1}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data:
            print(f"✅ Got ratios: PE={data[0].get('priceEarningsRatio')}, ROE={data[0].get('returnOnEquity')}")
        else:
            print("❌ No ratios data")
    else:
        print(f"❌ Error: {response.text[:200]}")
    
    # Test 3: Income Statement
    print("\n3. Testing /stable/income-statement")
    response = await client.get(
        f"{BASE_URL}/income-statement",
        params={"symbol": SYMBOL, "apikey": API_KEY, "limit": 2}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data:
            print(f"✅ Got income statement: Revenue={data[0].get('revenue')}")
        else:
            print("❌ No income statement data")
    else:
        print(f"❌ Error: {response.text[:200]}")
    
    # Test 4: Key Metrics TTM
    print("\n4. Testing /stable/key-metrics-ttm")
    response = await client.get(
        f"{BASE_URL}/key-metrics-ttm",
        params={"symbol": SYMBOL, "apikey": API_KEY}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data:
            print(f"✅ Got key metrics: Market Cap={data[0].get('marketCapTTM')}")
        else:
            print("❌ No key metrics data")
    else:
        print(f"❌ Error: {response.text[:200]}")
    
    # Test 5: News
    print("\n5. Testing /stable/news/stock")
    response = await client.get(
        f"{BASE_URL}/news/stock",
        params={"symbols": SYMBOL, "apikey": API_KEY, "page": 0, "limit": 5}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if data:
            print(f"✅ Got {len(data)} news articles")
            print(f"   Latest: {data[0]['title'][:60]}...")
        else:
            print("❌ No news data")
    else:
        print(f"❌ Error: {response.text[:200]}")
    
    await client.aclose()
    
    print("\n" + "="*80)
    print("FMP TESTING COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_fmp_endpoints())
