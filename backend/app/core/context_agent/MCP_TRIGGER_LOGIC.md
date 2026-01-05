# MCP Trigger Logic Documentation

## Overview

The Market Context Agent (MCP) does **NOT run on every price tick**. It uses intelligent triggering to minimize API calls while ensuring fresh context when needed.

## Design Principles

1. **Efficiency First**: Avoid redundant MCP calls for unchanged conditions
2. **Event-Driven**: Trigger only on meaningful state changes
3. **Debounced**: Enforce minimum cooldown between calls
4. **Non-Blocking**: Never delay core analysis - MCP is optional

## Trigger Rules

### Rule 1: New Opportunity Detection
**Trigger MCP when**: A new opportunity is detected for a ticker  
**Example**: First time analyzing RELIANCE.NS in current session  
**Rationale**: Fresh analysis needs fresh context

### Rule 2: Opportunity Type Change
**Trigger MCP when**: Opportunity type changes (overrides cooldown)  
**Example**: BREAKOUT → REVERSAL  
**Rationale**: Different opportunity types need different context

### Rule 3: Volatility Threshold Crossed
**Trigger MCP when**: Volatility changes by > 5% (overrides cooldown)  
**Example**: Volatility 10% → 16% (6% spike)  
**Rationale**: High volatility suggests market regime change

### Rule 4: Cooldown Enforcement
**Block MCP when**: Last call was < 5 minutes ago (unless overridden by rules 2-3)  
**Example**: Analyzing same ticker with same conditions after 2 minutes  
**Rationale**: Context doesn't change that fast

### Rule 5: Price Refresh Only
**Block MCP when**: Only price updated, no opportunity change  
**Example**: Price update from $150.00 → $150.50 with same HOLD recommendation  
**Rationale**: Simple price updates don't need new context

## Configuration

```python
# backend/app/config/settings.py

MCP_ENABLED: bool = False  # Master switch
MCP_TRIGGER_COOLDOWN_MINUTES: int = 5  # Minimum time between calls
```

```python
# Initialize trigger manager
from app.core.context_agent import get_trigger_manager

trigger_mgr = get_trigger_manager(
    cooldown_minutes=5,  # Configurable cooldown
    volatility_threshold=0.05,  # 5% volatility change triggers MCP
    enabled=True
)
```

## Usage Example

```python
from app.core.context_agent import MarketContextAgent, get_trigger_manager

# Initialize
agent = MarketContextAgent(enabled=True)
trigger_mgr = get_trigger_manager(cooldown_minutes=5)

# Check if should trigger
should_trigger = trigger_mgr.should_trigger(
    ticker="RELIANCE.NS",
    opportunity_type="BREAKOUT",
    volatility=0.15
)

if should_trigger:
    # Trigger MCP
    context = await agent.enrich_opportunity(opportunity_data)
else:
    # Skip MCP (cooldown or no change)
    context = None
```

## Trigger Decision Matrix

| Scenario | Time Since Last | Type Change | Volatility Spike | Result |
|----------|----------------|-------------|------------------|--------|
| First analysis | N/A | N/A | N/A | ✅ Trigger |
| 2 min, same type, same vol | 2 min | ❌ | ❌ | ❌ Skip (cooldown) |
| 2 min, type changed | 2 min | ✅ | ❌ | ✅ Trigger (override) |
| 2 min, vol spiked >5% | 2 min | ❌ | ✅ | ✅ Trigger (override) |
| 6 min, same conditions | 6 min | ❌ | ❌ | ✅ Trigger (cooldown expired) |
| Force flag | Any | Any | Any | ✅ Trigger (force) |

## Monitoring

Track MCP trigger behavior with built-in stats:

```python
trigger_mgr = get_trigger_manager()
stats = trigger_mgr.get_stats()

# Returns:
{
    "enabled": True,
    "cooldown_minutes": 5,
    "volatility_threshold": 0.05,
    "tracked_tickers": 25,
    "total_triggers": 38,
    "avg_triggers_per_ticker": 1.52
}
```

## Testing

### Unit Tests

```bash
pytest tests/test_trigger_manager.py -v
```

