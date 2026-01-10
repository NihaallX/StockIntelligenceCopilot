"""FastAPI application"""

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from app.config import settings
from app.api import api_router

logger = logging.getLogger(__name__)


class SimpleSecurityMiddleware(BaseHTTPMiddleware):
    """Simple security middleware for serverless"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response


def validate_startup_config():
    """Validate configuration on startup"""
    data_provider = os.getenv("DATA_PROVIDER", "yahoo").lower()
    
    if data_provider == "yahoo":
        print("LIVE DATA MODE: Using Yahoo Finance (no API key required)")
    elif data_provider == "live":
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "").strip()
        if not api_key or api_key == "your_api_key_here":
            raise RuntimeError(
                "CONFIGURATION ERROR: DATA_PROVIDER=live requires valid ALPHA_VANTAGE_API_KEY. "
                "Get free key at: https://www.alphavantage.co/support/#api-key"
            )
        print("LIVE DATA MODE: Alpha Vantage API configured")
    else:
        print("DEMO MODE: Using mock market data provider")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "AI-assisted stock market analysis system. "
        "Provides probabilistic insights for retail investors. "
        "NOT financial advice. Read-only by design."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
async def startup_event():
    """Run startup validation"""
    try:
        validate_startup_config()
        logger.info("Application startup successful")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        # Don't raise - allow app to start anyway


# Security Middleware (simplified for serverless)
# 1. Security Headers
app.add_middleware(SimpleSecurityMiddleware)

# 2. CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "docs": "/docs",
        "disclaimer": settings.DISCLAIMER
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint with diagnostic info"""
    import os
    
    # Check critical environment variables
    env_status = {
        "SUPABASE_URL": "✓" if os.getenv("SUPABASE_URL") and "dummy" not in os.getenv("SUPABASE_URL", "") else "✗",
        "SUPABASE_ANON_KEY": "✓" if os.getenv("SUPABASE_ANON_KEY") and "dummy" not in os.getenv("SUPABASE_ANON_KEY", "") else "✗",
        "JWT_SECRET_KEY": "✓" if os.getenv("JWT_SECRET_KEY") and "your_super_secret" not in os.getenv("JWT_SECRET_KEY", "") else "✗",
        "GROQ_API_KEY": "✓" if os.getenv("GROQ_API_KEY") and "dummy" not in os.getenv("GROQ_API_KEY", "") else "✗"
    }
    
    all_configured = all(v == "✓" for v in env_status.values())
    
    return {
        "status": "healthy" if all_configured else "degraded",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "env_configured": env_status,
        "message": "All systems operational" if all_configured else "⚠️ Environment variables not configured - see VERCEL_ENV_SETUP.md"
    }

