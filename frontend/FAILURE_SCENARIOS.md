# Failure Scenario Hardening - Implementation Summary

## Overview
This document outlines the comprehensive failure scenario handling implemented across the frontend to ensure the UI **never shows certainty during failures** and maintains **calm, explanatory messaging** that guides users rather than alarming them.

## Philosophy
- **Protective, not punitive**: Errors styled as amber warnings, not red failures
- **Calm and explanatory**: User-friendly messages, not technical jargon
- **Transparent uncertainty**: Show data quality issues, conflicting signals
- **No misleading confidence**: Block recommendations if data integrity compromised
- **Guided recovery**: Provide clear next steps, not dead ends

---

## 1. Auth Token Expiry ✅ COMPLETE

### Implementation Location
- `lib/api.ts` - Error categorization and localStorage clearing
- All dashboard pages - Redirect logic on auth errors

### What Happens
1. **Detection**: API layer catches 401 responses
2. **Automatic cleanup**: Clears `localStorage` tokens
3. **Calm message**: "Your session has expired. Please sign in again to continue."
4. **Auto-redirect**: User redirected to `/login` after 2 seconds
5. **No alarm**: Amber warning styling, not red error

### Code Implementation
```typescript
// lib/api.ts
if (response.status === 401) {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('user');
    localStorage.removeItem('tokens');
  }
}

// dashboard pages
if (err.category === 'auth') {
  setTimeout(() => window.location.href = '/login', 2000);
}
```

### User Experience
- ⏱️ Session expires after inactivity
- 🔔 Sees calm message: "Session expired"
- 🔄 Automatically redirected to login
- ✅ Can sign back in and resume work

---

## 2. Network Latency (>3s) ✅ COMPLETE

### Implementation Location
- `lib/api.ts` - Timeout wrappers on all API calls
- `app/dashboard/analysis/page.tsx` - Slow loading indicator
- `app/dashboard/portfolio/page.tsx` - Slow loading indicator
- `app/dashboard/page.tsx` - Slow loading indicator

### What Happens
1. **Timeout protection**: All API calls have timeouts (10-30s based on complexity)
2. **Latency warning**: After 3 seconds, show "taking longer than usual" message
3. **Calm explanation**: "This can happen with complex data or high server load"
4. **Automatic recovery**: Timer cleared when request completes
5. **Blue info styling**: Not error red, just informational

### Code Implementation
```typescript
// lib/api.ts - Timeout wrapper
function fetchWithTimeout(url: string, options: RequestInit, timeout = 30000): Promise<Response> {
  return Promise.race([
    fetch(url, options),
    new Promise<Response>((_, reject) =>
      setTimeout(() => reject(new ApiError(408, 'Request timed out')), timeout)
    ),
  ]);
}

// Endpoint-specific timeouts
getPortfolioSummary: 10s timeout (fast operation)
getEnhancedAnalysis: 30s timeout (complex ML operation)

// UI component
const [isSlowLoading, setIsSlowLoading] = useState(false);

useEffect(() => {
  if (isLoading) {
    const timer = setTimeout(() => setIsSlowLoading(true), 3000);
    return () => clearTimeout(timer);
  }
}, [isLoading]);

{isSlowLoading && (
  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
    <p>⏱️ Analysis is taking longer than usual. This can happen with complex data or high server load. Please wait...</p>
  </div>
)}
```

### User Experience
- 🔄 Submits analysis request
- ⏱️ After 3 seconds, sees calm info message
- 📊 Analysis completes normally
- ✅ No anxiety from silent hanging

---

## 3. Backend 5xx Errors ✅ COMPLETE

### Implementation Location
- `lib/api.ts` - Error categorization by status code
- All dashboard pages - Category-specific error display

### What Happens
1. **Automatic categorization**: 5xx errors tagged as `category: 'server'`
2. **User-friendly message**: "Our service is temporarily unavailable. Please try again in a few moments."
3. **Retryable flag**: `isRetryable: true` signals this is transient
4. **Calm styling**: Amber warning, not red failure
5. **Recovery guidance**: "Try again in a few moments" provides clear action