**Test Coverage:**
- First analysis triggers ✅
- Cooldown blocks trigger ✅
- Type change overrides cooldown ✅
- Volatility spike overrides cooldown ✅
- Force flag works ✅
- Disabled mode blocks all triggers ✅
- Different tickers independent ✅
- Stats tracking accurate ✅

### Integration Test

```python
# Test in real analysis endpoint
from app.api.v1.context_analysis import analyze_with_context

# First call - should trigger MCP
response1 = await analyze_with_context(ticker="RELIANCE.NS")
assert response1["market_context"] is not None

# Second call 2 minutes later - should skip MCP
response2 = await analyze_with_context(ticker="RELIANCE.NS")
# MCP skipped due to cooldown, context from cache or null
```

## Production Considerations

### 1. Cooldown Tuning

**Default**: 5 minutes  
**Range**: 1-15 minutes

- **Higher cooldown (10-15 min)**: Reduce API costs, suitable for long-term investors
- **Lower cooldown (1-3 min)**: More responsive, suitable for active traders
- **Production recommendation**: Start at 5 minutes, monitor hit rate

### 2. Volatility Threshold Tuning

**Default**: 5% (0.05)  
**Range**: 3-10%

- **Lower threshold (3%)**: More sensitive to market changes, more MCP calls
- **Higher threshold (8-10%)**: Only trigger on major volatility events
- **Production recommendation**: 5% for balanced approach

### 3. Caching Strategy

Combine trigger logic with caching:

```python
# Cache MCP results for 1 hour
@cache(ttl=3600)
async def _fetch_moneycontrol_news(ticker):
    # ... implementation
```

**Effect**: Even if trigger allows MCP, cache prevents redundant network calls

### 4. Monitoring Alerts

Set up alerts for:
- **High trigger rate**: > 20 triggers/minute → Possible cooldown too low
- **Zero triggers**: 0 triggers/hour → Possible MCP disabled or broken
- **High skip rate**: > 95% skips → Possible cooldown too high

### 5. A/B Testing

Test different cooldown settings:
- **Group A**: 3-minute cooldown
- **Group B**: 5-minute cooldown (control)
- **Group C**: 10-minute cooldown

**Metrics to track**:
- Context freshness (time since last MCP)
- User engagement (click-through on context sources)
- API cost per user
- Analysis completion time

## Deployment Checklist

- [ ] Set `MCP_ENABLED=false` initially (safe default)
- [ ] Deploy trigger manager code
- [ ] Run unit tests (13 tests should pass)
- [ ] Set `MCP_TRIGGER_COOLDOWN_MINUTES=5` in .env
- [ ] Monitor logs for "MCP triggered" vs "MCP skipped" messages
- [ ] Enable MCP for 10% of users
- [ ] Monitor trigger stats with `get_stats()`
- [ ] Tune cooldown based on usage patterns
- [ ] Enable for 100% of users

## Logs to Monitor

```bash
# Check trigger behavior
grep "MCP triggered\|MCP skipped" logs/*.log

# Count triggers per ticker
grep "MCP triggered" logs/*.log | awk '{print $NF}' | sort | uniq -c

# Average time between triggers
grep "MCP triggered" logs/*.log | awk '{print $1, $2}' | ...
```

## FAQ

**Q: Why not run MCP on every analysis?**  
A: Context doesn't change every second. Running MCP on every price tick wastes API calls and slows analysis.

**Q: What if I want real-time context?**  
A: Set `cooldown_minutes=0` for instant triggers (not recommended for production).

**Q: Can I force MCP for specific users?**  
A: Yes, use `force=True` parameter: `trigger_mgr.should_trigger(..., force=True)`

**Q: How do I disable MCP entirely?**  
A: Set `MCP_ENABLED=false` in settings. Trigger manager will block all triggers.

**Q: What happens if MCP times out?**  
A: Trigger manager doesn't handle timeouts - that's in `mcp_fetcher.py`. Analysis continues without context.

**Q: Can different tickers have different cooldowns?**  
A: Not currently. Global cooldown applies to all tickers. Feature request for future.

---

**Last Updated**: January 2026  
**Version**: 1.0  
**Status**: Production Ready ✅
