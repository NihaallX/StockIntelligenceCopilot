# Phase 2D: Multi-Market Support Architecture

**Status**: Implementation Plan  
**Date**: January 2, 2026  
**Scope**: Ticker Search, INR Support, Indian Markets (NSE/BSE)

---

## 1. ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                       │
├─────────────────────────────────────────────────────────────┤
│  • Semantic Ticker Search (Dropdown)                        │
│  • Exchange Badges (NYSE/NASDAQ/NSE/BSE)                    │
│  • Currency Display ($/₹)                                    │
│  • Market Hours Indicator                                   │
│  • Country-Aware Analysis Screen                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   API LAYER (FastAPI)                       │
├─────────────────────────────────────────────────────────────┤
│  GET /api/v1/search/tickers?q={query}&country={US|IN}      │
│  GET /api/v1/markets/status?exchange={NSE|NYSE}             │
│  POST /api/v1/analyze (extended with currency/exchange)    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  DATA PROVIDER FACTORY                      │
├─────────────────────────────────────────────────────────────┤
│  • LiveUSMarketDataProvider (Alpha Vantage)                 │
│  • LiveIndianMarketDataProvider (Yahoo Finance)             │
│  • MockMarketDataProvider (Demo)                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   UNIFIED DATA MODEL                        │
├─────────────────────────────────────────────────────────────┤
│  MarketData:                                                │
│    - ticker: str                                            │
│    - exchange: Enum[NYSE, NASDAQ, NSE, BSE]                 │
│    - country: Enum[US, IN]                                  │
│    - currency: Enum[USD, INR]                               │
│    - prices: List[StockPrice]                               │
│    - fundamentals: Optional[StockFundamentals]              │
│    - data_source: str                                       │
│    - data_quality_warning: Optional[str]                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. DATA MODEL CHANGES

### 2.1 New Database Table: `ticker_metadata`

```sql
CREATE TABLE ticker_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(20) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    exchange VARCHAR(20) NOT NULL,  -- NYSE, NASDAQ, NSE, BSE
    country VARCHAR(2) NOT NULL,    -- US, IN
    currency VARCHAR(3) NOT NULL,   -- USD, INR
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap DECIMAL,
    is_active BOOLEAN DEFAULT true,
    data_provider VARCHAR(50),      -- alpha_vantage, yahoo_finance
    ticker_format VARCHAR(50),      -- RELIANCE.NS, RELIANCE.BO, AAPL
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(ticker, exchange)
);

-- Full-text search index
CREATE INDEX idx_ticker_search ON ticker_metadata 
    USING GIN(to_tsvector('english', ticker || ' ' || company_name));

-- Exchange filter index
CREATE INDEX idx_ticker_exchange ON ticker_metadata(exchange, is_active);

-- Country filter index
CREATE INDEX idx_ticker_country ON ticker_metadata(country, is_active);
```

### 2.2 Updated Schema: `MarketData`

```python
class MarketData(BaseModel):
    ticker: str
    company_name: str
    exchange: ExchangeEnum  # NEW
    country: CountryEnum    # NEW
    currency: CurrencyEnum  # NEW
    prices: List[StockPrice]
    fundamentals: Optional[StockFundamentals]
    last_updated: datetime
    data_source: str
    data_quality_warning: Optional[str]
```

### 2.3 Updated Schema: `PortfolioPosition`

```python
class PortfolioPosition(BaseModel):
    ticker: str
    exchange: ExchangeEnum       # NEW
    currency: CurrencyEnum       # NEW
    quantity: Decimal
    average_price: Decimal       # In native currency
    current_price: Decimal       # In native currency
    total_value: Decimal         # In native currency
    unrealized_pnl: Decimal      # In native currency
    unrealized_pnl_percent: float
```

---

## 3. TICKER SEARCH IMPLEMENTATION

### 3.1 Backend Endpoint

