# LLM Explanation Layer Integration Guide

## Overview

The Stock Intelligence Copilot now includes an **optional** LLM explanation layer that generates plain-English interpretations of deterministic trading signals.

**CRITICAL**: The LLM is read-only and runs DOWNSTREAM of signal generation. It explains existing results, never generates new signals.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  1. DETERMINISTIC SIGNAL GENERATION (VWAP + Volume)     │
│     - Pure math, no LLM involvement                      │
│     - Outputs: bias, confidence, key levels             │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  2. MARKET CONTEXT PROTOCOL (MCP)                       │
│     - Fetches regime, volume, index alignment           │
│     - No LLM involvement                                 │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  3. LLM EXPLANATION SERVICE (OPTIONAL)                  │
│     - Takes signal + MCP context as input                │
│     - Generates plain-English explanation                │
│     - Falls back to templates if LLM unavailable         │
└─────────────────────────────────────────────────────────┘
```

## Setup Instructions

### 1. Get OpenRouter API Key

1. Visit https://openrouter.ai/
2. Sign up for a free account
3. Get your API key from the dashboard
4. Free tier includes GPT-4o-Mini with generous limits

### 2. Configure Environment

Add to your `.env` file:

```ini
# OpenRouter Configuration (Optional - for LLM explanations)
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=xiaomi/mimo-v2-flash:free
LLM_EXPLANATIONS_ENABLED=true
```

**Models:**
- `xiaomi/mimo-v2-flash:free` (recommended - FREE, fast, good quality)
- `openai/gpt-4o-mini` (paid - fast, cheap)
- `anthropic/claude-3-haiku` (paid alternative)
- `meta-llama/llama-3.1-8b-instruct` (free option)

### 3. Test the Integration

```bash
# Backend tests
cd backend
pytest tests/test_explanation_service.py -v

# Check health endpoint
curl http://localhost:8080/api/v1/explain/health
```

### 4. Verify in UI

The "Interpretation by AI" section will appear in the analysis page when:
- A stock analysis is performed
- LLM explanations are enabled
- OpenRouter API key is configured

If the LLM is unavailable, a fallback template-based explanation is shown instead.

## API Usage

### Endpoint: `POST /api/v1/explain/vwap`

**Request:**
```json
{
  "ticker": "RELIANCE.NS",
  "signal": {
    "bias": "long",
    "confidence": 71,
    "method": "VWAP + Volume",
    "keyLevels": {
      "VWAP": 2850,
      "invalidation": 2810
    }
  },
  "mcp_context": {
    "regime": "trending",
    "indexAlignment": "aligned",
    "volumeState": "expansion",
    "sessionTime": "early open"
  },
  "price_data": {
    "current": 2850,
    "vwap": 2840
  }
}
```

**Response:**
```json
{
  "explanation": "This setup shows a bullish intraday bias based on VWAP + Volume criteria. Price is above VWAP with expanding volume, and the index is aligned, indicating buyers are active. The regime suggests early open strength. Confidence is moderate (71%).",
  "what_went_right": [
    "Volume expansion supports the trend",
    "Index behavior is not contradictory"
  ],
  "what_could_go_wrong": [
    "If price falls below invalidation (2810), pattern weakens",
    "Early open volatility may cause false signals"
  ],
  "confidence_label": "medium",
  "fallback": false,
  "disclaimer": "This is an AI interpretation of pre-computed deterministic signals. It is not financial advice."
}
```

## LLM Constraints

The LLM prompt enforces these constraints:

✅ **DO:**
- Explain existing signal logic
- Use conditional language ("may indicate", "conditions favor")
- Reference provided structured data only
- Include confidence indicators
- Highlight supporting factors and risks

❌ **DON'T:**
- Generate new trading signals
- Predict future prices
- Use action verbs ("buy", "sell", "go long")
- Override confidence scores
- Recommend position sizes
- Hallucinate data not in input

## Fallback Behavior

If the LLM service fails:
1. A template-based explanation is generated
2. The response includes `"fallback": true`
3. The UI shows a note: "Basic explanation - LLM temporarily unavailable"
4. **The deterministic signal remains valid and unaffected**

## Cost Management

**OpenRouter Pricing (xiaomi/mimo-v2-flash:free):**
- Input: **FREE** ✅
- Output: **FREE** ✅
- No limits on free tier

**Alternative Models (if needed):**
- `openai/gpt-4o-mini`: $0.15/$0.60 per 1M tokens (in/out)
  - ~$0.0002 per request
  - 100 requests/day = ~$0.60/month
  - 1000 requests/day = ~$6/month

**Built-in Rate Limiting:**
- 20 requests per minute
- Automatic exponential backoff on errors
- Request caching recommended for repeated queries

## Rate Limiting

The client includes built-in rate limiting:

```python
# Default limits
max_requests_per_window = 20  # Per minute
timeout = 30.0  # Seconds
max_retries = 3
```

## Testing

### Run All Tests
```bash
cd backend
pytest tests/test_explanation_service.py -v
```

### Run Specific Tests
```bash
# Test fallback works
pytest tests/test_explanation_service.py::test_fallback_explanation_always_works -v

# Test forbidden language constraints
pytest tests/test_explanation_service.py::test_fallback_explanation_no_forbidden_language -v

# Test live LLM (requires API key)
OPENROUTER_API_KEY=your_key pytest tests/test_explanation_service.py::test_live_llm_explanation -v
```

## Monitoring

Check service health:
```bash
curl http://localhost:8080/api/v1/explain/health
```

Response:
```json
{
  "enabled": true,
  "configured": true,
  "service_ready": true,
  "model": "openai/gpt-4o-mini",
  "fallback_available": true
}
```

## Troubleshooting

### LLM Explanations Not Showing

1. **Check environment variables:**
   ```bash
   echo $OPENROUTER_API_KEY
   echo $LLM_EXPLANATIONS_ENABLED
   ```

2. **Check logs:**
   ```bash
   # Backend logs
   tail -f backend/logs/app.log | grep explanation
   ```

3. **Verify endpoint:**
   ```bash
   curl http://localhost:8080/api/v1/explain/health
   ```

### Rate Limit Errors

If you hit rate limits:
1. Reduce request frequency
2. Implement response caching
3. Use fallback mode temporarily

### API Key Issues

Common errors:
- `401 Unauthorized`: Invalid API key
- `402 Payment Required`: Free tier exhausted (rare with GPT-4o-Mini)
- `429 Too Many Requests`: Rate limit exceeded

## Security Notes

1. **Never commit API keys** to version control
2. Use environment variables only
3. Rotate keys periodically
4. Monitor usage via OpenRouter dashboard
5. Set up billing alerts

## Future Enhancements

Potential improvements:
- Response caching (Redis)
- Multiple model fallbacks
- A/B testing different prompts
- User feedback collection
- Fine-tuned models for financial explanations

## Support

For issues:
- Backend: Check logs in `backend/logs/`
- Frontend: Browser console errors
- OpenRouter: https://openrouter.ai/docs
- Project: Create GitHub issue

## License & Compliance

- LLM explanations are informational only
- NOT financial advice
- Subject to same disclaimers as deterministic signals
- User bears all responsibility for investment decisions
