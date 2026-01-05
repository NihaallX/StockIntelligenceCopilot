# 🔌 Data Sources & API Keys Reference

## Current Setup (What You're Using Right Now)

### 1️⃣ **Market Data (Price History, Technical Indicators)**

| Source | Used For | API Key Needed? | Status |
|--------|----------|-----------------|--------|
| **Yahoo Finance (yfinance)** | Indian stocks (.NS, .BO) | ❌ NO | ✅ **ACTIVE** |
| **Alpha Vantage** | US stocks (AAPL, TSLA, etc.) | ✅ YES | ⚠️ Only if analyzing US stocks |

**What this means:**
- ✅ **Indian stocks work out of the box** (RELIANCE.NS, TCS.NS, etc.)
- ⚠️ US stocks need Alpha Vantage API key (free: 25 calls/day)

---

### 2️⃣ **Fundamental Data (Financial Statements, Ratios)**

| Source | Used For | API Key Needed? | Status |
|--------|----------|-----------------|--------|
| **FMP (Financial Modeling Prep)** | Company financials, ratios | ✅ YES | ⚠️ **OPTIONAL** |
| **Database Cache** | Cached fundamentals | ❌ NO | ✅ Fallback |

**What this means:**
- ⚠️ **FMP API key is OPTIONAL** (free tier: 250 calls/day)
- ❌ **Without FMP:** You see "Limited Fundamental Data" warning
- ✅ **System still works** using technical analysis only

---

### 3️⃣ **Market Context / News (MCP - Citations)**

| Source | Used For | API Key Needed? | Status |
|--------|----------|-----------------|--------|
| **Moneycontrol** | Indian stock news | ❌ NO | ⚠️ Blocked (403) |
| **Economic Times** | Indian financial news | ❌ NO | 📝 Placeholder |
| **NSE India** | Official announcements | ❌ NO | 📝 Placeholder |
| **BSE India** | Official announcements | ❌ NO | 📝 Placeholder |

**What this means:**
- ⚠️ **Moneycontrol is blocked** (anti-bot protection)
- 📝 **Other sources are placeholders** (not implemented)
- ✅ **System works without MCP** (graceful degradation)

---

## 🔑 API Keys You Need (Current Setup)

### **Required: None! ✅**
Your system works right now for Indian stocks without any API keys.

### **Optional (Recommended):**

#### **FMP (Financial Modeling Prep)** - For Fundamental Data
```bash
# Get free key at: https://site.financialmodelingprep.com/developer/docs
# Free tier: 250 API calls/day
# Add to backend/.env:
FMP_API_KEY=your_key_here
```

**Benefits:**
- ✅ Company financial statements (balance sheet, income, cash flow)
- ✅ Financial ratios (P/E, debt/equity, ROE, etc.)
- ✅ Better analysis quality
- ✅ Supports NSE/BSE stocks

**Without it:**
- ⚠️ Technical analysis only (still works!)
- ⚠️ "Limited Fundamental Data" warning shows

---

#### **Alpha Vantage** - For US Stocks (If Needed)
```bash
# Get free key at: https://www.alphavantage.co/support/#api-key
# Free tier: 25 API calls/day (5 per minute)
# Add to backend/.env:
ALPHA_VANTAGE_API_KEY=your_key_here
```

**Benefits:**
- ✅ Analyze US stocks (AAPL, MSFT, TSLA, etc.)
- ✅ Real-time US market data

**Without it:**
- ✅ Indian stocks still work (using yfinance)
- ❌ US stocks won't work

---

## 📝 How to Add API Keys

### **Step 1: Create .env file**
```bash
cd "D:\Stock Intelligence Copilot\backend"
notepad .env
```

### **Step 2: Add keys**
```bash
# Database (already configured)
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_SERVICE_KEY=...

# Optional: FMP for fundamentals
FMP_API_KEY=your_fmp_key_here

# Optional: Alpha Vantage for US stocks
ALPHA_VANTAGE_API_KEY=your_av_key_here
```

### **Step 3: Restart backend**
```bash
# Stop with Ctrl+C, then restart:
& "D:/Stock Intelligence Copilot/.venv/Scripts/python.exe" -m uvicorn app.main:app --reload
```

---

## 🎯 What You Should Do

### **Option A: Use As-Is (Recommended for Testing)**
✅ **No API keys needed**
- Works for Indian stocks (NSE/BSE)
- Technical analysis fully functional
- Scenario analysis works
- Some features limited (fundamentals, MCP context)

### **Option B: Add FMP (Recommended for Production)**
💰 **Free tier: 250 calls/day**
- Get key: https://site.financialmodelingprep.com/developer/docs
- Add to `.env`: `FMP_API_KEY=your_key`
- Restart backend
- **Result**: Full fundamental analysis for Indian stocks!

### **Option C: Add Both FMP + Alpha Vantage (Full Featured)**
💰 **Both free tiers**
- FMP: 250 calls/day
- Alpha Vantage: 25 calls/day
- Add both to `.env`
- Restart backend
- **Result**: Analyze both Indian AND US stocks with fundamentals!

---

## 🐛 Current Warnings Explained

### **"No fundamental data found for RELIANCE.NS"**
- **Cause**: FMP_API_KEY not configured
- **Impact**: Technical analysis only (still works!)
- **Fix**: Add FMP API key (optional)

### **"Moneycontrol returned status 403"**
- **Cause**: Moneycontrol blocking web scraper (anti-bot)
- **Impact**: No MCP context/citations (system designed to handle this)
- **Fix**: Use official APIs or paid aggregators (Task #9 decision)

---

## 💡 My Recommendation

**Start with Option A (No API keys)**:
1. Test everything with Indian stocks
2. Verify technical + scenario analysis works
3. Decide if you need fundamentals

**If you like it, upgrade to Option B**:
1. Get free FMP key (5 minutes)
2. Add to `.env`
3. Get full fundamental analysis!

**Total cost: $0** ✅

---

## 📊 Feature Matrix

| Feature | No API Keys | + FMP | + FMP + AlphaVantage |
|---------|-------------|-------|---------------------|
| Indian stock analysis | ✅ | ✅ | ✅ |
| US stock analysis | ❌ | ❌ | ✅ |
| Technical indicators | ✅ | ✅ | ✅ |
| Scenario analysis | ✅ | ✅ | ✅ |
| Fundamental scoring | ⚠️ Limited | ✅ Full | ✅ Full |
| MCP citations | ⚠️ Blocked | ⚠️ Blocked | ⚠️ Blocked |
| Cost | Free | Free | Free |

**Note**: MCP citations need different solution (Task #9) - not related to FMP/AlphaVantage.

---

## 🚀 Quick Start Commands

### **Get FMP Key (2 minutes):**
1. Visit: https://site.financialmodelingprep.com/developer/docs
2. Sign up (free)
3. Copy API key
4. Add to `backend/.env`: `FMP_API_KEY=your_key`
5. Restart backend

### **Get Alpha Vantage Key (2 minutes):**
1. Visit: https://www.alphavantage.co/support/#api-key
2. Enter email
3. Copy API key
4. Add to `backend/.env`: `ALPHA_VANTAGE_API_KEY=your_key`
5. Restart backend

---

**Bottom line: You don't NEED any API keys right now. Your system works for Indian stocks without them!** ✅