### Code Implementation
```typescript
// lib/api.ts
class ApiError extends Error {
  public readonly category: ErrorCategory;
  public readonly isRetryable: boolean;
  
  constructor(status: number, message: string, originalError?: any) {
    super(message);
    
    if (status >= 500) {
      this.category = 'server';
      this.isRetryable = true;
    }
  }
  
  getUserMessage(): string {
    switch (this.category) {
      case 'server':
        return 'Our service is temporarily unavailable. Please try again in a few moments.';
      // ... other categories
    }
  }
}

// UI component
catch (err: any) {
  if (err.getUserMessage) {
    setError(err.getUserMessage());
  } else {
    setError(err.message || "Analysis failed");
  }
}

{error && (
  <div className="p-4 bg-amber-50 border border-amber-300 rounded-lg">
    <Shield className="w-5 h-5 text-amber-600" />
    <span className="font-semibold">Analysis Unavailable</span>
    <p className="text-sm">{error}</p>
  </div>
)}
```

### User Experience
- 📊 Requests stock analysis
- ⚠️ Backend returns 503 Service Unavailable
- 💬 Sees: "Our service is temporarily unavailable. Please try again in a few moments."
- 🔄 Can retry immediately
- ✅ No panic, just calm guidance

---

## 4. Data Integrity Issues ✅ COMPLETE

### Implementation Location
- `app/dashboard/analysis/page.tsx` - `validateAnalysisIntegrity()` function

### What Happens
1. **Pre-display validation**: Before showing recommendation, check data consistency
2. **Contradiction detection**: High score (>70) with AVOID recommendation = data corrupted
3. **Block display**: If integrity fails, show error and **hide recommendation entirely**
4. **Protective message**: Explains why we're blocking display (transparency)
5. **No false confidence**: Never show recommendation if data is suspect

### Code Implementation
```typescript
// Validation function
function validateAnalysisIntegrity(analysis: EnhancedAnalysis): string | null {
  const score = parseInt(analysis.combined_score);
  const rec = parseRecommendation(analysis.recommendation);
  
  // Check for impossible combinations
  if (score > 70 && rec.action.includes('AVOID')) {
    return 'Data integrity issue: High score conflicts with AVOID recommendation. Analysis suspended.';
  }
  if (score < 30 && rec.action.includes('BUY')) {
    return 'Data integrity issue: Low score conflicts with BUY signal. Analysis suspended.';
  }
  
  return null; // Data integrity OK
}

// Usage
const integrityIssue = validateAnalysisIntegrity(result);
if (integrityIssue) {
  setDataIntegrityIssue(integrityIssue);
  setAnalysis(null); // Don't show compromised data
}

// UI
{dataIntegrityIssue && (
  <div className="p-4 bg-red-50 border border-red-300 rounded-lg">
    <AlertCircle className="w-5 h-5 text-red-600" />
    <span className="font-semibold">Data Integrity Issue</span>
    <p>{dataIntegrityIssue}</p>
    <p className="text-xs">We cannot display this analysis as the data appears inconsistent. This is a protective measure to prevent misleading recommendations.</p>
  </div>
)}
```

### User Experience
- 📊 Requests analysis for ticker
- 🔍 System detects: score=85 but recommendation="AVOID" (impossible)
- 🛡️ Sees: "Data Integrity Issue: High score conflicts with AVOID recommendation. Analysis suspended."
- ❌ Recommendation **not displayed** (protective block)
- ✅ Trust maintained - system admits uncertainty rather than showing bad data

---

## 5. Conflicting Signals ✅ COMPLETE

### Implementation Location
- `app/dashboard/analysis/page.tsx` - `detectConflictingSignals()` function

### What Happens
1. **Automatic conflict detection**: Compare technical vs fundamental signals
2. **Uncertainty disclosure**: Show amber warning when signals disagree
3. **Context explanation**: Explain why conflict exists and what it means
4. **No forced consensus**: Let user see both perspectives
5. **Risk advisory**: "Increased uncertainty requires extra caution"

