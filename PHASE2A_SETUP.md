# Phase 2A Setup Instructions

## Step 1: Run Database Migration

1. Go to your Supabase Dashboard: https://supabase.com/dashboard/project/qbjidkkkryokdcpunblw

2. Navigate to **SQL Editor** in the left sidebar

3. Click **"New Query"**

4. Copy the entire contents of `database/migrations/001_phase2a_schema.sql`

5. Paste into the SQL editor and click **"Run"**

6. Verify tables were created by going to **Table Editor** - you should see:
   - `users`
   - `user_risk_profiles`
   - `audit_logs`

## Step 2: Verify Environment Variables

Check that `.env` file contains:

```
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
GROQ_API_KEY=your_groq_api_key_here
```

## Step 3: Install Dependencies

Dependencies already installed:
- ✅ supabase
- ✅ python-jose[cryptography]
- ✅ passlib[bcrypt]  
- ✅ python-multipart
- ✅ groq
- ✅ python-dotenv

## Step 4: Test Authentication System

After completing steps 1-2, the system is ready for testing!

## Next Steps

I'll now create:
1. Auth API endpoints (register, login, logout, refresh)
2. Authentication middleware
3. User risk profile models
4. Integration with existing risk engine

Ready to proceed? ✅
