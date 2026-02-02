import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.services.tavily_service import tavily_service

def test_indian_stocks():
    print("--- Testing Tavily Search for Indian Stocks ---")
    
    # Test Case 1: Reliance Industries (Large Cap)
    query = "Reliance Industries stock latest news NSE"
    print(f"\n1. Searching for: '{query}'...")
    results = tavily_service.search_market_news(query, max_results=3)
    
    if results:
        print(f"✅ Success! Found {len(results)} results.")
        for i, res in enumerate(results):
            print(f"   [{i+1}] {res['title']} ({res['url']})")
    else:
        print("❌ Failed. No results found.")

    # Test Case 2: Tata Motors (Specific Context)
    ticker = "TATA MOTORS"
    print(f"\n2. Getting context for: '{ticker}'...")
    context = tavily_service.get_stock_context(ticker)
    
    if context and "Recent news" in context:
        print("✅ Success! Retrieved context.")
        print(f"Preview: {context[:150]}...")
    else:
        print("❌ Failed to retrieve context.")

if __name__ == "__main__":
    test_indian_stocks()
