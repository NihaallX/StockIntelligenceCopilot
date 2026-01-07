# Stock Intelligence Copilot - Architecture Documentation

## System Overview

**Purpose**: AI-assisted stock market analysis for retail investors  
**Architecture**: Modular, pipeline-based backend  
**Technology Stack**: Python 3.11+, FastAPI, NumPy, Pydantic  
**Deployment Model**: REST API (backend-only MVP)

## Design Principles

### 1. Safety First
- No trade execution capabilities
- Probabilistic outputs only (never certainty)
- Confidence capped at 95%
- Deterministic risk engine
- "No action" is a valid and encouraged outcome

### 2. Explainability
- Every signal has clear reasoning
- Assumptions explicitly stated
- Limitations acknowledged
- Human-readable summaries
- LLM-friendly structured output

### 3. Modularity
- Single Responsibility Principle per module
- Loose coupling between components
- Easy to test in isolation
- Simple to replace/upgrade components

### 4. Compliance-Aware
- Built-in disclaimers
- Risk warnings
- Conservative defaults
- Audit trail ready

## Module Architecture

### Data Flow
```
Request → Orchestrator → [Market Data → Indicators → Signals → Risk → Explanation] → Response
```

### Core Modules

#### 1. Market Data Provider (`market_data/`)
**Purpose**: Fetch and normalize stock data

**MVP Implementation**: Mock data generator
- 10 pre-defined stocks (AAPL, MSFT, etc.)
- Generates realistic OHLCV data
- Includes fundamental data (P/E, market cap)
- Seeded for reproducibility

**Production Path**:
- Integrate Yahoo Finance API
- Add Alpha Vantage support
- Polygon.io for real-time data
- Redis caching layer

**Interface**:
```python
def get_stock_data(ticker: str, lookback_days: int) -> MarketData
```

---

#### 2. Technical Indicators (`indicators/`)
**Purpose**: Calculate technical indicators from price data

**Indicators Implemented**:
- **Trend**: SMA (20, 50), EMA (12, 26)
- **Momentum**: RSI (14), MACD
- **Volatility**: Bollinger Bands (20, 2σ)

**Algorithm Notes**:
- RSI uses standard 14-period calculation
- MACD: 12/26/9 periods (industry standard)
- Bollinger: 2 standard deviations

**Future Enhancements**:
- Volume-weighted indicators (VWAP)
- Stochastic oscillator
- ADX (trend strength)
- Fibonacci retracements

**Interface**:
```python
def calculate_all(ticker: str, prices: List[StockPrice]) -> TechnicalIndicators
```

---

#### 3. Signal Generator (`signals/`)
**Purpose**: Generate buy/sell/hold signals from indicators

**Logic**:
- Rule-based evaluation (no ML in MVP)
- Each indicator votes with weighted score
- Bullish/bearish/neutral aggregation
- Confidence = weighted agreement
- Contradicting factors reduce confidence

**Signal Rules**:
- **MA Crossover**: SMA(20) vs SMA(50)
- **RSI**: <30 = oversold, >70 = overbought
- **MACD**: Crossover with signal line
- **Bollinger**: Price vs bands (mean reversion)

**Confidence Calculation**:
```
confidence = agreeing_weight / total_weight
confidence = min(confidence, 0.95)  # Epistemic humility
```

**Future Enhancements**:
- ML-based signal refinement
- Sentiment analysis integration
- Pattern recognition (head-and-shoulders, etc.)

**Interface**:
```python
def generate_signal(
    market_data: MarketData,
    indicators: TechnicalIndicators,
    time_horizon: TimeHorizon
) -> Signal
```

---

#### 4. Risk Engine (`risk/`)
**Purpose**: Assess risk and enforce safety constraints

**Risk Factors Evaluated**:
1. **Confidence Threshold**: Below 60% = high risk
2. **Volatility**: Bollinger width >15% = high risk
3. **Extreme Indicators**: RSI >85 or <15 = high risk
4. **Mixed Signals**: Multiple contradictions = moderate risk
5. **Time Horizon**: Short-term disabled in MVP = critical risk
6. **Market Context**: Individual stock only = low risk (reminder)

**Actionability Logic**:
- Neutral signals → never actionable
- Critical risk → never actionable
- High risk → aggressive users only
- Moderate risk → moderate/aggressive users
- Low risk → all users

**User Risk Profiles**:
- **Conservative**: Only low-risk signals
- **Moderate**: Low + moderate risk
- **Aggressive**: All except critical

**Constraints Applied**:
- Confidence never >95%
- Mandatory disclaimers
- Position sizing reminders
- Independent verification requirement

**Interface**:
```python
def assess_risk(
    signal: Signal,
    indicators: TechnicalIndicators,
    user_risk_tolerance: str
) -> RiskAssessment
```

---

#### 5. Explanation Generator (`explanation/`)
**Purpose**: Transform technical signals into human-readable insights

**Output Components**:
- **Summary**: Plain-language overview (2-3 sentences)
- **Key Points**: Bullet list (6-8 points with emojis)
- **Recommendation**: consider/monitor/avoid/no_action
- **Overall Confidence**: Risk-adjusted confidence

