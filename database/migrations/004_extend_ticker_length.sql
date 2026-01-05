-- Migration: Extend ticker column length in audit_logs
-- Date: 2026-01-03
-- Reason: Support longer ticker symbols like "RELIANCE.NS" (11 chars)

-- Extend ticker column from VARCHAR(10) to VARCHAR(20)
ALTER TABLE public.audit_logs 
ALTER COLUMN ticker TYPE VARCHAR(20);

-- Add comment
COMMENT ON COLUMN public.audit_logs.ticker IS 'Stock ticker symbol (e.g., AAPL, RELIANCE.NS) - supports up to 20 characters';
