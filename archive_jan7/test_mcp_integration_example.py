"""
MCP Context Engine - Integration Example

This file demonstrates how the MCP Context Engine integrates with 
the Stock Intelligence Copilot system.

ARCHITECTURE:
1. Signal generated (deterministic, technical indicators)
2. Risk assessed
3. MCP optionally enriches with real-world context
4. Frontend displays combined result

READ-ONLY LAYER: MCP never influences signal scores or decisions.
"""

import asyncio
from backend.app.core.context_agent.agent import MarketContextAgent
from backend.app.core.context_agent.models import ContextEnrichmentInput

async def example_mcp_enrichment():
    """
    Example: Enrich a LONG signal with market context
    """
    
    print("\n" + "="*70)
    print("MCP CONTEXT ENGINE - INTEGRATION EXAMPLE")
    print("="*70 + "\n")
    
    # Step 1: Assume we already have a signal from the deterministic engine
    print("📊 STEP 1: Signal Generated (Technical Indicators)")
    print("-" * 70)
    
    example_signal = {
        "ticker": "RELIANCE.NS",
        "signal_type": "LONG",
        "signal_score": 75,  # 0-100 scale
        "signal_reasons": [
            "Strong RSI (60) indicates bullish momentum",
            "MACD crossover detected",
            "Price above 50-day moving average",
            "Volume 1.8x above average"
        ],
        "time_horizon": "LONG_TERM",
        "price": 2850.50,
        "target_price": 3100.00,
        "stop_loss": 2700.00
    }
    
    print(f"Ticker: {example_signal['ticker']}")
    print(f"Signal: {example_signal['signal_type']}")
    print(f"Score: {example_signal['signal_score']}/100")
    print(f"Reasons:")
    for reason in example_signal['signal_reasons']:
        print(f"  • {reason}")
    
    # Step 2: MCP enrichment (READ-ONLY context layer)
    print("\n📰 STEP 2: MCP Context Enrichment (Read-Only)")
    print("-" * 70)
    print("Fetching real-world context from approved sources...")
    print("Sources: Moneycontrol, Economic Times, NSE, BSE, Reuters\n")
    
    # Initialize MCP agent
    mcp_agent = MarketContextAgent(enabled=True)
    
    # Create enrichment input
    enrichment_input = ContextEnrichmentInput(
        opportunity=example_signal,
        user_id="demo_user_123"
    )
    
    # Fetch context
    try:
        context = await mcp_agent.enrich_opportunity(enrichment_input)
        
        if context:
            print(f"✅ MCP Status: {context.mcp_status}")
            print(f"📚 Sources Used: {', '.join(context.data_sources_used)}")
            print(f"\n📝 Context Summary:")
            print(f"   {context.context_summary}")
            
            if context.supporting_points:
                print(f"\n🔍 Supporting Evidence ({len(context.supporting_points)} points):")
                for i, point in enumerate(context.supporting_points[:3], 1):
                    print(f"\n   {i}. {point.claim}")
                    print(f"      Confidence: {point.confidence.upper()}")
                    print(f"      Sources: {len(point.sources)} citation(s)")
                    for source in point.sources:
                        print(f"        - {source.publisher}: {source.title[:60]}...")
        else:
            print("⚠️  No context available (graceful fallback)")
            
    except Exception as e:
        print(f"❌ MCP Error: {e}")
        print("   System continues with technical analysis only")
    
    # Step 3: Combined response
    print("\n📤 STEP 3: Combined Response to User")
    print("-" * 70)
    print("SIGNAL DETAILS:")
    print(f"  Type: {example_signal['signal_type']}")
    print(f"  Score: {example_signal['signal_score']}/100")
    print(f"  Entry: ₹{example_signal['price']}")
    print(f"  Target: ₹{example_signal['target_price']}")
    print(f"  Stop Loss: ₹{example_signal['stop_loss']}")
    
    if context and context.supporting_points:
        print(f"\nMARKET CONTEXT:")
        print(f"  Status: Context Available ({context.mcp_status})")
        print(f"  Summary: {context.context_summary[:100]}...")
        print(f"  Evidence: {len(context.supporting_points)} supporting points")
    else:
        print(f"\nMARKET CONTEXT:")
        print(f"  Status: No additional context")
        print(f"  Note: Technical analysis only")
    
    print(f"\n⚖️  DISCLAIMER:")
    print(f"  {example_signal.get('disclaimer', 'Not financial advice. DYOR.')}")
    
    print("\n" + "="*70)
    print("INTEGRATION EXAMPLE COMPLETE")
    print("="*70 + "\n")
    
    # Show key architectural points
    print("🏗️  KEY ARCHITECTURAL POINTS:")
    print("  ✅ Signal generated FIRST (deterministic)")
    print("  ✅ MCP runs AFTER (read-only enrichment)")
    print("  ✅ MCP never modifies signal score")
    print("  ✅ System works with MCP disabled")
    print("  ✅ Citations required for all claims")
    print("  ✅ Graceful failure handling")
    print("  ✅ SEBI-compliant language")
    print()


if __name__ == "__main__":
    asyncio.run(example_mcp_enrichment())
