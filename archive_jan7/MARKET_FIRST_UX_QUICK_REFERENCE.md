# Market-First UX Quick Reference

## User Flow

```
LOGIN
  ↓
MARKET PULSE (/dashboard/pulse)
├─ Worth trading? YES → View Opportunities
│                 NO  → Stand Down Today
│
├─ VIEW OPPORTUNITIES → OPPORTUNITIES FEED (/dashboard/opportunities)
│  └─ Select ticker → ANALYSIS (/dashboard/analysis)
│     └─ Decision Header + Risk Zone + Actions
│
└─ STAND DOWN TODAY → Stand Down Banner
   └─ Resume Trading button
```

## API Endpoints

### GET /api/v1/market/pulse
**Returns:** Current market conditions
```json
{
  "regime": "trending",
  "index_bias": [
    {"name": "NIFTY", "bias": "Strong Bullish", "change_percent": 1.2},
    {"name": "BANKNIFTY", "bias": "Neutral", "change_percent": 0.3}
  ],
  "liquidity": "high",
  "summary": "Market showing strong trending behavior...",
  "worth_trading": true,
  "session_time": "mid_day",
  "timestamp": "2024-12-20T14:30:00Z"
}
```

### GET /api/v1/opportunities/feed
**Returns:** Pre-filtered actionable setups
```json
{
  "opportunities": [
    {
      "ticker": "RELIANCE",
      "setup_type": "vwap_bounce",
      "confidence": 75,
      "time_sensitivity": "today",
      "summary": "RELIANCE bouncing off VWAP with 2.1x volume",
      "mcp_context": {
        "price_vs_vwap": "At",
        "volume_ratio": 2.1,
        "index_alignment": "Aligned",
        "regime": "trending",
        "news_status": "positive"
      },
      "current_price": 2450.50,
      "target_price": 2499.01,
      "stop_loss": 2402.49,
      "bias": "bullish"
    }
  ],
  "market_regime": "trending",
  "total_scanned": 5,
  "filtered_by_confidence": 2,
  "timestamp": "2024-12-20T14:30:00Z"
}
```

## Frontend Pages

### /dashboard/pulse
**Purpose:** Is today worth trading?
**Components:**
- Regime strip (3 pills)
- Market summary card
- View Opportunities button
- Stand Down Today button

### /dashboard/opportunities
**Purpose:** What's actionable right now?
**Components:**
- Opportunity cards (grid)
- Confidence + time sensitivity badges
- MCP context bullets
- Analyze/Ignore actions

### /dashboard/analysis
**Purpose:** What are my specific options?
**New Components:**
- DecisionHeader (bias + confidence)
- RiskZone (stop loss + what can go wrong)
- PossibleActions (entry/exit/hold/avoid)

## Key Components

### DecisionHeader
```tsx
<DecisionHeader
  ticker="RELIANCE"
  bias="bullish"
  confidence={75}
  regime="trending"
  currentPrice={2450.50}
  timestamp="2024-12-20T14:30:00Z"
/>
```

### RiskZone
```tsx
<RiskZone
  stopLoss={2402.49}
  invalidationLevel={2380.00}
  worstCaseScenario="Market reverses, breaks support"
  riskFactors={[
    "Index divergence",
    "Volume drying up",
    "News event risk"
  ]}
/>
```

### PossibleActions
```tsx
<PossibleActions
  actions={[
    {
      type: "entry",
      label: "Enter Long",
      description: "Buy at current levels",
      conditions: ["Price > VWAP", "Volume > 1.5x"],
      enabled: true
    },
    {
      type: "hold",
      label: "Hold Position",
      description: "Maintain current exposure",
      conditions: ["Stop loss not hit"],
      enabled: true
    }
  ]}
  onActionSelect={(action) => console.log(action)}
/>
```

## Regime Types

| Regime | Description | Worth Trading? |
|--------|-------------|----------------|
| **trending** | Clear directional move | ✅ YES |
| **range-bound** | Oscillating in range | ⚠️ MAYBE |
| **choppy** | No clear direction | ❌ NO |
| **low-liquidity** | Thin volume | ❌ NO |

## Setup Types

