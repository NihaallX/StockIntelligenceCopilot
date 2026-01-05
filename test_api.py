"""Test API endpoints"""
import httpx
import json

print("Testing Stock Intelligence Copilot API Endpoints\n")
print("="*60)

# Test 1: Root endpoint
print("\n1. Testing root endpoint (/)...")
response = httpx.get("http://localhost:8000/")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 2: Health check
print("\n2. Testing health endpoint (/health)...")
response = httpx.get("http://localhost:8000/health")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 3: Supported tickers (NEW PATH - no /stocks prefix)
print("\n3. Testing supported-tickers endpoint (/api/v1/supported-tickers)...")
response = httpx.get("http://localhost:8000/api/v1/supported-tickers")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 4: Analyze endpoint (NEW PATH - no /stocks prefix)
print("\n4. Testing analyze endpoint (/api/v1/analyze)...")
payload = {"ticker": "AAPL"}
response = httpx.post("http://localhost:8000/api/v1/analyze", json=payload)
print(f"Status: {response.status_code}")
result = response.json()

# Print simplified output
print(f"\nTicker: {result.get('ticker')}")
print(f"Timestamp: {result.get('timestamp')}")
print(f"Signal: {result.get('signal')}")
print(f"Confidence: {result.get('confidence')}")
print(f"Risk Level: {result.get('risk_level')}")
print(f"Is Actionable: {result.get('is_actionable')}")

# Test 5: Verify OLD paths are NOT working (should get 404)
print("\n5. Testing OLD path (should fail - /api/v1/stocks/analyze)...")
try:
    response = httpx.post("http://localhost:8000/api/v1/stocks/analyze", json={"ticker": "AAPL"})
    print(f"Status: {response.status_code}")
    if response.status_code == 404:
        print("✓ OLD PATH CORRECTLY RETURNS 404 - Routing fix successful!")
    else:
        print("✗ OLD PATH STILL WORKS - Routing issue NOT fixed")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("API Testing Complete!")
