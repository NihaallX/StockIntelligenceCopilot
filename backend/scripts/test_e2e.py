"""
End-to-End Validation Script
Tests the full user flow against the running local API.
"""
import requests
import json
import uuid
import time

BASE_URL = "http://localhost:8000"
API_PREFIX = "/v1"

# Generate random user for this test run
TEST_EMAIL = f"test_{uuid.uuid4().hex[:8]}@example.com"
TEST_PASSWORD = "Password123!"
TEST_TICKER = "RELIANCE.NS"

def print_step(step):
    print(f"\n👉 {step}...")

def fail(msg):
    print(f"❌ FAILED: {msg}")
    exit(1)

def main():
    print(f"🧪 Starting E2E Test for {TEST_EMAIL}")
    
    # 1. Health Check
    print_step("Checking Health")
    max_retries = 10
    for i in range(max_retries):
        try:
            r = requests.get(f"{BASE_URL}/health")
            if r.status_code == 200:
                print("✅ Health Check Passed")
                break
            else:
                print(f"⏳ Waiting for server... ({i+1}/{max_retries})")
        except requests.exceptions.ConnectionError:
            print(f"⏳ Connection refused, server not up yet... ({i+1}/{max_retries})")
        
        if i == max_retries - 1:
            fail("Could not connect to server after multiple attempts.")
        time.sleep(2)

    # 2. Register
    print_step("Registering User")
    payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "full_name": "Test User",
        "terms_accepted": True,
        "risk_acknowledged": True
    }
    r = requests.post(f"{BASE_URL}{API_PREFIX}/auth/register", json=payload)
    if r.status_code != 201:
        fail(f"Registration failed: {r.text}")
    print("✅ Registration Passed")
    
    # 3. Login
    print_step("Logging In")
    login_payload = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    r = requests.post(f"{BASE_URL}{API_PREFIX}/auth/login", json=login_payload)
    if r.status_code != 200:
        fail(f"Login failed: {r.text}")
    data = r.json()
    access_token = data["tokens"]["access_token"]
    print("✅ Login Passed (Token Received)")
    
    headers = {"Authorization": f"Bearer {access_token}"}

    # 4. Get Profile
    print_step("Fetching Profile")
    r = requests.get(f"{BASE_URL}{API_PREFIX}/auth/me", headers=headers)
    if r.status_code != 200:
        fail(f"Get Profile failed: {r.text}")
    print("✅ Profile Fetch Passed")

    # 5. Add Position
    print_step(f"Adding Position ({TEST_TICKER})")
    pos_payload = {
        "ticker": TEST_TICKER,
        "quantity": 10,
        "entry_price": 2500.50,
        "entry_date": "2024-01-01",
        "notes": "E2E Test Position"
    }
    r = requests.post(f"{BASE_URL}{API_PREFIX}/portfolio/positions", json=pos_payload, headers=headers)
    if r.status_code != 201:
        fail(f"Add Position failed: {r.text}")
    pos_data = r.json()
    pos_id = pos_data["id"]
    print(f"✅ Position Added (ID: {pos_id})")

    # 6. Verify Position
    print_step("Verifying Portfolio")
    r = requests.get(f"{BASE_URL}{API_PREFIX}/portfolio/positions", headers=headers)
    if r.status_code != 200:
        fail(f"List Positions failed: {r.text}")
    positions = r.json()
    if len(positions) != 1 or positions[0]["ticker"] != TEST_TICKER:
        fail(f"Portfolio verification failed. Expected 1 position, got {len(positions)}")
    print("✅ Portfolio Verification Passed")

    # 7. Test AI Suggestions (Optional)
    print_step("Testing AI Suggestions (Mock)")
    ai_payload = {
        "positions": [{
            "ticker": TEST_TICKER,
            "quantity": 10,
            "entry_price": 2500.50
        }],
        "risk_tolerance": "moderate"
    }
    r = requests.post(f"{BASE_URL}{API_PREFIX}/portfolio/ai-suggestions", json=ai_payload, headers=headers)
    if r.status_code == 200:
        print("✅ AI Suggestions Passed")
    else:
        print(f"⚠️ AI Suggestions Failed (Expected if keys missing): {r.text}")

    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
