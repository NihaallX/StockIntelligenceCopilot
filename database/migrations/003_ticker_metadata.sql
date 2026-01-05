-- Phase 2D: Ticker Metadata Table
-- Purpose: Unified ticker search and metadata storage

CREATE TABLE IF NOT EXISTS ticker_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Core identifiers
    ticker VARCHAR(20) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    exchange VARCHAR(20) NOT NULL CHECK (exchange IN ('NYSE', 'NASDAQ', 'NSE', 'BSE')),
    country VARCHAR(2) NOT NULL CHECK (country IN ('US', 'IN')),
    currency VARCHAR(3) NOT NULL CHECK (currency IN ('USD', 'INR')),
    
    -- Classification
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap DECIMAL,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_supported BOOLEAN DEFAULT true,
    
    -- Provider mapping
    data_provider VARCHAR(50) NOT NULL,  -- 'alpha_vantage', 'yahoo_finance', 'mock'
    ticker_format VARCHAR(50) NOT NULL,  -- 'AAPL', 'RELIANCE.NS', 'RELIANCE.BO'
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(ticker, exchange),
    CHECK(LENGTH(ticker) >= 1 AND LENGTH(ticker) <= 20)
);

-- Full-text search index for ticker and company name
CREATE INDEX idx_ticker_search ON ticker_metadata 
    USING GIN(to_tsvector('english', ticker || ' ' || company_name));

-- Fast lookups by exchange
CREATE INDEX idx_ticker_exchange ON ticker_metadata(exchange, is_active) 
    WHERE is_active = true;

-- Fast lookups by country
CREATE INDEX idx_ticker_country ON ticker_metadata(country, is_active) 
    WHERE is_active = true;

-- Fast lookups by exact ticker
CREATE INDEX idx_ticker_lookup ON ticker_metadata(ticker, exchange) 
    WHERE is_active = true;

-- Audit trigger for updated_at
CREATE OR REPLACE FUNCTION update_ticker_metadata_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_ticker_metadata_timestamp
    BEFORE UPDATE ON ticker_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_ticker_metadata_timestamp();

-- Row-level security (authenticated users can read, admins can write)
ALTER TABLE ticker_metadata ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Authenticated users can read ticker metadata"
    ON ticker_metadata FOR SELECT
    TO authenticated
    USING (is_active = true);

CREATE POLICY "Service role can manage ticker metadata"
    ON ticker_metadata FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Initial seed data will be added via migration script
COMMENT ON TABLE ticker_metadata IS 'Unified ticker metadata for semantic search and validation';
COMMENT ON COLUMN ticker_metadata.ticker_format IS 'Provider-specific ticker format (e.g., RELIANCE.NS for Yahoo Finance)';
COMMENT ON COLUMN ticker_metadata.data_provider IS 'Data source: alpha_vantage, yahoo_finance, or mock';
