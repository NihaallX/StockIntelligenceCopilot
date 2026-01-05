# Legal Documentation - Stock Intelligence Copilot

## Compliance Overview

This document outlines the legal framework and compliance measures implemented in the Stock Intelligence Copilot system. **This system is designed as a decision support tool, NOT a financial advisor or trading platform.**

---

## Core Legal Principles

### 1. No Financial Advice
**Status**: ✅ Implemented Across System

The system does NOT provide financial advice. All language is structured to:
- Present factual analysis only
- Use conditional language ("may", "consider", "if")
- Avoid directive commands ("buy", "sell", "now")
- Include explicit disclaimers

**Evidence**:
- Settings disclaimer: [settings.py](../backend/app/config/settings.py#L73-L77)
- Frontend footer: [footer.tsx](../frontend/components/ui/footer.tsx)
- Registration page: [register/page.tsx](../frontend/app/register/page.tsx)
- Every API response includes disclaimer

### 2. MCP Context is Informational Only
**Status**: ✅ Explicitly Labeled

Market Context (MCP) data is clearly labeled as:
- "Informational context. Not a recommendation."
- Sources are cited with external links
- No trading signals generated from context
- Separated from core analysis

**Implementation**:
- Frontend UI: Dedicated "Market Context (Sources)" section with disclaimer
- Model schema: `disclaimer: str = "Informational only. Not financial advice."`
- API responses: Context wrapped with explicit non-recommendation label

### 3. No Trade Execution
**Status**: ✅ System Design

The system:
- Does NOT connect to any brokerage APIs
- Does NOT place orders
- Does NOT hold user funds
- Does NOT execute trades automatically
- Requires manual action for all investment decisions

**User Control**: Users must independently choose to act on any suggestions.

### 4. Probabilistic, Not Certain
**Status**: ✅ Language Enforced

All recommendations:
- Are probability-based
- Include scenario analysis (best/base/worst case)
- Show confidence levels
- Acknowledge uncertainty explicitly
- Never use "guaranteed", "will", "certain"

---

## Disclaimer Text

### Primary Disclaimer (Backend)
Location: `backend/app/config/settings.py`

```python
DISCLAIMER: str = (
    "This is not financial advice. All suggestions are probabilistic and "
    "should be independently verified. Past performance does not guarantee "
    "future results. Invest at your own risk."
)
```

### Frontend Registration Disclaimer
Location: `frontend/app/register/page.tsx`

Users must acknowledge:
- This is NOT financial advice
- They are solely responsible for investment decisions
- Past performance doesn't guarantee future results
- All analysis should be independently verified

### MCP-Specific Disclaimer
Location: `backend/app/core/context_agent/models.py`

```python
disclaimer: str = "Informational only. Not financial advice."
```

---

## Language Compliance

### Allowed Verbs (Conditional)
✅ **Use these**:
- "consider"
- "may"
- "might"
- "could"
- "if"
- "historically"
- "appears"
- "suggests"

### Forbidden Words (Directive)
❌ **NEVER use**:
- "buy" / "sell" (except in past tense: "signal suggests buying conditions")
- "now" / "immediately"
- "must" / "should"
- "will" / "guaranteed"
- "target price" / "predicted price"
- "act now"

### Recommendation Format
**Before** (Directive):
- ❌ "STRONG BUY - Buy immediately"
- ❌ "Sell 50% of your position now"

**After** (Conditional):
- ✅ "STRONG SIGNAL - If considering entry, conditions appear favorable"
- ✅ "If concerned about downside, reducing position size may lower risk"

---

## System Architecture (Legal Perspective)

### What the System DOES
1. ✅ **Analyzes** technical and fundamental data
2. ✅ **Calculates** probability-weighted scenarios
3. ✅ **Presents** market context from reputable sources
4. ✅ **Suggests** possible considerations
5. ✅ **Tracks** user's portfolio positions (read-only)

### What the System Does NOT Do
1. ❌ **Recommend** specific buy/sell actions
2. ❌ **Execute** trades
3. ❌ **Predict** future prices
4. ❌ **Guarantee** outcomes
5. ❌ **Act** as a licensed financial advisor

---

## Tactical Mode Explanation

**What It Is**:
- A **decision support interface** showing conditional suggestions
- Presents risk-first analysis with probability distributions
- Uses conditional language throughout

**What It Is NOT**:
- NOT an auto-trading system
- NOT a "buy/sell signal generator"
- NOT financial advice
- NOT predictive (only probabilistic)

**Compliance Measures**:
- All suggestions use "consider", "may", "if"
- Scenario analysis shows downside cases prominently
- HOLD/NO ACTION states are non-punitive
- Disclaimers on every page

---

## Market Context Agent (MCP) Legal Framework

### Purpose
Provide **READ-ONLY factual context** from reputable sources to enrich user understanding.

### Constraints
1. ✅ **Read-Only**: Does NOT modify opportunity data
2. ✅ **Factual Only**: Does NOT invent claims
3. ✅ **Citation Required**: Every claim has source + URL
4. ✅ **No Predictions**: Does NOT predict prices or timing
5. ✅ **Safe Fallback**: Returns null if unavailable

### Data Sources
**Approved**:
- Moneycontrol (reputable Indian financial news)
- NSE/BSE official data (if implemented)
- Reuters, Economic Times Markets (if implemented)

**Forbidden**:
- Social media (Twitter, Reddit)
- Unverified blogs or forums
- User-generated content
- Promotional content

### User-Facing Label
"**Market Context (Sources)** - Informational context. Not a recommendation."

---

## Compliance Checklist

### Registration & Terms
- [ ] ✅ Users acknowledge disclaimer at registration
- [ ] ✅ Terms version tracked (`TERMS_VERSION: "1.0.0"`)
- [ ] ✅ User must check "I understand this is not financial advice"

### Every Analysis Response
- [ ] ✅ Includes `disclaimer` field
- [ ] ✅ Uses conditional language ("may", "consider")
- [ ] ✅ Shows probability distributions (scenario analysis)
- [ ] ✅ Clearly labeled as "decision support" not "recommendation"

### MCP Context
- [ ] ✅ Separate section labeled "Informational only"
- [ ] ✅ All claims have citations (source + URL)
- [ ] ✅ No trading signals derived from context
- [ ] ✅ Hidden if no data available (no placeholders)

### Frontend UI
- [ ] ✅ Footer disclaimer on every page
- [ ] ✅ Portfolio suggestions: "conditional suggestions, not financial advice"
- [ ] ✅ Analysis page: "probability-based assessment, not financial advice"
- [ ] ✅ No green/red "buy/sell" buttons

### Backend Logic
- [ ] ✅ No automatic trade execution
- [ ] ✅ No price predictions
- [ ] ✅ Risk engine enforces conservative defaults
- [ ] ✅ All recommendations use conditional language

---

## Audit Log & Record Keeping

### Data Retention
```python
AUDIT_LOG_RETENTION_YEARS: int = 7
```

**Purpose**: Maintain records of user interactions for compliance audits.

**What's Logged**:
- User actions (analysis requests, portfolio updates)
- Recommendations shown to users
- Disclaimers displayed
- MCP trigger events

**What's NOT Logged**:
- User's actual investment decisions (we don't have this data)
- Brokerage account information
- Trade executions (N/A - we don't execute)

---

## Legal Protections

### 1. No Fiduciary Relationship
The system:
- Does NOT create a fiduciary duty
- Does NOT act as a registered investment advisor
- Does NOT have custody of user funds
- Users retain full control and responsibility

### 2. Explicit User Responsibility
Users acknowledge:
- They are solely responsible for investment decisions
- System provides information, NOT advice
- They must verify all data independently
- Past performance ≠ future results

### 3. No Performance Guarantees
System explicitly:
- Does NOT guarantee returns
- Does NOT promise accuracy
- Shows probability distributions (not certainties)
- Includes worst-case scenarios in every analysis

### 4. Limitation of Liability
Registration terms include:
- "Invest at your own risk"
- "Should be independently verified"
- "No guarantee of accuracy"

---

## Regulatory Compliance

### SEBI Compliance (India)
**Status**: ✅ Designed for Compliance

1. **Not a SEBI-registered advisor**: System does NOT provide "financial advice" as defined by SEBI
2. **No investment recommendations**: Uses conditional language only
3. **No execution**: Does not facilitate trades
4. **Disclaimer present**: On every page

### US SEC Compliance (If Expanding)
**Status**: ⚠️ Review Required

If expanding to US markets:
- [ ] Review Investment Advisers Act of 1940
- [ ] Ensure compliance with SEC Regulation Best Interest
- [ ] Consider "robo-advisor" regulations
- [ ] May require SEC registration if providing "personalized advice"

**Mitigation**: Current design avoids personalized recommendations by using conditional language and disclaimers.

---

## Documentation Maintenance

### Review Schedule
- **Quarterly**: Review disclaimer text
- **After updates**: Audit new features for compliance
- **Annually**: Full legal review

### Version Control
- Current version: `1.0.0`
- Last updated: January 2026
- Next review: April 2026

---

## Contact & Questions

**For legal compliance questions**:
1. Review this documentation
2. Check disclaimer text in code
3. Verify UI labels
4. Consult legal counsel if uncertain

**For implementation questions**:
1. See [README.md](../README.md)
2. Check [MCP_TRIGGER_LOGIC.md](../backend/app/core/context_agent/MCP_TRIGGER_LOGIC.md)
3. Review API documentation

---

## Appendix: Key Files

### Disclaimers
- Backend: `backend/app/config/settings.py` (line 73)
- Frontend footer: `frontend/components/ui/footer.tsx`
- Registration: `frontend/app/register/page.tsx`
- MCP models: `backend/app/core/context_agent/models.py`

### Language Implementation
- Portfolio suggestions: `backend/app/api/v1/portfolio.py` (lines 620-858)
- Enhanced analysis: `backend/app/api/v1/enhanced.py` (lines 250-280)
- LLM system prompt: `backend/app/api/v1/portfolio.py` (lines 745-778)

### UI Labels
- Market Context section: `frontend/app/dashboard/analysis/page.tsx`
- Analysis page: `frontend/app/dashboard/analysis/page.tsx`
- Portfolio suggestions: `frontend/app/dashboard/portfolio/suggestions/page.tsx`

---

**Last Updated**: January 3, 2026  
**Version**: 1.0  
**Status**: Production Ready ✅

**IMPORTANT**: This document does NOT constitute legal advice. Consult qualified legal counsel for specific compliance questions.
