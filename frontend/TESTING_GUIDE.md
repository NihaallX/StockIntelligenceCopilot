# Quick Testing Guide - Failure Scenarios

This guide helps you manually test all failure scenarios implemented in the frontend.

---

## Prerequisites
- Backend running on http://localhost:8001
- Frontend running on http://localhost:3001
- Browser DevTools open (F12)

---

## Test 1: Slow Loading Indicator (>3s latency)

**Steps:**
1. Open browser DevTools (F12)
2. Go to **Network** tab
3. Click throttling dropdown (usually says "No throttling")
4. Select **"Slow 3G"** or **"Fast 3G"**
5. Navigate to `/dashboard/analysis`
6. Enter a ticker (e.g., "AAPL") and click "Analyze"

**Expected Result:**
- ✅ After 3 seconds, blue info box appears:
  - "⏱️ Analysis is taking longer than usual. This can happen with complex data or high server load. Please wait..."
- ✅ Analysis eventually completes normally
- ✅ Info box disappears when complete

**Same test works for:**
- Dashboard overview (reload page with throttling)
- Portfolio page (reload with throttling)

---

## Test 2: Auth Token Expiry

**Steps:**
1. Log in to dashboard normally
2. Open browser DevTools (F12)
3. Go to **Application** tab → **Local Storage** → `http://localhost:3001`
4. Delete the `tokens` key (or change its value to garbage)
5. Try to analyze a stock or load portfolio

**Expected Result:**
- ✅ Amber warning appears:
  - "Your session has expired. Please sign in again to continue."
- ✅ After 2 seconds, automatically redirected to `/login`
- ✅ No red error styling (amber only)

---

## Test 3: Backend 5xx Server Error

**Option A: Stop Backend**
1. Stop the FastAPI backend server (Ctrl+C in terminal)
2. Try to load dashboard or analyze stock

**Option B: Simulate 503 (requires backend modification)**
1. In backend, temporarily modify endpoint to return 503
2. Make request from frontend

**Expected Result:**
- ✅ Amber warning appears:
  - "Our service is temporarily unavailable. Please try again in a few moments."
- ✅ Shield icon with amber styling (protective, not destructive)
- ✅ No technical jargon (no "500 Internal Server Error")

---

## Test 4: Data Integrity Issue

**Note:** This requires backend to return contradictory data. You can simulate by:

**Option A: Mock in Browser**
1. Open DevTools → Sources → Overrides
2. Enable local overrides
3. Intercept `/api/v1/analysis/enhanced` response
4. Modify JSON to have:
   ```json
   {
     "combined_score": "85",
     "recommendation": "AVOID - High risk detected"
   }
   ```

**Option B: Backend Mock Data**
1. Temporarily modify backend to return contradictory data for a specific ticker
2. Analyze that ticker

**Expected Result:**
- ✅ Red error box appears (protective block):
  - "Data Integrity Issue: High score conflicts with AVOID recommendation. Analysis suspended."
- ✅ Recommendation is NOT displayed at all
- ✅ Explanation: "We cannot display this analysis as the data appears inconsistent. This is a protective measure to prevent misleading recommendations."

---

## Test 5: Conflicting Signals

**Steps:**
1. Find a ticker with diverging technical/fundamental signals
2. Common examples:
   - **TSLA** - Often has strong technical but weak fundamentals
   - **GME** - Technical momentum vs poor fundamentals
   - **High-growth tech stocks** - Often have this conflict
3. Analyze the ticker

**Expected Result:**
- ✅ Amber warning box appears below recommendation:
  - "Conflicting Signals Detected"
- ✅ Explanation provided:
  - "Technical indicators suggest buying, but fundamental analysis shows weakness. This creates uncertainty — consider your investment time horizon and risk tolerance."
- ✅ Advisory at bottom:
  - "⚠️ Increased uncertainty requires extra caution. Consider seeking additional research or professional advice."
- ✅ Both technical and fundamental data still visible (not hidden)

---

## Test 6: Network Timeout

**Steps:**
1. Open DevTools → Network tab
2. Enable **"Offline"** mode (checkbox at top)
3. Try to analyze a stock or load portfolio

