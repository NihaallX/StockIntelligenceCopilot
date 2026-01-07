# Stock Intelligence Copilot - System Diagram

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│  (HTTP Client, Browser, cURL, Python requests, etc.)            │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/JSON
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       FASTAPI SERVER                             │
│                    (Port 8000, Uvicorn)                          │
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐               │
│  │   /health  │  │ /supported │  │  /analyze  │               │
│  │            │  │  -tickers  │  │   (POST)   │               │
│  └────────────┘  └────────────┘  └──────┬─────┘               │
│                                          │                       │
└──────────────────────────────────────────┼───────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR LAYER                            │
│              (Pipeline Coordination & Error Handling)            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. Validate Request → 2. Fetch Data → 3. Calculate     │  │
│  │  → 4. Generate Signal → 5. Assess Risk → 6. Explain     │  │
│  └──────────────────────────────────────────────────────────┘  │
└───┬────────────┬────────────┬────────────┬────────────┬────────┘
    │            │            │            │            │
    ▼            ▼            ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ Market  │  │Technical│  │ Signal  │  │  Risk   │  │Explain- │
│  Data   │→ │Indica-  │→ │Genera-  │→ │ Assess- │→ │ ation   │
│Provider │  │tors     │  │tor      │  │ment     │  │Generator│
└─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ USER REQUEST                                                     │
│ {                                                                │
│   "ticker": "AAPL",                                              │
│   "time_horizon": "long_term",                                   │
│   "risk_tolerance": "moderate"                                   │
│ }                                                                │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Market Data Provider                                     │
│                                                                  │
│ Input:  ticker="AAPL", lookback_days=90                         │
│ Output: MarketData                                               │
│         ├─ prices: List[StockPrice] (90 days OHLCV)            │
│         └─ fundamentals: StockFundamentals                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Technical Indicators Calculator                          │
│                                                                  │
│ Input:  MarketData.prices                                        │
│ Output: TechnicalIndicators                                      │
│         ├─ sma_20, sma_50                                       │
│         ├─ ema_12, ema_26                                       │
│         ├─ rsi (0-100)                                          │
│         ├─ macd, macd_signal, macd_histogram                   │
│         └─ bollinger_upper, bollinger_middle, bollinger_lower  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Signal Generator                                         │
│                                                                  │
│ Input:  MarketData + TechnicalIndicators                        │
│                                                                  │
│ Process:                                                         │
│  ┌─────────────────────────────────────────────┐               │
│  │ Evaluate Each Indicator:                    │               │
│  │ • MA Crossover  → Vote + Weight             │               │
│  │ • RSI Level     → Vote + Weight             │               │
│  │ • MACD Position → Vote + Weight             │               │
│  │ • Bollinger     → Vote + Weight             │               │
│  │                                              │               │
│  │ Aggregate:                                   │               │
│  │ • Bullish Score = Σ(bullish weights)        │               │
│  │ • Bearish Score = Σ(bearish weights)        │               │
│  │ • Confidence = dominant / total              │               │
│  │ • Confidence = min(confidence, 0.95)  ⚠️    │               │
│  └─────────────────────────────────────────────┘               │
│                                                                  │
│ Output: Signal                                                   │
│         ├─ signal_type: bullish/bearish/neutral                │
│         ├─ confidence: 0.0 - 0.95                              │
│         ├─ strength: weak/moderate/strong                      │
│         └─ reasoning: detailed explanation                     │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Risk Engine                                              │
│                                                                  │
│ Input:  Signal + TechnicalIndicators + user_risk_tolerance     │
│                                                                  │
│ Process:                                                         │
│  ┌─────────────────────────────────────────────┐               │
│  │ Run Risk Checks:                            │               │
│  │ ✓ Confidence threshold                     │               │
│  │ ✓ Volatility (Bollinger width)             │               │
│  │ ✓ Extreme indicators (RSI >85 or <15)      │               │
│  │ ✓ Contradicting signals                    │               │
│  │ ✓ Time horizon restrictions                │               │
│  │ ✓ Market context limitations               │               │
│  │                                              │               │
│  │ Determine Actionability:                    │               │
│  │ • If neutral → NOT actionable              │               │
│  │ • If critical risk → NOT actionable        │               │
│  │ • If high risk → aggressive only           │               │
│  │ • If moderate → moderate/aggressive        │               │
│  │ • If low → all users                       │               │
│  └─────────────────────────────────────────────┘               │
│                                                                  │
│ Output: RiskAssessment                                           │
│         ├─ overall_risk: low/moderate/high/critical            │
│         ├─ risk_factors: List[RiskFactor]                      │
│         ├─ is_actionable: bool                                 │
│         ├─ warnings: List[str]                                 │
│         └─ constraints_applied: List[str]                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Explanation Generator                                    │
│                                                                  │
│ Input:  Signal + RiskAssessment + TechnicalIndicators          │
│                                                                  │
│ Process:                                                         │
│  ┌─────────────────────────────────────────────┐               │
│  │ Generate Plain Language:                    │               │
│  │ • Summary (2-3 sentences)                   │               │
│  │ • Key points (6-8 bullets with emojis)      │               │
│  │ • Recommendation (consider/monitor/avoid)   │               │
│  │ • Overall confidence (risk-adjusted)        │               │
│  │ • Mandatory disclaimer                      │               │
│  └─────────────────────────────────────────────┘               │
│                                                                  │
│ Output: Insight                                                  │
│         ├─ signal: Signal                                       │
│         ├─ risk_assessment: RiskAssessment                     │
│         ├─ technical_indicators: TechnicalIndicators           │
│         ├─ recommendation: str                                  │
│         ├─ summary: str                                         │
│         ├─ key_points: List[str]                               │
│         ├─ disclaimer: str                                      │
│         └─ overall_confidence: float                           │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ RESPONSE TO USER                                                 │
│ {                                                                │
│   "success": true,                                               │
│   "insight": { ... },                                            │
│   "processing_time_ms": 42.5                                     │
│ }                                                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Signal Generation Logic

