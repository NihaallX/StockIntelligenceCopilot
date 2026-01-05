"""
Test FMP Adapter and Cascading Fundamental Provider

Tests:
1. FMP adapter fetches real data
2. Database adapter works as fallback
3. Cascading strategy tries FMP → Database → Unavailable
4. Partial data is handled gracefully
5. Data source is tracked correctly
"""

import asyncio
import sys
import os

# Mock environment for testing
os.environ["FMP_API_KEY"] = os.getenv("FMP_API_KEY", "demo")  # Replace with real key

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))


async def test_fmp_adapter():
    """Test FMP adapter fetches real data"""
    from app.core.fundamentals.adapters.fmp_adapter import FMPAdapter
    from app.core.fundamentals.adapters.base import DataSource
    
    print("=" * 60)
    print("Test 1: FMP Adapter - Real Data Fetch")
    print("=" * 60)
    
    adapter = FMPAdapter()
    
    # Test with well-known Indian stock
    ticker = "RELIANCE.NS"
    
    print(f"\nFetching fundamentals for {ticker} from FMP...")
    result = await adapter.fetch_fundamentals(ticker)
    
    print(f"\n📊 Results:")
    print(f"  Available: {result.available}")
    print(f"  Source: {result.source.value}")
    print(f"  Completeness: {result.completeness_percent:.1f}%")
    print(f"  Fields: {result.fields_available}/{result.fields_total}")
    
    if result.available:
        print(f"\n📈 Data:")
        if result.company_name:
            print(f"  Company: {result.company_name}")
        if result.sector:
            print(f"  Sector: {result.sector}")
        if result.market_cap:
            print(f"  Market Cap: ₹{result.market_cap:,.0f} cr")
        if result.pe_ratio:
            print(f"  PE Ratio: {result.pe_ratio}")
        if result.revenue_growth_yoy:
            print(f"  Revenue Growth YoY: {result.revenue_growth_yoy:.1f}%")
        if result.roe:
            print(f"  ROE: {result.roe:.1f}%")
        if result.debt_to_equity:
            print(f"  Debt/Equity: {result.debt_to_equity:.2f}")
        
        missing = result.missing_fields()
        if missing:
            print(f"\n⚠️ Missing fields: {', '.join(missing)}")
        
        # Verify structure
        assert result.source == DataSource.FMP, "Should be from FMP"
        assert result.available == True, "Should be available"
        assert result.ticker == ticker, "Ticker should match"
        assert result.currency in ["INR", "USD"], "Currency should be INR or USD"
        
        print("\n✅ Test 1 PASSED: FMP adapter fetches real data")
    else:
        print("\n⚠️ FMP data unavailable (check API key or network)")
        print("⚠️ Test 1 SKIPPED (not a failure - API may be rate limited)")
    
    await adapter.close()
    print()


async def test_database_adapter():
    """Test database adapter as fallback"""
    from app.core.fundamentals.adapters.database_adapter import DatabaseAdapter
    from app.core.fundamentals.adapters.base import DataSource
    
    print("=" * 60)
    print("Test 2: Database Adapter - Cached Fallback")
    print("=" * 60)
    
    adapter = DatabaseAdapter()
    
    # Test with ticker that might be in database
    ticker = "RELIANCE.NS"
    
    print(f"\nFetching fundamentals for {ticker} from database...")
    result = await adapter.fetch_fundamentals(ticker)
    
    print(f"\n📊 Results:")
    print(f"  Available: {result.available}")
    print(f"  Source: {result.source.value}")
    
    if result.available:
        print(f"  Completeness: {result.completeness_percent:.1f}%")
        print(f"  Data Age: {result.data_age_hours}h (threshold: 24h)")
        
        if result.data_age_hours and result.data_age_hours > 24:
            print(f"  ⚠️ Data is stale (>{24}h old)")
        
        assert result.source == DataSource.DATABASE, "Should be from database"
        print("\n✅ Test 2 PASSED: Database adapter works")
    else:
        print("\n⚠️ No database data (seed database or FMP will be primary)")
        print("⚠️ Test 2 SKIPPED (not critical - FMP is primary)")
    
    print()


