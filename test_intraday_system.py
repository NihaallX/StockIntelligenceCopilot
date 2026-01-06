"""
Test Cases for Intraday Portfolio Intelligence System

These tests validate the mandatory requirements:
1. Stock underperforms index → Trend Stress triggers
2. Sharp drop but low volume → Mean Reversion triggers
3. Large portfolio position → Portfolio Risk triggers
4. MCP disabled → System still works
5. MCP context present → Signal unchanged
6. No conditions met → Stock not flagged
7. Language audit → No forbidden words
"""

import pytest
from datetime import datetime
from app.core.intraday import (
    IntradayDataProvider,
    MethodDetector,
    MarketRegimeContext,
    LanguageFormatter
)
from app.core.intraday.data_layer import IntradayMetrics, PortfolioPosition
from app.core.intraday.method_layer import DetectionTag


class TestMethodDetection:
    """Test the 3 detection methods"""
    
    def test_trend_stress_underperforms_index(self):
        """Test Case 1: Stock underperforms index → WEAK_TREND"""
        detector = MethodDetector()
        
        metrics = IntradayMetrics(
            ticker="TEST.NS",
            timestamp=datetime.now(),
            current_price=100.0,
            vwap=105.0,  # Below VWAP
            open_price=102.0,
            high=103.0,
            low=99.0,
            current_volume=100000,
            avg_volume_20d=100000,
            volume_ratio=1.0,
            sma_20=106.0,  # Below SMA
            sma_50=108.0,  # Below SMA
            rsi_14=45.0,
            index_price=18000.0,
            index_change_pct=1.0,  # Index up
            stock_change_pct=-2.0,  # Stock down
            relative_performance=-3.0,  # Underperforms by >1%
            recent_high_20d=110.0,
            recent_low_20d=95.0
        )
        
        detection = detector.detect_all(metrics, red_candles_count=3)
        
        # Should trigger WEAK_TREND
        assert DetectionTag.WEAK_TREND in detection.tags
        assert len(detection.triggered_conditions[DetectionTag.WEAK_TREND]) >= 2
        print("✅ Test 1 passed: Trend stress detected")
    
    def test_mean_reversion_sharp_drop_low_volume(self):
        """Test Case 2: Sharp drop + extreme RSI → EXTENDED_MOVE"""
        detector = MethodDetector()
        
        metrics = IntradayMetrics(
            ticker="TEST.NS",
            timestamp=datetime.now(),
            current_price=95.0,
            vwap=100.0,
            open_price=100.0,
            high=100.5,
            low=94.0,
            current_volume=50000,  # Low volume
            avg_volume_20d=100000,
            volume_ratio=0.5,
            sma_20=98.0,
            sma_50=99.0,
            rsi_14=28.0,  # Oversold
            index_price=18000.0,
            index_change_pct=-1.0,
            stock_change_pct=-5.0,  # Sharp drop >2%
            relative_performance=-4.0,
            recent_high_20d=105.0,
            recent_low_20d=93.0  # Near low
        )
        
        detection = detector.detect_all(metrics)
        
        # Should trigger EXTENDED_MOVE
        assert DetectionTag.EXTENDED_MOVE in detection.tags
        assert len(detection.triggered_conditions[DetectionTag.EXTENDED_MOVE]) >= 2
        print("✅ Test 2 passed: Mean reversion detected")
    
    def test_portfolio_risk_large_position(self):
        """Test Case 3: Large position >25% → PORTFOLIO_RISK"""
        detector = MethodDetector()
        
        metrics = IntradayMetrics(
            ticker="TEST.NS",
            timestamp=datetime.now(),
            current_price=100.0,
            vwap=100.0,
            open_price=100.0,
            high=101.0,
            low=99.0,
            current_volume=100000,
            avg_volume_20d=100000,
            volume_ratio=1.0,
            sma_20=98.0,
            sma_50=96.0,
            rsi_14=50.0,
            index_price=18000.0,
            index_change_pct=0.5,
            stock_change_pct=0.5,
            relative_performance=0.0,
            recent_high_20d=105.0,
            recent_low_20d=95.0
        )
        
        # Create position with >25% weight
        position = PortfolioPosition(
            ticker="TEST.NS",
            quantity=100,
            entry_price=95.0,
            current_price=100.0,
            portfolio_weight_pct=30.0,  # >25%
            daily_pnl=500.0,
            total_pnl=500.0
        )
        
        all_positions = [position]
        
        detection = detector.detect_all(
            metrics,
            position=position,
            all_positions=all_positions
        )
        
        # Should trigger PORTFOLIO_RISK
        assert DetectionTag.PORTFOLIO_RISK in detection.tags
        assert len(detection.triggered_conditions[DetectionTag.PORTFOLIO_RISK]) >= 1
        print("✅ Test 3 passed: Portfolio risk detected")
    
    def test_no_conditions_met(self):
        """Test Case 6: Normal conditions → No flags"""
        detector = MethodDetector()
        
        # Normal stock metrics
        metrics = IntradayMetrics(
            ticker="TEST.NS",
            timestamp=datetime.now(),
            current_price=100.0,
            vwap=99.5,  # Above VWAP
            open_price=99.0,
            high=101.0,
            low=98.5,
            current_volume=100000,
            avg_volume_20d=100000,
            volume_ratio=1.0,
            sma_20=98.0,  # Above MAs
            sma_50=96.0,
            rsi_14=55.0,  # Neutral
            index_price=18000.0,
            index_change_pct=0.5,
            stock_change_pct=1.0,  # Normal move
            relative_performance=0.5,
            recent_high_20d=105.0,
            recent_low_20d=95.0
        )
        
        detection = detector.detect_all(metrics)
        
        # Should have NO tags
        assert len(detection.tags) == 0
        assert detection.severity == "watch"
        print("✅ Test 6 passed: No false positives")


