"""
MCP Provider Factory & Market Regime Context Builder
=====================================================

SIMPLIFIED: Yahoo Finance only provider.
MarketRegimeContext enrichment that runs AFTER signals.

⚠️ CRITICAL: Context does NOT modify signals
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime
from .base import (
    MCPProvider,
    TimeframeEnum,
    OHLCVData,
    IndicatorData,
    IndexData,
    MCPDataUnavailable,
    MCPRateLimitError
)
from .yahoo_fundamentals import YahooFinanceMCPProvider

logger = logging.getLogger(__name__)


@dataclass
class MarketRegimeContext:
    """
    Market context enrichment (NOT a signal modifier)
    
    Attached to response payload AFTER signal generation.
    """
    # Index alignment
    index_alignment: str  # "aligned" | "diverging" | "neutral" | "unavailable"
    
    # Volume state
    volume_state: str  # "dry" | "normal" | "expansion" | "unavailable"
    
    # Volatility state
    volatility_state: str  # "compressed" | "expanding" | "normal" | "unavailable"
    
    # Time regime
    time_regime: str  # "open" | "lunch" | "close" | "after_hours"
    
    # Trade environment (read-only label)
    trade_environment: str  # "trending" | "choppy" | "mean_reverting" | "unknown"
    
    # Metadata
    data_source: str  # Which provider(s) used
    timestamp: datetime
    intraday_data_available: bool
    
    # Optional fields (must come after required fields)
    index_change_percent: Optional[float] = None
    volume_ratio: Optional[float] = None  # Current vol / avg vol
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for API response"""
        return asdict(self)