| Setup | Description | Time Sensitivity |
|-------|-------------|------------------|
| **vwap_bounce** | Price bouncing off VWAP | Today |
| **vwap_rejection** | Price rejected at VWAP | Today |
| **breakout** | Breaking above resistance | Immediate |
| **breakdown** | Breaking below support | Immediate |
| **consolidation** | Range-bound consolidation | This week |

## Confidence Scoring

```typescript
BASE_CONFIDENCE = {
  vwap_bounce: 75,
  vwap_rejection: 75,
  breakout: 70,
  breakdown: 70,
  consolidation: 50
}

// Adjustments:
+ Volume > 2.0x:         +10
+ Volume > 1.5x:         +5
+ Index aligned:         +10
+ Index diverging:       -5
+ Choppy regime:         -15
+ Low liquidity regime:  -25

// Final: max(0, min(100, adjusted_confidence))
// Only show if confidence > 60%
```

## Stand Down Mode

**Set:**
```typescript
localStorage.setItem("stand_down_mode", "true");
```

**Check:**
```typescript
const isStandDown = localStorage.getItem("stand_down_mode") === "true";
```

**Clear:**
```typescript
localStorage.setItem("stand_down_mode", "false");
```

**Banner shows when:** stand_down_mode === "true"
**Button text:** "Resume Trading"

## Navigation Order

1. **Market Pulse** ← LANDING PAGE
2. Opportunities
3. Overview
4. Portfolio
5. Analysis
6. Legal

## Color Schemes

### Regime Colors
- **Trending:** Green (bg-green-100, border-green-300)
- **Range-bound:** Blue (bg-blue-100, border-blue-300)
- **Choppy:** Amber (bg-amber-100, border-amber-300)
- **Low-liquidity:** Red (bg-red-100, border-red-300)

### Confidence Colors
- **75-100%:** Green (strong)
- **55-74%:** Blue (moderate)
- **0-54%:** Amber (weak)

### Time Sensitivity Colors
- **Immediate:** Red + animate-pulse
- **Today:** Amber
- **This week:** Blue

## Testing Checklist

- [ ] Login redirects to /dashboard/pulse
- [ ] Market Pulse shows regime strip
- [ ] "View Opportunities" navigates to /dashboard/opportunities
- [ ] "Stand Down Today" shows banner
- [ ] Resume Trading clears banner
- [ ] Opportunities cards show confidence badges
- [ ] Ignore button hides card
- [ ] Analyze button navigates to /dashboard/analysis
- [ ] DecisionHeader shows bias icon
- [ ] RiskZone shows stop loss
- [ ] PossibleActions shows enabled actions
- [ ] Stand down banner persists across page loads
- [ ] Navigation shows active page indicator

## Common Issues

### Market Pulse shows fallback
**Cause:** MCP data unavailable
**Fix:** Check Alpha Vantage API key, retry

### Opportunities feed empty
**Cause:** All setups filtered (confidence < 60%)
**Fix:** Normal behavior, show empty state

### Stand down banner not persisting
**Cause:** localStorage not working
**Fix:** Check browser settings, use sessionStorage

### DecisionHeader confidence wrong
**Cause:** combined_score not mapped correctly
**Fix:** Ensure analysis.combined_score is 0-100

## File Locations

```
backend/
  app/api/v1/
    market_pulse.py       ← Market conditions endpoint
    opportunities.py      ← Opportunities scanner
    
frontend/
  app/dashboard/
    pulse/page.tsx        ← Market Pulse page
    opportunities/page.tsx ← Opportunities page
    analysis/page.tsx     ← Enhanced with new components
  components/
    DecisionHeader.tsx    ← Bias + confidence
    RiskZone.tsx          ← Stop loss + risks
    PossibleActions.tsx   ← Structured actions
  lib/
    api.ts                ← API types + functions
```

## Next Steps

1. **Wire Real Data:** Replace placeholder MCP data in opportunities scanner
2. **Test Edge Cases:** Empty states, stale data, errors
3. **Mobile Testing:** Responsive layouts on all pages
4. **Performance:** Add loading skeletons, optimize renders
5. **Tracking:** Add analytics events for user interactions

---

**Quick Start:**
```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev

# Test
1. Login
2. Should land on Market Pulse
3. Click "View Opportunities"
4. Click "Analyze" on a ticker
5. Verify DecisionHeader + RiskZone + Actions
```

**Documentation:** See MARKET_FIRST_UX_COMPLETE.md for full details
