"""
Legacy MCP Adapter
==================

Maintains compatibility with old MCPContextFetcher API while using new providers.

This adapter transforms the new MarketRegimeContext format into the legacy
format expected by existing routes, enabling gradual migration without
breaking changes.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from .factory import get_mcp_provider, MarketRegimeContext, MCPProviderFactory
from .base import TimeframeEnum, MCPDataUnavailable
from ..config.settings import settings

logger = logging.getLogger(__name__)


class LegacyMCPAdapter:
    """
    Adapter that wraps new MCP providers to provide legacy API compatibility
    
    Usage:
        adapter = LegacyMCPAdapter()
        context = await adapter.fetch_context(ticker="RELIANCE.NS", signal_direction="bullish")
    """
    
    def __init__(self):
        """Initialize with Yahoo Finance only (simplified MCP)"""
        self.factory = get_mcp_provider()
    
    async def fetch_context(
        self,
        ticker: str,
        signal_direction: Optional[str] = None,
        timeframe: TimeframeEnum = TimeframeEnum.FIFTEEN_MIN
    ) -> Dict[str, Any]:
        """
        Fetch market context using new MCP providers
        Returns format compatible with old MCPContextFetcher
        
        Args:
            ticker: Stock symbol (e.g., "RELIANCE.NS")
            signal_direction: "bullish" | "bearish" | "neutral" (from signal engine)
            timeframe: Analysis timeframe
            
        Returns:
            Dict with legacy-compatible format:
            {
                "market_sentiment": str,
                "index_trend": str,
                "volume_analysis": str,
                "volatility": str,
                "time_of_day": str,
                "data_source": str,
                "metadata": {...}
            }
        """
        try:
            context = await self.factory.build_market_regime_context(
                symbol=ticker,
                timeframe=timeframe,
                signal_direction=signal_direction,
                current_hour=datetime.now().hour
            )
            
            # Transform to legacy format
            return self._transform_to_legacy(context)
            
        except MCPDataUnavailable as e:
            logger.warning(f"MCP data unavailable for {ticker}: {e}")
            return self._get_fallback_context()
        
        except Exception as e:
            logger.error(f"Error fetching MCP context for {ticker}: {e}")
            return self._get_fallback_context()
    
    def _transform_to_legacy(self, context: MarketRegimeContext) -> Dict[str, Any]:
        """Transform new MarketRegimeContext to legacy format"""
        
        return {
            # Map trade_environment to market_sentiment
            "market_sentiment": self._map_sentiment(context.trade_environment),
            
            # Map index_alignment to index_trend
            "index_trend": self._map_index_trend(
                context.index_alignment,
                context.index_change_percent
            ),
            
            # Map volume_state to volume_analysis
            "volume_analysis": self._map_volume_analysis(
                context.volume_state,
                context.volume_ratio
            ),
            
            # Map volatility_state directly
            "volatility": context.volatility_state,
            
            # Map time_regime to time_of_day
            "time_of_day": context.time_regime,
            
            # Data source from new MCP
            "data_source": context.data_source,
            
            # Metadata for debugging
            "metadata": {
                "intraday_available": context.intraday_data_available,
                "timestamp": context.timestamp.isoformat(),
                "mcp_version": "2.0",  # Indicate new MCP system
                "raw_context": {
                    "index_alignment": context.index_alignment,
                    "index_change_percent": context.index_change_percent,
                    "volume_state": context.volume_state,
                    "volume_ratio": context.volume_ratio,
                    "volatility_state": context.volatility_state,
                    "trade_environment": context.trade_environment,
                    "time_regime": context.time_regime
                }
            }
        }
    
    def _map_sentiment(self, trade_environment: str) -> str:
        """Map trade_environment to legacy market_sentiment"""
        mapping = {
            "trending": "strong_trend",
            "choppy": "range_bound",
            "mean_reverting": "mean_reverting",
            "unknown": "neutral"
        }
        return mapping.get(trade_environment, "neutral")
    
    def _map_index_trend(
        self,
        index_alignment: str,
        index_change_percent: Optional[float]
    ) -> str:
        """Map index_alignment to legacy index_trend"""
        
        if index_alignment == "unavailable":
            return "unavailable"
        
        if index_alignment == "aligned":
            if index_change_percent and index_change_percent > 0:
                return "bullish_aligned"
            elif index_change_percent and index_change_percent < 0:
                return "bearish_aligned"
            else:
                return "neutral_aligned"
        
        elif index_alignment == "diverging":
            return "diverging"
        
        else:  # neutral
            return "neutral"
    
    def _map_volume_analysis(
        self,
        volume_state: str,
        volume_ratio: Optional[float]
    ) -> str:
        """Map volume_state to legacy volume_analysis"""
        
        if volume_state == "unavailable":
            return "unavailable"
        
        if volume_state == "dry":
            return "below_average"
        elif volume_state == "expansion":
            return "high_volume"
        else:  # normal
            return "average"
    
    def _get_fallback_context(self) -> Dict[str, Any]:
        """Return safe fallback context when MCP unavailable"""
        return {
            "market_sentiment": "neutral",
            "index_trend": "unavailable",
            "volume_analysis": "unavailable",
            "volatility": "unavailable",
            "time_of_day": self._get_current_time_regime(),
            "data_source": "fallback",
            "metadata": {
                "intraday_available": False,
                "timestamp": datetime.now().isoformat(),
                "mcp_version": "2.0",
                "fallback": True
            }
        }
    
    def _get_current_time_regime(self) -> str:
        """Get current time regime based on hour"""
        hour = datetime.now().hour
        if 9 <= hour < 10:
            return "open"
        elif 12 <= hour < 14:
            return "lunch"
        elif 14 <= hour < 16:
            return "close"
        else:
            return "after_hours"
    
    async def cleanup(self):
        """Close all provider connections"""
        await self.factory.cleanup()


# Convenience function for quick usage
async def fetch_market_context_legacy(
    ticker: str,
    signal_direction: Optional[str] = None,
    timeframe: TimeframeEnum = TimeframeEnum.FIFTEEN_MIN
) -> Dict[str, Any]:
    """
    Convenience function to fetch market context with automatic cleanup
    
    Args:
        ticker: Stock symbol
        signal_direction: Signal direction from signal engine
        timeframe: Analysis timeframe
        
    Returns:
        Legacy-compatible context dict
    """
    adapter = LegacyMCPAdapter()
    try:
        return await adapter.fetch_context(ticker, signal_direction, timeframe)
    finally:
        await adapter.cleanup()


# Singleton adapter instance (optional, for performance)
_adapter_instance: Optional[LegacyMCPAdapter] = None


def get_legacy_adapter() -> LegacyMCPAdapter:
    """Get or create singleton adapter instance"""
    global _adapter_instance
    
    if _adapter_instance is None:
        _adapter_instance = LegacyMCPAdapter()
    
    return _adapter_instance
