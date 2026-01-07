# ARCHITECTURE - Intraday Decision Support System

**Purpose**: Personal intraday trading assistant focused on VWAP + Volume detection

**Philosophy**: Deterministic, transparent, testable. No news scraping, no ML predictions.

---

## 🎯 SYSTEM GOAL

Answer one question: **"Should I care about this stock right now or not?"**

In 10 seconds or less.

---

## 🏗️ CORE ARCHITECTURE

```
┌─────────────────────────────────────────┐
│          USER (Login)                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      TODAY'S WATCH                       │
│  3-7 stocks, regime label, bias          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      STOCK DETAIL                        │
│  VWAP position, volume, risk note        │
└─────────────────────────────────────────┘
```

**Flow**: 3 screens max. No multi-tab dashboards.

---

## 📊 DATA FLOW

```
Yahoo Finance (5-min candles)
      ↓
Data Layer (fetch VWAP, volume, index)
      ↓
Method Layer (detect: Weak Trend, Extended Move, Portfolio Risk)
      ↓
Regime MCP (label: INDEX_LED_MOVE, LOW_LIQUIDITY_CHOP, etc.)
      ↓
Language Layer (plain English: "looks weak", "risk rising")
      ↓
Frontend (Today's Watch → Stock Detail)
```

**NO NEWS APIs**. **NO ML**. **NO PREDICTIONS**.

---

## 🔍 CORE METHOD: VWAP + VOLUME

### Method A: Trend Stress Detection
Triggers when ≥2 conditions met:
- Price below VWAP
- Underperforms index by >1%
- Red candles with volume
- Below moving averages

**Output**: `WEAK_TREND` tag

### Method B: Mean Reversion Detection
Triggers when ≥2 conditions met:
- Sharp move >2% intraday
- RSI extreme (<30 or >70)
- Near support/resistance

**Output**: `EXTENDED_MOVE` tag

### Method C: Portfolio Risk Detection
Triggers when ≥1 condition met:
- Position >25% of portfolio
- Multiple large holdings
- Driving >40% of daily P&L

**Output**: `PORTFOLIO_RISK` tag

---

## 🧠 MARKET REGIME CONTEXT (MCP)

**NOT news scraping**. Just regime labels based on data patterns.

### Regime Labels:
- `INDEX_LED_MOVE` - Moving with Nifty/BankNifty
- `LOW_LIQUIDITY_CHOP` - Dry volume, no direction
- `POST_LUNCH_VOLATILITY` - After 1:30 PM IST
- `EXPIRY_PRESSURE` - Near monthly expiry
- `SECTOR_BASKET_MOVE` - Sectoral rotation
- `PRE_MARKET_GAP` - Gap up/down at open
- `LAST_HOUR_VOLATILITY` - 2:30-3:30 PM IST

### Determined Using:
- Time of day (9:15 AM, 1:30 PM, 2:30 PM IST)
- Index correlation (^NSEI, ^NSEBANK)
- Volume patterns (expansion, dry, normal)
- Volatility expansion (Bollinger width, ATR)

**NO external news**. **NO sentiment APIs**.

---

## 🗂️ MODULE STRUCTURE

```
backend/
├── app/
│   ├── core/
│   │   ├── intraday/           ⭐ CORE SYSTEM
│   │   │   ├── data_layer.py       (fetch 5-min candles)
│   │   │   ├── method_layer.py     (VWAP+Volume detection)
│   │   │   ├── regime_mcp.py       (regime labels)
│   │   │   └── language_layer.py   (plain English)
│   │   │
│   │   ├── indicators/         (RSI, VWAP, SMA, EMA, MACD)
│   │   ├── auth/               (JWT authentication)
│   │   └── context_agent/      (simplified regime provider)
│   │
│   ├── mcp/                    (Yahoo Finance only)
│   │   ├── factory.py
│   │   └── yahoo_fundamentals.py
│   │
│   ├── api/v1/                 (REST endpoints)
│   │   ├── intraday_routes.py   ⭐ PRIMARY API
│   │   ├── portfolio.py
│   │   └── auth.py
│   │
│   └── config/
│       └── settings.py         (INTRADAY_MODE=True)
│
frontend/
├── app/
│   └── dashboard/
│       ├── page.tsx            (redirect to intraday)
│       ├── intraday/           ⭐ PRIMARY UI
│       │   └── page.tsx        (Today's Watch)
│       └── portfolio/
│
tests/
└── test_indicators.py          ✅ All passing
```

---

## 🔌 DATA PROVIDERS

### Current:
- **Yahoo Finance** - Free, unlimited, Indian & US stocks
  - Intraday OHLCV (5/15-min candles)
  - Fundamentals (PE, ROE, market cap)
  - Index data (^NSEI, ^NSEBANK)

### Removed (Jan 7, 2026):
- ❌ Alpha Vantage (rate limited, 25 req/day)
- ❌ Twelve Data (Indian stocks paywalled)
- ❌ News APIs (Moneycontrol, Reuters, RSS)

