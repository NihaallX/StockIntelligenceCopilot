# Market Context Agent - Quick Reference

## 🚀 Quick Start

### 1. Enable the Agent

Add to `.env`:
```bash
MCP_ENABLED=true
MCP_TIMEOUT_SECONDS=10
```

### 2. Use in Your Code

```python
from app.core.context_agent import MarketContextAgent, ContextEnrichmentInput
from app.config import settings

# Initialize agent
agent = MarketContextAgent(enabled=settings.MCP_ENABLED)

# Prepare input (after generating opportunity)
input_data = ContextEnrichmentInput(
    opportunity=opportunity_dict,  # From your rules engine
    ticker="RELIANCE.NS",
    market="NSE",
    time_horizon="LONG_TERM"
)

# Enrich with context
context = await agent.enrich_opportunity(input_data)

# Use the result
print(context.context_summary)
for point in context.supporting_points:
    print(f"  • {point.claim} ({point.source})")
```

### 3. Test It

```bash
cd backend
python test_context_integration.py
```

## 📋 Files Created

```
backend/
├── app/
│   ├── core/
│   │   └── context_agent/
│   │       ├── __init__.py              # Module exports
│   │       ├── agent.py                 # MarketContextAgent class
│   │       ├── models.py                # I/O contracts
│   │       ├── mcp_fetcher.py          # MCP fetching (placeholder)
│   │       └── README.md               # Full documentation
│   ├── api/
│   │   └── v1/
│   │       └── context_analysis.py     # Example endpoint
│   └── config/
│       └── settings.py                 # Added MCP_ENABLED flag
├── tests/
│   └── test_context_agent.py          # Unit tests
├── test_context_integration.py        # Integration test
└── CONTEXT_AGENT_SUMMARY.md           # Implementation summary
```

## ⚙️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_ENABLED` | `false` | Enable/disable context enrichment |
| `MCP_TIMEOUT_SECONDS` | `10` | Timeout for MCP operations |

## 🎯 Key Constraints

| Constraint | Status |
|------------|--------|
| READ-ONLY (no trading advice) | ✅ |
| NO PREDICTIONS (no prices/timing) | ✅ |
| NO MODIFICATIONS (doesn't alter opportunity) | ✅ |
| FACTUAL ONLY (no invented data) | ✅ |
| CITATION REQUIRED (all claims need sources) | ✅ |
| SAFE FALLBACK (works if MCP fails) | ✅ |
| OPTIONAL (system works if disabled) | ✅ |

## 📊 Input Contract

```python
{
  "opportunity": {
    "type": "MOMENTUM_BREAKOUT",
    "confidence": 0.75,
    "risk_level": "MEDIUM"
  },
  "ticker": "RELIANCE.NS",
  "market": "NSE",
  "time_horizon": "SHORT_TERM" | "LONG_TERM"
}
```

## 📤 Output Contract

```python
{
  "context_summary": "Neutral explanation (3-6 sentences)",
  "supporting_points": [
    {
      "claim": "NIFTY declined 2.3% this week",
      "source": "NSE",
      "url": "https://www.nseindia.com/..."
    }
  ],
  "data_sources_used": ["NSE", "Reuters"],
  "disclaimer": "Informational only. Not financial advice.",
  "enriched_at": "2026-01-02T12:00:00Z",
  "mcp_status": "success" | "partial" | "failed" | "disabled"
}
```

## 🔧 API Integration

```python
@router.post("/analyze")
async def analyze_stock(request: AnalysisRequest):
    # Step 1: Generate opportunity (existing)
    analysis = await orchestrator.analyze_stock(request)
    
    # Step 2: Enrich with context (optional)
    context = None
    if settings.MCP_ENABLED:
        agent = MarketContextAgent(enabled=True)
        context = await agent.enrich_opportunity(
            ContextEnrichmentInput(
                opportunity=analysis.insight.model_dump(),
                ticker=request.ticker,
                market="NSE",
                time_horizon=request.time_horizon
            )
        )
    
    # Step 3: Return
    return {
        "analysis": analysis,
        "market_context": context  # Optional
    }
```

## 🧪 Testing

### Run Unit Tests
```bash
cd backend
pytest tests/test_context_agent.py -v
```

### Run Integration Test
```bash
cd backend
python test_context_integration.py
```

### Test Coverage
- ✅ Normal case with valid input
- ✅ No sources found
- ✅ MCP failure
- ✅ Invalid input (no opportunity)
- ✅ MCP disabled

## 📚 Documentation

- **Full README:** `backend/app/core/context_agent/README.md`
- **Implementation Summary:** `backend/CONTEXT_AGENT_SUMMARY.md`
- **Example API:** `backend/app/api/v1/context_analysis.py`

## 🔐 Approved Sources

Only these sources allowed:
- Reuters
- NSE
- BSE
- Moneycontrol
- Economic Times
- Bloomberg
- Financial Times
- SEBI
- RBI

**NOT ALLOWED:** Social media, forums, blogs

## ⚠️ Failure Behavior

| Scenario | Behavior |
|----------|----------|
| MCP timeout | Safe fallback: "No additional market context available" |
| No sources | Partial status with empty points |
| Validation fails | Safe fallback with "failed" status |
| MCP disabled | Immediate return with "disabled" status |

## 🎨 Example Output

```json
{
  "context_summary": "RELIANCE.NS operates in the energy sector which has seen increased volatility. The NIFTY index has declined 2.3% this week. Recent regulatory changes may impact refineries.",
  "supporting_points": [
    {
      "claim": "NIFTY declined 2.3% this week",
      "source": "NSE",
      "url": "https://www.nseindia.com/market-data"
    },
    {
      "claim": "New refinery regulations announced",
      "source": "Reuters",
      "url": "https://www.reuters.com/..."
    }
  ],
  "data_sources_used": ["NSE", "Reuters"],
  "disclaimer": "Informational only. Not financial advice.",
  "enriched_at": "2026-01-02T12:00:00Z",
  "mcp_status": "success"
}
```

## 🚀 Next Steps

1. **Test:** Run `python test_context_integration.py`
2. **Deploy:** Set `MCP_ENABLED=false` (safe default)
3. **Implement:** Fill in MCP fetching methods in `mcp_fetcher.py`
4. **Enable:** Set `MCP_ENABLED=true` when ready
5. **Monitor:** Watch logs for performance

## 💡 Tips

- Start with `MCP_ENABLED=false` in production
- Enable feature gradually after testing
- Monitor timeout settings for performance
- Add caching for frequently accessed context
- Log all MCP calls for debugging

## 📞 Support

Check logs:
```python
import logging
logging.getLogger("app.core.context_agent").setLevel(logging.DEBUG)
```

Verify configuration:
```python
from app.config import settings
print(f"MCP Enabled: {settings.MCP_ENABLED}")
```

Get status:
```bash
GET /api/v1/analysis/context-agent/status
```

## ✅ Checklist

- [ ] Tests pass: `python test_context_integration.py`
- [ ] Configuration added to `.env`
- [ ] Agent integrates with existing endpoints
- [ ] Safe fallback behavior verified
- [ ] Documentation reviewed
- [ ] Ready for production (with MCP_ENABLED=false)