### Code Implementation
```typescript
// Detection function
function detectConflictingSignals(analysis: EnhancedAnalysis): string | null {
  if (!analysis.fundamental_score) return null;
  
  const rec = parseRecommendation(analysis.recommendation);
  const fundAssessment = analysis.fundamental_score.overall_assessment;
  const fundScore = analysis.fundamental_score.overall_score;
  
  // Technical bullish + fundamentals bearish
  if (rec.action.includes('BUY') && fundAssessment === 'POOR') {
    return 'Technical indicators suggest buying, but fundamental analysis shows weakness. This creates uncertainty — consider your investment time horizon and risk tolerance.';
  }
  
  // Technical bearish + fundamentals bullish
  if ((rec.action.includes('HOLD') || rec.action.includes('AVOID')) && fundAssessment === 'STRONG' && fundScore > 70) {
    return 'Strong fundamental profile but technical signals advise caution. May be suitable for long-term investors willing to wait for better entry points.';
  }
  
  // Scenario analysis conflicts
  if (analysis.scenario_analysis) {
    const expectedReturn = parseFloat(analysis.scenario_analysis.expected_return_weighted);
    if (rec.action.includes('BUY') && expectedReturn < 0) {
      return 'Recommendation is positive but probability-weighted expected return is negative. This indicates high uncertainty in our models.';
    }
  }
  
  return null;
}

// UI
{(() => {
  const conflictWarning = detectConflictingSignals(analysis);
  if (!conflictWarning) return null;
  
  return (
    <div className="p-4 bg-amber-50 border border-amber-300 rounded-lg">
      <AlertTriangle className="w-5 h-5 text-amber-600" />
      <span className="font-semibold">Conflicting Signals Detected</span>
      <p>{conflictWarning}</p>
      <p className="text-xs">⚠️ Increased uncertainty requires extra caution. Consider seeking additional research or professional advice.</p>
    </div>
  );
})()}
```

### User Experience
- 📊 Analyzes ticker: AAPL
- 🔍 Technical says "BUY" but fundamentals say "POOR"
- ⚠️ Sees amber warning: "Conflicting Signals Detected"
- 💬 Explanation: "Technical indicators suggest buying, but fundamental analysis shows weakness. Consider your time horizon."
- ✅ Transparency maintained - no false certainty during disagreement

---

## Error Message Guidelines

### ✅ DO (Implemented)
- "Your session has expired. Please sign in again to continue."
- "Our service is temporarily unavailable. Please try again in a few moments."
- "Analysis is taking longer than usual. This can happen with complex data."
- "Data integrity issue: High score conflicts with AVOID recommendation."
- "Conflicting signals detected. Increased uncertainty requires extra caution."

### ❌ DON'T (Avoided)
- "Error 401: Unauthorized"
- "500 Internal Server Error"
- "Request failed"
- "Something went wrong"
- "Critical error - contact admin"

### Principles
1. **User-centric language**: Explain impact, not technical details
2. **Calm tone**: Never alarming, always explanatory
3. **Clear next steps**: What can user do?
4. **Honest uncertainty**: Admit when data is uncertain
5. **Protective framing**: Errors are safeguards, not failures

---

## Testing Protocol

### Manual Test Cases

**Test 1: Auth Expiry**
1. Log in to dashboard
2. Manually clear `localStorage` tokens in browser DevTools
3. Try to analyze a stock
4. ✅ Should see: "Your session has expired. Please sign in again."
5. ✅ Should auto-redirect to login after 2s

**Test 2: Network Latency**
1. Open browser DevTools Network tab
2. Throttle connection to "Slow 3G"
3. Submit stock analysis
4. ✅ After 3s should see: "⏱️ Analysis is taking longer than usual..."
5. ✅ Should complete normally (just slower)

**Test 3: Backend 5xx Error**
1. Stop backend server (or modify to return 503)
2. Try to load portfolio summary
3. ✅ Should see: "Our service is temporarily unavailable. Please try again in a few moments."
4. ✅ Should use amber styling (not red)