**Language Guidelines**:
- No jargon unless necessary
- Always probabilistic ("may", "suggests", "indicates")
- Never guaranteed ("will", "must", "certain")
- Acknowledge uncertainty

**Recommendation Logic**:
```
if neutral → no_action
if not actionable → monitor or avoid
if critical/high risk → avoid
if confidence ≥ 70% and actionable → consider
else → monitor
```

**Interface**:
```python
def generate_insight(
    signal: Signal,
    risk_assessment: RiskAssessment,
    indicators: TechnicalIndicators,
    time_horizon: TimeHorizon
) -> Insight
```

---

#### 6. Orchestrator (`orchestrator/`)
**Purpose**: Coordinate the entire analysis pipeline

**Pipeline Steps**:
1. Validate ticker
2. Fetch market data
3. Calculate indicators (requires 50+ days)
4. Generate signal
5. Assess risk
6. Generate explanations
7. Package insight

**Error Handling**:
- Invalid ticker → 400 error
- Insufficient data → informative message
- Calculation errors → graceful degradation
- Processing time tracked

**Interface**:
```python
async def analyze_stock(request: AnalysisRequest) -> AnalysisResponse
```

---

## API Layer

### Endpoints

#### `POST /api/v1/stocks/analyze`
Main analysis endpoint

**Request**:
```json
{
  "ticker": "AAPL",
  "time_horizon": "long_term",
  "risk_tolerance": "moderate",
  "lookback_days": 90
}
```

**Response**: Complete `Insight` object

#### `GET /api/v1/stocks/supported-tickers`
Returns mock tickers (MVP only)

#### `GET /health`
Health check

#### `GET /`
API info + disclaimer

---

## Data Models (Pydantic)

### Key Models
- `StockPrice`: OHLCV data point
- `MarketData`: Complete stock data package
- `TechnicalIndicators`: Calculated indicator values
- `Signal`: Trading signal with reasoning
- `RiskAssessment`: Risk evaluation results
- `Insight`: Complete analysis package

### Validation
- Price values > 0
- High ≥ Low, Open, Close
- RSI bounded [0, 100]
- Confidence bounded [0, 1]
- Ticker pattern: 1-5 uppercase letters

---

## Testing Strategy

### Unit Tests
- `test_indicators.py`: Indicator calculations
- `test_signals.py`: Signal generation logic
- `test_risk.py`: Risk assessment rules

### Test Approach
- Mock data for reproducibility
- Boundary condition testing
- Edge case coverage (extreme values)
- Integration tests (pipeline)

### Run Tests
```bash
cd backend
pytest tests/ -v
```

---

## Configuration

### Settings (`config/settings.py`)
- API version and prefix
- Risk thresholds
- Default parameters
- Feature flags (short-term disabled)
- Disclaimers

### Environment Variables
See `.env.example`

---

## Deployment Considerations

### MVP Deployment
- Single server sufficient
- No database required (stateless)
- Can run on Heroku/Railway/Render
- Docker-ready

### Production Requirements
- Load balancer
- Redis for caching
- PostgreSQL for audit logs
- Real-time data streaming
- Rate limiting
- Authentication/Authorization

### Scalability
- Stateless design = horizontal scaling
- Cache indicator calculations
- Async processing for bulk requests
- WebSocket for real-time updates

---

## Security & Compliance

### MVP Considerations
- Read-only by design
- No user data stored
- No PII collected
- Disclaimer on all responses

### Production Requirements
- User authentication
- Audit logging
- Rate limiting (prevent abuse)
- HTTPS only
- Data encryption at rest
- Compliance review (FINRA, SEC)

### Legal Disclaimers
- Not financial advice
- No guarantees of accuracy
- Past performance ≠ future results
- User assumes all risk

---

## Future Enhancements

### Phase 2
- Real market data integration
- User accounts and portfolios
- Historical backtest results
- Email/SMS alerts

### Phase 3
- Machine learning signal refinement
- News sentiment analysis
- Sector/market correlation
- Options analysis

### Phase 4
- Multi-asset support (crypto, forex)
- Portfolio optimization
- Paper trading simulator
- Social features (shared insights)

---

## Maintenance

### Monitoring
- API response times
- Error rates
- Signal accuracy (backtest)
- User feedback

### Updates
- Indicator library expansion
- Risk rule refinement
- Model retraining (if ML added)
- Market data source rotation

---

## Development Guidelines

### Code Style
- Black formatter
- Flake8 linting
- Type hints everywhere
- Docstrings for public methods

### Git Workflow
- Feature branches
- PR reviews required
- Semantic versioning
- Changelog maintained

### Documentation
- Inline comments for complex logic
- Module docstrings
- API documentation (OpenAPI)
- Architecture updates (this doc)

---

## Questions for Phase 2

1. Which real market data provider to integrate?
2. Should we add user authentication?
3. Database for storing analysis history?
4. Caching strategy for indicators?
5. Rate limiting approach?
6. Frontend framework choice?
7. Deployment platform?
8. Compliance review requirements?
