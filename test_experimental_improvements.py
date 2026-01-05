"""
TEST: Enhanced Experimental Agent
===================================

Tests the improved experimental agent with:
- Index override logic
- Liquidity filter
- Signal freshness
- Analysis frequency guard
"""

import asyncio
import sys
from datetime import datetime, timedelta

sys.path.append("backend")

from app.core.experimental.trading_agent import ExperimentalTradingAgent


async def test_index_override():
    """Test index override reducing confidence"""
    print("\n" + "="*80)
    print("TEST 1: Index Override")
    print("="*80)
    
    agent = ExperimentalTradingAgent(enabled=True)
    
    # Long signal but bearish index
    thesis = agent.analyze_setup(
        ticker="TCS",
        current_price=3500.0,
        ohlcv={
            "open": 3480.0,
            "high": 3520.0,
            "low": 3475.0,
            "close": 3500.0,
            "volume": 5000000,
            "volume_ratio": 1.5,  # Good volume
            "volume_vs_avg": 1.5,
            "recent_high": 3450.0,  # Breaking higher
            "recent_low": 3400.0
        },
        indicators={
            "rsi": 65,  # Trending up
            "macd": 15.0,
            "macd_signal": 10.0,
            "macd_histogram": 5.0,
            "macd_slope": 0.8  # Strong uptrend
        },
        index_context={
            "trend": "down",  # Bearish index
            "strength": 0.7   # Strong bearish
        },
        time_of_day="mid_day"
    )
    
    if thesis:
        print(f"\n✅ Thesis Generated:")
        print(f"   Ticker: {thesis.ticker}")
        print(f"   Bias: {thesis.bias}")
        print(f"   Confidence: {thesis.confidence}%")
        print(f"   Index Alignment: {thesis.index_alignment}")
        print(f"   Adjustments: {thesis.confidence_adjustments}")
        print(f"   Risk Notes: {thesis.risk_notes}")
        
        # Verify index adjustment was applied
        if thesis.bias in ["long", "short"]:  # Only if there's a trade
            assert "Index:" in str(thesis.confidence_adjustments) or len(thesis.risk_notes) > 1, \
                "Expected index adjustment or risk note"
            print("\n✅ Index override/notification worked correctly")
        else:
            print("\n⚠️ No trade generated, skipping index override check")
    else:
        print("❌ No thesis generated")
    
    return thesis


async def test_liquidity_filter():
    """Test liquidity filter forcing scalp/no trade"""
    print("\n" + "="*80)
    print("TEST 2: Liquidity Filter")
    print("="*80)
    
    agent = ExperimentalTradingAgent(enabled=True)
    
    # Long signal but very low volume
    thesis = agent.analyze_setup(
        ticker="SMALLCAP",
        current_price=150.0,
        ohlcv={
            "open": 149.0,
            "high": 151.0,
            "low": 148.5,
            "close": 150.0,
            "volume": 100000,
            "volume_ratio": 0.4  # Only 40% of average - LOW!
        },
        indicators={
            "rsi": 55,
            "macd": 2.0,
            "macd_signal": 1.0,
            "macd_histogram": 1.0
        },
        time_of_day="mid_day"
    )
    
    if thesis:
        print(f"\n✅ Thesis Generated:")
        print(f"   Ticker: {thesis.ticker}")
        print(f"   Bias: {thesis.bias}")
        print(f"   Confidence: {thesis.confidence}%")
        print(f"   Volume Analysis: {thesis.volume_analysis}")
        print(f"   Risk Notes: {thesis.risk_notes}")
        
        # Verify bias was downgraded
        assert thesis.bias in ["scalp_only", "no_trade"], f"Expected scalp/no trade, got {thesis.bias}"
        print(f"\n✅ Liquidity filter worked: Downgraded to {thesis.bias}")
    else:
        print("❌ No thesis generated")
    
    return thesis


