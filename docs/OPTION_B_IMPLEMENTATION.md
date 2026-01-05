# Option B (Balanced System) - Implementation Guide

## Overview

This system provides **confident, actionable signals** backed by evidence and citations. It balances clarity with legal defensibility.

---

## Language Style

### ✅ GOOD (Option B - Balanced)

**Signals:**
```
STRONG BUY SIGNAL DETECTED - High-probability entry zone identified with favorable risk profile.
BUY SIGNAL DETECTED - Conditions favor entry with appropriate position sizing.
STRONG CAUTION SIGNAL - High-confidence bearish pattern. Consider reducing exposure.
```

**Recommendations:**
```
Weakness signal detected in RELIANCE, TCS. Reducing position size may lower downside exposure.
Concentration alert: INFY represents 35% of portfolio. Diversification signals favor broader allocation.
Strong momentum signals in HDFCBANK, ICICIBANK. Current positions show favorable pattern continuation.
```

### ❌ BAD (Too Weak - Option C)

```
If considering entry, conditions appear favorable...
You might want to consider reducing exposure if worried...
```

### ❌ BAD (Too Directive - Option A)

```
BUY RELIANCE NOW at ₹2,500!
Sell immediately before losses mount.
You must diversify to 10% portfolio weight.
```

---

## Architecture

### Signal Generation (Core Engine)
1. **Technical Analysis** → Generates buy/sell signals
2. **Fundamental Analysis** → Validates signals
3. **Risk Assessment** → Calculates confidence
4. **Scenario Analysis** → Projects outcomes

### MCP Layer (Context Enrichment)
```
┌─────────────────────────────┐
│   SIGNAL GENERATED          │
│   (BUY, confidence: 0.85)   │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│   MCP Fetcher (READ-ONLY)   │
│   ✓ Fetch news articles     │
│   ✓ Add citations           │
│   ✗ Does NOT alter signal   │
│   ✗ Does NOT predict prices │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│   Final Output              │
│   Signal + Context          │
└─────────────────────────────┘
```

**CRITICAL**: MCP runs AFTER signals are generated. It provides supporting evidence, NOT the signal itself.

---

## Key Components

### 1. Recommendation Generation

**Location:** `backend/app/api/v1/portfolio.py` (lines 620-648)

```python
# Option B style - confident but defensible
if signal_type == "BUY":
    if confidence > 0.8:
        recommendation = "STRONG BUY SIGNAL DETECTED - High-probability entry zone identified with favorable risk profile."
    elif confidence > 0.6:
        recommendation = "BUY SIGNAL DETECTED - Conditions favor entry with appropriate position sizing."
    else:
        recommendation = "WEAK BUY SIGNAL - Marginal setup. Stronger confirmation recommended before entry."
```

### 2. LLM System Prompt

**Location:** `backend/app/api/v1/portfolio.py` (lines 745-778)

```python
system_prompt = """You are a confident financial analysis assistant providing actionable portfolio insights.

CRITICAL RULES:
- Use CLEAR, CONFIDENT language (Option B: Balanced System)
- Be direct but defensible
- Use signal-based framing: "Signal detected", "Pattern identified", "Conditions favor"
- AVOID absolute commands: "buy now", "sell immediately", "must"
- ALLOWED confident language: "signals suggest", "conditions favor", "pattern detected"

TONE: Professional analyst providing signal-based insights, not personal commands
"""
```

### 3. Frontend UI

**Location:** `frontend/app/dashboard/analysis/page.tsx`

**Updated Labels:**
```tsx
<h3>Why The System Thinks This Matters (Sources)</h3>

<p className="text-sm text-muted-foreground">
  📊 These sources SUPPORT the signal above. They did not generate it. 
  The signal was produced by technical + fundamental analysis, then these 
  news articles were retrieved to provide market context.
</p>
```

---

## Price Predictions (Option B Style)

### Short-term Ranges (Probabilistic)

```python
# Good - probabilistic range
"Price may move toward ₹2,700-₹3,000 with moderate confidence (70% probability)"

# Bad - exact target with date
"Will reach ₹2,850 by March 15, 2024"
```

### Implementation Location
Add to scenario analysis output:
- `backend/app/api/v1/enhanced.py` - `_generate_recommendation()`

---

## Risk Zones (Not Commands)

### ✅ Option B Style

```python
"Support zone at ₹2,380. Risk increases below this level."
"Resistance at ₹2,750. Profit-taking may emerge near this zone."
```

### ❌ Not Allowed

```python
"Set stop loss at ₹2,380"
"Sell immediately if price drops below ₹2,380"
```

---

## Position Sizing Warnings

### ✅ Option B Style

```python
"High concentration in this sector"
"Portfolio weight suggests elevated single-stock risk"
```

### ❌ Not Allowed

```python
"Reduce to 10% of portfolio"
"Increase position to 5,000 shares"
```

---

## MCP Context Agent

### What It Does
1. **Fetches News:** Retrieves recent articles from Moneycontrol
2. **Adds Citations:** Provides source + URL for each claim
3. **Enriches Context:** Explains WHY the signal matters

### What It Does NOT Do
- ❌ Generate buy/sell signals
- ❌ Predict prices
- ❌ Alter confidence levels
- ❌ Make recommendations

### Code Location
- `backend/app/core/context_agent/agent.py` - Main orchestrator
- `backend/app/core/context_agent/mcp_fetcher.py` - News fetcher
- `backend/app/core/context_agent/trigger_manager.py` - Debouncing logic
- `backend/app/core/context_agent/models.py` - Data contracts

