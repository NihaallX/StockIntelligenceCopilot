# Stock Intelligence Copilot - Module Reference

## 📦 Module Map

### 🎯 Core Modules Overview

```
app/core/
├── market_data/         → Data ingestion layer
├── indicators/          → Technical analysis calculations  
├── signals/             → Trading signal generation
├── risk/                → Risk assessment & constraints
├── explanation/         → Human-readable insights
└── orchestrator/        → Pipeline coordination
```

---

## 1️⃣ Market Data Provider

**Path**: `app/core/market_data/provider.py`

### Class: `MockMarketDataProvider`

#### Methods
```python
get_stock_data(ticker: str, lookback_days: int) -> MarketData
    """Fetch OHLCV and fundamental data for a ticker"""
    
is_valid_ticker(ticker: str) -> bool
    """Check if ticker is supported"""
```

#### Supported Tickers (MVP)
- AAPL, MSFT, GOOGL, TSLA, AMZN
- NVDA, META, JPM, V, WMT

#### Returns
- `MarketData` with:
  - List of `StockPrice` (OHLCV + timestamp)
  - `StockFundamentals` (company info, P/E, market cap)

---

## 2️⃣ Technical Indicators

**Path**: `app/core/indicators/calculator.py`

### Class: `IndicatorCalculator`

#### Main Method
```python
calculate_all(ticker: str, prices: List[StockPrice]) -> TechnicalIndicators
    """Calculate all technical indicators"""
    # Requires minimum 50 price points
```

#### Indicators Calculated
| Indicator | Type | Period | Description |
|-----------|------|--------|-------------|
| SMA 20 | Trend | 20 days | Simple Moving Average |
| SMA 50 | Trend | 50 days | Long-term trend |
| EMA 12 | Trend | 12 days | Exponential MA (fast) |
| EMA 26 | Trend | 26 days | Exponential MA (slow) |
| RSI | Momentum | 14 days | Relative Strength Index (0-100) |
| MACD | Momentum | 12/26/9 | Moving Average Convergence Divergence |
| Bollinger Bands | Volatility | 20d, 2σ | Upper, Middle, Lower bands |

#### Private Methods
```python
_sma(data: np.ndarray, period: int) -> float
_ema(data: np.ndarray, period: int) -> float
_rsi(data: np.ndarray, period: int) -> float
_macd(data: np.ndarray) -> (macd, signal, histogram)
_bollinger_bands(data: np.ndarray) -> (upper, middle, lower)
```

---

## 3️⃣ Signal Generator

**Path**: `app/core/signals/generator.py`

### Class: `SignalGenerator`

#### Main Method
```python
generate_signal(
    market_data: MarketData,
    indicators: TechnicalIndicators,
    time_horizon: TimeHorizon
) -> Signal
    """Generate bullish/bearish/neutral signal"""
```

#### Signal Logic
**Evaluates 4 categories**:
1. **MA Crossover** (Trend)
   - Bullish: SMA(20) > SMA(50)
   - Bearish: SMA(20) < SMA(50)
   - Weight: up to 0.3

2. **RSI** (Momentum)
   - Bullish: RSI < 30 (oversold)
   - Bearish: RSI > 70 (overbought)
   - Neutral: 30 ≤ RSI ≤ 70
   - Weight: up to 0.25

3. **MACD** (Trend + Momentum)
   - Bullish: MACD > Signal
   - Bearish: MACD < Signal
   - Weight: up to 0.25

4. **Bollinger Bands** (Volatility)
   - Bullish: Price < Lower Band
   - Bearish: Price > Upper Band
   - Neutral: Price within bands
   - Weight: up to 0.2

#### Confidence Calculation
```python
confidence = sum(agreeing_weights) / sum(all_weights)
confidence = min(confidence, 0.95)  # Epistemic humility cap
```

#### Signal Strength
- **Weak**: confidence < 0.6
- **Moderate**: 0.6 ≤ confidence < 0.75
- **Strong**: confidence ≥ 0.75

