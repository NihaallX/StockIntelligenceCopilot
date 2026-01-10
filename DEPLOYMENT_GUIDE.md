# 🚀 Deployment Guide - Stock Intelligence Copilot

## Overview
- **Frontend**: Next.js → Vercel
- **Backend**: FastAPI → Vercel (Serverless Functions)
- **Database**: Supabase (already cloud-hosted)
- **Cost**: 100% FREE (Vercel free tier)

---

## 📦 Step 1: Prepare for Deployment

### 1.1 Create GitHub Repository
1. Initialize git in your project (if not already done):
```bash
git init
git add .
git commit -m "Initial commit"
```

2. Create a repository on GitHub
3. Push your code:
```bash
git remote add origin https://github.com/yourusername/stock-intelligence-copilot.git
git branch -M main
git push -u origin main
```

### 1.2 Update .gitignore
Make sure your `.gitignore` includes:
```
.env
.env.local
.env.production
node_modules/
.venv/
__pycache__/
.next/
```

---

## 🌐 Step 2: Deploy to Vercel (Frontend + Backend)

### 2.1 Sign Up for Vercel
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "Add New..." → "Project"

### 2.2 Import Repository
1. Select your GitHub repository
2. Vercel will auto-detect Next.js configuration

### 2.3 Configure Project Settings
- **Framework Preset**: Next.js
- **Root Directory**: Leave as `/` (monorepo)
- **Build Command**: `cd frontend && npm run build`
- **Output Directory**: `frontend/.next`
- **Install Command**: `cd frontend && npm install`

### 2.4 Configure Environment Variables
In Vercel → Settings → Environment Variables, add ALL of these:

```bash
# Supabase
SUPABASE_URL=https://qbjidkkkryokdcpunblw.supabase.co
SUPABASE_ANON_KEY=<your-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>

# JWT
JWT_SECRET_KEY=<your-secret-key>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# LLM
GROQ_API_KEY=<your-groq-key>
GROQ_MODEL=llama-3.1-70b-versatile

# OpenRouter (optional)
OPENROUTER_API_KEY=<your-openrouter-key>
OPENROUTER_MODEL=xiaomi/mimo-v2-flash:free
LLM_EXPLANATIONS_ENABLED=true

# Application
ENVIRONMENT=production
DEBUG=false
API_V1_PREFIX=/api/v1

# Data Provider
DATA_PROVIDER=live
FMP_API_KEY=<your-fmp-key>
CACHE_TTL_INTRADAY=300
CACHE_TTL_HISTORICAL=86400

# CORS - Add your Vercel domain
BACKEND_CORS_ORIGINS=["https://your-app.vercel.app","http://localhost:3000"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
LOGIN_RATE_LIMIT_PER_15_MIN=5

# Compliance
TERMS_VERSION=1.0.0
AUDIT_LOG_RETENTION_YEARS=7
```

**IMPORTANT**: Set these for "Production" environment:

```bash
# Frontend Environment Variable
NEXT_PUBLIC_API_URL=https://your-app.vercel.app/api

# Backend Environment Variables (for Vercel serverless)
SUPABASE_URL=https://qbjidkkkryokdcpunblw.supabase.co
SUPABASE_ANON_KEY=<paste-from-your-.env>
SUPABASE_SERVICE_ROLE_KEY=<paste-from-your-.env>

JWT_SECRET_KEY=<paste-from-your-.env>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

GROQ_API_KEY=<paste-from-your-.env>
GROQ_MODEL=llama-3.1-70b-versatile

OPENROUTER_API_KEY=<paste-from-your-.env>
OPENROUTER_MODEL=xiaomi/mimo-v2-flash:free
LLM_EXPLANATIONS_ENABLED=true

ENVIRONMENT=production
DEBUG=false
API_V1_PREFIX=/api/v1

DATA_PROVIDER=live
FMP_API_KEY=<paste-from-your-.env>
CACHE_TTL_INTRADAY=300
CACHE_TTL_HISTORICAL=86400

BACKEND_CORS_ORIGINS=["https://your-app.vercel.app"]
RATE_LIMIT_PER_MINUTE=60
LOGIN_RATE_LIMIT_PER_15_MIN=5

TERMS_VERSION=1.0.0
AUDIT_LOG_RETENTION_YEARS=7
```

**Note**: Replace `https://your-app.vercel.app` with your actual Vercel URL after first deployment.

### 2.5 Deploy
Click "Deploy" and wait for build to complete.

You'll get a URL like:
```
https://stock-intelligence-copilot.vercel.app
```

---

## 🔄 Step 3: Update CORS and API URL

### 3.1 Update Environment Variables
After first deployment, go back to Vercel:

1. **Update NEXT_PUBLIC_API_URL**:
   - Change to: `https://your-actual-vercel-url.vercel.app/api`

2. **Update BACKEND_CORS_ORIGINS**:
   - Change to: `["https://your-actual-vercel-url.vercel.app"]`