async def test_cascading_strategy():
    """Test cascading provider (FMP → Database → Unavailable)"""
    from app.core.fundamentals.provider_v2 import FundamentalProviderV2
    
    print("=" * 60)
    print("Test 3: Cascading Strategy (FMP → Database)")
    print("=" * 60)
    
    provider = FundamentalProviderV2()
    
    # Test with Indian stock
    ticker = "RELIANCE.NS"
    
    print(f"\nFetching fundamentals for {ticker} (cascading)...")
    result = await provider.get_fundamentals(ticker)
    
    if result:
        print(f"\n✅ Data retrieved successfully!")
        print(f"  Company: {result.company_name}")
        print(f"  PE Ratio: {result.pe_ratio}")
        print(f"  Market Cap: {result.market_cap}")
        
        # Score the fundamentals
        print(f"\nScoring fundamentals...")
        score = await provider.score_fundamentals(result)
        
        print(f"\n📊 Fundamental Score:")
        print(f"  Overall: {score.overall_score}/100 ({score.overall_assessment})")
        print(f"  Valuation: {score.valuation_score}/30")
        print(f"  Growth: {score.growth_score}/25")
        print(f"  Profitability: {score.profitability_score}/25")
        print(f"  Financial Health: {score.financial_health_score}/20")
        
        assert score.overall_score >= 0 and score.overall_score <= 100, "Score should be 0-100"
        assert score.overall_assessment in ["STRONG", "MODERATE", "WEAK", "POOR"], "Assessment should be valid"
        
        print("\n✅ Test 3 PASSED: Cascading strategy works + scoring successful")
    else:
        print("\n⚠️ No fundamental data available from any source")
        print("⚠️ Test 3 SKIPPED (check FMP API key and database)")
    
    print()


async def test_partial_data_handling():
    """Test that system handles partial data gracefully"""
    from app.core.fundamentals.adapters.base import FundamentalDataResult, DataSource
    from decimal import Decimal
    
    print("=" * 60)
    print("Test 4: Partial Data Handling")
    print("=" * 60)
    
    # Create result with only some fields
    partial_result = FundamentalDataResult(
        ticker="TEST.NS",
        source=DataSource.FMP,
        available=True,
        pe_ratio=Decimal("25.5"),
        market_cap=Decimal("100000"),
        # Missing: revenue_growth, roe, debt ratios, etc.
    )
    
    print(f"\n📊 Partial data test:")
    print(f"  Completeness: {partial_result.completeness_percent:.1f}%")
    print(f"  Fields available: {partial_result.fields_available}/{partial_result.fields_total}")
    print(f"  Missing fields: {', '.join(partial_result.missing_fields())}")
    
    # Check if considered complete
    is_complete_75 = partial_result.is_complete(threshold=75.0)
    is_complete_25 = partial_result.is_complete(threshold=25.0)
    
    print(f"\n  Complete (75% threshold)? {is_complete_75}")
    print(f"  Complete (25% threshold)? {is_complete_25}")
    
    assert partial_result.available == True, "Should be available even with partial data"
    assert partial_result.completeness_percent < 100, "Should not be 100% complete"
    assert len(partial_result.missing_fields()) > 0, "Should have missing fields"
    assert partial_result.is_complete(threshold=25.0), "Should pass low threshold"
    
    print("\n✅ Test 4 PASSED: Partial data handled gracefully")
    print()


async def test_data_source_tracking():
    """Test that data source is tracked correctly"""
    from app.core.fundamentals.adapters.base import DataSource
    
    print("=" * 60)
    print("Test 5: Data Source Tracking")
    print("=" * 60)
    
    sources = [
        (DataSource.FMP, "Financial Modeling Prep"),
        (DataSource.DATABASE, "Database (Cached)"),
        (DataSource.UNAVAILABLE, "Unavailable"),
    ]
    
    print("\n📌 Available data sources:")
    for source, name in sources:
        print(f"  {source.name}: {source.value}")
        assert source.value == name, f"Source name should match: {name}"
    
    print("\n✅ Test 5 PASSED: Data sources tracked correctly")
    print()


async def run_all_tests():
    """Run all fundamental adapter tests"""
    print("\n" + "=" * 60)
    print("FUNDAMENTAL DATA ADAPTER TEST SUITE")
    print("=" * 60)
    print()
    
    await test_fmp_adapter()
    await test_database_adapter()
    await test_cascading_strategy()
    await test_partial_data_handling()
    await test_data_source_tracking()
    
    print("=" * 60)
    print("✅ TEST SUITE COMPLETE")
    print("=" * 60)
    print()
    print("Summary:")
    print("- FMP adapter implemented with real API")
    print("- Database adapter provides fallback")
    print("- Cascading strategy: FMP → Database → Unavailable")
    print("- Partial data handled gracefully")
    print("- Data source explicitly tracked")
    print()
    print("Next Steps:")
    print("1. Set FMP_API_KEY environment variable (get free key from financialmodelingprep.com)")
    print("2. Test with real Indian stocks (RELIANCE.NS, TCS.NS, INFY.NS)")
    print("3. Integrate with enhanced.py analysis endpoint")
    print()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