#### Private Methods
```python
_evaluate_indicators(indicators) -> Dict[str, (SignalType, weight, explanation)]
_aggregate_signals(signals_data) -> (SignalType, confidence)
_determine_strength(confidence) -> str
_build_reasoning(signals_data, final_signal, indicators) -> SignalReasoning
```

---

## 4️⃣ Risk Engine

**Path**: `app/core/risk/engine.py`

### Class: `RiskEngine`

#### Main Method
```python
assess_risk(
    signal: Signal,
    indicators: TechnicalIndicators,
    user_risk_tolerance: Literal["conservative", "moderate", "aggressive"]
) -> RiskAssessment
    """Evaluate risk and determine actionability"""
```

#### Risk Checks

| Check | Trigger | Risk Level |
|-------|---------|------------|
| **Low Confidence** | < 60% | HIGH |
| **Moderate Confidence** | < 70% | MODERATE |
| **High Volatility** | BB width > 15% | HIGH |
| **Moderate Volatility** | BB width > 10% | MODERATE |
| **Extreme RSI** | > 85 or < 15 | HIGH |
| **Mixed Signals** | ≥2 contradictions | MODERATE |
| **Short-term Mode** | Disabled in MVP | CRITICAL |
| **Limited Context** | Stock-only analysis | LOW |

#### Actionability Logic
```python
if signal == NEUTRAL:
    return False  # Never actionable

if risk == CRITICAL:
    return False  # Never actionable

if risk == HIGH:
    return user == "aggressive"  # Only aggressive

if risk == MODERATE:
    return user in ["moderate", "aggressive"]  # Not conservative

if risk == LOW:
    return True  # All users
```

#### Constraints Applied
- Confidence capped at 95%
- Mandatory disclaimers
- Position sizing reminders (1-2% per position)
- Independent verification requirement

#### Private Methods
```python
_check_confidence_threshold(signal) -> RiskFactor?
_check_volatility(indicators) -> RiskFactor?
_check_extreme_indicators(indicators) -> RiskFactor?
_check_contradictions(signal) -> RiskFactor?
_check_time_horizon(signal) -> RiskFactor?
_check_market_context(indicators) -> RiskFactor?
_aggregate_risk_level(risk_factors) -> RiskLevel
_determine_actionability(...) -> bool
_apply_constraints(signal, constraints_applied, warnings)
```

---

## 5️⃣ Explanation Generator

**Path**: `app/core/explanation/generator.py`

### Class: `ExplanationGenerator`

#### Main Method
```python
generate_insight(
    signal: Signal,
    risk_assessment: RiskAssessment,
    indicators: TechnicalIndicators,
    time_horizon: TimeHorizon
) -> Insight
    """Transform technical analysis into human-readable insight"""
```

#### Output Components

**1. Summary** (2-3 sentences)
- Plain language overview
- Key numbers (price, confidence, risk)
- Never implies certainty

**2. Key Points** (6-8 bullets with emojis)
- 📈/📉/➡️ Signal type
- ✓ Supporting factors (top 2)
- 🟢/🟡/🔴 Risk level
- ⚠️ Top risk factors (max 2)
- ✅/⛔ Actionability status
- ℹ️ Key limitation

**3. Recommendation**
```python
if signal == NEUTRAL:
    return "no_action"
    
if not actionable or confidence < 0.5:
    return "avoid"
    
if not actionable:
    return "monitor"
    
if risk in [CRITICAL, HIGH]:
    return "avoid"
    
if confidence >= 0.70 and actionable:
    return "consider"
    
else:
    return "monitor"
```

**4. Overall Confidence** (Risk-adjusted)
```python
penalty = {LOW: 0.0, MODERATE: 0.1, HIGH: 0.2, CRITICAL: 0.4}
adjusted = max(0.1, base_confidence - penalty)
return min(adjusted, 0.95)
```

#### Private Methods
```python
_generate_summary(signal, risk_assessment, indicators) -> str
_extract_key_points(signal, risk_assessment, indicators) -> List[str]
_determine_recommendation(signal, risk_assessment) -> str
_calculate_overall_confidence(signal, risk_assessment) -> float
```