```python
@router.get("/search/tickers")
async def search_tickers(
    q: str = Query(..., min_length=1, max_length=50),
    country: Optional[CountryEnum] = None,
    exchange: Optional[ExchangeEnum] = None,
    limit: int = Query(default=10, le=50),
    current_user: dict = Depends(get_current_user)
) -> List[TickerSearchResult]:
    """
    Search tickers by symbol or company name.
    
    - Supports partial matches
    - Prioritizes exact ticker matches
    - Filters by country/exchange if provided
    """
    # Query ticker_metadata with full-text search
    # Return ranked results
```

### 3.2 Search Response

```json
{
  "results": [
    {
      "ticker": "RELIANCE",
      "company_name": "Reliance Industries Limited",
      "exchange": "NSE",
      "country": "IN",
      "currency": "INR",
      "sector": "Energy",
      "ticker_format": "RELIANCE.NS",
      "is_supported": true
    },
    {
      "ticker": "AAPL",
      "company_name": "Apple Inc.",
      "exchange": "NASDAQ",
      "country": "US",
      "currency": "USD",
      "sector": "Technology",
      "ticker_format": "AAPL",
      "is_supported": true
    }
  ],
  "total": 2,
  "query": "rel"
}
```

### 3.3 Frontend Search Component

```typescript
interface TickerSearchProps {
  onSelect: (ticker: TickerMetadata) => void;
  defaultCountry?: 'US' | 'IN';
}

const TickerSearch: React.FC<TickerSearchProps> = ({ onSelect, defaultCountry }) => {
  // Debounced search (300ms)
  // Keyboard navigation (↑ ↓ Enter Esc)
  // Group by country
  // Show exchange badges
  // Clear selection state
}
```

---

## 4. CURRENCY HANDLING

### 4.1 Display Rules

```typescript
const formatPrice = (price: number, currency: Currency): string => {
  if (currency === 'INR') {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(price);
  } else {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(price);
  }
};
```

### 4.2 Portfolio Currency Grouping

```json
{
  "portfolio_summary": {
    "positions": [
      {
        "currency": "USD",
        "total_value": 50000.00,
        "positions_count": 5,
        "unrealized_pnl": 2500.00
      },
      {
        "currency": "INR",
        "total_value": 500000.00,
        "positions_count": 3,
        "unrealized_pnl": 15000.00
      }
    ],
    "conversion_info": {
      "usd_to_inr": 83.50,
      "rate_date": "2026-01-02",
      "source": "RBI Reference Rate",
      "disclaimer": "Conversion rates are approximate and for reference only"
    }
  }
}
```

### 4.3 NO Silent Conversions

```python
# WRONG - Silent conversion
total_value = usd_value * fx_rate  # Hidden conversion

# RIGHT - Explicit grouping
portfolio_summary = {
    "usd_total": usd_value,
    "inr_total": inr_value,
    "approximate_inr_equivalent": {
        "value": usd_value * fx_rate,
        "rate": fx_rate,
        "disclaimer": "Approximate conversion using {source} rate"
    }
}
```

---

## 5. INDIAN MARKET DATA PROVIDER

### 5.1 Provider Architecture

```python
class LiveIndianMarketDataProvider(BaseMarketDataProvider):
    """
    Indian market data provider using Yahoo Finance.
    
    Supported:
    - NSE equities (*.NS format)
    - BSE equities (*.BO format)
    - Historical daily data
    - Current prices
    
    NOT Supported:
    - Intraday data
    - F&O contracts
    - Fundamental ratios (use technical only)
    """
    
    SUPPORTED_EXCHANGES = ["NSE", "BSE"]
    TICKER_FORMATS = {
        "NSE": "{ticker}.NS",
        "BSE": "{ticker}.BO"
    }
    
    def get_stock_data(self, ticker: str, exchange: str, lookback_days: int) -> MarketData:
        # Format ticker for Yahoo Finance
        # Fetch OHLCV data
        # Validate data quality
        # Return MarketData with INR currency
```

