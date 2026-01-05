-- Phase 2B: Portfolio Tracking Tables
-- Add to existing Supabase database

-- =====================================================
-- PORTFOLIO POSITIONS
-- =====================================================
CREATE TABLE IF NOT EXISTS public.portfolio_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Position details
    ticker VARCHAR(10) NOT NULL,
    quantity NUMERIC(15, 4) NOT NULL CHECK (quantity > 0),
    entry_price NUMERIC(15, 4) NOT NULL CHECK (entry_price > 0),
    entry_date DATE NOT NULL,
    notes TEXT,
    
    -- Calculated fields (updated periodically)
    current_price NUMERIC(15, 4),
    current_value NUMERIC(15, 2),
    cost_basis NUMERIC(15, 2),
    unrealized_pnl NUMERIC(15, 2),
    unrealized_pnl_percent NUMERIC(8, 4),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_price_update TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT portfolio_positions_user_ticker_unique UNIQUE(user_id, ticker)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_portfolio_positions_user_id ON public.portfolio_positions(user_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_positions_ticker ON public.portfolio_positions(ticker);
CREATE INDEX IF NOT EXISTS idx_portfolio_positions_entry_date ON public.portfolio_positions(entry_date DESC);

-- Enable RLS
ALTER TABLE public.portfolio_positions ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view their own positions"
    ON public.portfolio_positions FOR SELECT
    USING (user_id IN (SELECT id FROM public.users WHERE supabase_auth_id = auth.uid()));

CREATE POLICY "Users can insert their own positions"
    ON public.portfolio_positions FOR INSERT
    WITH CHECK (user_id IN (SELECT id FROM public.users WHERE supabase_auth_id = auth.uid()));

CREATE POLICY "Users can update their own positions"
    ON public.portfolio_positions FOR UPDATE
    USING (user_id IN (SELECT id FROM public.users WHERE supabase_auth_id = auth.uid()));

CREATE POLICY "Users can delete their own positions"
    ON public.portfolio_positions FOR DELETE
    USING (user_id IN (SELECT id FROM public.users WHERE supabase_auth_id = auth.uid()));

-- Trigger for updated_at
CREATE TRIGGER update_portfolio_positions_updated_at
    BEFORE UPDATE ON public.portfolio_positions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- FUNDAMENTAL DATA CACHE (for mock/future data)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.fundamental_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker VARCHAR(10) UNIQUE NOT NULL,
    
    -- Valuation
    market_cap NUMERIC(20, 2),
    pe_ratio NUMERIC(10, 2),
    pb_ratio NUMERIC(10, 2),
    ps_ratio NUMERIC(10, 2),
    peg_ratio NUMERIC(10, 2),
    
    -- Growth
    revenue_growth_yoy NUMERIC(8, 4),
    earnings_growth_yoy NUMERIC(8, 4),
    eps_growth_3y NUMERIC(8, 4),
    
    -- Profitability
    profit_margin NUMERIC(8, 4),
    operating_margin NUMERIC(8, 4),
    roe NUMERIC(8, 4),
    roa NUMERIC(8, 4),
    
    -- Financial health
    debt_to_equity NUMERIC(10, 4),
    current_ratio NUMERIC(10, 4),
    quick_ratio NUMERIC(10, 4),
    
    -- Dividend
    dividend_yield NUMERIC(8, 4),
    payout_ratio NUMERIC(8, 4),
    
    -- Metadata
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    data_quality VARCHAR(20) DEFAULT 'medium',
    
    CONSTRAINT data_quality_check CHECK (data_quality IN ('high', 'medium', 'low'))
);

-- Index
CREATE INDEX IF NOT EXISTS idx_fundamental_data_ticker ON public.fundamental_data(ticker);

-- Public read access (no auth required for fundamental data)
ALTER TABLE public.fundamental_data ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Anyone can read fundamental data"
    ON public.fundamental_data FOR SELECT
    USING (true);

-- =====================================================
-- SEED MOCK FUNDAMENTAL DATA
-- =====================================================
INSERT INTO public.fundamental_data (ticker, market_cap, pe_ratio, pb_ratio, revenue_growth_yoy, earnings_growth_yoy, profit_margin, roe, debt_to_equity, dividend_yield, data_quality) VALUES
('AAPL', 2800000000000, 28.5, 45.2, 0.085, 0.12, 0.26, 1.47, 1.73, 0.0052, 'high'),
('MSFT', 2500000000000, 32.4, 12.8, 0.12, 0.15, 0.36, 0.42, 0.34, 0.0078, 'high'),
('GOOGL', 1600000000000, 24.8, 6.2, 0.09, 0.11, 0.25, 0.28, 0.15, 0.00, 'high'),
('TSLA', 650000000000, 65.3, 15.8, 0.18, 0.25, 0.15, 0.28, 0.17, 0.00, 'medium'),
('AMZN', 1400000000000, 58.2, 8.4, 0.11, 0.08, 0.062, 0.21, 0.48, 0.00, 'high'),
('NVDA', 1200000000000, 72.5, 28.6, 0.126, 0.188, 0.48, 1.21, 0.32, 0.0006, 'high'),
('META', 850000000000, 22.7, 6.8, 0.16, 0.35, 0.29, 0.32, 0.00, 0.00, 'high'),
('JPM', 450000000000, 11.2, 1.6, 0.08, 0.12, 0.32, 0.15, 1.24, 0.025, 'high'),
('V', 520000000000, 32.8, 14.2, 0.10, 0.14, 0.52, 0.42, 0.68, 0.0074, 'high'),
('WMT', 410000000000, 28.4, 5.2, 0.058, 0.065, 0.025, 0.19, 0.78, 0.014, 'high')
ON CONFLICT (ticker) DO UPDATE SET
    market_cap = EXCLUDED.market_cap,
    pe_ratio = EXCLUDED.pe_ratio,
    pb_ratio = EXCLUDED.pb_ratio,
    revenue_growth_yoy = EXCLUDED.revenue_growth_yoy,
    earnings_growth_yoy = EXCLUDED.earnings_growth_yoy,
    profit_margin = EXCLUDED.profit_margin,
    roe = EXCLUDED.roe,
    debt_to_equity = EXCLUDED.debt_to_equity,
    dividend_yield = EXCLUDED.dividend_yield,
    last_updated = NOW();
