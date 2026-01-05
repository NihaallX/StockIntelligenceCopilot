# Market Context Agent - Documentation

## Overview

The **Market Context Agent** is a READ-ONLY context enrichment layer that uses MCP (Model Context Protocol) to fetch real-world market context from reputable sources. It does **NOT** generate signals, predictions, or recommendations.

## ✅ Implementation Status

### Company News Fetcher - **IMPLEMENTED**

The first real MCP data fetcher is now operational:

- **Source:** Moneycontrol (reputable Indian financial news)
- **Data:** Recent company-specific news headlines
- **Validation:** Input validation, spam filtering, sanitization
- **Error Handling:** Timeout protection, graceful failures
- **Testing:** 10/10 unit tests passing

**See:** `IMPLEMENTATION_NOTES.md` for detailed technical documentation.

### Other Fetchers - **PLACEHOLDER**

- Sector performance (NSE/BSE) - Placeholder
- Index movement (NIFTY, Bank NIFTY) - Placeholder
- Macro headlines - Placeholder

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Existing System                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Technical Analysis → Fundamental Analysis →          │   │
│  │  Risk Assessment → Opportunity Generation             │   │
│  └─────────────────────┬────────────────────────────────┘   │
│                        │                                     │
│                        │ Structured Opportunity              │
│                        ▼                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Market Context Agent (NEW)                    │   │
│  │  ┌──────────────────────────────────────────────┐    │   │
│  │  │  Input: Opportunity + Ticker + Market        │    │   │
│  │  └─────────────────┬──────────────────────────────┘   │   │
│  │                    │                                  │   │
│  │  ┌─────────────────▼──────────────────────────────┐  │   │
│  │  │  MCP Context Fetcher                           │  │   │
│  │  │  - Company news (Reuters, ET, etc.)            │  │   │
│  │  │  - Sector performance (NSE/BSE)                │  │   │
│  │  │  - Index movement (NIFTY, Bank NIFTY)          │  │   │
│  │  │  - Macro headlines (RBI, inflation, etc.)      │  │   │
│  │  └─────────────────┬──────────────────────────────┘  │   │
│  │                    │                                  │   │
│  │  ┌─────────────────▼──────────────────────────────┐  │   │
│  │  │  Output: Context Summary + Citations           │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                        │                                     │
│                        │ Enriched Opportunity                │
│                        ▼                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Return to User (with context)                        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Hard Constraints

The Market Context Agent operates under strict constraints:

1. **READ-ONLY**: Does NOT generate buy/sell recommendations
2. **NO PREDICTIONS**: Does NOT predict prices or timing
3. **NO MODIFICATIONS**: Does NOT alter opportunity type, confidence, or risk
4. **FACTUAL ONLY**: Does NOT invent data
5. **CITATION REQUIRED**: Every claim must have a source
6. **SAFE FALLBACK**: Returns safe output if MCP fails
7. **OPTIONAL**: System works normally if disabled or failed

## Data Flow

### Input Contract

```python
{
  "opportunity": {
    "type": "MOMENTUM_BREAKOUT",
    "confidence": 0.75,
    "risk_level": "MEDIUM",
    # ... other fields from rules engine
  },
  "ticker": "RELIANCE.NS",
  "market": "NSE",
  "time_horizon": "SHORT_TERM" | "LONG_TERM"
}
```

### Output Contract

```python
{
  "context_summary": "3-6 neutral sentences explaining market context",
  "supporting_points": [
    {
      "claim": "Factual statement",
      "source": "Reuters",
      "url": "https://www.reuters.com/..."
    }
  ],
  "data_sources_used": ["Reuters", "NSE"],
  "disclaimer": "Informational only. Not financial advice.",
  "enriched_at": "2026-01-02T12:00:00Z",
  "mcp_status": "success" | "partial" | "failed" | "disabled"
}
```

## Usage

### Basic Usage

```python
from app.core.context_agent import MarketContextAgent, ContextEnrichmentInput

# Initialize agent (disabled by default)
agent = MarketContextAgent(enabled=settings.MCP_ENABLED)

# Prepare input
input_data = ContextEnrichmentInput(
    opportunity={
        "type": "MOMENTUM_BREAKOUT",
        "confidence": 0.75,
        "risk_level": "MEDIUM"
    },
    ticker="RELIANCE.NS",
    market="NSE",
    time_horizon="LONG_TERM"
)

# Enrich with market context
context = await agent.enrich_opportunity(input_data)

# Use the enriched context
print(context.context_summary)
for point in context.supporting_points:
    print(f"{point.claim} (Source: {point.source})")
```

### Integration with Existing System

```python
from app.core.orchestrator import orchestrator
from app.core.context_agent import MarketContextAgent, ContextEnrichmentInput

# Step 1: Generate opportunity (existing system)
analysis = await orchestrator.analyze_stock(analysis_request)
opportunity = analysis.insight  # Structured opportunity

# Step 2: Enrich with context (new layer)
if settings.MCP_ENABLED:
    agent = MarketContextAgent(enabled=True)
    
    context_input = ContextEnrichmentInput(
        opportunity=opportunity.model_dump(),
        ticker=analysis_request.ticker,
        market="NSE",
        time_horizon=analysis_request.time_horizon
    )
    
    context = await agent.enrich_opportunity(context_input)
    
    # Attach context to response
    response = {
        "opportunity": opportunity,
        "market_context": context  # Optional enrichment
    }
else:
    # System works normally without context
    response = {
        "opportunity": opportunity
    }
```

