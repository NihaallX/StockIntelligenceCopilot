"""Test Reuters India Fetcher - Standalone"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def test_reuters():
    print("\n" + "="*70)
    print("TESTING REUTERS INDIA FETCHER")
    print("="*70 + "\n")
    
    try:
        from app.core.context_agent.reuters_india_fetcher import ReutersIndiaFetcher
        
        fetcher = ReutersIndiaFetcher()
        print("✅ Reuters India Fetcher initialized\n")
        
        # Test 1: Macro news
        print("Test 1: Fetching macro news (RBI, India, inflation)...")
        sources = await fetcher.fetch_macro_news(
            keywords=["RBI", "India", "inflation"],
            hours_back=48
        )
        
        if sources:
            print(f"✅ Found {len(sources)} articles\n")
            for i, source in enumerate(sources[:3], 1):
                print(f"  {i}. {source.title[:80]}")
                print(f"     Publisher: {source.publisher}")
                print(f"     URL: {source.url[:60]}...")
                if source.published_at:
                    print(f"     Published: {source.published_at}\n")
        else:
            print("⚠️  No articles found (this is OK if no matching news exists)\n")
        
        # Test 2: Global cues
        print("-"*70)
        print("Test 2: Fetching global market cues...")
        global_sources = await fetcher.fetch_global_cues(hours_back=48)
        
        if global_sources:
            print(f"✅ Found {len(global_sources)} global articles\n")
            for i, source in enumerate(global_sources[:2], 1):
                print(f"  {i}. {source.title[:80]}")
                print(f"     Publisher: {source.publisher}\n")
        else:
            print("⚠️  No global articles found\n")
        
        print("="*70)
        print("REUTERS TEST COMPLETE ✅")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_reuters())
