"""Unit tests for MCP Trigger Manager

Tests the intelligent triggering logic that controls when MCP runs.
"""

import pytest
from datetime import datetime, timedelta
from app.core.context_agent.trigger_manager import MCPTriggerManager


class TestMCPTriggerManager:
    """Test suite for MCP Trigger Manager"""
    
    def test_first_analysis_triggers(self):
        """First analysis for a ticker should always trigger"""
        mgr = MCPTriggerManager(cooldown_minutes=5)
        
        should_trigger = mgr.should_trigger(
            ticker="RELIANCE.NS",
            opportunity_type="BREAKOUT",
            volatility=0.10
        )
        
        assert should_trigger is True
    
    def test_cooldown_blocks_trigger(self):
        """Within cooldown period, should not trigger"""
        mgr = MCPTriggerManager(cooldown_minutes=5)
        
        # First call - triggers
        mgr.should_trigger("RELIANCE.NS", "BREAKOUT", volatility=0.10)
        
        # Second call immediately - should not trigger
        should_trigger = mgr.should_trigger(
            "RELIANCE.NS",
            "BREAKOUT",
            volatility=0.10
        )
        
        assert should_trigger is False
    
    def test_opportunity_type_change_overrides_cooldown(self):
        """Opportunity type change should trigger even in cooldown"""
        mgr = MCPTriggerManager(cooldown_minutes=5)
        
        # First call
        mgr.should_trigger("RELIANCE.NS", "BREAKOUT", volatility=0.10)
        
        # Type changed - should trigger despite cooldown
        should_trigger = mgr.should_trigger(
            "RELIANCE.NS",
            "REVERSAL",  # Changed type
            volatility=0.10
        )
        
        assert should_trigger is True
    
    def test_volatility_spike_overrides_cooldown(self):
        """Volatility crossing threshold should trigger even in cooldown"""
        mgr = MCPTriggerManager(
            cooldown_minutes=5,
            volatility_threshold=0.05  # 5% threshold
        )
        
        # First call with low volatility
        mgr.should_trigger("RELIANCE.NS", "BREAKOUT", volatility=0.10)
        
        # Volatility spiked to 0.16 (6% increase > 5% threshold)
        should_trigger = mgr.should_trigger(
            "RELIANCE.NS",
            "BREAKOUT",
            volatility=0.16
        )
        
        assert should_trigger is True
    
    def test_volatility_small_change_blocked(self):
        """Small volatility changes should not override cooldown"""
        mgr = MCPTriggerManager(
            cooldown_minutes=5,
            volatility_threshold=0.05
        )
        
        # First call
        mgr.should_trigger("RELIANCE.NS", "BREAKOUT", volatility=0.10)
        
        # Small change (3% < 5% threshold)
        should_trigger = mgr.should_trigger(
            "RELIANCE.NS",
            "BREAKOUT",
            volatility=0.13
        )
        
        assert should_trigger is False
    
    def test_force_override(self):
        """Force flag should always trigger"""
        mgr = MCPTriggerManager(cooldown_minutes=5)
        
        # First call
        mgr.should_trigger("RELIANCE.NS", "BREAKOUT", volatility=0.10)
        
        # Force trigger - should work despite cooldown
        should_trigger = mgr.should_trigger(
            "RELIANCE.NS",
            "BREAKOUT",
            volatility=0.10,
            force=True
        )
        
        assert should_trigger is True
    
    def test_disabled_never_triggers(self):
        """When disabled, should never trigger"""
        mgr = MCPTriggerManager(enabled=False)
        
        # Even first analysis should not trigger
        should_trigger = mgr.should_trigger(
            "RELIANCE.NS",
            "BREAKOUT",
            volatility=0.10
        )
        
        assert should_trigger is False
    
    def test_disabled_ignores_force(self):
        """When disabled, even force should not trigger"""
        mgr = MCPTriggerManager(enabled=False)
        
        should_trigger = mgr.should_trigger(
            "RELIANCE.NS",
            "BREAKOUT",
            volatility=0.10,
            force=True
        )
        
        assert should_trigger is False
    
    def test_different_tickers_independent(self):
        """Different tickers should have independent cooldowns"""
        mgr = MCPTriggerManager(cooldown_minutes=5)
        
        # Trigger for RELIANCE
        mgr.should_trigger("RELIANCE.NS", "BREAKOUT", volatility=0.10)
        
        # TCS should still trigger (different ticker)
        should_trigger = mgr.should_trigger(
            "TCS.NS",
            "BREAKOUT",
            volatility=0.08
        )
        
        assert should_trigger is True
    
    def test_reset_ticker(self):
        """Reset should clear ticker state"""
        mgr = MCPTriggerManager(cooldown_minutes=5)
        
        # First call - triggers
        mgr.should_trigger("RELIANCE.NS", "BREAKOUT", volatility=0.10)
        
        # Reset ticker
        mgr.reset_ticker("RELIANCE.NS")
        
        # Should trigger again (state cleared)
        should_trigger = mgr.should_trigger(
            "RELIANCE.NS",
            "BREAKOUT",
            volatility=0.10
        )
        
        assert should_trigger is True
    
    def test_get_stats(self):
        """Stats should track triggers correctly"""
        mgr = MCPTriggerManager(cooldown_minutes=5)
        
        # Trigger for 2 tickers, multiple times
        mgr.should_trigger("RELIANCE.NS", "BREAKOUT", volatility=0.10)
        mgr.should_trigger("TCS.NS", "BREAKOUT", volatility=0.08)
        
        # Force trigger RELIANCE again
        mgr.should_trigger("RELIANCE.NS", "BREAKOUT", force=True)
        
        stats = mgr.get_stats()
        
        assert stats["enabled"] is True
        assert stats["cooldown_minutes"] == 5
        assert stats["tracked_tickers"] == 2
        assert stats["total_triggers"] == 3
        assert stats["avg_triggers_per_ticker"] == 1.5
    
    def test_cooldown_expiry(self):
        """After cooldown expires, should trigger again"""
        mgr = MCPTriggerManager(cooldown_minutes=0)  # 0 minutes = instant expiry
        
        # First call
        mgr.should_trigger("RELIANCE.NS", "BREAKOUT", volatility=0.10)
        
        # Second call after "cooldown" (instant)
        should_trigger = mgr.should_trigger(
            "RELIANCE.NS",
            "BREAKOUT",
            volatility=0.10
        )
        
        # With 0-minute cooldown, should trigger immediately
        assert should_trigger is True
    
    def test_none_volatility_handled(self):
        """None volatility should not crash or trigger"""
        mgr = MCPTriggerManager(cooldown_minutes=5)
        
        # First call with None volatility
        mgr.should_trigger("RELIANCE.NS", "BREAKOUT", volatility=None)
        
        # Second call with None volatility
        should_trigger = mgr.should_trigger(
            "RELIANCE.NS",
            "BREAKOUT",
            volatility=None
        )
        
        # Should be blocked by cooldown (volatility check skipped)
        assert should_trigger is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