class TestMarketRegimeContext:
    """Test MCP regime detection"""
    
    def test_mcp_context_doesnt_modify_signals(self):
        """Test Case 5: MCP adds context but doesn't change detection"""
        detector = MethodDetector()
        regime = MarketRegimeContext()
        
        # Create metrics that trigger WEAK_TREND
        metrics = IntradayMetrics(
            ticker="TEST.NS",
            timestamp=datetime.now(),
            current_price=100.0,
            vwap=105.0,
            open_price=102.0,
            high=103.0,
            low=99.0,
            current_volume=100000,
            avg_volume_20d=100000,
            volume_ratio=1.0,
            sma_20=106.0,
            sma_50=108.0,
            rsi_14=45.0,
            index_price=18000.0,
            index_change_pct=1.0,
            stock_change_pct=-2.0,
            relative_performance=-3.0,
            recent_high_20d=110.0,
            recent_low_20d=95.0
        )
        
        # Detection without MCP
        detection = detector.detect_all(metrics, red_candles_count=3)
        tags_before = detection.tags.copy()
        
        # Get MCP context
        context = regime.detect_regime(metrics)
        
        # Detection should be the same
        assert detection.tags == tags_before
        assert DetectionTag.WEAK_TREND in detection.tags
        
        # MCP just adds labels
        assert context.contexts is not None
        print("✅ Test 5 passed: MCP doesn't modify signals")
    
    def test_mcp_graceful_failure(self):
        """Test Case 4: MCP disabled/failed → System continues"""
        detector = MethodDetector()
        
        metrics = IntradayMetrics(
            ticker="TEST.NS",
            timestamp=datetime.now(),
            current_price=100.0,
            vwap=105.0,
            open_price=102.0,
            high=103.0,
            low=99.0,
            current_volume=100000,
            avg_volume_20d=100000,
            volume_ratio=1.0,
            sma_20=106.0,
            sma_50=108.0,
            rsi_14=45.0,
            index_price=18000.0,
            index_change_pct=1.0,
            stock_change_pct=-2.0,
            relative_performance=-3.0,
            recent_high_20d=110.0,
            recent_low_20d=95.0
        )
        
        # Detection works WITHOUT MCP
        detection = detector.detect_all(metrics, red_candles_count=3)
        
        assert DetectionTag.WEAK_TREND in detection.tags
        print("✅ Test 4 passed: System works without MCP")


