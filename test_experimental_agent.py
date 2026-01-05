"""Test Experimental Trading Agent"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from app.core.experimental.trading_agent import ExperimentalTradingAgent, format_experimental_output


def test_experimental_agent():
    """Test experimental trading agent with various scenarios"""
    
    print("\n" + "="*70)
    print("EXPERIMENTAL TRADING AGENT - TEST SUITE")
    print("⚠️ FOR PERSONAL EXPERIMENTATION ONLY")
    print("="*70 + "\n")
    
    # Initialize agent (DISABLED by default for safety)
    agent = ExperimentalTradingAgent(enabled=True)
    
    # Test 1: Strong Trend Day
    print("\n📊 TEST 1: STRONG TREND DAY")
    print("-" * 70)
    
    thesis1 = agent.analyze_setup(
        ticker="RELIANCE.NS",
        current_price=2850.0,
        ohlcv={
            'recent_high': 2800.0,
            'recent_low': 2700.0,
            'volume_vs_avg': 1.8
        },
        indicators={
            'rsi': 65,
            'macd': 0.8,
            'macd_signal': 0.5,
            'macd_slope': 0.6
        },
        index_context={'strength': 0.8}
    )
    
    if thesis1:
        print(format_experimental_output(thesis1))
    
    # Test 2: Chop / No Trade
    print("\n📊 TEST 2: CHOPPY CONDITIONS - NO TRADE")
    print("-" * 70)
    
    thesis2 = agent.analyze_setup(
        ticker="INFY.NS",
        current_price=1500.0,
        ohlcv={
            'recent_high': 1520.0,
            'recent_low': 1480.0,
            'volume_vs_avg': 0.6
        },
        indicators={
            'rsi': 52,
            'macd': 0.1,
            'macd_signal': 0.1,
            'macd_slope': 0.05
        }
    )
    
    if thesis2:
        print(format_experimental_output(thesis2))
    
    # Test 3: Fake Breakout Warning
    print("\n📊 TEST 3: FAKE BREAKOUT (LOW VOLUME)")
    print("-" * 70)
    
    thesis3 = agent.analyze_setup(
        ticker="TCS.NS",
        current_price=3800.0,
        ohlcv={
            'recent_high': 3750.0,
            'recent_low': 3600.0,
            'volume_vs_avg': 0.5  # Low volume
        },
        indicators={
            'rsi': 72,  # Overbought
            'macd': 0.3,
            'macd_signal': 0.4,
            'macd_slope': -0.2  # Negative slope
        },
        time_of_day="open"  # Early morning
    )
    
    if thesis3:
        print(format_experimental_output(thesis3))
    
    # Test 4: Intraday Mean Reversion
    print("\n📊 TEST 4: INTRADAY MEAN REVERSION")
    print("-" * 70)
    
    thesis4 = agent.analyze_setup(
        ticker="HDFC.NS",
        current_price=1650.0,
        ohlcv={
            'recent_high': 1600.0,
            'recent_low': 1550.0,
            'volume_vs_avg': 0.7
        },
        indicators={
            'rsi': 78,  # Very overbought
            'macd': 0.2,
            'macd_signal': 0.3,
            'macd_slope': -0.3
        },
        time_of_day="open"
    )
    
    if thesis4:
        print(format_experimental_output(thesis4))
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print("\n⚠️  REMEMBER:")
    print("   • This is experimental - can and will be wrong")
    print("   • User assumes all responsibility")
    print("   • Not compliant with regulations")
    print("   • For personal learning only")
    print()


if __name__ == "__main__":
    test_experimental_agent()
