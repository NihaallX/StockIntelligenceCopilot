"""
Fundamental Data Adapters

Adapter pattern for multiple fundamental data providers:
- Financial Modeling Prep (FMP) - Primary provider
- EODHD - Indian market support  
- Database fallback - Cached data

Each adapter implements the FundamentalAdapter interface.
"""

from .base import FundamentalAdapter, FundamentalDataResult, DataSource
from .fmp_adapter import FMPAdapter
from .database_adapter import DatabaseAdapter

__all__ = [
    "FundamentalAdapter",
    "FundamentalDataResult",
    "DataSource",
    "FMPAdapter",
    "DatabaseAdapter",
]