**Expected Result:**
- ✅ Amber warning appears:
  - "Connection timed out. Please check your network and try again."
- ✅ Blue info styling (network issue, not error)

---

## Test 7: Missing Fundamental Data

**Steps:**
1. Analyze a ticker that has no fundamental data available
2. Common examples:
   - New IPOs
   - Small cap stocks
   - Non-US stocks (depending on data provider)
   - Made-up tickers (e.g., "ZZZZZ")

**Expected Result:**
- ✅ Amber warning box appears:
  - "Limited Fundamental Data"
- ✅ Explanation:
  - "Fundamental analysis is unavailable for [TICKER]. This recommendation is based solely on technical indicators."
- ✅ Combined score shows "⚠ Partial Data" badge
- ✅ Still shows recommendation (technical-only is valid)

---

## Test 8: Empty Portfolio (Cold Start)

**Steps:**
1. Register a brand new account (or delete all positions from existing account)
2. Navigate to `/dashboard`

**Expected Result:**
- ✅ Shows onboarding card (not broken-looking $0 stats):
  - Briefcase icon
  - "Start Building Your Portfolio"
  - "Add your first position to unlock portfolio-aware insights..."
  - "Add First Position →" button
  - "💡 Tip: Adding positions helps us provide better risk assessments"
- ✅ Stats grid is NOT visible (conditional rendering)

---

## Verification Checklist

After running all tests, verify:

- [ ] No error messages use technical jargon ("500 error", "401 unauthorized", etc.)
- [ ] All error styling is amber or blue (protective), not red (destructive) - EXCEPT data integrity which is intentionally red (blocking)
- [ ] Every error message provides next steps ("Try again", "Sign in again", "Check network")
- [ ] Slow loading indicators appear after 3s for long operations
- [ ] Auth expiry auto-redirects to login
- [ ] Data integrity issues block recommendation display entirely
- [ ] Conflicting signals are disclosed, not hidden
- [ ] Missing data is explicit with "⚠ Partial Data" badge
- [ ] Empty portfolio shows onboarding, not $0 stats

---

## Common Issues & Solutions

### Issue: "Taking longer than usual" appears too quickly
**Solution:** Check timeout is set to 3000ms (3 seconds) in component

### Issue: Auth expiry doesn't redirect
**Solution:** Check browser console for errors, verify redirect logic in catch block

### Issue: Error messages still show technical jargon
**Solution:** Verify error has `.getUserMessage()` method and is being called

### Issue: Recommendation still shows despite integrity failure
**Solution:** Check `setAnalysis(null)` is called when integrity check fails

---

## Browser DevTools Shortcuts

- **F12** - Open DevTools
- **Ctrl+Shift+I** - Open DevTools (alternative)
- **Ctrl+Shift+C** - Inspect element
- **Ctrl+Shift+M** - Toggle device toolbar (mobile view)
- **F5** - Refresh page
- **Ctrl+Shift+R** - Hard refresh (clear cache)

---

## Network Throttling Presets

| Preset | Download | Upload | Latency | Use Case |
|--------|----------|--------|---------|----------|
| Slow 3G | 400 Kbps | 400 Kbps | 2000ms | Extreme test |
| Fast 3G | 1.6 Mbps | 750 Kbps | 562ms | Realistic mobile |
| Offline | 0 Kbps | 0 Kbps | - | Timeout test |

---

## Expected vs Actual Log

Use this table to track test results:

| Test Case | Status | Notes |
|-----------|--------|-------|
| Slow loading (>3s) | ⏳ | |
| Auth expiry | ⏳ | |
| Backend 5xx | ⏳ | |
| Data integrity | ⏳ | |
| Conflicting signals | ⏳ | |
| Network timeout | ⏳ | |
| Missing fundamentals | ⏳ | |
| Empty portfolio | ⏳ | |

Legend: ⏳ Not tested | ✅ Pass | ❌ Fail

---

**Happy Testing!** 🧪

Report any issues or unexpected behavior. All error messages should be calm, explanatory, and guide the user toward resolution.
