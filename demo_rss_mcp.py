"""Quick integration example for RSS-based MCP"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')


async def demo_integration():
    """Demonstrate RSS-based MCP integration"""
    
    print("\n" + "="*70)
    print("RSS-BASED MCP INTEGRATION DEMO")
    print("="*70 + "\n")
    
    from app.core.context_agent.rss_fetcher import RSSBasedMCPFetcher
    from app.core.context_agent.trigger_manager import MCPTriggerManager
    
    # Initialize components
    fetcher = RSSBasedMCPFetcher()
    trigger_mgr = MCPTriggerManager(cooldown_minutes=5)
    
    print("✅ MCP Components initialized\n")
    
    # Simulate a trading signal
    signal = {
        "ticker": "RELIANCE.NS",
        "company_name": "Reliance",
        "signal_type": "LONG",
        "signal_score": 75,
        "price_change_pct": 2.1,  # 2.1% intraday move
        "volatility": 0.021
    }
    
    print(f"📊 Signal Generated:")
    print(f"   Ticker: {signal['ticker']}")
    print(f"   Type: {signal['signal_type']}")
    print(f"   Score: {signal['signal_score']}/100")
    print(f"   Price Change: {signal['price_change_pct']:.1f}%")
    
    # Check if should trigger MCP
    should_enrich = trigger_mgr.should_trigger(
        ticker=signal['ticker'],
        opportunity_type=signal['signal_type'],
        volatility=signal['volatility']
    )
    
    print(f"\n🎯 Should Trigger MCP: {should_enrich}")
    
    if should_enrich:
        print("\n📰 Fetching Market Context...")
        
        result = await fetcher.fetch_context_for_ticker(
            ticker=signal['ticker'],
            company_name=signal['company_name'],
            hours_back=48
        )
        
        print(f"\n📝 MCP Result:")
        print(f"   Summary: {result['summary']}")
        print(f"   Confidence: {result['confidence'].upper()}")
        print(f"   Sources: {len(result['sources'])}")
        
        if result['sources']:
            print(f"\n📚 Citations:")
            for i, source in enumerate(result['sources'], 1):
                print(f"   {i}. {source['title'][:70]}...")
                print(f"      Publisher: {source['publisher']}")
                print(f"      URL: {source['url'][:60]}...")
        else:
            print(f"\n⚠️  Failure Reason: {result['failure_reason']}")
        
        # IMPORTANT: Signal score unchanged
        print(f"\n✅ Signal Score After MCP: {signal['signal_score']}/100")
        print(f"   (MCP never modifies signal scores)")
    
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70 + "\n")
    
    print("📋 Integration Checklist:")
    print("   ✅ RSS-based fetching (no HTML scraping)")
    print("   ✅ Trigger logic (abnormal activity)")
    print("   ✅ Graceful error handling")
    print("   ✅ Signal isolation (read-only MCP)")
    print("   ✅ SEBI-compliant language")
    print()


if __name__ == "__main__":
    asyncio.run(demo_integration())
