"""Fundamental analysis module"""

from .provider import FundamentalProvider
from .provider_v2 import FundamentalProviderV2

# Create singleton instance of V2 provider
_provider_v2_instance = FundamentalProviderV2()

# Backward compatibility: Keep old interface but use V2 under the hood
class FundamentalProviderCompat:
    """Compatibility wrapper for FundamentalProvider using V2 backend"""
    
    @staticmethod
    async def get_fundamentals(ticker: str):
        """Get fundamentals using V2 provider (with FMP support)"""
        return await _provider_v2_instance.get_fundamentals(ticker)
    
    @staticmethod
    async def score_fundamentals(fundamentals):
        """Score fundamentals using V2 provider"""
        return await _provider_v2_instance.score_fundamentals(fundamentals)

# Use V2 by default for new code
__all__ = ["FundamentalProvider", "FundamentalProviderV2", "FundamentalProviderCompat"]
