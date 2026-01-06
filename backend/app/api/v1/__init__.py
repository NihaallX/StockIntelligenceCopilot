"""API v1 routes"""

from fastapi import APIRouter
from .stocks import router as stocks_router
from .auth import router as auth_router
from .portfolio import router as portfolio_router
from .enhanced import router as enhanced_router
from .search import router as search_router
from .notable_signals import router as notable_signals_router
from .experimental import router as experimental_router
from .intraday_routes import router as intraday_router

api_router = APIRouter()

# Phase 2A: Authentication routes (public)
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])

# Phase 1: Stock analysis routes (requires authentication)
api_router.include_router(stocks_router, tags=["stocks"])

# Phase 2B: Portfolio tracking (requires authentication)
api_router.include_router(portfolio_router, prefix="/portfolio", tags=["portfolio"])

# Phase 2B: Enhanced analysis with fundamentals + scenarios (requires authentication)
api_router.include_router(enhanced_router, prefix="/analysis", tags=["enhanced-analysis"])

# Phase 2D: Ticker search and market status (requires authentication)
api_router.include_router(search_router, tags=["search"])

# Task 3: Notable signals for dashboard (requires authentication)
api_router.include_router(notable_signals_router, tags=["portfolio"])

# NEW: Intraday Portfolio Intelligence (deterministic, rule-based)
api_router.include_router(intraday_router, tags=["intraday"])

# Experimental: Personal trading agent (⚠️ NOT SEBI COMPLIANT)
api_router.include_router(experimental_router, tags=["experimental"])