### 5.2 Ticker Format Handling

```python
def format_ticker_for_provider(ticker: str, exchange: str, provider: str) -> str:
    """
    Convert internal ticker to provider-specific format.
    
    Examples:
    - RELIANCE + NSE + yahoo -> RELIANCE.NS
    - RELIANCE + BSE + yahoo -> RELIANCE.BO
    - AAPL + NASDAQ + alpha_vantage -> AAPL
    """
    if provider == "yahoo_finance":
        if exchange == "NSE":
            return f"{ticker}.NS"
        elif exchange == "BSE":
            return f"{ticker}.BO"
    return ticker
```

### 5.3 Fundamentals Handling

```python
class IndianMarketData(MarketData):
    fundamentals: Optional[StockFundamentals] = None
    fundamentals_disclaimer: str = (
        "Fundamental data unavailable for Indian equities. "
        "Analysis based on technical indicators and scenario modeling only."
    )
```

---

## 6. MARKET HOURS & STATUS

### 6.1 Market Hours Service

```python
class MarketHoursService:
    """Track market open/closed status"""
    
    MARKET_HOURS = {
        "NYSE": {
            "timezone": "America/New_York",
            "open": "09:30",
            "close": "16:00",
            "days": [0, 1, 2, 3, 4]  # Mon-Fri
        },
        "NSE": {
            "timezone": "Asia/Kolkata",
            "open": "09:15",
            "close": "15:30",
            "days": [0, 1, 2, 3, 4]  # Mon-Fri
        }
    }
    
    @staticmethod
    def is_market_open(exchange: str) -> bool:
        """Check if market is currently open"""
        # Check timezone-aware current time
        # Check market hours
        # Check holidays (placeholder for now)
```

### 6.2 Frontend Market Status Badge

```tsx
<Badge color={isOpen ? "green" : "gray"}>
  {isOpen ? "Market Open" : "Market Closed"}
</Badge>
```

---

## 7. SAFETY & COMPLIANCE

### 7.1 Indian Market Disclaimers

```python
INDIAN_MARKET_DISCLAIMER = """
IMPORTANT NOTICE - Indian Market Data:
• Prices shown in INR (Indian Rupees)
• Data sourced from {provider}
• Fundamental analysis may be limited
• Market hours: 9:15 AM - 3:30 PM IST
• This is NOT SEBI-registered investment advice
• For educational purposes only
"""
```

### 7.2 Feature Flags

```python
# backend/app/config/settings.py

class Settings(BaseSettings):
    # Phase 2D Feature Flags
    ENABLE_INDIAN_MARKETS: bool = False  # Default OFF
    ENABLE_MULTI_CURRENCY: bool = False  # Default OFF
    SUPPORTED_EXCHANGES: list[str] = ["NYSE", "NASDAQ"]
    SUPPORTED_CURRENCIES: list[str] = ["USD"]
```

### 7.3 Validation Rules

```python
def validate_ticker_selection(
    ticker: str,
    exchange: str,
    country: str
) -> ValidationResult:
    """
    Validate ticker is supported before analysis.
    
    Checks:
    - Exchange enabled in settings
    - Currency supported
    - Data provider available
    - Ticker exists in metadata
    """
    if country == "IN" and not settings.ENABLE_INDIAN_MARKETS:
        raise UnsupportedMarketError(
            "Indian markets not enabled. "
            "Contact administrator to enable feature."
        )
```

---

## 8. UX STATES & ERROR HANDLING

### 8.1 Search States

```typescript
type SearchState = 
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success', results: TickerMetadata[] }
  | { status: 'error', message: string }
  | { status: 'no_results' };
```

### 8.2 Error Messages

```typescript
const ERROR_MESSAGES = {
  MARKET_NOT_SUPPORTED: "This market is not currently supported. Available: US equities.",
  TICKER_NOT_FOUND: "Ticker not found. Please select from dropdown.",
  DATA_UNAVAILABLE: "Market data unavailable for this ticker. Try another.",
  FUNDAMENTALS_MISSING: "Fundamental analysis unavailable. Technical analysis only.",
  MARKET_CLOSED: "Market is closed. Last price shown.",
};
```

