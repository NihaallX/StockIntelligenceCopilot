# 🧪 Testing Checklist - MCP-Backed Fundamentals

## Prerequisites
- [ ] Backend running: `cd backend && uvicorn app.main:app --reload`
- [ ] Frontend running: `cd frontend && npm run dev`
- [ ] Valid user account created and logged in
- [ ] At least one stock position in portfolio (RELIANCE.NS recommended)

---

## ✅ Test 1: Navigation & Legal Disclaimer

### Steps:
1. Log in to dashboard at http://localhost:3000/dashboard
2. Check top navigation bar

### Expected Results:
- [ ] Navigation shows: Overview | Portfolio | Analysis | **Legal**
- [ ] Click "Legal" → navigates to /legal/disclaimer
- [ ] Disclaimer page loads with:
  - [ ] Blue header with Scale icon
  - [ ] "Educational and Informational Purpose Only" section
  - [ ] Risk warnings in red box
  - [ ] SEBI compliance section
  - [ ] "Back to Dashboard" button works

---

## ✅ Test 2: Dashboard Disclaimer Banner

### Steps:
1. Navigate to http://localhost:3000/dashboard

### Expected Results:
- [ ] Blue disclaimer banner appears at bottom
- [ ] Text includes: "Educational Tool • Not Financial Advice"
- [ ] "Full Disclaimer" link → navigates to /legal/disclaimer

---

## ✅ Test 3: Analysis Page - MCP Context Display

### Steps:
1. Navigate to http://localhost:3000/dashboard/analysis
2. Search for "RELIANCE.NS" in the search box
3. Wait for analysis to complete (~5-10 seconds)

### Expected Results:

#### Basic Analysis:
- [ ] Technical insight displays (signal, confidence, indicators)
- [ ] Fundamental score displays (if available)
- [ ] Combined score shows (0-100)
- [ ] Recommendation displays

#### MCP Context Section (if successful):
- [ ] Section titled "Why The System Thinks This Matters (Sources)"
- [ ] **Context Verified Badge** shows:
  - [ ] Green badge: "Context verified by N sources"
  - [ ] Shows source count
- [ ] Blue info box explains: "These sources SUPPORT the signal"
- [ ] **Citations Panel** displays:
  - [ ] Each supporting point has a claim
  - [ ] Confidence badge (High/Medium/Low) for each point
  - [ ] First source shows: Title, Publisher, Date
  - [ ] "Show N more sources" button (if multiple sources)
  - [ ] Clicking button expands additional sources
  - [ ] Each source has clickable "View source" link with external link icon
  - [ ] Links open in new tab

#### MCP Failure Scenario:
- [ ] Red warning box appears: "Context data unavailable"
- [ ] Text: "Analysis based on technical indicators only"
- [ ] Analysis still works (signals show)

#### Legal Disclaimer:
- [ ] Blue disclaimer banner at bottom
- [ ] "Decision-Support Tool • Not Financial Advice"
- [ ] "Full Disclaimer" link works

---

## ✅ Test 4: Analysis Page - Confidence Badges

### Steps:
1. After running analysis with MCP context
2. Examine confidence badges on each citation

### Expected Results:

#### High Confidence (2+ sources):
- [ ] Green badge
- [ ] Shows "High confidence (2+ independent sources)"
- [ ] CheckCircle icon

#### Medium Confidence (1 source):
- [ ] Yellow badge
- [ ] Shows "Medium confidence (1 source)"
- [ ] AlertCircle icon

#### Low Confidence (0 sources):
- [ ] Red badge
- [ ] Shows "Low confidence (No direct sources)"
- [ ] XCircle icon

---

## ✅ Test 5: Citation Links & Sources

### Steps:
1. In MCP context section, find a citation
2. Click "View source" link

### Expected Results:
- [ ] Link opens in new browser tab
- [ ] URL goes to actual source (Moneycontrol, NSE, etc.)
- [ ] Page loads successfully (if scraper working)

---

## ✅ Test 6: Today's Situations Component

### Steps:
1. Navigate to http://localhost:3000/dashboard
2. Check "Today's Situations" section

### Expected Results:
- [ ] **If signals implemented**: Shows 0-5 signal cards
- [ ] **If not implemented**: Shows "No notable signals at the moment"
- [ ] Each card shows: Ticker, signal type, confidence, headline
- [ ] Clicking card → navigates to analysis page

**Note:** This will show empty until notable signals logic is implemented (Task #9)

---

## ✅ Test 7: Mobile Responsiveness

### Steps:
1. Open Chrome DevTools (F12)
2. Click "Toggle device toolbar" (Ctrl+Shift+M)
3. Test on: iPhone SE, iPad, Desktop

### Expected Results:
- [ ] Navigation collapses appropriately
- [ ] Citations panel readable on mobile
- [ ] Confidence badges don't overflow
- [ ] Disclaimer text wraps correctly

---

## ✅ Test 8: Dark Mode

### Steps:
1. Toggle system dark mode (Windows: Settings → Personalization → Colors)
2. Refresh page

### Expected Results:
- [ ] All pages switch to dark theme
- [ ] Confidence badges readable (text contrast good)
- [ ] Citations panel background appropriate
- [ ] Disclaimer banners readable

---

## 🐛 Common Issues & Fixes

### Issue: "Context unavailable" always shows
**Cause:** Moneycontrol scraper might be blocked or rate limited  
**Fix:** Check backend logs for errors. This is expected if scrapers fail (system design).

### Issue: No citations panel appears
**Cause:** MCP returned 0 sources  
**Expected:** System works without MCP (graceful degradation)

### Issue: TypeScript errors in console
**Run:** `cd frontend && npx tsc --noEmit`  
**Fix:** Address any type mismatches

### Issue: Backend crashes on analysis
**Check:** Backend terminal for stack trace  
**Common:** Missing API keys, database connection issues

---

## 📊 Backend Logs to Monitor

When testing analysis, watch backend logs for:

```
✅ Good:
INFO:     Starting enhanced analysis for RELIANCE.NS
INFO:     ✅ Technical analysis complete for RELIANCE.NS
INFO:     Fetching MCP context for RELIANCE.NS
INFO:     ✅ MCP context fetched for RELIANCE.NS: 3 points

⚠️ Expected Warnings (OK):
WARNING:  ⚠️ No high-quality MCP context available for RELIANCE.NS
WARNING:  MCP context fetch failed: [reason]

❌ Errors (Need fixing):
ERROR:    Technical analysis failed: [stack trace]
ERROR:    Database connection failed
```

---

## 🎯 Success Criteria

All tests pass when:
- [x] Navigation includes Legal link
- [x] Disclaimers visible on dashboard & analysis pages
- [x] Analysis works with or without MCP context
- [x] Citations display with confidence badges
- [x] Source links clickable and open in new tab
- [x] No TypeScript errors
- [x] No critical backend errors
- [x] Graceful degradation when MCP fails

---

## 🚀 Next Steps After Testing

If all tests pass:
1. ✅ Ready for **Task #8** decision (Indian data sources)
2. ✅ Ready for **Task #9** implementation (Notable signals logic)
3. ✅ Consider production deployment

If tests fail:
1. Note which tests failed
2. Check browser console for errors (F12)
3. Check backend logs for stack traces
4. Fix issues and re-test

---

**Last Updated:** January 3, 2026  
**Sprint:** MCP-Backed Fundamentals  
**Status:** Ready for Manual Testing