```
                    ┌──────────────────┐
                    │  Raw Price Data   │
                    │   (OHLCV x 90)    │
                    └────────┬──────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ MA Crossover │ │   RSI Level  │ │     MACD     │
    │              │ │              │ │              │
    │ SMA20 > 50?  │ │  < 30 = Buy  │ │  Line > Sig? │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           ▼                ▼                ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │Vote: BULLISH │ │Vote: BULLISH │ │Vote: BEARISH │
    │Weight: 0.25  │ │Weight: 0.20  │ │Weight: 0.15  │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           └────────────────┼────────────────┘
                            │
                            ▼
                    ┌──────────────────┐
                    │   Aggregation    │
                    │                  │
                    │ Bullish: 0.45    │
                    │ Bearish: 0.15    │
                    │ Neutral: 0.05    │
                    │                  │
                    │ Winner: BULLISH  │
                    │ Confidence: 69%  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Confidence Cap  │
                    │  min(0.69, 0.95) │
                    │  = 0.69 ✓        │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Final Signal    │
                    │                  │
                    │ Type: BULLISH    │
                    │ Confidence: 0.69 │
                    │ Strength: MODERATE│
                    └──────────────────┘
```

---

## 🛡️ Risk Assessment Flow

```
                    ┌──────────────────┐
                    │      Signal      │
                    │  (with reasoning)│
                    └────────┬─────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │ Confidence  │  │ Volatility  │  │  Extreme    │
    │   Check     │  │   Check     │  │ Indicators  │
    │             │  │             │  │             │
    │ < 60%? HIGH │  │BB >15%? HIGH│  │RSI >85? HIGH│
    └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
           │                │                │
           └────────────────┼────────────────┘
                            │
                            ▼
                    ┌──────────────────┐
                    │  Risk Factors    │
                    │  Collection      │
                    │                  │
                    │  [MODERATE, LOW, │
                    │   MODERATE]      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Aggregate      │
                    │  (Take Highest)  │
                    │                  │
                    │ Result: MODERATE │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Actionability   │
                    │  Determination   │
                    │                  │
                    │  Risk: MODERATE  │
                    │  User: MODERATE  │
                    │  → ACTIONABLE ✓  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Risk Assessment  │
                    │                  │
                    │ ✓ Risk: MODERATE │
                    │ ✓ Actionable: YES│
                    │ ✓ Warnings: [2]  │
                    └──────────────────┘
```

---

## 📦 Module Dependencies

```
                    ┌──────────────────┐
                    │   Orchestrator   │
                    │  (Pipeline Core) │
                    └────────┬─────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Market Data  │ │  Indicators  │ │    Signals   │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           │     ┌──────────┼────────┐      │
           │     ▼          ▼        ▼      │
           │  ┌────────┐ ┌────────┐ ┌────────┐
           │  │  Risk  │ │Explain-│ │ Models │
           │  │ Engine │ │ation   │ │(Schemas)│
           │  └────┬───┘ └────┬───┘ └────┬───┘
           │       │          │          │
           └───────┼──────────┼──────────┘
                   │          │
                   └────┬─────┘
                        │
                        ▼
                 ┌────────────┐
                 │   Config   │
                 │ (Settings) │
                 └────────────┘
```

---

## 🎯 Signal Confidence Scale

```
0%                                                    100%
│─────────────┼─────────────┼─────────────┼──────────│
0.0         0.60          0.75          0.95        1.0
             │             │             │
             │             │             │
        ┌────┴────┐   ┌────┴────┐  ┌────┴────┐
        │  WEAK   │   │MODERATE │  │ STRONG  │
        │ < 60%   │   │ 60-75%  │  │  > 75%  │
        │         │   │         │  │         │
        │ Monitor │   │Consider │  │Consider │
        │  Only   │   │w/Caution│  │ Strongly│
        └─────────┘   └─────────┘  └─────────┘

Note: Confidence is ALWAYS capped at 95% (never reaches 100%)
```

---

## 🚦 Risk → Actionability Matrix