---

## 9. ROLLOUT PLAN

### Phase 1: Search Infrastructure (Week 1)
- ✅ Create ticker_metadata table
- ✅ Seed US tickers (existing ~50 stocks)
- ✅ Build search endpoint
- ✅ Frontend dropdown component
- ✅ Testing with US tickers only

### Phase 2: Currency Support (Week 2)
- ✅ Add currency field to schemas
- ✅ Update display formatting
- ✅ Portfolio currency grouping
- ✅ FX rate service (read-only)

### Phase 3: Indian Markets - Alpha (Week 3)
- ⚠️ Feature flag OFF by default
- ✅ Seed top 50 NSE tickers
- ✅ LiveIndianMarketDataProvider
- ✅ Indian disclaimers
- ✅ Internal testing only

### Phase 4: Production Readiness (Week 4)
- ✅ Full ticker validation
- ✅ Market hours service
- ✅ Error handling polish
- ✅ Compliance review
- ✅ Documentation

### Phase 5: Controlled Rollout (Week 5+)
- 🚀 Enable for beta users
- 📊 Monitor data quality
- 🐛 Bug fixes
- 📈 Gradual expansion

---

## 10. EXAMPLE API FLOWS

### 10.1 US Stock Analysis (Unchanged)

```http
POST /api/v1/analyze
{
  "ticker": "AAPL",
  "exchange": "NASDAQ",
  "time_horizon": "long_term"
}

Response:
{
  "success": true,
  "insight": {
    "ticker": "AAPL",
    "exchange": "NASDAQ",
    "country": "US",
    "currency": "USD",
    "current_price": 185.50,
    "signal": "HOLD",
    ...
  }
}
```

### 10.2 Indian Stock Analysis (New)

```http
POST /api/v1/analyze
{
  "ticker": "RELIANCE",
  "exchange": "NSE",
  "time_horizon": "long_term"
}

Response:
{
  "success": true,
  "insight": {
    "ticker": "RELIANCE",
    "exchange": "NSE",
    "country": "IN",
    "currency": "INR",
    "current_price": 2450.75,
    "signal": "HOLD",
    "warnings": [
      "Fundamental data unavailable for Indian equities",
      "Analysis based on technical indicators only"
    ],
    ...
  }
}
```

---

## 11. NON-NEGOTIABLE CONSTRAINTS

### ❌ FORBIDDEN
- Free-text ticker input without validation
- Silent currency conversions
- Assuming US fundamentals apply to India
- Inflating confidence for Indian stocks
- Auto-enabling features without explicit flags
- Mixing currencies in single calculations

### ✅ REQUIRED
- Explicit ticker selection from dropdown
- Currency shown on every price
- Exchange badge on every ticker
- Data quality warnings for Indian stocks
- Feature flags for market enablement
- Clear disclaimers per jurisdiction

---

## 12. SUCCESS CRITERIA

### Technical
- ✅ Search returns results <200ms
- ✅ Keyboard navigation works
- ✅ No free-text ticker execution
- ✅ Currency never mixed silently
- ✅ Indian markets behind feature flag

### Safety
- ✅ All prices show currency
- ✅ All tickers show exchange
- ✅ Disclaimers visible
- ✅ Invalid selections blocked at UI

### Compliance
- ✅ SEBI disclaimer for Indian stocks
- ✅ SEC disclaimer unchanged
- ✅ Audit logs track market/currency
- ✅ No regulatory violations

---

**Implementation Priority**: Search → Currency → India (Gated)  
**Risk Level**: MEDIUM (new markets require careful validation)  
**Estimated Effort**: 3-4 weeks with testing  
**Dependencies**: Yahoo Finance API access, Ticker metadata seeding