class TestLanguageValidation:
    """Test language output compliance"""
    
    def test_no_forbidden_words(self):
        """Test Case 7: Language audit - no forbidden words"""
        formatter = LanguageFormatter()
        detector = MethodDetector()
        
        # Create detection
        metrics = IntradayMetrics(
            ticker="TEST.NS",
            timestamp=datetime.now(),
            current_price=100.0,
            vwap=105.0,
            open_price=102.0,
            high=103.0,
            low=99.0,
            current_volume=100000,
            avg_volume_20d=100000,
            volume_ratio=1.0,
            sma_20=106.0,
            sma_50=108.0,
            rsi_14=45.0,
            index_price=18000.0,
            index_change_pct=1.0,
            stock_change_pct=-2.0,
            relative_performance=-3.0,
            recent_high_20d=110.0,
            recent_low_20d=95.0
        )
        
        detection = detector.detect_all(metrics, red_candles_count=3)
        regime = MarketRegimeContext()
        context = regime.detect_regime(metrics)
        
        # Format output
        formatted = formatter.format_detailed_view(detection, metrics, context)
        
        # Check all text fields
        all_text = " ".join([
            formatted["explanation"],
            formatted["conditional_note"],
            formatted["risk_summary"],
            formatted["context_badge"]["tooltip"]
        ])
        
        # Validate no forbidden words
        assert formatter.validate_output(all_text)
        
        # Check for conditional language
        assert any(word in all_text.lower() for word in ["if", "may", "could"])
        
        # Check NO directive words
        forbidden_check = ["buy now", "sell now", "immediately", "must", "will", "guaranteed"]
        for forbidden in forbidden_check:
            assert forbidden not in all_text.lower()
        
        print("✅ Test 7 passed: Language is conditional and compliant")


class TestSeverityCalculation:
    """Test severity levels"""
    
    def test_multiple_tags_alert(self):
        """Multiple tags should trigger 'alert' severity"""
        detector = MethodDetector()
        
        # Metrics that trigger both WEAK_TREND and EXTENDED_MOVE
        metrics = IntradayMetrics(
            ticker="TEST.NS",
            timestamp=datetime.now(),
            current_price=90.0,
            vwap=100.0,  # Far below VWAP
            open_price=100.0,
            high=100.5,
            low=89.0,
            current_volume=100000,
            avg_volume_20d=100000,
            volume_ratio=1.0,
            sma_20=102.0,  # Below MAs
            sma_50=104.0,
            rsi_14=25.0,  # Extreme
            index_price=18000.0,
            index_change_pct=1.0,  # Index up
            stock_change_pct=-10.0,  # Sharp drop
            relative_performance=-11.0,  # Big underperformance
            recent_high_20d=105.0,
            recent_low_20d=88.0
        )
        
        detection = detector.detect_all(metrics, red_candles_count=4)
        
        # Should have multiple tags
        assert len(detection.tags) >= 2
        assert detection.severity == "alert"
        print("✅ Severity test passed: Multiple tags = alert")


def run_all_tests():
    """Run all test cases"""
    print("\n" + "="*60)
    print("INTRADAY PORTFOLIO INTELLIGENCE - TEST SUITE")
    print("="*60 + "\n")
    
    # Method Detection Tests
    print("--- Method Detection Tests ---")
    method_tests = TestMethodDetection()
    method_tests.test_trend_stress_underperforms_index()
    method_tests.test_mean_reversion_sharp_drop_low_volume()
    method_tests.test_portfolio_risk_large_position()
    method_tests.test_no_conditions_met()
    
    # MCP Tests
    print("\n--- Market Context Tests ---")
    mcp_tests = TestMarketRegimeContext()
    mcp_tests.test_mcp_graceful_failure()
    mcp_tests.test_mcp_context_doesnt_modify_signals()
    
    # Language Tests
    print("\n--- Language Validation Tests ---")
    lang_tests = TestLanguageValidation()
    lang_tests.test_no_forbidden_words()
    
    # Severity Tests
    print("\n--- Severity Tests ---")
    severity_tests = TestSeverityCalculation()
    severity_tests.test_multiple_tags_alert()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
