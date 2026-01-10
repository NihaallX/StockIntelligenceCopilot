# Vercel Environment Variables Setup

Your app is deployed at: **https://stock-intelligence-copilot.vercel.app/**

## Required Environment Variables

Go to your Vercel project → Settings → Environment Variables and add these:

### Database (Supabase)
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

### Authentication
```
JWT_SECRET_KEY=your_generated_secret_key_min_32_chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

### LLM Services
```
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-70b-versatile
OPENROUTER_API_KEY=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
OPENROUTER_MODEL=xiaomi/mimo-v2-flash:free
LLM_EXPLANATIONS_ENABLED=true
```

### Market Data
```
FMP_API_KEY=qty5ZwSYBANWmtoWHYi1zfE8zDbKXXOV
DATA_PROVIDER=live
MCP_PROVIDER=yahoo
```

### Application Settings
```
ENVIRONMENT=production
DEBUG=false
BACKEND_CORS_ORIGINS=["https://stock-intelligence-copilot.vercel.app"]
```

### Frontend Environment
```
NEXT_PUBLIC_API_URL=/api
```

## Quick Setup Steps

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com/dashboard
   - Select your project: stock-intelligence-copilot

2. **Add Environment Variables**
   - Settings → Environment Variables
   - Add each variable above
   - Apply to: Production, Preview, Development

3. **Redeploy**
   - Go to Deployments tab
   - Click "..." on latest deployment
   - Click "Redeploy"

4. **Test**
   - Visit: https://stock-intelligence-copilot.vercel.app/api/health
   - Should return: `{"status":"healthy","version":"0.2.0"}`
   - Then test frontend login

## Important Notes

⚠️ **Without these environment variables, the backend will fail to start**
- Database connections will fail
- Authentication won't work
- Market data APIs won't function

✅ **After setting variables:**
- Redeploy the application
- Wait 2-3 minutes for deployment to complete
- Test the /api/health endpoint first
- Then test the frontend

## Generate JWT Secret

Run this to generate a secure JWT secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Get Your API Keys

- **Supabase**: https://supabase.com/dashboard (free tier)
- **Groq**: https://console.groq.com (free tier)
- **OpenRouter**: Already included (free model)
- **FMP**: Already included (working key)