## Configuration

Add to `.env`:

```bash
# Market Context Agent
MCP_ENABLED=false  # Set to true to enable context enrichment
MCP_TIMEOUT_SECONDS=10  # Timeout for MCP operations
```

Access in code:

```python
from app.config import settings

agent = MarketContextAgent(enabled=settings.MCP_ENABLED)
```

## MCP Sources

The agent only fetches from approved sources:

- **Reuters**: Global financial news
- **NSE**: National Stock Exchange of India
- **BSE**: Bombay Stock Exchange
- **Moneycontrol**: Indian financial news
- **Economic Times**: Business news
- **Bloomberg**: Global markets
- **Financial Times**: Business news
- **SEBI**: Market regulator
- **RBI**: Central bank

**NOT ALLOWED**: Social media, forums, blogs, unverified sources

## Failure Behavior

The agent fails gracefully:

1. **MCP Timeout**: Returns safe fallback
2. **No Sources Found**: Returns partial status with empty points
3. **Validation Fails**: Returns safe fallback
4. **MCP Disabled**: Returns disabled status immediately

Safe fallback output:

```python
{
  "context_summary": "No additional market context available at this time.",
  "supporting_points": [],
  "data_sources_used": [],
  "disclaimer": "Informational only. Not financial advice.",
  "enriched_at": "2026-01-02T12:00:00Z",
  "mcp_status": "failed" | "disabled"
}
```

## Testing

Run tests:

```bash
cd backend
pytest tests/test_context_agent.py -v
```

Test coverage:

1. ✅ Normal case with valid input
2. ✅ No sources found
3. ✅ MCP failure
4. ✅ Invalid input (no opportunity)
5. ✅ MCP disabled
6. ✅ Source validation

## API Integration Example

Add to existing analysis endpoint:

```python
@router.post("/api/v1/analysis/enhanced")
async def enhanced_analysis(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    # Step 1: Generate opportunity (existing)
    analysis = await orchestrator.analyze_stock(request)
    
    # Step 2: Enrich with context (optional)
    market_context = None
    if settings.MCP_ENABLED:
        try:
            agent = MarketContextAgent(enabled=True)
            context_input = ContextEnrichmentInput(
                opportunity=analysis.insight.model_dump(),
                ticker=request.ticker,
                market="NSE",
                time_horizon=request.time_horizon
            )
            market_context = await agent.enrich_opportunity(context_input)
        except Exception as e:
            logger.warning(f"Context enrichment failed: {e}")
            # Continue without context
    
    # Step 3: Return response
    return {
        "analysis": analysis,
        "market_context": market_context  # Optional
    }
```

## Security & Compliance

1. **No Trading Advice**: Agent is explanatory only
2. **Citation Required**: All claims must have sources
3. **Reputable Sources Only**: No social media or unverified sources
4. **Disclaimer Included**: All outputs include legal disclaimer
5. **Audit Trail**: All MCP calls logged
6. **Timeout Protection**: 10-second timeout prevents hanging
7. **Fail-Safe**: System works normally if disabled or failed

## Maintenance

### Adding New Sources

Edit `mcp_fetcher.py`:

```python
APPROVED_SOURCES = [
    "Reuters",
    "NSE",
    # ... existing sources
    "New Approved Source"  # Add here
]
```

### Adjusting Timeout

Edit `.env`:

```bash
MCP_TIMEOUT_SECONDS=15  # Increase if needed
```

### Debugging

Enable debug logging:

```python
import logging

logging.getLogger("app.core.context_agent").setLevel(logging.DEBUG)
```

## Performance Considerations

- **Async Operations**: All MCP calls are async
- **Timeout**: 10-second timeout prevents hanging
- **Caching**: Consider adding caching for frequently accessed context
- **Rate Limiting**: MCP calls should respect rate limits
- **Parallel Fetching**: Multiple sources fetched in parallel

## Future Enhancements

1. **Real MCP Integration**: Currently placeholder methods
2. **LLM Summary Generation**: Use LLM to generate better summaries
3. **Context Caching**: Cache context for X minutes
4. **More Sources**: Add more reputable sources
5. **Sentiment Analysis**: Extract sentiment from news (factual only)
6. **Historical Context**: Compare current context to historical patterns

## FAQs

**Q: Does this generate buy/sell recommendations?**
A: No. It only provides factual market context with citations.

**Q: What if MCP fails?**
A: The system returns a safe fallback and continues to work normally.

**Q: Is MCP enabled by default?**
A: No. Set `MCP_ENABLED=true` in `.env` to enable.

**Q: Can I add my own sources?**
A: Yes, but only add reputable financial outlets to `APPROVED_SOURCES`.

**Q: How do I test the agent?**
A: Run `pytest tests/test_context_agent.py -v`

## Support

For issues or questions:
1. Check logs: `app.core.context_agent`
2. Verify configuration: `settings.MCP_ENABLED`
3. Run tests: `pytest tests/test_context_agent.py`
4. Check MCP timeout: `settings.MCP_TIMEOUT_SECONDS`
