-- Update ticker column length to support Indian stock tickers (e.g., RELIANCE.NS)
-- Old: VARCHAR(10)
-- New: VARCHAR(20) to support suffixes like .NS, .BO, etc.

ALTER TABLE portfolio_positions 
ALTER COLUMN ticker TYPE VARCHAR(20);

-- Also update any indexes if needed
-- Note: This script should be run against your Supabase database
