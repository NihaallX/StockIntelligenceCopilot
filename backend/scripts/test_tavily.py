import sys
import os
import asyncio

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.services.tavily_service import tavily_service

def test_tavily_integration():
    print("--- Testing Tavily Search Integration ---")
    
    # Test Case 1: specialized query
    query = "NVIDIA stock performance 2025"
    print(f"\n1. Searching for: '{query}'...")
    results = tavily_service.search_market_news(query, max_results=2)
    
    if results:
        print(f"✅ Success! Found {len(results)} results.")
        for i, res in enumerate(results):
            print(f"   [{i+1}] {res['title'][:50]}... ({res['url']})")
    else:
        print("❌ Failed. No results found.")

    # Test Case 2: Stock Context
    ticker = "TSLA"
    print(f"\n2. Getting context for ticker: '{ticker}'...")
    context = tavily_service.get_stock_context(ticker)
    
    if context and "Recent news" in context:
        print("✅ Success! Retrieved context.")
        print(f"Preview: {context[:100]}...")
    else:
        print("❌ Failed to retrieve context.")

    # Test Case 3: Edge Case (Empty Query or Gibberish)
    query = "dsafkjhdskjfhsdkjfds"
    print(f"\n3. Testing edge case: '{query}'...")
    results = tavily_service.search_market_news(query)
    
    if not results:
        print("✅ Correctly handled empty/irrelevant results.")
    else:
        print(f"⚠️ Unexpected results found: {len(results)}")
        for i, res in enumerate(results):
            print(f"   [{i+1}] {res['title']} ({res['url']})")

if __name__ == "__main__":
    test_tavily_integration()
