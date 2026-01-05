-- Phase 2A Database Schema Migration
-- Run this in Supabase SQL Editor
-- Created: 2026-01-01

-- =====================================================
-- 1. USERS TABLE (extends Supabase auth.users)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supabase_auth_id UUID UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Compliance fields
    terms_accepted_at TIMESTAMP WITH TIME ZONE NOT NULL,
    terms_version VARCHAR(20) NOT NULL,
    risk_acknowledgment_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    CONSTRAINT users_email_valid CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_supabase_auth_id ON public.users(supabase_auth_id);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON public.users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON public.users(is_active);

-- Enable Row Level Security
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view their own data"
    ON public.users FOR SELECT
    USING (auth.uid() = supabase_auth_id);

CREATE POLICY "Users can update their own data"
    ON public.users FOR UPDATE
    USING (auth.uid() = supabase_auth_id);

-- =====================================================
-- 2. USER RISK PROFILES
-- =====================================================
CREATE TABLE IF NOT EXISTS public.user_risk_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Risk tolerance
    risk_tolerance VARCHAR(20) NOT NULL DEFAULT 'conservative',
    
    -- Position limits (per stock)
    max_position_size_usd NUMERIC(15, 2) NOT NULL DEFAULT 10000.00,
    max_position_size_percent NUMERIC(5, 2) NOT NULL DEFAULT 5.00,
    
    -- Portfolio limits
    max_total_exposure_usd NUMERIC(15, 2) NOT NULL DEFAULT 100000.00,
    max_capital_at_risk_percent NUMERIC(5, 2) NOT NULL DEFAULT 2.00,
    
    -- Drawdown protection
    max_drawdown_percent NUMERIC(5, 2) NOT NULL DEFAULT 20.00,
    
    -- Asset class toggles
    allow_high_volatility_stocks BOOLEAN DEFAULT FALSE,
    allow_penny_stocks BOOLEAN DEFAULT FALSE,
    allow_international_stocks BOOLEAN DEFAULT TRUE,
    allowed_sectors JSONB DEFAULT '[]'::jsonb,
    excluded_sectors JSONB DEFAULT '[]'::jsonb,
    
    -- Time horizon
    preferred_time_horizon VARCHAR(20) DEFAULT 'long_term',
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    version INTEGER DEFAULT 1,
    
    -- Constraints
    CONSTRAINT user_risk_profiles_unique_user UNIQUE(user_id),
    CONSTRAINT risk_tolerance_check CHECK (risk_tolerance IN ('conservative', 'moderate', 'aggressive')),
    CONSTRAINT max_position_size_percent_check CHECK (max_position_size_percent > 0 AND max_position_size_percent <= 100),
    CONSTRAINT max_capital_at_risk_percent_check CHECK (max_capital_at_risk_percent > 0 AND max_capital_at_risk_percent <= 100),
    CONSTRAINT max_drawdown_percent_check CHECK (max_drawdown_percent > 0 AND max_drawdown_percent <= 100),
    CONSTRAINT preferred_time_horizon_check CHECK (preferred_time_horizon IN ('long_term', 'medium_term'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_user_risk_profiles_user_id ON public.user_risk_profiles(user_id);

-- Enable RLS
ALTER TABLE public.user_risk_profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view their own risk profile"
    ON public.user_risk_profiles FOR SELECT
    USING (user_id IN (SELECT id FROM public.users WHERE supabase_auth_id = auth.uid()));

CREATE POLICY "Users can update their own risk profile"
    ON public.user_risk_profiles FOR UPDATE
    USING (user_id IN (SELECT id FROM public.users WHERE supabase_auth_id = auth.uid()));

-- =====================================================
-- 3. AUDIT LOGS (IMMUTABLE)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Event identification
    event_type VARCHAR(50) NOT NULL,
    
    -- User context
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    session_id UUID,
    
    -- Request context
    ip_address INET,
    user_agent TEXT,
    
    -- Event data (immutable)
    input_data JSONB NOT NULL,
    input_hash VARCHAR(64) NOT NULL,
    output_data JSONB NOT NULL,
    output_hash VARCHAR(64) NOT NULL,
    
    -- Analysis metadata
    ticker VARCHAR(10),
    signal_type VARCHAR(20),
    confidence_score NUMERIC(5, 4),
    risk_level VARCHAR(20),
    was_actionable BOOLEAN,
    
    -- Timestamps (immutable)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Compliance metadata
    compliance_version VARCHAR(20) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    
    -- Additional context
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Constraints
    CONSTRAINT event_type_check CHECK (event_type IN (
        'signal_generated',
        'risk_assessment_performed',
        'recommendation_issued',
        'user_login',
        'user_logout',
        'risk_profile_updated',
        'portfolio_position_added',
        'portfolio_position_removed',
        'analysis_requested'
    ))
);

-- Indexes for querying
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON public.audit_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type ON public.audit_logs(event_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_ticker ON public.audit_logs(ticker, created_at DESC) WHERE ticker IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON public.audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_session_id ON public.audit_logs(session_id) WHERE session_id IS NOT NULL;

-- Enable RLS (admin only can read audit logs)
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policy - users cannot access audit logs directly (backend only)
CREATE POLICY "Service role only can access audit logs"
    ON public.audit_logs FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- =====================================================
-- 4. TRIGGERS FOR UPDATED_AT
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_risk_profiles_updated_at
    BEFORE UPDATE ON public.user_risk_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 5. DEFAULT RISK PROFILE CREATION TRIGGER
-- =====================================================
CREATE OR REPLACE FUNCTION create_default_risk_profile()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_risk_profiles (
        user_id,
        risk_tolerance,
        max_position_size_usd,
        max_position_size_percent,
        max_total_exposure_usd,
        max_capital_at_risk_percent,
        max_drawdown_percent,
        allow_high_volatility_stocks,
        allow_penny_stocks,
        allow_international_stocks,
        preferred_time_horizon
    ) VALUES (
        NEW.id,
        'conservative',
        10000.00,
        5.00,
        100000.00,
        2.00,
        20.00,
        FALSE,
        FALSE,
        TRUE,
        'long_term'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER create_user_default_risk_profile
    AFTER INSERT ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION create_default_risk_profile();

-- =====================================================
-- 6. GRANT PERMISSIONS
-- =====================================================
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT SELECT, INSERT, UPDATE ON public.users TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.user_risk_profiles TO authenticated;
GRANT SELECT ON public.audit_logs TO service_role;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================
-- Verify tables created:
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