class MCPProviderFactory:
    """
    Simplified MCP provider using Yahoo Finance only
    """
    
    def __init__(self):
        self._yahoo_provider: Optional[YahooFinanceMCPProvider] = None
    
    def get_yahoo_provider(self) -> YahooFinanceMCPProvider:
        """Get Yahoo Finance provider (intraday + fundamentals)"""
        if not self._yahoo_provider:
            self._yahoo_provider = YahooFinanceMCPProvider()
        
        return self._yahoo_provider
    
    async def fetch_with_fallback(
        self,
        fetch_func_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        Fetch from Yahoo Finance provider
        
        Args:
            fetch_func_name: Method name to call (e.g., "fetch_index_data")
            *args, **kwargs: Arguments to pass to method
            
        Returns:
            Data from Yahoo Finance
            
        Raises:
            MCPDataUnavailable: If Yahoo Finance fails
        """
        provider = self.get_yahoo_provider()
        
        try:
            method = getattr(provider, fetch_func_name)
            result = await method(*args, **kwargs)
            logger.info(f"Successfully fetched data from Yahoo Finance")
            return result
            
        except MCPDataUnavailable as e:
            logger.warning(f"Yahoo Finance data unavailable: {e}")
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error from Yahoo Finance: {e}")
            raise MCPDataUnavailable(f"Yahoo Finance error: {e}")
    
    async def build_market_regime_context(
        self,
        symbol: str,
        timeframe: TimeframeEnum,
        signal_direction: Optional[str] = None,  # From deterministic signal
        current_hour: int = datetime.now().hour
    ) -> MarketRegimeContext:
        """
        Build market regime context AFTER signal generation
        
        Args:
            symbol: Stock ticker
            timeframe: Analysis timeframe
            signal_direction: "bullish" | "bearish" | "neutral" (from signal engine)
            current_hour: Current hour (for time regime)
            
        Returns:
            MarketRegimeContext with enrichment data
            
        ⚠️ This does NOT modify signals - it only adds context
        """
        
        # Default context (all unavailable)
        context = MarketRegimeContext(
            index_alignment="unavailable",
            volume_state="unavailable",
            volatility_state="unavailable",
            time_regime=self._get_time_regime(current_hour),
            trade_environment="unknown",
            data_source="none",
            timestamp=datetime.now(),
            intraday_data_available=False
        )
        
        try:
            # Fetch intraday OHLCV from Yahoo Finance
            # Note: Yahoo Finance intraday may be limited, use for basic context only
            try:
                yahoo_provider = self.get_yahoo_provider()
                # Get ticker data for volume/volatility analysis
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d", interval="15m")
                
                if not hist.empty and len(hist) > 0:
                    context.intraday_data_available = True
                    context.data_source = "yahoo_finance"
                    
                    # Calculate volume state from available data
                    if len(hist) >= 10:
                        recent_volume = hist['Volume'].iloc[-1]
                        avg_volume = hist['Volume'].mean()
                        
                        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
                        context.volume_ratio = round(volume_ratio, 2)
                        
                        if volume_ratio < 0.7:
                            context.volume_state = "dry"
                        elif volume_ratio > 1.5:
                            context.volume_state = "expansion"
                        else:
                            context.volume_state = "normal"
                    
                    # Calculate volatility state
                    if len(hist) >= 10:
                        hist['Range'] = (hist['High'] - hist['Low']) / hist['Close']
                        recent_volatility = hist['Range'].iloc[-5:].mean()
                        baseline_volatility = hist['Range'].mean()
                        
                        if recent_volatility > baseline_volatility * 1.3:
                            context.volatility_state = "expanding"
                        elif recent_volatility < baseline_volatility * 0.7:
                            context.volatility_state = "compressed"
                        else:
                            context.volatility_state = "normal"
                
            except Exception as e:
                logger.warning(f"Could not fetch intraday data: {e}")
            
            # Fetch index data for alignment
            try:
                index_data = await self.fetch_with_fallback(
                    "fetch_index_data",
                    index_symbol="^NSEI"
                )
                
                context.index_change_percent = index_data.change_percent
                
                # Check alignment with signal
                if signal_direction and index_data.change_percent != 0:
                    if signal_direction == "bullish" and index_data.change_percent > 0:
                        context.index_alignment = "aligned"
                    elif signal_direction == "bearish" and index_data.change_percent < 0:
                        context.index_alignment = "aligned"
                    elif abs(index_data.change_percent) < 0.3:
                        context.index_alignment = "neutral"
                    else:
                        context.index_alignment = "diverging"
                else:
                    context.index_alignment = "neutral"
                    
            except MCPDataUnavailable:
                logger.warning("Index data unavailable for alignment check")
        
        except MCPDataUnavailable as e:
            logger.warning(f"Could not build full market context: {e}")
        
        return context
    
    def _get_time_regime(self, hour: int) -> str:
        """Determine time regime (India market hours)"""
        if 9 <= hour < 10:
            return "open"
        elif 12 <= hour < 14:
            return "lunch"
        elif 14 <= hour < 16:
            return "close"
        else:
            return "after_hours"
    
    def _determine_trade_environment(self, candles: List[OHLCVData]) -> str:
        """Determine trade environment from price action (read-only label)"""
        if len(candles) < 10:
            return "unknown"
        
        # Calculate trend strength
        closes = [c.close for c in candles[:10]]
        
        # Simple trend detection
        up_moves = sum(1 for i in range(1, len(closes)) if closes[i] > closes[i-1])
        down_moves = sum(1 for i in range(1, len(closes)) if closes[i] < closes[i-1])
        
        if up_moves >= 7 or down_moves >= 7:
            return "trending"
        elif up_moves <= 4 and down_moves <= 4:
            return "choppy"
        else:
            return "mean_reverting"
    
    async def cleanup(self):
        """Close provider connections"""
        # Yahoo Finance provider doesn't need cleanup
        pass


# Singleton instance
_factory_instance: Optional[MCPProviderFactory] = None


def get_mcp_provider() -> MCPProviderFactory:
    """Get or create MCP provider factory (Yahoo Finance only)"""
    global _factory_instance
    
    if _factory_instance is None:
        _factory_instance = MCPProviderFactory()
    
    return _factory_instance
