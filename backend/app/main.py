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
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION
    }