**Test 4: Data Integrity Issue**
(Requires backend mock data with score=85, recommendation="AVOID - high risk")
1. Analyze ticker with contradictory data
2. ✅ Should see: "Data Integrity Issue: High score conflicts with AVOID recommendation."
3. ✅ Recommendation should NOT be displayed
4. ✅ Error should be in red (protective block)

**Test 5: Conflicting Signals**
(Requires ticker with technical=BUY, fundamentals=POOR)
1. Analyze ticker: e.g., "TSLA" (often has technical/fundamental divergence)
2. ✅ Should see amber warning: "Conflicting Signals Detected"
3. ✅ Should still show recommendation (both signals visible)
4. ✅ Should include advisory: "Increased uncertainty requires extra caution"

---

## API Error Categories

| Category | HTTP Status | Retryable | User Message | UI Color |
|----------|-------------|-----------|--------------|----------|
| `auth` | 401, 403 | No | "Your session has expired. Please sign in again." | Amber |
| `server` | 500-599 | Yes | "Our service is temporarily unavailable. Try again in a few moments." | Amber |
| `network` | 408, 0 | Yes | "Connection timed out. Please check your network and try again." | Blue |
| `validation` | 400-499 | No | (Use specific backend message) | Amber |
| `unknown` | Other | No | "An unexpected issue occurred. Please try again." | Amber |

---

## Timeouts by Operation

| Operation | Timeout | Rationale |
|-----------|---------|-----------|
| Portfolio Summary | 10s | Fast DB query |
| Portfolio Positions | 10s | Fast DB query |
| Enhanced Analysis | 30s | Complex ML inference + external data |
| Add Position | 10s | Simple DB write |

---

## File Modifications

### Core API Layer
- ✅ `lib/api.ts` - Enhanced error categorization, timeout wrappers, auth expiry detection

### Dashboard Pages
- ✅ `app/dashboard/analysis/page.tsx` - Data integrity validation, conflicting signals detection, slow loading indicator
- ✅ `app/dashboard/portfolio/page.tsx` - Error handling for position addition, slow loading indicator
- ✅ `app/dashboard/page.tsx` - Error handling for summary loading, slow loading indicator

### New Documentation
- ✅ `FAILURE_SCENARIOS.md` (this file)

---

## Success Criteria ✅

- [x] UI never shows certainty during failures
- [x] All error messages are calm and explanatory (no technical jargon)
- [x] No recommendation shown if data integrity compromised
- [x] User is guided, not alarmed
- [x] Auth expiry handled gracefully with auto-redirect
- [x] Network latency surfaced to user (>3s warning)
- [x] Backend 5xx errors differentiated from client errors
- [x] Conflicting signals disclosed with context
- [x] All errors use protective amber styling (not destructive red)
- [x] Timeouts prevent indefinite hanging
- [x] Response validation catches malformed data

---

## Maintenance Notes

### Adding New API Endpoints
When adding new API calls, always:
1. Use `fetchWithTimeout()` with appropriate timeout
2. Use `handleResponse<T>()` to get automatic error categorization
3. Add slow loading indicator in UI if operation can take >3s
4. Test with network throttling and backend downtime

### Adding New Error Categories
If adding new error types:
1. Update `ErrorCategory` type in `lib/api.ts`
2. Add user-friendly message in `ApiError.getUserMessage()`
3. Update UI components to handle new category
4. Document in this file

### Testing Checklist
Before production release:
- [ ] Test auth expiry with real expired JWT
- [ ] Test with backend completely down (5xx)
- [ ] Test with network throttling (slow 3G)
- [ ] Test with contradictory mock data (integrity)
- [ ] Test with real tickers that have conflicting signals
- [ ] Verify all error messages are user-friendly
- [ ] Verify no technical jargon in UI
- [ ] Verify amber/blue styling (no red except integrity blocks)

---

**Implementation Date**: 2024  
**Philosophy**: Restraint-oriented fintech UI - never show certainty during failures, guide users with calm explanations
