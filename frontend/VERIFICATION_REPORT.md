# FRONTEND VERIFICATION REPORT
## Stock Intelligence Copilot - Trust & Restraint Audit

**Date**: January 2, 2026  
**Reviewer**: Senior Frontend Engineer & UX  
**Status**: ⚠️ CRITICAL ISSUES FOUND - NOT TRUST-READY

---

## PART 1: VERIFICATION RESULTS

### 1.1 API Wiring ✅ PASS
- ✅ Real backend endpoints called (`/api/v1/auth/*`, `/api/v1/portfolio/*`, `/api/v1/analysis/enhanced`)
- ✅ JWT authentication enforced (Bearer token in all protected calls)
- ✅ No mock data - all responses from live backend
- ✅ Portfolio state fetched live from database
- ✅ Enhanced analysis renders real backend responses

**Evidence**: `lib/api.ts` lines 1-175 - all fetch calls use `API_BASE` with proper auth headers

---

### 1.2 Recommendation Rendering ❌ CRITICAL FAILURE

**Issues Found**:

1. **NO HOLD/NO ACTION STYLING**
   - Current: Recommendation displayed in generic `bg-muted` gray box
   - Problem: HOLD, AVOID, NO ACTION look identical to BUY/SELL
   - No visual distinction between action vs. inaction
   - **Location**: `app/dashboard/analysis/page.tsx` line 93

2. **RECOMMENDATION TEXT NOT PARSED**
   - Backend sends: "HOLD - Technical signals bullish but fundamentals weak"
   - Frontend shows: Entire string with no emphasis or structure
   - Should highlight: Action word + clear reasoning
   - **Location**: `app/dashboard/analysis/page.tsx` line 94

3. **NO CONFIDENCE DISPLAY**
   - Combined score shown but technical signal confidence missing
   - User cannot see if recommendation is 60% confident vs 95%
   - **Requirement**: Show "Confidence: X%" near recommendation

4. **COMBINED SCORE MISLEADING**
   - Shown as `X/100` in large bold primary-colored text
   - Appears authoritative even when fundamentals are missing
   - No indication of data completeness or uncertainty
   - **Location**: `app/dashboard/analysis/page.tsx` lines 84-91

---

### 1.3 Risk Blocks ❌ CRITICAL FAILURE

**Issues Found**:

1. **NO RISK VIOLATION HANDLING**
   - Backend returns 400/403 for risk-blocked actions
   - Frontend shows generic error: "Analysis failed" or "Request failed"
   - No explanation of which risk limit was violated
   - **Location**: `app/dashboard/analysis/page.tsx` line 26

2. **SILENT PORTFOLIO FAILURE**
   - `addPortfolioPosition` errors caught but only logged to console
   - User sees alert() with generic message
   - No mention of: position size limit, drawdown limit, or exposure constraints
   - **Location**: `app/dashboard/portfolio/page.tsx` line 63

3. **ERROR STYLING IS RED/DESTRUCTIVE**
   - Risk blocks styled as `bg-destructive/10 text-destructive`
   - Feels like system failure, not protective constraint
   - Should be: neutral warning with explanation
   - **Location**: `app/dashboard/analysis/page.tsx` line 64

---

### 1.4 Scenario Display ⚠️ PARTIAL PASS

**Issues Found**:

1. **VISUAL HIERARCHY BIAS** ⚠️ MODERATE
   - Best case: Green border, green background, large font
   - Worst case: Red border, red background, same size
   - Layout order: Best → Base → Worst (left to right)
   - **Problem**: Visual weight favors upside
   - **Location**: `app/dashboard/analysis/page.tsx` lines 143-189

2. **PROBABILITIES TOO SMALL** ⚠️ MODERATE  
   - Shown in `text-sm text-muted-foreground`
   - Less prominent than return percentages
   - Should be equal visual weight to returns
   - **Location**: `app/dashboard/analysis/page.tsx` lines 155, 172, 188

3. **MISSING DOWNSIDE CONTEXT** ❌ CRITICAL
   - No explanation that worst case can occur even with "BUY" signal
   - No probability-weighted interpretation
   - Expected return shown but not emphasized vs. scenarios
   - **Location**: `app/dashboard/analysis/page.tsx` lines 195-214

---

## PART 2: MANUAL TEST CASE FINDINGS

### TEST A: Overexposure ❌ NOT TESTABLE

**Reason**: Frontend has NO UI for:
- Portfolio exposure warnings
- Risk profile violations in analysis display
- Correlation between current holdings and new analysis

**Expected**:
- If user holds AAPL (20% of portfolio) and analyzes AAPL
- Backend should return NO ACTION due to concentration risk
- Frontend should show: "⚠️ Blocked by risk profile: You already hold 20% in AAPL (limit: 15%)"

**Actual**: 
- No code to display portfolio-aware recommendations
- No code to check current holdings before displaying analysis
- Recommendation shown without context

---

### TEST B: Missing Fundamentals ⚠️ PARTIAL FAIL

**Current Behavior**:
```tsx
{analysis.fundamental_score && (
  <div>...</div>
)}
```
- If `fundamental_score` is null, section simply doesn't render
- **Problem**: Silent failure - user doesn't know data is missing