---

## 6️⃣ Orchestrator

**Path**: `app/core/orchestrator/pipeline.py`

### Class: `InsightOrchestrator`

#### Main Method (Async)
```python
async def analyze_stock(request: AnalysisRequest) -> AnalysisResponse
    """Execute complete analysis pipeline"""
```

#### Pipeline Steps
```
1. Validate ticker → market_data_provider.is_valid_ticker()
2. Fetch data → market_data_provider.get_stock_data()
3. Calculate indicators → indicator_calculator.calculate_all()
   └─ Requires: 50+ days of data
4. Generate signal → signal_generator.generate_signal()
5. Assess risk → risk_engine.assess_risk()
6. Generate explanations → explanation_generator.generate_insight()
7. Package response → AnalysisResponse
   └─ Includes: processing_time_ms
```

#### Error Handling
- Invalid ticker → 400 error with message
- Insufficient data → Descriptive error
- Calculation failure → Graceful degradation
- Exception → Generic error + stack trace (dev only)

---

## 📊 Data Models Reference

**Path**: `app/models/schemas.py`

### Core Models

#### `StockPrice`
```python
timestamp: datetime
open: float (> 0)
high: float (> 0, >= low/open/close)
low: float (> 0)
close: float (> 0)
volume: int (≥ 0)
```

#### `TechnicalIndicators`
```python
ticker: str
timestamp: datetime
sma_20, sma_50: float?
ema_12, ema_26: float?
rsi: float? (0-100)
macd, macd_signal, macd_histogram: float?
bollinger_upper, bollinger_middle, bollinger_lower: float?
current_price: float
```

#### `Signal`
```python
ticker: str
timestamp: datetime
strength: SignalStrength
    ├─ signal_type: SignalType (bullish/bearish/neutral)
    ├─ confidence: float (0-1, capped at 0.95)
    └─ strength: str (weak/moderate/strong)
reasoning: SignalReasoning
    ├─ primary_factors: List[str]
    ├─ supporting_indicators: Dict[str, float]
    ├─ contradicting_factors: List[str]
    ├─ assumptions: List[str]
    └─ limitations: List[str]
time_horizon: TimeHorizon
```

#### `RiskAssessment`
```python
overall_risk: RiskLevel (low/moderate/high/critical)
risk_factors: List[RiskFactor]
    └─ RiskFactor:
        ├─ name: str
        ├─ level: RiskLevel
        ├─ description: str
        └─ mitigation: str?
is_actionable: bool
warnings: List[str]
constraints_applied: List[str]
```

#### `Insight`
```python
ticker: str
timestamp: datetime
signal: Signal
risk_assessment: RiskAssessment
technical_indicators: TechnicalIndicators
analysis_mode: TimeHorizon
recommendation: str (consider/monitor/avoid/no_action)
summary: str
key_points: List[str]
disclaimer: str
overall_confidence: float
```

---

## 🌐 API Routes

**Path**: `app/api/v1/stocks.py`

### Endpoints

#### `POST /api/v1/stocks/analyze`
```python
Request: AnalysisRequest
    ├─ ticker: str (uppercase, 1-5 chars)
    ├─ time_horizon: TimeHorizon (default: long_term)
    ├─ risk_tolerance: str (default: moderate)
    └─ lookback_days: int (30-365, default: 90)

Response: AnalysisResponse
    ├─ success: bool
    ├─ insight: Insight?
    ├─ error: str?
    └─ processing_time_ms: float
```

#### `GET /api/v1/stocks/supported-tickers`
```python
Response: Dict[str, str]
{
    "AAPL": {"name": "Apple Inc.", ...},
    "MSFT": {"name": "Microsoft Corporation", ...},
    ...
}
```

---

## ⚙️ Configuration

**Path**: `app/config/settings.py`

