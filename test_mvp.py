"""
Quick test script to verify the Stock Intelligence Copilot MVP is working.

Run this script to test all core functionality.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.market_data import get_market_data_provider
from app.core.indicators import indicator_calculator
from app.core.signals import signal_generator
from app.core.risk import risk_engine
from app.core.explanation import explanation_generator
from app.core.orchestrator import orchestrator
from app.models.schemas import AnalysisRequest, TimeHorizon
import asyncio

# Get the active market data provider
market_data_provider = get_market_data_provider()


def test_market_data():
    """Test market data provider"""
    print("🔍 Testing Market Data Provider...")
    data = market_data_provider.get_stock_data("AAPL", lookback_days=90)
    assert data.ticker == "AAPL"
    assert len(data.prices) > 0
    assert data.fundamentals is not None
    print(f"   ✅ Fetched {len(data.prices)} days of data for {data.fundamentals.company_name}")
    return data


def test_indicators(market_data):
    """Test technical indicators"""
    print("\n📊 Testing Technical Indicators...")
    indicators = indicator_calculator.calculate_all("AAPL", market_data.prices)
    assert indicators is not None
    assert indicators.sma_20 is not None
    assert indicators.rsi is not None
    print(f"   ✅ SMA(20): ${indicators.sma_20:.2f}")
    print(f"   ✅ SMA(50): ${indicators.sma_50:.2f}")
    print(f"   ✅ RSI: {indicators.rsi:.1f}")
    print(f"   ✅ MACD: {indicators.macd:.2f}")
    return indicators


def test_signal_generation(market_data, indicators):
    """Test signal generation"""
    print("\n🎯 Testing Signal Generation...")
    signal = signal_generator.generate_signal(
        market_data=market_data,
        indicators=indicators,
        time_horizon=TimeHorizon.LONG_TERM
    )
    assert signal is not None
    print(f"   ✅ Signal Type: {signal.strength.signal_type.value.upper()}")
    print(f"   ✅ Confidence: {signal.strength.confidence:.1%}")
    print(f"   ✅ Strength: {signal.strength.strength}")
    print(f"   ✅ Primary Factors: {len(signal.reasoning.primary_factors)}")
    return signal


def test_risk_assessment(signal, indicators):
    """Test risk assessment"""
    print("\n⚠️  Testing Risk Assessment...")
    risk = risk_engine.assess_risk(
        signal=signal,
        indicators=indicators,
        user_risk_tolerance="moderate"
    )
    assert risk is not None
    print(f"   ✅ Overall Risk: {risk.overall_risk.value.upper()}")
    print(f"   ✅ Actionable: {risk.is_actionable}")
    print(f"   ✅ Risk Factors: {len(risk.risk_factors)}")
    print(f"   ✅ Warnings: {len(risk.warnings)}")
    return risk


def test_explanation(signal, risk, indicators):
    """Test explanation generation"""
    print("\n💬 Testing Explanation Generation...")
    insight = explanation_generator.generate_insight(
        signal=signal,
        risk_assessment=risk,
        indicators=indicators,
        time_horizon=TimeHorizon.LONG_TERM
    )
    assert insight is not None
    print(f"   ✅ Recommendation: {insight.recommendation}")
    print(f"   ✅ Overall Confidence: {insight.overall_confidence:.1%}")
    print(f"   ✅ Key Points: {len(insight.key_points)}")
    print(f"\n   Summary: {insight.summary[:150]}...")
    return insight


async def test_orchestrator():
    """Test full pipeline orchestration"""
    print("\n🔄 Testing Full Pipeline (Orchestrator)...")
    request = AnalysisRequest(
        ticker="MSFT",
        time_horizon=TimeHorizon.LONG_TERM,
        risk_tolerance="moderate",
        lookback_days=90
    )
    
    response = await orchestrator.analyze_stock(request)
    assert response.success
    assert response.insight is not None
    print(f"   ✅ Analysis completed in {response.processing_time_ms:.1f}ms")
    print(f"   ✅ Ticker: {response.insight.ticker}")
    print(f"   ✅ Signal: {response.insight.signal.strength.signal_type.value}")
    print(f"   ✅ Risk: {response.insight.risk_assessment.overall_risk.value}")
    return response


def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 Stock Intelligence Copilot - Component Tests")
    print("=" * 60)
    
    try:
        # Test individual components
        market_data = test_market_data()
        indicators = test_indicators(market_data)
        signal = test_signal_generation(market_data, indicators)
        risk = test_risk_assessment(signal, indicators)
        insight = test_explanation(signal, risk, indicators)
        
        # Test full pipeline
        response = asyncio.run(test_orchestrator())
        
        print("\n" + "=" * 60)
        print("✅ All Tests Passed!")
        print("=" * 60)
        print("\n🎉 Stock Intelligence Copilot MVP is fully operational!")
        print("\n📝 Next Steps:")
        print("   1. Run the server: cd backend && python main.py")
        print("   2. Open docs: http://localhost:8000/docs")
        print("   3. Test API: POST to /api/v1/stocks/analyze")
        print("\n✨ Ready for Phase 2!")
        
    except Exception as e:
        print(f"\n❌ Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