### Trigger Logic
```python
# When MCP runs:
✓ First analysis for ticker
✓ Opportunity type change (BUY → SELL or vice versa)
✓ Volatility spike > 5%

# When MCP is skipped:
✗ Within 5-minute cooldown
✗ Simple price refresh (no signal change)
```

---

## Legal & Compliance (SEBI-Defensible)

### Disclaimers

**Analysis Page:**
```
ℹ️ This is a probability-based assessment, not financial advice. 
All investments carry risk.
```

**Market Context:**
```
📊 These sources SUPPORT the signal above. They did not generate it.
The signal was produced by technical + fundamental analysis.
```

### Key Principles

1. **Signal-Based Language:** Frame as detected patterns, not commands
2. **Evidence-Backed:** Every claim has citation (source + URL)
3. **Risk Disclosure:** Always mention risk, probability, uncertainty
4. **No Guarantees:** Use "may", "signals suggest", "conditions favor"
5. **Decision Support:** Present analysis, let user decide

### What Makes It Defensible

✅ **Transparent:** Shows HOW signal was generated (technical + fundamental)
✅ **Cited:** All market context has sources
✅ **Probabilistic:** Acknowledges uncertainty
✅ **Non-Directive:** "Signal detected" not "Buy now"
✅ **Educational:** Explains reasoning with evidence

---

## Testing

### Run All Tests
```bash
cd backend
pytest app/tests/ -v
```

### Expected Results
```
✓ test_mcp_fetcher.py - 10/10 passing
✓ test_trigger_manager.py - 13/13 passing
✓ Total: 23/23 passing
```

### Manual Testing

1. **Generate Analysis:**
```bash
curl http://localhost:8000/api/v1/analysis/enhanced?ticker=RELIANCE.NS
```

2. **Check Recommendation Language:**
   - Should see: "STRONG BUY SIGNAL DETECTED"
   - Should NOT see: "If considering entry..."

3. **Check MCP Context:**
   - `market_context.supporting_points` should have news articles
   - Each point should have `claim`, `source`, `url`

4. **Check Trigger Logic:**
   - First call → MCP runs
   - Second call (within 5 min) → MCP skipped (null context)
   - After 5 min → MCP runs again

---

## Next Steps (Optional Enhancements)

### 1. Add Price Ranges to Recommendations
```python
# In enhanced.py - _generate_recommendation()
if signal_type == "BUY" and scenario_analysis:
    best_case = scenario_analysis["best_case"]["expected_return_percent"]
    recommendation += f" Price may move toward ₹{target_low}-₹{target_high} with moderate confidence."
```

### 2. Add Stop-Loss Zones
```python
# Risk zones, not commands
"Support zone identified at ₹2,380. Risk increases below this level."
```

### 3. Enhanced Position Warnings
```python
# Relative warnings only
if portfolio_weight > 0.30:
    warning = "High concentration detected. Consider broader diversification."
```

---

## FAQ

### Q: Is this using Anthropic's Model Context Protocol?
**A:** No. This is a custom "Market Context Protocol" that fetches news via HTTP scraping. To use real MCP:
- Implement MCP server/client per Anthropic spec
- Replace `mcp_fetcher.py` with MCP client calls

### Q: Can users sue us for bad recommendations?
**A:** Option B is designed to be SEBI-defensible:
- No direct commands ("Buy now")
- All claims cited with sources
- Clear disclaimers ("Not financial advice")
- Probabilistic language ("may", "signals suggest")
- Risk disclosure ("All investments carry risk")

**But:** Always consult legal counsel before public launch.

### Q: How is this different from Option C (what we had before)?
**A:**
- **Option C:** "If considering entry, conditions appear favorable..."
- **Option B:** "STRONG BUY SIGNAL DETECTED - Entry conditions favorable."

Option B is more confident and actionable while remaining defensible.

### Q: What if MCP fails to fetch news?
**A:** System gracefully degrades:
```json
{
  "market_context": null,
  "mcp_status": "error"
}
```
Signal is still shown. MCP is optional enrichment.

---

## Maintenance

### Updating Language
To adjust tone, edit these files:
1. `backend/app/api/v1/portfolio.py` - Recommendation generation
2. `backend/app/api/v1/enhanced.py` - Analysis recommendations
3. `frontend/app/dashboard/analysis/page.tsx` - UI labels

### Monitoring MCP Performance
```python
# Check trigger stats
from app.core.context_agent.trigger_manager import TriggerManager
manager = TriggerManager()
stats = manager.get_statistics()
print(stats)
```

### Common Issues

**Issue:** MCP always returning null
- Check trigger manager state (may be in cooldown)
- Verify news fetcher works: `pytest app/tests/test_mcp_fetcher.py`

**Issue:** Language too weak/strong
- Adjust confidence thresholds in `portfolio.py` (lines 627-647)
- Update LLM system prompt (lines 745-778)

---

## Conclusion

Option B provides **confident, actionable signals** while remaining **SEBI-defensible** through:
- Signal-based language (not commands)
- Evidence-backed claims (citations)
- Risk disclosure (probability, uncertainty)
- Transparent methodology (shows technical + fundamental)

The system is production-ready for **sophisticated retail investors** who want clear guidance with proof.

**Remember:** MCP SUPPORTS signals, it does NOT generate them. The signal comes from technical + fundamental analysis, then MCP adds "here's why this matters" context.
