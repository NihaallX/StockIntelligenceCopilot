# ✅ Pre-Deployment Checklist

## Before Pushing to GitHub

### 1. Sensitive Data
- [ ] `.env` is in `.gitignore`
- [ ] No API keys committed to code
- [ ] No passwords in plain text
- [ ] Supabase credentials only in `.env`

### 2. Environment Files
- [ ] `.env` has all required variables
- [ ] `frontend/.env.production` created
- [ ] Ready to copy values to Vercel dashboard

### 3. Git Setup
- [ ] Git initialized (`git init`)
- [ ] GitHub repository created
- [ ] All files committed
- [ ] Pushed to `main` branch

### 4. Dependencies
- [ ] `frontend/package.json` exists
- [ ] `backend/requirements.txt` exists
- [ ] All dependencies listed

### 5. Configuration Files
- [ ] `vercel.json` in root
- [ ] `backend/vercel.json` exists
- [ ] `.vercelignore` configured

---

## Deployment Steps

### 1. Vercel Account
- [ ] Signed up at vercel.com
- [ ] Connected GitHub account

### 2. Import Project
- [ ] Selected repository
- [ ] Framework: Next.js detected
- [ ] Root directory: `/`
- [ ] Build command: `cd frontend && npm run build`
- [ ] Output directory: `frontend/.next`

### 3. Environment Variables
Copy from `.env` to Vercel dashboard:

**Required Variables:**
- [ ] `SUPABASE_URL`
- [ ] `SUPABASE_ANON_KEY`
- [ ] `SUPABASE_SERVICE_ROLE_KEY`
- [ ] `JWT_SECRET_KEY`
- [ ] `JWT_ALGORITHM`
- [ ] `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
- [ ] `JWT_REFRESH_TOKEN_EXPIRE_DAYS`
- [ ] `GROQ_API_KEY`
- [ ] `GROQ_MODEL`
- [ ] `FMP_API_KEY`
- [ ] `OPENROUTER_API_KEY` (optional)
- [ ] `OPENROUTER_MODEL` (optional)
- [ ] `LLM_EXPLANATIONS_ENABLED`
- [ ] `NEXT_PUBLIC_API_URL=/api`
- [ ] `BACKEND_CORS_ORIGINS=["https://your-app.vercel.app"]`
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=false`
- [ ] `DATA_PROVIDER=live`
- [ ] `API_V1_PREFIX=/api/v1`

### 4. Deploy
- [ ] Clicked "Deploy"
- [ ] Build successful
- [ ] No errors in logs

### 5. Post-Deployment
- [ ] Got Vercel URL
- [ ] Updated `BACKEND_CORS_ORIGINS` with actual URL
- [ ] Tested `/api/health` endpoint
- [ ] Tested login functionality
- [ ] Checked Today's Watch page
- [ ] Verified auto-refresh works

---

## Testing Checklist

### API Endpoints
- [ ] `https://your-app.vercel.app/api/health` returns 200
- [ ] `https://your-app.vercel.app/api/v1/auth/register` works
- [ ] `https://your-app.vercel.app/api/v1/auth/login` works

### Frontend
- [ ] Homepage loads
- [ ] Can create account
- [ ] Can login
- [ ] Dashboard shows data
- [ ] Today's Watch displays
- [ ] Opportunities page works
- [ ] Auto-refresh functions

### Performance
- [ ] First load < 3s
- [ ] API responses < 2s
- [ ] No CORS errors
- [ ] No 500 errors

---

## If Something Fails

### Build Errors
→ Check Vercel build logs
→ Verify `package.json` and `requirements.txt`

### API Errors
→ Check Vercel Functions logs
→ Verify environment variables

### CORS Errors
→ Update `BACKEND_CORS_ORIGINS`
→ Redeploy

### Database Errors
→ Check Supabase dashboard
→ Verify credentials

---

## Success!

If all checks pass, your app is live! 🎉

Share your URL: `https://your-app.vercel.app`