### Settings Class
```python
# API
API_V1_PREFIX: str = "/api/v1"
PROJECT_NAME: str = "Stock Intelligence Copilot"
VERSION: str = "0.1.0"

# Risk Engine
MAX_CONFIDENCE_THRESHOLD: float = 0.95
MIN_ACTIONABLE_CONFIDENCE: float = 0.60
DEFAULT_RISK_TOLERANCE: str = "moderate"

# Signals
LONG_TERM_MODE: bool = True
SHORT_TERM_ENABLED: bool = False

# Data
DEFAULT_LOOKBACK_DAYS: int = 90

# Compliance
DISCLAIMER: str = "This is not financial advice..."
```

---

## 🧪 Testing Reference

**Path**: `backend/tests/`

### Test Files

#### `test_indicators.py`
- `test_calculate_indicators_success()`
- `test_calculate_indicators_insufficient_data()`
- `test_rsi_bounds()`
- `test_bollinger_bands_order()`

#### `test_signals.py`
- `test_bullish_signal_generation()`
- `test_bearish_signal_generation()`
- `test_confidence_cap()`

#### `test_risk.py`
- `test_high_confidence_signal_passes()`
- `test_low_confidence_signal_blocked()`
- `test_high_volatility_risk()`
- `test_extreme_rsi_risk()`
- `test_conservative_user_blocks_high_risk()`
- `test_neutral_signal_not_actionable()`

### Run Tests
```bash
cd backend
pytest tests/ -v
pytest tests/test_indicators.py -v
pytest --cov=app --cov-report=html
```

---

## 🔄 Data Flow Summary

```
User Request (ticker, params)
    ↓
API Layer (validation)
    ↓
Orchestrator
    ↓
┌───────────────────────────────────────┐
│ 1. Market Data Provider               │
│    → Returns: OHLCV + Fundamentals    │
└─────────────┬─────────────────────────┘
              ↓
┌───────────────────────────────────────┐
│ 2. Indicator Calculator               │
│    → Returns: SMA, RSI, MACD, BB      │
└─────────────┬─────────────────────────┘
              ↓
┌───────────────────────────────────────┐
│ 3. Signal Generator                   │
│    → Returns: Signal + Reasoning      │
└─────────────┬─────────────────────────┘
              ↓
┌───────────────────────────────────────┐
│ 4. Risk Engine                        │
│    → Returns: Risk Assessment         │
└─────────────┬─────────────────────────┘
              ↓
┌───────────────────────────────────────┐
│ 5. Explanation Generator              │
│    → Returns: Complete Insight        │
└─────────────┬─────────────────────────┘
              ↓
Orchestrator (packages response)
    ↓
API Layer (JSON serialization)
    ↓
User Response (Insight + metadata)
```

---

## 📝 Quick Import Reference

```python
# Market Data
from app.core.market_data import market_data_provider

# Indicators
from app.core.indicators import indicator_calculator

# Signals
from app.core.signals import signal_generator

# Risk
from app.core.risk import risk_engine

# Explanation
from app.core.explanation import explanation_generator

# Orchestrator
from app.core.orchestrator import orchestrator

# Models
from app.models.schemas import (
    AnalysisRequest, AnalysisResponse,
    Signal, SignalType, RiskLevel,
    TechnicalIndicators, Insight
)

# Config
from app.config import settings
```

---

## 🎯 Module Dependencies

```
orchestrator
    ├─ depends on: ALL modules
    └─ used by: API layer

explanation_generator
    ├─ depends on: models
    └─ used by: orchestrator

risk_engine
    ├─ depends on: models, config
    └─ used by: orchestrator

signal_generator
    ├─ depends on: models
    └─ used by: orchestrator

indicator_calculator
    ├─ depends on: models, numpy
    └─ used by: orchestrator

market_data_provider
    ├─ depends on: models
    └─ used by: orchestrator

models (schemas)
    ├─ depends on: pydantic
    └─ used by: ALL modules

config (settings)
    ├─ depends on: pydantic-settings
    └─ used by: risk_engine, api
```

---

**✨ This reference guide covers all core modules, methods, and data flows in the Stock Intelligence Copilot MVP.**
