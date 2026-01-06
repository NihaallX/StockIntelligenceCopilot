"""Intraday Portfolio Intelligence System

A deterministic, intraday-aware portfolio intelligence engine that:
- Monitors existing holdings for risk, weakness, or opportunity
- Detects daily anomalies using rule-based methods
- Explains changes with beginner-friendly language
- Suggests conditional actions (never commands)

This is NOT an execution bot or prediction system.
"""

from .data_layer import IntradayDataProvider
from .method_layer import MethodDetector, DetectionTag
from .regime_mcp import MarketRegimeContext
from .language_layer import LanguageFormatter

__all__ = [
    "IntradayDataProvider",
    "MethodDetector",
    "DetectionTag",
    "MarketRegimeContext",
    "LanguageFormatter",
]
