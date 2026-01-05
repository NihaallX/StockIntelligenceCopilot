# API Usage Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Server
```bash
cd backend
python main.py
```

Server will start at: `http://localhost:8000`

### 3. View API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### Get Supported Tickers (MVP)
```http
GET /api/v1/supported-tickers
```

**Response:**
```json
{
  "AAPL": {"name": "Apple Inc.", "sector": "Technology", ...},
  "MSFT": {"name": "Microsoft Corporation", ...},
  ...
}
```

### Analyze Stock
```http
POST /api/v1/analyze
Content-Type: application/json

{
  "ticker": "AAPL",
  "time_horizon": "long_term",
  "risk_tolerance": "moderate",
  "lookback_days": 90
}
```

**Parameters:**
- `ticker` (required): Stock symbol (uppercase, e.g., "AAPL")
- `time_horizon` (optional): "long_term" or "short_term" (default: "long_term")
- `risk_tolerance` (optional): "conservative", "moderate", or "aggressive" (default: "moderate")
- `lookback_days` (optional): Historical days to analyze (30-365, default: 90)

**Response Example:**
```json
{
  "success": true,
  "insight": {
    "ticker": "AAPL",
    "timestamp": "2026-01-01T10:00:00Z",
    "signal": {
      "strength": {
        "signal_type": "bullish",
        "confidence": 0.75,
        "strength": "moderate"
      },
      "reasoning": {
        "primary_factors": [
          "20-day SMA above 50-day SMA",
          "RSI suggests oversold conditions"
        ],
        "supporting_indicators": {
          "RSI": 28.5,
          "MACD": 1.2
        },
        "contradicting_factors": [],
        "assumptions": [...],
        "limitations": [...]
      }
    },
    "risk_assessment": {
      "overall_risk": "moderate",
      "is_actionable": true,
      "risk_factors": [...],
      "warnings": [...]
    },
    "recommendation": "consider",
    "summary": "AAPL exhibits a moderate bullish signal...",
    "key_points": [
      "📈 Signal: BULLISH (moderate, 75.0% confidence)",
      "✓ 20-day SMA above 50-day SMA",
      "🟡 Risk Level: MODERATE"
    ],
    "overall_confidence": 0.72
  },
  "processing_time_ms": 45.2
}
```

## Python Example

```python
import requests

# Analyze a stock
response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={
        "ticker": "AAPL",
        "time_horizon": "long_term",
        "risk_tolerance": "moderate",
        "lookback_days": 90
    }
)

if response.status_code == 200:
    data = response.json()
    if data["success"]:
        insight = data["insight"]
        print(f"Signal: {insight['signal']['strength']['signal_type']}")
        print(f"Confidence: {insight['signal']['strength']['confidence']:.1%}")
        print(f"Recommendation: {insight['recommendation']}")
        print(f"\nSummary: {insight['summary']}")
    else:
        print(f"Error: {data['error']}")
else:
    print(f"HTTP Error: {response.status_code}")
```

## Understanding the Response

### Signal Types
- **bullish**: Indicators suggest potential upward movement
- **bearish**: Indicators suggest potential downward movement
- **neutral**: No clear directional signal

### Signal Strength
- **weak**: Low conviction (confidence < 60%)
- **moderate**: Medium conviction (60% ≤ confidence < 75%)
- **strong**: High conviction (confidence ≥ 75%)

### Risk Levels
- **low**: Minimal identified risks
- **moderate**: Some risks present, manageable
- **high**: Significant risks, caution advised
- **critical**: Severe risks, action blocked

### Recommendations
- **consider**: Signal meets criteria, worth considering
- **monitor**: Watch but don't act yet
- **avoid**: Too risky for your profile
- **no_action**: No clear signal, do nothing

## Important Notes

1. **Not Financial Advice**: All outputs are probabilistic suggestions, not guarantees
2. **Maximum Confidence**: System caps confidence at 95% (epistemic humility)
3. **Risk-Aware**: Signals can be blocked if they don't meet safety criteria
4. **MVP Data**: Currently uses mock data (10 tickers available)
5. **Always Verify**: Conduct independent research before any investment decision

## Error Responses

```json
{
  "success": false,
  "error": "Invalid or unsupported ticker: XYZ",
  "processing_time_ms": 0
}
```

Common errors:
- Invalid ticker symbol
- Insufficient historical data
- Unsupported time horizon (short-term disabled in MVP)