**Expected**:
```tsx
{!analysis.fundamental_score && (
  <div className="p-4 bg-amber-500/10 border border-amber-500/30">
    ⚠️ Fundamental data unavailable for this ticker.
    Analysis based on technical signals only. Confidence reduced.
  </div>
)}
```

**Location**: `app/dashboard/analysis/page.tsx` line 98

---

### TEST C: Cold Start User ❌ CRITICAL FAILURE

**Current Behavior**:
- Empty portfolio shows: "No positions yet. Add your first position to get started."
- Analysis runs without portfolio context
- **Location**: `app/dashboard/portfolio/page.tsx` line 170

**Problems**:

1. **NO EXPLANATION OF IMPACT**
   - User doesn't know empty portfolio reduces analysis quality
   - Should show: "📊 Tip: Add positions to get portfolio-aware insights"

2. **DASHBOARD SHOWS EMPTY STATS**
   - Total Value: $0, Positions: 0
   - Looks broken, not intentionally minimal
   - Should show: Onboarding guidance instead

3. **RISK PROFILE NOT EXPLAINED**
   - New user sees "Risk Tolerance: conservative" but doesn't know what it means
   - No link to risk profile settings
   - **Location**: `app/dashboard/page.tsx` lines 101-114

---

## PART 3: PRIORITIZED FIXES

### 🔴 CRITICAL (Must Fix Before Trust-Ready)

#### 1. Recommendation Rendering Overhaul
**File**: `app/dashboard/analysis/page.tsx`

**Changes Needed**:
```tsx
// Parse recommendation into action + reasoning
const parseRecommendation = (rec: string) => {
  const match = rec.match(/^(HOLD|AVOID|BUY|SELL|NO ACTION|WEAK BUY|STRONG BUY|STRONG SELL)(\s*-\s*(.+))?$/);
  return {
    action: match?.[1] || rec,
    reason: match?.[3] || ""
  };
};

// Display with proper styling
const rec = parseRecommendation(analysis.recommendation);
const isInaction = ['HOLD', 'AVOID', 'NO ACTION'].includes(rec.action);

<div className={cn(
  "p-6 rounded-xl border-2",
  isInaction 
    ? "bg-amber-50 border-amber-200 dark:bg-amber-900/10 dark:border-amber-700"
    : "bg-muted border-border"
)}>
  <div className="flex items-center gap-3 mb-2">
    {isInaction && <AlertCircle className="w-6 h-6 text-amber-600" />}
    <span className="text-2xl font-bold">{rec.action}</span>
  </div>
  {rec.reason && (
    <p className="text-sm text-muted-foreground">{rec.reason}</p>
  )}
  <div className="mt-4 text-xs text-muted-foreground">
    ℹ️ This is a probability-based assessment, not financial advice.
  </div>
</div>
```

---

#### 2. Risk Block Error Handling
**File**: `lib/api.ts`

**Add Interface**:
```tsx
export interface RiskViolation {
  type: 'position_size' | 'concentration' | 'drawdown' | 'confidence';
  message: string;
  current_value?: number;
  limit_value?: number;
}
```

**Update Error Handler**:
```tsx
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    
    // Check for risk violations
    if (error.risk_violation) {
      throw new ApiError(
        response.status, 
        error.risk_violation.message,
        error.risk_violation
      );
    }
    
    throw new ApiError(response.status, error.detail || 'Request failed');
  }
  return response.json();
}
```

**File**: `app/dashboard/analysis/page.tsx`

**Display Risk Blocks**:
```tsx
{error && (
  <div className="mt-4 p-4 bg-amber-50 border border-amber-200 rounded-lg">
    <div className="flex items-center gap-2 mb-2">
      <Shield className="w-5 h-5 text-amber-600" />
      <span className="font-semibold">Protected by Risk Profile</span>
    </div>
    <p className="text-sm">{error}</p>
    {/* If RiskViolation data available, show specifics */}
  </div>
)}
```

---

#### 3. Missing Fundamental Data Warning
**File**: `app/dashboard/analysis/page.tsx`

**Add After Line 98**:
```tsx
{!analysis.fundamental_score && (
  <div className="bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-700 rounded-xl p-6">
    <div className="flex items-center gap-2 mb-2">
      <AlertTriangle className="w-5 h-5 text-amber-600" />
      <h3 className="font-semibold">Limited Data Available</h3>
    </div>
    <p className="text-sm text-muted-foreground">
      Fundamental analysis is unavailable for {ticker}. 
      This recommendation is based solely on technical indicators and may be less reliable.
    </p>
  </div>
)}
```

---

#### 4. Scenario Display De-biasing
**File**: `app/dashboard/analysis/page.tsx`