### Why Yahoo Only?
- Free forever
- No rate limits
- Indian stock support
- Good enough for personal use

---

## 🛡️ RISK CONSTRAINTS

### Hard Limits:
- ✅ **Max Confidence: 95%** (epistemic humility)
- ✅ **Min Actionable: 60%** (below that = "no edge")
- ✅ **No predictions** ("will hit", "target price" forbidden)
- ✅ **No directives** ("buy now", "sell immediately" forbidden)

### Language Rules:
✅ **Use**: "looks weak", "may increase", "if price stays below"
❌ **Never**: "buy", "sell", "now", "immediately", "will", "guaranteed"

---

## 📱 UI DESIGN PRINCIPLES

### Primary Workflow:
1. **Login** → See Today's Watch immediately
2. **Today's Watch** → 3-7 stocks with:
   - Regime label
   - Bias: Favorable / Risky / No Edge
   - One-line explanation
3. **Stock Detail** → VWAP, volume, regime, risk note

### NOT Included:
- ❌ Multi-tab dashboards
- ❌ Deep analysis pages by default
- ❌ Excessive charts
- ❌ Long-term scenario analysis

### Design Goal:
Answer "Should I care?" in **10 seconds**.

---

## 🧪 TESTING STRATEGY

### Unit Tests:
- `test_indicators.py` - RSI, VWAP, SMA calculations ✅
- `test_signals.py` - Signal generation logic ✅
- `test_intraday_system.py` - Method detection ⏳

### Integration Tests:
- Intraday API endpoints
- Portfolio P&L calculation
- Auth flow

### Manual Testing:
- UI flow: Login → Today's Watch → Detail
- Language compliance (no forbidden words)
- Regime label accuracy

---

## 🔒 SECURITY & COMPLIANCE

### Personal Use Only:
- ⚠️ **NOT SEBI-compliant** for distribution
- ⚠️ **NOT financial advice** (decision support)
- ⚠️ **Read-only** (no trade execution)

### Authentication:
- JWT-based tokens (15-min expiry)
- Supabase backend (PostgreSQL + RLS)
- User-specific portfolio isolation

---

## 📈 SCALABILITY

### Current Capacity:
- **1 user** (you)
- **10-20 stocks** monitored
- **~100 API calls/day** to Yahoo Finance
- **Local deployment** (no cloud costs)

### Not Designed For:
- ❌ Multiple users
- ❌ High-frequency trading
- ❌ Institutional scale
- ❌ Real-time tick data

---

## 🚀 DEPLOYMENT

### Current:
- **Backend**: Local (`http://localhost:8000`)
- **Frontend**: Local (`http://localhost:3000`)
- **Database**: Supabase (cloud)

### Production-Ready For:
- Personal use on local machine
- Single-user deployment
- VPS hosting (optional)

### NOT Ready For:
- Public SaaS
- Multi-tenant deployment
- High-availability requirements

---

## 🔮 FUTURE ENHANCEMENTS

### Maybe Later:
- Mobile app (React Native)
- Real-time WebSocket updates
- Backtesting engine
- More technical patterns (head & shoulders, triangles)

### NOT Planned:
- News scraping (removed by design)
- ML predictions (deterministic only)
- Automated trading (legal risk)
- Multi-market expansion (focus)

---

## 💡 DESIGN DECISIONS

### Why VWAP + Volume Only?
- Deterministic, reproducible
- Works on 1-day timeframe
- No history needed
- Testable with clear pass/fail

### Why No News?
- News = opinions = unreliable
- Regime labels sufficient
- Reduces complexity
- Fewer dependencies

### Why Intraday-First?
- Original goal: small daily profits
- Matches user's actual usage
- Honest positioning
- Better than pretending to be long-term platform

---

## ✅ SYSTEM STRENGTHS

1. **Transparent** - No black boxes, every rule visible
2. **Testable** - Deterministic thresholds, reproducible
3. **Fast** - Answers in seconds, not minutes
4. **Focused** - Does one thing well (intraday detection)
5. **Honest** - Matches real use case
6. **Maintainable** - Simple codebase, easy to debug
7. **Free** - No API costs, Yahoo Finance only

---

## ⚠️ SYSTEM LIMITATIONS

1. **Personal use only** - Not SEBI-compliant for distribution
2. **Delayed data** - 15-min delay typical (free tier)
3. **Intraday-focused** - Not for long-term investing
4. **Indian markets** - Optimized for NSE/BSE
5. **No automation** - Manual execution required
6. **Single user** - Not multi-tenant
7. **No real-time** - WebSocket not implemented

---

## 📖 RELATED DOCS

- `INTRADAY_QUICK_REFERENCE.md` - Quick command reference
- `REFACTORING_SUMMARY_JAN7.md` - What changed today
- `README.md` - Setup instructions

---

**Last Updated**: January 7, 2026
**Status**: Production-ready for personal use
**Philosophy**: Simple > Complex, Honest > Impressive