### 3.2 Redeploy API
Visit: `https://your-app.vercel.app/api/health`

You should see: `{"status": "healthy"}`

### 4.2 Test Frontend
Visit: `https://your-app.vercel.app`

Try:
- Creating an account
- Logging in
- Viewing portfolio
- Checking Today's Watch

### 4.3 Check Logs
- **Vercel**: Settings → Logs
- View function invocations, errors, and performance
Visit: `https://your-app.vercel.app`

Try logging in and accessing features.

### 4.3 Check Logs
- **Railway**: View logs in Railway dashboard
- **Vercel**: View logs in Vercel dashboard

---

## 🎨 Optional: Custom Domain

### Frontend (Vercel)
1. Vercel →
Backend shares the same domain (Vercel handles routing via `/api/*`)
1. Railway → Settings → Domains
2. Add custom domain
3. Update DNS records
4. Update `NEXT_PUBLIC_API_URL` in Vercel

---

## 🔐 Security Checklist

- [ ] Changed `JWT_SECRET_KEY` to a new random value
- [ ] Set `DEBUG=false` in production
- [ ] Added production URLs to CORS origins
- [ ] Secured API keys (not committed to Git)
- [ ] Enabled HTTPS only
- [ ] Set up Supabase RLS (Row Level Security)

---

## 📊 Monitoring

### Backend Health Check
```bash
curl https://your-backend-url.up.railway.app/health
```

### Frontend
Vercel provides automatic monitoring in dashboard.

---

## 🚨 Troubleshooting

### Backend Issues
- Check Railway logs
- Verify all environment variables are set
- Test `/heaAPI Issues
- Check Vercel → Functions logs
- Verify all environment variables are set
- Test `/api/health` endpoint
- Check cold start times (first request may be slow)

### Frontend Issues
- Check Vercel build logs
- Verify `NEXT_PUBLIC_API_URL` ends with `/api`
- Check browser console for errors

### CORS Errors
- Verify `BACKEND_CORS_ORIGINS` matches your Vercel URL exactly
- No trailing slashes in URLs
- Redeploy after changing environment variables

### Database Connection
- Verify Supabase credentials are correct
- Check Supabase dashboard for connection errors
- Test with a simple query from Vercel Functions logs

### 100% FREE with these limits:
- **Vercel**: 
  - 100GB bandwidth/month
  - 100GB-hours serverless function execution
  - Unlimited API requests
  - Unlimited deployments
- **Supabase**: 
  - 500MB database
  - 2GB bandwidth/month
  - 50MB file storage

### Expected Usage:
- **Single user**: Well within free tier
- **Light usage (5-10 users)**: Still free
- **Heavy usage**: May need Vercel Pro ($20/month) for more bandwidth
- **Railway**: $5 free credit/month (~500 hours)
- **Supabase**: 500MB database, 2GB bandwidth/month

### Expected Usage:
Vercel auto-deploys everything on Git push:
1. Push to `main` branch
2. Vercel builds frontend and backend automatically
3. Both frontend and API routes update together
4. Preview deployments for branches (free)

## 🔄 Continuous Deployment

Both Vercel and Railway auto-deploy on Git push:
1. PAll in Vercel (Production Environment):

**Frontend:**
- `NEXT_PUBLIC_API_URL` - Points to `/api` (same domain)

**Backend (Serverless Functions):**
- Supabase credentials
- JWT secrets
- API keys (Groq, FMP, OpenRouter)
- CORS origins
- Feature flags
- App configuration
- Supabase credentials
- JWT secrets
- API keys (Groq, FMP, OpenRouter)
- CORS origins
- Feature flags

### Frontend (Vercel)
- `NEXT_PUBLIC_API_URL` only

---Push code to GitHub
2. Connect Vercel to your GitHub repo
3. Configure environment variables
4. Deploy (Vercel handles both frontend + backend)
5. Update CORS with your Vercel URL
6. Test live deployment
7. (Optional) Add custom domain
8. Monitor usage and logs

---

## ⚡ Vercel Serverless Function Limits

### Free Tier:
- **10 second timeout** per function
- **50MB max deployment size** per function
- **4.5MB max request body**
- **6MB max response body**

### Tips:
- FastAPI responses are typically < 1MB (OK)
- Most queries complete in < 2s (OK)
- Cache expensive operations
- Use background jobs for long tasks (if needed)

---

## 📞 Support

- Vercel: [vercel.com/docs](https://vercel.com/docs)
- Supabase: [supabase.com/docs](https://supabase.com/docs)
- FastAPI on Vercel: [vercel.com/docs/concepts/functions/serverless-functions/runtimes/python](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python

- Railway: [docs.railway.app](https://docs.railway.app)
- Vercel: [vercel.com/docs](https://vercel.com/docs)
- Supabase: [supabase.com/docs](https://supabase.com/docs)
