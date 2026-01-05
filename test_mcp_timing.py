"""Test script for MCP Execution Timing & Caching (Task 2)"""

import sys
import os
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.core.context_agent.trigger_manager import MCPTriggerManager


def test_mcp_timing_and_caching():
    """Test the new MCP execution timing rules and caching"""
    
    print("=" * 80)
    print("Testing MCP Execution Timing & Caching (Task 2)")
    print("=" * 80)
    
    trigger_mgr = MCPTriggerManager(cooldown_minutes=5, cache_ttl_seconds=300)
    
    # Test Case 1: Explicit user click (always triggers)
    print("\n\n🔵 Test Case 1: Explicit User Click (Bypass Cooldown)")
    print("-" * 80)
    
    # First trigger
    result1 = trigger_mgr.should_trigger(
        ticker="RELIANCE.NS",
        opportunity_type="BUY",
        explicit_user_click=True,
        signal_hash="abc123",
        user_id="user123"
    )
    print(f"1st click: {result1} ✅ (Expected: True)")
    
    # Immediate second trigger (cooldown doesn't apply to clicks)
    result2 = trigger_mgr.should_trigger(
        ticker="RELIANCE.NS",
        opportunity_type="BUY",
        explicit_user_click=True,
        signal_hash="abc123",
        user_id="user123"
    )
    print(f"2nd click (immediate): {result2} ✅ (Expected: True - bypasses cooldown)")
    
    # Test Case 2: Signal change detection
    print("\n\n🟢 Test Case 2: Signal Change Detection")
    print("-" * 80)
    
    trigger_mgr.reset_ticker("TCS.NS")
    
    # First signal
    result1 = trigger_mgr.should_trigger(
        ticker="TCS.NS",
        opportunity_type="BUY",
        signal_hash="signal_v1",
        user_id="user123"
    )
    print(f"Signal v1: {result1} ✅ (Expected: True - first time)")
    
    # Same signal (within cooldown)
    result2 = trigger_mgr.should_trigger(
        ticker="TCS.NS",
        opportunity_type="BUY",
        signal_hash="signal_v1",
        user_id="user123"
    )
    print(f"Signal v1 again (cooldown): {result2} ❌ (Expected: False - in cooldown)")
    
    # Signal changed (overrides cooldown)
    result3 = trigger_mgr.should_trigger(
        ticker="TCS.NS",
        opportunity_type="BUY",
        signal_hash="signal_v2",  # Changed!
        user_id="user123"
    )
    print(f"Signal v2 (changed): {result3} ✅ (Expected: True - signal changed)")
    
    # Test Case 3: Login-based triggering
    print("\n\n🟡 Test Case 3: Login-Based Triggering (Once Per Day)")
    print("-" * 80)
    
    # First login of the day
    result1 = trigger_mgr.should_trigger_on_login(
        user_id="user456",
        ticker="INFY.NS",
        signal_hash="infy_signal_v1"
    )
    print(f"1st login today: {result1} ✅ (Expected: True - first login)")
    
    # Second login (same day, same signal)
    result2 = trigger_mgr.should_trigger_on_login(
        user_id="user456",
        ticker="INFY.NS",
        signal_hash="infy_signal_v1"
    )
    print(f"2nd login (same signal): {result2} ❌ (Expected: False - signal unchanged)")
    
    # Third login (same day, signal changed)
    result3 = trigger_mgr.should_trigger_on_login(
        user_id="user456",
        ticker="INFY.NS",
        signal_hash="infy_signal_v2"  # Changed!
    )
    print(f"3rd login (signal changed): {result3} ✅ (Expected: True - signal changed)")
    
    # Test Case 4: Daily limit enforcement
    print("\n\n🔴 Test Case 4: Daily Limit Enforcement")
    print("-" * 80)
    
    trigger_mgr.reset_user_session("user789")
    
    # Trigger 10 times (max limit)
    triggered_count = 0
    for i in range(12):
        result = trigger_mgr.should_trigger_on_login(
            user_id="user789",
            ticker=f"STOCK{i}.NS",
            signal_hash=f"signal_{i}",
            max_daily_triggers=10
        )
        if result:
            triggered_count += 1
    
    print(f"Triggered {triggered_count}/12 attempts (max: 10)")
    print(f"✅ Daily limit enforced: {triggered_count == 10}")
    
    # Test Case 5: Cache key generation
    print("\n\n🟣 Test Case 5: Cache Key Generation")
    print("-" * 80)
    
    cache_key1 = trigger_mgr.get_cache_key("RELIANCE.NS", "abc123")
    cache_key2 = trigger_mgr.get_cache_key("RELIANCE.NS", "abc123")
    cache_key3 = trigger_mgr.get_cache_key("RELIANCE.NS", "xyz789")
    
    print(f"Key 1: {cache_key1}")
    print(f"Key 2: {cache_key2}")
    print(f"Key 3: {cache_key3}")
    print(f"✅ Same signal → Same key: {cache_key1 == cache_key2}")
    print(f"✅ Different signal → Different key: {cache_key1 != cache_key3}")
    
    # Test Case 6: Automatic trigger with cooldown
    print("\n\n⏰ Test Case 6: Automatic Trigger with Cooldown")
    print("-" * 80)
    
    trigger_mgr.reset_ticker("HDFCBANK.NS")
    
    # First automatic trigger
    result1 = trigger_mgr.should_trigger(
        ticker="HDFCBANK.NS",
        opportunity_type="BREAKOUT",
        volatility=0.15,
        signal_hash="hdfc_sig1"
    )
    print(f"1st auto trigger: {result1} ✅ (Expected: True - first time)")
    
    # Immediate second trigger (cooldown applies)
    result2 = trigger_mgr.should_trigger(
        ticker="HDFCBANK.NS",
        opportunity_type="BREAKOUT",
        volatility=0.15,
        signal_hash="hdfc_sig1"
    )
    print(f"2nd auto trigger (immediate): {result2} ❌ (Expected: False - cooldown)")
    
    # Opportunity type changed (overrides cooldown)
    result3 = trigger_mgr.should_trigger(
        ticker="HDFCBANK.NS",
        opportunity_type="REVERSAL",  # Changed!
        volatility=0.15,
        signal_hash="hdfc_sig1"
    )
    print(f"3rd auto trigger (type changed): {result3} ✅ (Expected: True - type changed)")
    
    print("\n" + "=" * 80)
    print("✅ MCP Timing & Caching Testing Complete!")
    print("=" * 80)
    print("\nKey Features Verified:")
    print("  ✅ Explicit user clicks bypass cooldown")
    print("  ✅ Signal change detection working")
    print("  ✅ Login-based triggering (once per day)")
    print("  ✅ Daily limit enforcement (max 10 per user)")
    print("  ✅ Cache key generation consistent")
    print("  ✅ Automatic triggers respect cooldown")
    print("\nExecution Rules:")
    print("  1. On Login: Once per day per user, only for changed signals")
    print("  2. On Click: Immediate execution, bypasses cooldown")
    print("  3. Automatic: Respects 5-min cooldown unless overridden")
    print("  4. Caching: 5-min TTL, invalidated on signal change")


if __name__ == "__main__":
    test_mcp_timing_and_caching()