async def test_signal_freshness():
    """Test signal freshness warnings"""
    print("\n" + "="*80)
    print("TEST 3: Signal Freshness")
    print("="*80)
    
    agent = ExperimentalTradingAgent(enabled=True)
    
    # Analyze once with strong trending setup
    print("\nFirst analysis (fresh signal):")
    thesis1 = agent.analyze_setup(
        ticker="INFY",
        current_price=1500.0,
        ohlcv={
            "open": 1495.0,
            "high": 1505.0,
            "low": 1490.0,
            "close": 1500.0,
            "volume": 3000000,
            "volume_ratio": 1.3,
            "volume_vs_avg": 1.3,
            "recent_high": 1480.0,
            "recent_low": 1460.0
        },
        indicators={
            "rsi": 65,  # Trending
            "macd": 8.0,
            "macd_signal": 5.0,
            "macd_histogram": 3.0,
            "macd_slope": 0.6  # Trending
        },
        time_of_day="mid_day"
    )
    
    if thesis1:
        print(f"   Bias: {thesis1.bias}")
        print(f"   Signal Age: {thesis1.signal_age_minutes or 0} minutes")
        print(f"   Risk Notes: {thesis1.risk_notes}")
    
    # Simulate time passing by manually updating last_analysis_time
    print("\nSimulating 35 minutes passing...")
    agent.last_analysis_time["INFY"] = datetime.now() - timedelta(minutes=35)
    
    # Analyze again (stale signal)
    print("\nSecond analysis (stale signal):")
    thesis2 = agent.analyze_setup(
        ticker="INFY",
        current_price=1502.0,
        ohlcv={
            "open": 1500.0,
            "high": 1503.0,
            "low": 1499.0,
            "close": 1502.0,
            "volume": 2900000,
            "volume_ratio": 1.25,
            "volume_vs_avg": 1.25,
            "recent_high": 1485.0,
            "recent_low": 1465.0
        },
        indicators={
            "rsi": 66,
            "macd": 8.5,
            "macd_signal": 5.5,
            "macd_histogram": 3.0,
            "macd_slope": 0.6
        },
        time_of_day="mid_day"
    )
    
    if thesis2:
        print(f"   Bias: {thesis2.bias}")
        print(f"   Signal Age: {thesis2.signal_age_minutes or 0} minutes")
        print(f"   Risk Notes: {thesis2.risk_notes}")
        
        # Verify freshness warning if trade was generated
        if thesis2.bias in ["long", "short"]:
            assert thesis2.signal_age_minutes and thesis2.signal_age_minutes > 30, "Expected age > 30 min"
            assert any("freshness" in note.lower() or "degraded" in note.lower() for note in thesis2.risk_notes), "Expected freshness warning"
            print("\n✅ Signal freshness tracking worked")
        else:
            print("\n⚠️ No trade generated, skipping freshness check")
    
    return thesis2


async def test_analysis_frequency():
    """Test analysis frequency guard"""
    print("\n" + "="*80)
    print("TEST 4: Analysis Frequency Guard")
    print("="*80)
    
    agent = ExperimentalTradingAgent(enabled=True)
    
    # Analyze same ticker 6 times with strong trending setup
    print("\nAnalyzing same ticker 6 times:")
    for i in range(6):
        thesis = agent.analyze_setup(
            ticker="RELIANCE",
            current_price=2850.0 + i,  # Small price variation
            ohlcv={
                "open": 2845.0,
                "high": 2855.0,
                "low": 2840.0,
                "close": 2850.0 + i,
                "volume": 8000000,
                "volume_ratio": 1.3,
                "volume_vs_avg": 1.3,
                "recent_high": 2830.0,
                "recent_low": 2800.0
            },
            indicators={
                "rsi": 65,  # Trending
                "macd": 10.0,
                "macd_signal": 8.0,
                "macd_histogram": 2.0,
                "macd_slope": 0.6  # Trending
            },
            time_of_day="mid_day"
        )
        
        if thesis:
            print(f"   Analysis {i+1}: Bias={thesis.bias}, Risk notes count = {len(thesis.risk_notes)}")
            if i >= 4:  # 5th and 6th analysis should have warning
                has_warning = any("over-analysis" in note.lower() or "trust your first" in note.lower() 
                                  for note in thesis.risk_notes)
                if has_warning:
                    print(f"      ✅ Over-analysis warning detected")
                else:
                    print(f"      ❌ No over-analysis warning!")
                    print(f"      Risk notes: {thesis.risk_notes}")
                
                assert has_warning, f"Expected over-analysis warning on attempt {i+1}"
    
    print("\n✅ Analysis frequency guard worked")
    return thesis


async def test_combined_improvements():
    """Test all improvements working together"""
    print("\n" + "="*80)
    print("TEST 5: Combined Improvements")
    print("="*80)
    
    agent = ExperimentalTradingAgent(enabled=True)
    
    # Worst-case scenario: low volume, bearish index, stale signal
    thesis = agent.analyze_setup(
        ticker="WORST",
        current_price=500.0,
        ohlcv={
            "open": 498.0,
            "high": 502.0,
            "low": 497.0,
            "close": 500.0,
            "volume": 200000,
            "volume_ratio": 0.5  # Low volume
        },
        indicators={
            "rsi": 58,
            "macd": 3.0,
            "macd_signal": 2.0,
            "macd_histogram": 1.0
        },
        index_context={
            "trend": "down",  # Bearish index
            "strength": 0.8   # Very strong bearish
        },
        time_of_day="mid_day"
    )
    
    if thesis:
        print(f"\n✅ Thesis Generated:")
        print(f"   Ticker: {thesis.ticker}")
        print(f"   Bias: {thesis.bias}")
        print(f"   Confidence: {thesis.confidence}%")
        print(f"   Adjustments: {thesis.confidence_adjustments}")
        print(f"   Risk Notes:")
        for note in thesis.risk_notes:
            print(f"      - {note}")
        
        # Should have multiple warnings
        assert len(thesis.risk_notes) >= 2, "Expected multiple risk notes"
        assert thesis.bias in ["scalp_only", "no_trade"], "Expected downgraded bias"
        assert thesis.confidence < 60, "Expected low confidence"
        
        print("\n✅ All improvements combined correctly")
    else:
        print("❌ No thesis generated")
    
    return thesis


async def main():
    """Run all tests"""
    print("\n🔬 TESTING ENHANCED EXPERIMENTAL AGENT")
    print("=" * 80)
    
    try:
        await test_index_override()
        await test_liquidity_filter()
        await test_signal_freshness()
        await test_analysis_frequency()
        await test_combined_improvements()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())