**Reorder Layout** (Worst → Base → Best):
```tsx
<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
  {/* Worst Case First */}
  <div className="p-4 border border-border rounded-lg bg-card order-1">
    <div className="flex items-center gap-2 mb-3">
      <TrendingDown className="w-5 h-5 text-muted-foreground" />
      <span className="font-semibold">Worst Case</span>
    </div>
    <div className="text-2xl font-bold mb-1">
      {parseFloat(analysis.scenario_analysis.worst_case.expected_return_percent).toFixed(1)}%
    </div>
    <div className="text-base font-medium">
      Probability: {parseFloat(analysis.scenario_analysis.worst_case.probability).toFixed(0)}%
    </div>
  </div>

  {/* Base Case */}
  <div className="p-4 border-2 border-primary rounded-lg bg-primary/5 order-2">
    {/* Emphasized as most likely */}
  </div>

  {/* Best Case Last */}
  <div className="p-4 border border-border rounded-lg bg-card order-3">
    {/* De-emphasized */}
  </div>
</div>

<div className="mt-4 p-4 bg-muted rounded-lg">
  <p className="text-sm text-muted-foreground">
    ⚠️ Even positive signals carry downside risk. 
    Base case ({analysis.scenario_analysis.base_case.probability}% likely) 
    suggests {analysis.scenario_analysis.base_case.expected_return_percent}% return.
  </p>
</div>
```

---

### 🟡 HIGH PRIORITY (Needed for Production)

#### 5. Confidence Display
Add technical signal confidence near combined score:
```tsx
<div className="text-center">
  <div className="text-5xl font-bold text-primary mb-2">
    {analysis.combined_score}/100
  </div>
  <div className="text-sm text-muted-foreground">Rating</div>
  {analysis.technical_insight?.signal?.strength?.confidence && (
    <div className="text-xs mt-2 text-amber-600">
      Signal Confidence: {(analysis.technical_insight.signal.strength.confidence * 100).toFixed(0)}%
    </div>
  )}
</div>
```

---

#### 6. Cold Start Onboarding
**File**: `app/dashboard/page.tsx`

Replace empty stats with guidance:
```tsx
{summary?.total_positions === 0 && (
  <div className="col-span-full p-8 bg-card border border-border rounded-xl text-center">
    <h3 className="text-xl font-semibold mb-2">Welcome! Let's Get Started</h3>
    <p className="text-muted-foreground mb-4">
      Add your first position to unlock portfolio-aware insights and risk management.
    </p>
    <Link href="/dashboard/portfolio" className="...">
      Add First Position
    </Link>
  </div>
)}
```

---

#### 7. Data Completeness Indicator
**File**: `app/dashboard/analysis/page.tsx`

Add "Data Quality" badge:
```tsx
<div className="flex items-center gap-2 text-sm">
  <span className="text-muted-foreground">Data Quality:</span>
  <span className={cn(
    "px-2 py-1 rounded text-xs font-medium",
    analysis.fundamental_score && analysis.scenario_analysis
      ? "bg-green-100 text-green-700"
      : "bg-amber-100 text-amber-700"
  )}>
    {analysis.fundamental_score && analysis.scenario_analysis ? "Complete" : "Partial"}
  </span>
</div>
```

---

### 🟢 MEDIUM PRIORITY (Polish)

#### 8. Uncertainty Language
Add disclaimers throughout:
- "This analysis assumes..." (show key assumptions)
- "Confidence reduces when..." (explain data gaps)
- "Why this could be wrong:" (contrarian view)

#### 9. Portfolio Context in Analysis
Show user's current holdings of analyzed ticker:
```tsx
{userHoldsPosition(ticker) && (
  <div className="p-3 bg-blue-50 border border-blue-200 rounded">
    📊 You currently hold {currentPosition.quantity} shares of {ticker} 
    ({currentPosition.portfolio_percent}% of portfolio)
  </div>
)}
```

---

## PART 4: FINAL CHECKLIST

### Before "Trust-Ready" Status:
- [ ] HOLD/AVOID recommendations visually distinct (amber/neutral, not gray)
- [ ] Risk violations show clear explanation (not generic error)
- [ ] Missing fundamental data explicitly stated
- [ ] Scenario display de-biased (worst case equal prominence)
- [ ] Combined score shows data completeness
- [ ] Cold start users see onboarding guidance
- [ ] Confidence levels visible on all recommendations
- [ ] Probabilistic language throughout
- [ ] "Why this could be wrong" sections added

### Trust Indicators:
- [ ] Inaction feels intentional, not indecisive
- [ ] Risk blocks feel protective, not punitive
- [ ] Uncertainty is visible, not hidden
- [ ] Downside emphasized equally with upside

---

## CONCLUSION

**Status**: ❌ NOT TRUST-READY

**Severity Breakdown**:
- 🔴 Critical: 4 issues (recommendation rendering, risk blocks, missing data, scenario bias)
- 🟡 High: 3 issues (confidence display, cold start, data quality)
- 🟢 Medium: 2 issues (uncertainty language, portfolio context)

**Estimated Fix Time**: 8-12 hours

**Next Steps**:
1. Implement Critical fixes (Priority 1-4)
2. Test with real backend responses
3. Validate all three test cases
4. Re-verify trust indicators
5. Request final sign-off

**Reviewer Notes**:
The backend appears conservative and restraint-oriented. The frontend, however, presents data in ways that could mislead users into overconfidence. The system's built-in caution is being undermined by presentation choices.

Focus on making HOLD/AVOID feel like wise decisions, not system failures.
