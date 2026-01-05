# Phase 2B - Database Migration Instructions

## Run Migration 002

**Before testing Phase 2B features, you must run the database migration.**

### Steps:

1. **Open Supabase SQL Editor:**
   - Go to https://supabase.com/dashboard/project/qbjidkkkryokdcpunblw/sql
   - Or navigate: Dashboard → SQL Editor → New Query

2. **Copy Migration SQL:**
   - Open: `database/migrations/002_phase2b_portfolio.sql`
   - Copy entire contents (Ctrl+A, Ctrl+C)

3. **Execute Migration:**
   - Paste into SQL Editor
   - Click "Run" button
   - Wait for success confirmation

4. **Verify Tables Created:**
   ```sql
   SELECT * FROM information_schema.tables 
   WHERE table_schema = 'public' 
   AND table_name IN ('portfolio_positions', 'fundamental_data');
   ```

5. **Verify Seed Data:**
   ```sql
   SELECT ticker, company_name, pe_ratio, market_cap 
   FROM fundamental_data 
   ORDER BY market_cap DESC;
   ```
   - Should return 10 stocks: AAPL, MSFT, GOOGL, TSLA, AMZN, NVDA, META, JPM, V, WMT

## What This Migration Creates:

### Table: portfolio_positions
- User stock holdings tracking
- Columns: ticker, quantity, entry_price, current_price, unrealized_pnl
- RLS enabled: Users can only see their own positions

### Table: fundamental_data
- Company financial metrics
- Columns: P/E ratio, market cap, growth rates, margins, ROE, debt ratios
- Seeded with 10 major stocks for testing

## Phase 2B Features Now Available:

### 1. Portfolio Tracking
- **POST /api/v1/portfolio/positions** - Add stock position
- **GET /api/v1/portfolio/positions** - List all positions
- **PATCH /api/v1/portfolio/positions/{id}** - Update position
- **DELETE /api/v1/portfolio/positions/{id}** - Remove position
- **GET /api/v1/portfolio/summary** - Aggregate portfolio stats

### 2. Enhanced Analysis
- **POST /api/v1/analysis/enhanced** - Combined technical + fundamental + scenario analysis
- Includes:
  - Technical indicators (existing)
  - Fundamental score (valuation, growth, profitability, financial health)
  - Scenario analysis (best/base/worst case with probabilities)
  - Combined score and actionable recommendation

## Testing Checklist:

```bash
# After migration, restart server
cd "D:\Stock Intelligence Copilot"
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload

# Test portfolio endpoints:
# 1. Add position (use your JWT token)
# POST /api/v1/portfolio/positions
{
  "ticker": "AAPL",
  "quantity": 10,
  "entry_price": 150.00,
  "entry_date": "2024-01-15",
  "notes": "Test position"
}

# 2. Get portfolio summary
# GET /api/v1/portfolio/summary

# Test enhanced analysis:
# POST /api/v1/analysis/enhanced
{
  "ticker": "AAPL",
  "include_fundamentals": true,
  "include_scenarios": true,
  "time_horizon": "long_term",
  "risk_tolerance": "moderate"
}
```

## Expected Results:

### Enhanced Analysis for AAPL:
- **Technical**: Signal + indicators (existing)
- **Fundamentals**: Score ~75/100 (Strong valuation, high P/E 28.5, excellent profitability)
- **Scenarios**: 
  - Best case: +40% upside (25% probability)
  - Base case: +15% (50% probability)
  - Worst case: -20% (25% probability)
  - Risk/reward: ~2:1
- **Recommendation**: "BUY - Positive signals align. Consider position sizing."

## Troubleshooting:

**Migration fails:**
- Check if tables already exist (drop them first if needed)
- Ensure RLS is enabled on your Supabase project
- Verify you're using service role key

**No fundamental data:**
- Run query to verify seed data exists
- Check fundamental_data table has 10 rows
- Ensure AAPL, MSFT, GOOGL etc are present

**Portfolio endpoints return empty:**
- User must add positions first via POST endpoint
- RLS ensures users only see their own data
- Check authentication token is valid

## Next Steps After Migration:

1. ✅ Test portfolio CRUD operations
2. ✅ Test enhanced analysis with AAPL (has fundamentals)
3. ✅ Verify audit logs for all operations
4. 🔄 Add Groq LLM integration for AI-powered insights (Phase 2C)
5. 🔄 Add real-time fundamental data provider integration
6. 🔄 Add portfolio risk analysis endpoint
