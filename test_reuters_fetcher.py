"""Test Reuters India Fetcher

Quick validation of Reuters India integration
"""

import asyncio
import logging
from backend.app.core.context_agent.reuters_india_fetcher import ReutersIndiaFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_reuters_macro_news():
    """Test fetching macro news from Reuters India"""
    print("\n" + "="*60)
    print("TESTING REUTERS INDIA MACRO NEWS FETCHER")
    print("="*60 + "\n")
    
    fetcher = ReutersIndiaFetcher()
    
    # Test 1: RBI and inflation keywords
    print("Test 1: Fetching RBI + inflation news...")
    sources = await fetcher.fetch_macro_news(
        keywords=["RBI", "inflation", "India"],
        hours_back=48
    )
    
    if sources:
        print(f"✅ Found {len(sources)} articles")
        for i, source in enumerate(sources[:3], 1):
            print(f"\n  {i}. {source.title}")
            print(f"     Publisher: {source.publisher}")
            print(f"     URL: {source.url}")
            if source.published_at:
                print(f"     Published: {source.published_at.strftime('%Y-%m-%d %H:%M')}")
    else:
        print("⚠️  No articles found (may be expected if no matching news)")
    
    # Test 2: Global cues
    print("\n" + "-"*60)
    print("Test 2: Fetching global market cues...")
    global_sources = await fetcher.fetch_global_cues(hours_back=48)
    
    if global_sources:
        print(f"✅ Found {len(global_sources)} global articles")
        for i, source in enumerate(global_sources[:2], 1):
            print(f"\n  {i}. {source.title}")
            print(f"     Publisher: {source.publisher}")
    else:
        print("⚠️  No global articles found")
    
    # Test 3: Sector news (Banking)
    print("\n" + "-"*60)
    print("Test 3: Fetching Banking sector news...")
    sector_sources = await fetcher.fetch_sector_news(
        sector="Banking",
        hours_back=48
    )
    
    if sector_sources:
        print(f"✅ Found {len(sector_sources)} banking sector articles")
        for i, source in enumerate(sector_sources[:2], 1):
            print(f"\n  {i}. {source.title}")
    else:
        print("⚠️  No banking sector articles found")
    
    print("\n" + "="*60)
    print("REUTERS TEST COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(test_reuters_macro_news())
