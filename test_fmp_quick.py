import httpx
import asyncio

async def test_fmp():
    client = httpx.AsyncClient(timeout=30.0)
    
    # Test with RELIANCE.NS
    response = await client.get(
        'https://financialmodelingprep.com/stable/profile',
        params={
            'symbol': 'RELIANCE.NS',
            'apikey': 'qty5ZwSYBANWmtoWHYi1zfE8zDbKXXOV'
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_fmp())
