"""Test Indian market source fetchers

Tests Economic Times, NSE, and BSE news/announcement fetchers.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from app.core.context_agent.indian_sources import (
    EconomicTimesMarketsFetcher,
    NSEAnnouncementsFetcher,
    BSEAnnouncementsFetcher,
    fetch_all_indian_market_sources
)


async def test_economic_times():
    """Test Economic Times Markets fetcher"""
    print("=" * 70)
    print("TEST 1: Economic Times Markets Fetcher")
    print("=" * 70)
    print()
    
    fetcher = EconomicTimesMarketsFetcher()
    
    # Test with RELIANCE
    print("Fetching news for RELIANCE.NS from Economic Times...")
    news = await fetcher.fetch_stock_news(
        ticker="RELIANCE.NS",
        company_name="Reliance Industries",
        max_results=3
    )
    
    print(f"✅ Found {len(news)} articles")
    for i, item in enumerate(news, 1):
        print(f"\n{i}. {item['title'][:80]}...")
        print(f"   Source: {item['source']}")
        print(f"   URL: {item['url'][:60]}...")
        if item.get('published_at'):
            print(f"   Published: {item['published_at']}")
    
    print()


async def test_nse_announcements():
    """Test NSE announcements fetcher"""
    print("=" * 70)
    print("TEST 2: NSE India Announcements Fetcher")
    print("=" * 70)
    print()
    
    fetcher = NSEAnnouncementsFetcher()
    
    # Test with TCS
    print("Fetching announcements for TCS from NSE...")
    announcements = await fetcher.fetch_announcements(
        symbol="TCS.NS",
        days_back=7,
        max_results=3
    )
    
    print(f"✅ Found {len(announcements)} announcements")
    for i, item in enumerate(announcements, 1):
        print(f"\n{i}. {item['title'][:80]}...")
        print(f"   Source: {item['source']}")
        print(f"   URL: {item['url'][:60]}...")
        if item.get('published_at'):
            print(f"   Published: {item['published_at']}")
    
    print()


async def test_bse_announcements():
    """Test BSE announcements fetcher"""
    print("=" * 70)
    print("TEST 3: BSE India Announcements Fetcher")
    print("=" * 70)
    print()
    
    fetcher = BSEAnnouncementsFetcher()
    
    # Test with ITC
    print("Fetching announcements for ITC from BSE...")
    announcements = await fetcher.fetch_announcements(
        company_name="ITC",
        max_results=3
    )
    
    print(f"✅ Found {len(announcements)} announcements")
    for i, item in enumerate(announcements, 1):
        print(f"\n{i}. {item['title'][:80]}...")
        print(f"   Source: {item['source']}")
        print(f"   URL: {item['url'][:60]}...")
        if item.get('published_at'):
            print(f"   Published: {item['published_at']}")
    
    print()


async def test_aggregated_fetch():
    """Test fetching from all sources"""
    print("=" * 70)
    print("TEST 4: Aggregated Fetch from All Indian Sources")
    print("=" * 70)
    print()
    
    print("Fetching news for RELIANCE.NS from all sources...")
    all_news = await fetch_all_indian_market_sources(
        ticker="RELIANCE.NS",
        company_name="Reliance Industries",
        max_per_source=2
    )
    
    print(f"✅ Total items found: {len(all_news)}")
    
    # Group by source
    by_source = {}
    for item in all_news:
        source = item['source']
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(item)
    
    print(f"✅ Sources: {list(by_source.keys())}")
    print()
    
    for source, items in by_source.items():
        print(f"{source}: {len(items)} items")
        for item in items:
            print(f"  • {item['title'][:70]}...")
    
    print()


async def test_citation_structure():
    """Test that items have proper citation structure"""
    print("=" * 70)
    print("TEST 5: Citation Structure Validation")
    print("=" * 70)
    print()
    
    all_news = await fetch_all_indian_market_sources(
        ticker="TCS.NS",
        max_per_source=1
    )
    
    print(f"Validating {len(all_news)} news items...")
    
    errors = []
    for i, item in enumerate(all_news, 1):
        print(f"\nItem {i}:")
        
        # Check required fields
        if 'title' not in item or not item['title']:
            errors.append(f"Item {i}: Missing title")
        elif len(item['title']) < 10:
            errors.append(f"Item {i}: Title too short ({len(item['title'])} chars)")
        else:
            print(f"  ✅ Title: {item['title'][:50]}...")
        
        if 'url' not in item or not item['url']:
            errors.append(f"Item {i}: Missing URL")
        elif not item['url'].startswith('http'):
            errors.append(f"Item {i}: Invalid URL format")
        else:
            print(f"  ✅ URL: {item['url'][:40]}...")
        
        if 'source' not in item or not item['source']:
            errors.append(f"Item {i}: Missing source")
        else:
            print(f"  ✅ Source: {item['source']}")
        
        if 'published_at' in item and item['published_at']:
            print(f"  ✅ Published: {item['published_at']}")
        else:
            print(f"  ⚠️ Published: Not available")
    
    print()
    if errors:
        print(f"❌ Found {len(errors)} validation errors:")
        for error in errors:
            print(f"  • {error}")
    else:
        print("✅ All items have valid citation structure")
    
    print()


async def run_all_tests():
    """Run all test scenarios"""
    print("\n" + "=" * 70)
    print("INDIAN MARKET SOURCES TEST SUITE")
    print("=" * 70)
    print()
    
    try:
        await test_economic_times()
    except Exception as e:
        print(f"❌ Economic Times test failed: {e}\n")
    
    try:
        await test_nse_announcements()
    except Exception as e:
        print(f"❌ NSE test failed: {e}\n")
    
    try:
        await test_bse_announcements()
    except Exception as e:
        print(f"❌ BSE test failed: {e}\n")
    
    try:
        await test_aggregated_fetch()
    except Exception as e:
        print(f"❌ Aggregated fetch test failed: {e}\n")
    
    try:
        await test_citation_structure()
    except Exception as e:
        print(f"❌ Citation structure test failed: {e}\n")
    
    print("=" * 70)
    print("TEST SUITE COMPLETE")
    print("=" * 70)
    print()
    print("Notes:")
    print("- Some sources may return 0 results (normal - depends on recent activity)")
    print("- NSE/BSE APIs may have rate limits")
    print("- Website structure changes may break scrapers")
    print("- published_at may not always be available")
    print()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