```
                        USER RISK TOLERANCE
                  ┌──────────┬──────────┬──────────┐
                  │Conservative│Moderate│Aggressive│
┌─────────────────┼──────────┼──────────┼──────────┤
│ RISK: CRITICAL  │    ❌    │    ❌    │    ❌    │
│ (System Block)  │          │          │          │
├─────────────────┼──────────┼──────────┼──────────┤
│ RISK: HIGH      │    ❌    │    ❌    │    ✅    │
│ (High Volatility│          │          │          │
│  Extreme RSI)   │          │          │          │
├─────────────────┼──────────┼──────────┼──────────┤
│ RISK: MODERATE  │    ❌    │    ✅    │    ✅    │
│ (Some concerns) │          │          │          │
├─────────────────┼──────────┼──────────┼──────────┤
│ RISK: LOW       │    ✅    │    ✅    │    ✅    │
│ (Clear signal)  │          │          │          │
└─────────────────┴──────────┴──────────┴──────────┘

✅ = Actionable (can consider)
❌ = Not Actionable (monitor only)
```

---

## 📈 Example Analysis Flow (AAPL)

```
1️⃣ REQUEST
   ┌─────────────────────────┐
   │ ticker: "AAPL"          │
   │ risk_tolerance: moderate│
   └────────┬────────────────┘
            ▼

2️⃣ FETCH DATA
   ┌─────────────────────────┐
   │ 90 days OHLCV           │
   │ Price: $145-$180        │
   │ Volume: 50M avg         │
   │ Fundamentals: P/E=28    │
   └────────┬────────────────┘
            ▼

3️⃣ CALCULATE INDICATORS
   ┌─────────────────────────┐
   │ SMA(20): $175.20        │
   │ SMA(50): $168.40        │
   │ RSI: 52.3 (neutral)     │
   │ MACD: 1.2 (positive)    │
   │ BB: $165-$185           │
   └────────┬────────────────┘
            ▼

4️⃣ GENERATE SIGNAL
   ┌─────────────────────────┐
   │ MA: Bullish (SMA20>50) │
   │ RSI: Neutral (50-70)    │
   │ MACD: Bullish (>signal) │
   │ BB: Neutral (in range)  │
   │                         │
   │ → BULLISH (72% conf)   │
   └────────┬────────────────┘
            ▼

5️⃣ ASSESS RISK
   ┌─────────────────────────┐
   │ Confidence: ✓ (>60%)   │
   │ Volatility: ✓ (normal)  │
   │ RSI: ✓ (not extreme)    │
   │                         │
   │ → MODERATE RISK        │
   │ → ACTIONABLE ✓         │
   └────────┬────────────────┘
            ▼

6️⃣ EXPLAIN
   ┌─────────────────────────┐
   │ Summary: "AAPL exhibits │
   │ moderate bullish signal"│
   │                         │
   │ Recommendation:         │
   │ → CONSIDER             │
   │                         │
   │ Confidence: 69%         │
   │ (72% - 3% risk penalty) │
   └────────┬────────────────┘
            ▼

7️⃣ RESPONSE
   ┌─────────────────────────┐
   │ success: true           │
   │ insight: { ... }        │
   │ processing_time: 45ms   │
   └─────────────────────────┘
```

---

## 🔐 Safety Layers

```
┌─────────────────────────────────────────────────────┐
│                  USER REQUEST                        │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
            ┌────────────────┐
            │  INPUT LAYER   │
            │  ✓ Validation  │
            │  ✓ Sanitization│
            └────────┬───────┘
                     │
                     ▼
            ┌────────────────┐
            │ ANALYSIS LAYER │
            │  ✓ Indicators  │
            │  ✓ Signals     │
            └────────┬───────┘
                     │
                     ▼
            ┌────────────────┐
            │   RISK LAYER   │
            │  ✓ Confidence  │ ⚠️ SAFETY GATE 1
            │  ✓ Volatility  │
            │  ✓ Extremes    │
            └────────┬───────┘
                     │
                     ▼
            ┌────────────────┐
            │ FILTERING LAYER│
            │  ✓ Actionable? │ ⚠️ SAFETY GATE 2
            │  ✓ User match? │
            └────────┬───────┘
                     │
                     ▼
            ┌────────────────┐
            │  CONSTRAINT    │
            │  ✓ Cap 95%     │ ⚠️ SAFETY GATE 3
            │  ✓ Disclaimer  │
            │  ✓ Warnings    │
            └────────┬───────┘
                     │
                     ▼
            ┌────────────────┐
            │ EXPLANATION    │
            │  ✓ Probabilistic│ ⚠️ LANGUAGE SAFETY
            │  ✓ Assumptions │
            │  ✓ Limitations │
            └────────┬───────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│              RESPONSE TO USER                        │
│        (Multiple Safety Layers Applied)              │
└─────────────────────────────────────────────────────┘
```

---

**🎨 Visual diagrams complete!**  
**📊 All system flows documented**  
**✅ Phase 1 architecture fully visualized**
