"""Application configuration and settings"""

from pydantic_settings import BaseSettings
from typing import List
import json
import os
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Stock Intelligence Copilot"
    VERSION: str = "0.2.0"  # Phase 2A
    
    # CORS
    BACKEND_CORS_ORIGINS: str = '["http://localhost:3000","http://localhost:3001","http://localhost:8080","http://localhost:8001"]'
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from JSON string"""
        return json.loads(self.BACKEND_CORS_ORIGINS)
    
    # Risk Engine Settings
    MAX_CONFIDENCE_THRESHOLD: float = 0.95  # Never show >95% confidence
    MIN_ACTIONABLE_CONFIDENCE: float = 0.60  # Minimum for recommendations
    DEFAULT_RISK_TOLERANCE: str = "moderate"  # Intraday-first: moderate default
    
    # Signal Settings (INTRADAY-FIRST)
    INTRADAY_MODE: bool = True  # Default to intraday analysis
    LONG_TERM_MODE: bool = False  # Disable long-term by default
    SHORT_TERM_ENABLED: bool = False  # Disable short-term trading
    
    # Data Settings (INTRADAY-FIRST)
    DEFAULT_LOOKBACK_DAYS: int = 1  # Intraday: current day only
    DEFAULT_TIMEFRAME: str = "INTRADAY"  # Default analysis timeframe
    
    # Phase 2C: Market Data Provider Configuration
    DATA_PROVIDER: str = "mock"  # Options: "mock" or "live"
    FMP_API_KEY: str = "qty5ZwSYBANWmtoWHYi1zfE8zDbKXXOV"  # Financial Modeling Prep API key (working!)
    CACHE_TTL_INTRADAY: int = 300  # 5 minutes
    CACHE_TTL_HISTORICAL: int = 86400  # 24 hours
    
    # MCP (Market Context Provider) - Simplified to Yahoo Finance Only
    # Removed: ALPHA_VANTAGE_KEY (rate limited), TWELVE_DATA_KEY (paywall for Indian stocks)
    MCP_PROVIDER: str = "yahoo"  # Yahoo Finance only (intraday + fundamentals)
    
    # Phase 2A: Supabase Configuration
    SUPABASE_URL: str = "https://dummy.supabase.co"
    SUPABASE_ANON_KEY: str = "dummy_anon_key"
    SUPABASE_SERVICE_ROLE_KEY: str = "dummy_service_key"
    
    # Phase 2A: JWT Configuration
    JWT_SECRET_KEY: str = "your_super_secret_jwt_key_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Phase 2A: LLM Configuration
    GROQ_API_KEY: str = "dummy_groq_key"
    GROQ_MODEL: str = "llama-3.1-70b-versatile"
    
    # OpenRouter Configuration (for explanation service)
    OPENROUTER_API_KEY: str = "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"  # Optional: For LLM explanations
    OPENROUTER_MODEL: str = "xiaomi/mimo-v2-flash:free"  # Free model for explanations
    LLM_EXPLANATIONS_ENABLED: bool = True  # Feature flag: Enable LLM explanations
    
    # Phase 2A: Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    LOGIN_RATE_LIMIT_PER_15_MIN: int = 5
    
    # Compliance
    TERMS_VERSION: str = "1.0.0"
    AUDIT_LOG_RETENTION_YEARS: int = 7
    DISCLAIMER: str = (
        "This is not financial advice. All suggestions are probabilistic and "
        "should be independently verified. Past performance does not guarantee "
        "future results. Invest at your own risk."
    )
    
    # Market Context Agent (MCP-based)
    MCP_ENABLED: bool = True  # Feature flag for MCP context enrichment
    MCP_TIMEOUT_SECONDS: int = 10  # Timeout for MCP operations
    MCP_TRIGGER_COOLDOWN_MINUTES: int = 5  # Minimum time between MCP calls per ticker
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        case_sensitive = True
        env_file = str(ENV_FILE)
        env_file_encoding = 'utf-8'


settings = Settings()
