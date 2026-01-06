# Intraday System - Quick Reference Card

## 🚀 Start System (30 seconds)

```bash
# Terminal 1: Backend
cd backend
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Test
python test_intraday_system.py
```

**URLs**:
- Frontend: http://localhost:3001/dashboard/intraday
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/intraday/health

---

## 📊 Detection Methods (3 Rules)

| Method | Tag | Triggers When | Example |
|--------|-----|---------------|---------|
| **Trend Stress** | `WEAK_TREND` | ≥2: Below VWAP, Underperforms index, Red candles, Below MAs | "Stock weaker than market" |
| **Mean Reversion** | `EXTENDED_MOVE` | ≥2: Sharp move >2%, RSI extreme, Near support/resistance | "Moved too far too fast" |
| **Portfolio Risk** | `PORTFOLIO_RISK` | ≥1: Position >25%, Multiple large holdings, Drives >40% P&L | "Too concentrated" |

---

## 🏷️ Market Contexts (7 Regimes)

| Context | When | Meaning |
|---------|------|---------|
| `INDEX_LED_MOVE` | Stock tracks index closely | "Following the crowd" |
| `LOW_LIQUIDITY_CHOP` | Volume <50% average | "Thin trading" |
| `POST_LUNCH_VOLATILITY` | 1:30-2:30 PM IST | "Afternoon session" |
| `EXPIRY_PRESSURE` | Thursdays (weekly/monthly) | "Options pressure" |
| `SECTOR_BASKET_MOVE` | Sector moves together | "Sector theme" |
| `PRE_MARKET_GAP` | Gap >2% from open | "Big gap move" |
| `LAST_HOUR_VOLATILITY` | 2:30-3:30 PM IST | "Closing volatility" |

---

## 🎨 Language Rules

### ✅ DO Use
- "looks weak"
- "may increase"
- "if price stays below"
- "consider"
- "appears to"

### ❌ NEVER Use
- "buy now"
- "sell immediately"
- "will hit"
- "must"
- "guaranteed"

---

## 🧪 Test Checklist

```bash
python test_intraday_system.py
```

Expected output:
```
✅ Test 1 passed: Trend stress detected
✅ Test 2 passed: Mean reversion detected
✅ Test 3 passed: Portfolio risk detected
✅ Test 4 passed: System works without MCP
✅ Test 5 passed: MCP doesn't modify signals
✅ Test 6 passed: No false positives
✅ Test 7 passed: Language is conditional
✅ ALL TESTS PASSED
```

---

## 📡 API Quick Reference

### Get Today's Watch
```bash
curl http://localhost:8000/api/v1/intraday/todays-watch
```

### Get Stock Detail
```bash
curl http://localhost:8000/api/v1/intraday/stock/RELIANCE.NS
```

### Health Check
```bash
curl http://localhost:8000/api/v1/intraday/health
```

---

## 🔧 Troubleshooting

| Issue | Fix |
|-------|-----|
| "No data for ticker" | Use format: `RELIANCE.NS` (not just `RELIANCE`) |
| "System unhealthy" | Check internet, Yahoo Finance may be down |
| "No stocks flagged" | Normal if market closed or no patterns |
| Frontend blank | Ensure backend running on port 8000 |

---

## 📁 File Locations

```
backend/app/core/intraday/
├── data_layer.py       # VWAP, volume, RSI
├── method_layer.py     # 3 detection methods
├── regime_mcp.py       # Market context (no news)
└── language_layer.py   # Conditional formatter

backend/app/api/v1/
└── intraday_routes.py  # API endpoints

frontend/components/
├── todays-watch-dashboard.tsx
└── intraday-stock-detail.tsx

frontend/app/dashboard/intraday/
├── page.tsx            # Homepage
└── [ticker]/page.tsx   # Detail page
```

---

## 🎯 Example Stocks to Try

Indian Stocks (NSE):
- `RELIANCE.NS`
- `TCS.NS`
- `INFY.NS`
- `HDFCBANK.NS`
- `ICICIBANK.NS`

US Stocks:
- `AAPL`
- `MSFT`
- `TSLA`

---

## ⚡ Performance

- **Response Time**: <2s per stock
- **Memory**: ~100MB
- **Data Refresh**: 5-min candles
- **Concurrent Users**: 50+

---

## 📊 Severity Levels

| Level | Color | Meaning | Example |
|-------|-------|---------|---------|
| **Alert** 🔴 | Red | ≥2 tags | Weak + Concentrated |
| **Caution** 🟡 | Yellow | 1 tag, many conditions | Extended move |
| **Watch** 🔵 | Blue | 1 tag, few conditions | Minor weakness |

---

## 💡 Pro Tips

1. **Best Time**: Use during market hours (9:15 AM - 3:30 PM IST)
2. **Refresh**: Re-check every 15-30 minutes for updates
3. **Context**: Always read the MCP badge for market regime
4. **Combine**: Use with portfolio weight for risk assessment
5. **Conditional**: Remember all notes are "if-then", not "do this"

---

## 🎓 Philosophy

> "This system detects patterns and provides context. It does not recommend trades or predict outcomes. All language is conditional to support YOUR decision-making process."

**You decide. Always.**

---

**Quick Start**: `python main.py` + `npm run dev` + Open browser → http://localhost:3001/dashboard/intraday

**Questions?** See `INTRADAY_IMPLEMENTATION_GUIDE.md` for full documentation.
