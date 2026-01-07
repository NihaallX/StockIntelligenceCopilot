"""
LLM Explanation Layer
=====================

Read-only explanation service for deterministic trading signals.

IMPORTANT:
- LLM does NOT generate signals
- LLM does NOT modify confidence scores
- LLM does NOT predict prices
- LLM ONLY explains existing deterministic results
"""

from .openrouter_client import OpenRouterClient
from .explanation_service import ExplanationService

__all__ = ["OpenRouterClient", "ExplanationService"]
