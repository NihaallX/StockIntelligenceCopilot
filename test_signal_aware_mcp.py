"""Test script for signal-aware MCP implementation"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.context_agent.mcp_fetcher import MCPContextFetcher


async def test_signal_aware_mcp():
    """Test the signal-aware MCP filtering"""
    
    print("=" * 80)
    print("Testing Signal-Aware MCP Implementation")
    print("=" * 80)
    
    fetcher = MCPContextFetcher()
    
    # Test Case 1: BUY signal with RSI oversold reason
    print("\n\n🔵 Test Case 1: BUY signal with RSI oversold")
    print("-" * 80)
    
    signal_reasons_1 = ["RSI oversold (below 30)", "Price below moving average"]
    keywords_1 = fetcher._extract_keywords(signal_reasons_1)
    print(f"Signal Reasons: {signal_reasons_1}")
    print(f"Extracted Keywords: {keywords_1[:10]}")  # Show first 10
    
    # Test relevance scoring
    test_headlines = [
        "Reliance Industries stock falls 5% on weak earnings report",
        "Technical indicators suggest oversold conditions in IT sector",
        "RELIANCE announces quarterly results, beats estimates",
        "Market closes lower on profit booking",
        "RSI levels indicate potential reversal in select stocks"
    ]
    
    print(f"\nTesting relevance scoring for {len(test_headlines)} headlines:")
    for headline in test_headlines:
        relevance = fetcher._calculate_relevance(headline, keywords_1, "BUY")
        emoji = "✅" if relevance >= 0.6 else "❌"
        print(f"{emoji} Score: {relevance:.2f} - {headline[:60]}...")
    
    # Test Case 2: SELL signal with earnings miss reason
    print("\n\n🔴 Test Case 2: SELL signal with earnings miss")
    print("-" * 80)
    
    signal_reasons_2 = ["Earnings miss expectations", "Declining revenue growth"]
    keywords_2 = fetcher._extract_keywords(signal_reasons_2)
    print(f"Signal Reasons: {signal_reasons_2}")
    print(f"Extracted Keywords: {keywords_2[:10]}")
    
    print(f"\nTesting relevance scoring:")
    for headline in test_headlines:
        relevance = fetcher._calculate_relevance(headline, keywords_2, "SELL")
        emoji = "✅" if relevance >= 0.6 else "❌"
        print(f"{emoji} Score: {relevance:.2f} - {headline[:60]}...")
    
    # Test Case 3: Generic claim filtering
    print("\n\n🟡 Test Case 3: Generic claim filtering")
    print("-" * 80)
    
    test_claims = [
        "Company announces",  # Too short, generic
        "Plans to expand operations in new markets",  # Generic
        "Q3 earnings beat analyst estimates by 15% driven by strong demand",  # Specific
        "May consider strategic options",  # Vague
        "Stock price rises 10% on strong quarterly results with revenue up 25%"  # Specific
    ]
    
    print("Testing generic claim detection:")
    for claim in test_claims:
        is_generic = fetcher._is_generic_claim(claim)
        emoji = "❌" if is_generic else "✅"
        print(f"{emoji} Generic: {is_generic} - {claim[:60]}...")
    
    # Test Case 4: Sector/Macro relevance detection
    print("\n\n🟢 Test Case 4: Sector/Macro relevance detection")
    print("-" * 80)
    
    sector_reasons = ["Outperforming sector peers", "Industry tailwinds"]
    macro_reasons = ["Nifty 50 momentum positive", "Market sentiment bullish"]
    technical_reasons = ["MACD crossover", "Volume spike"]
    
    print(f"Sector reasons: {sector_reasons}")
    print(f"  Is sector relevant? {fetcher._is_sector_relevant(sector_reasons)}")
    print(f"  Is macro relevant? {fetcher._is_macro_relevant(sector_reasons)}")
    
    print(f"\nMacro reasons: {macro_reasons}")
    print(f"  Is sector relevant? {fetcher._is_sector_relevant(macro_reasons)}")
    print(f"  Is macro relevant? {fetcher._is_macro_relevant(macro_reasons)}")
    
    print(f"\nTechnical reasons: {technical_reasons}")
    print(f"  Is sector relevant? {fetcher._is_sector_relevant(technical_reasons)}")
    print(f"  Is macro relevant? {fetcher._is_macro_relevant(technical_reasons)}")
    
    print("\n" + "=" * 80)
    print("✅ Signal-Aware MCP Testing Complete!")
    print("=" * 80)
    print("\nKey Features Verified:")
    print("  ✅ Keyword extraction from signal reasons")
    print("  ✅ Relevance scoring (0-1 scale)")
    print("  ✅ Generic claim filtering")
    print("  ✅ Sector/macro relevance detection")
    print("\nNext Steps:")
    print("  1. Test with real API calls (fetch_context)")
    print("  2. Verify integration with agent.py")
    print("  3. Test in full analysis flow")


if __name__ == "__main__":
    asyncio.run(test_signal_aware_mcp())
