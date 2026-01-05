"""FastAPI application"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import api_router


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
    validate_startup_config()


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
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
