# Quick Start - Deploy to Vercel (100% Free)

## One-Time Setup (5 minutes)

### 1. Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2. Deploy to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "Add New Project"
4. Select your repo
5. Configure:
   - Root: `/`
   - Build: `cd frontend && npm run build`
   - Output: `frontend/.next`

### 3. Add Environment Variables in Vercel
Copy ALL variables from your `.env` file to Vercel:

**Go to**: Project → Settings → Environment Variables

```bash
# Copy these from your .env file:
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
JWT_SECRET_KEY=...
GROQ_API_KEY=...
FMP_API_KEY=...
OPENROUTER_API_KEY=...

# Frontend variable:
NEXT_PUBLIC_API_URL=/api

# Backend config:
BACKEND_CORS_ORIGINS=["https://your-app.vercel.app"]
ENVIRONMENT=production
DEBUG=false
```

### 4. Deploy
Click "Deploy" - done! 🎉

### 5. After First Deploy
Update `BACKEND_CORS_ORIGINS` with your actual Vercel URL:
```
["https://your-actual-url.vercel.app"]
```

---

## That's It! 

Your app is now live at: `https://your-app.vercel.app`

- Frontend: `https://your-app.vercel.app`
- Backend API: `https://your-app.vercel.app/api`

100% free, auto-deploys on every git push!

---

## Troubleshooting

**CORS errors?** 
→ Make sure `BACKEND_CORS_ORIGINS` matches your Vercel URL exactly

**API not working?**
→ Check Vercel → Functions logs for errors

**Need help?**
→ See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed instructions
