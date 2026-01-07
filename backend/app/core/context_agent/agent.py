"""Market Regime Context Provider (Intraday-First)

SIMPLIFIED: Returns regime labels only.
NO news scraping. NO predictions. NO signal modification.
"""

import logging
from typing import Optional
from datetime import datetime

from .models import RegimeContextOutput, MarketContext
from app.mcp.factory import get_mcp_provider, MarketRegimeContext as FactoryRegimeContext

logger = logging.getLogger(__name__)


class MarketRegimeProvider:
    """
    Provides market regime context based ONLY on:
    - Time of day
    - Index correlation  
    - Volume patterns
    - Volatility expansion
    
    NO news. NO opinions. Just regime labels.
    """
    
    def __init__(self, enabled: bool = True):
        """
        Initialize regime provider
        
        Args:
            enabled: Whether regime detection is enabled (default: True)
        """
        self.enabled = enabled
        self.mcp_factory = get_mcp_provider() if enabled else None
        
        logger.info(f"Market Regime Provider initialized: enabled={enabled}")
    
    async def get_regime_context(
        self,
        ticker: str,
        timeframe: str = "INTRADAY"
    ) -> RegimeContextOutput:
        """
        Get current market regime for a ticker.
        
        Args:
            ticker: Stock symbol (e.g., "RELIANCE.NS")
            timeframe: INTRADAY or DAILY
            
        Returns:
            RegimeContextOutput with regime label and explanation
        """
        
        if not self.enabled or not self.mcp_factory:
            return self._neutral_regime()
        
        try:
            # Build regime context from MCP factory
            regime_context: FactoryRegimeContext = await self.mcp_factory.build_market_regime_context(
                ticker=ticker
            )
            
            # Map to simplified output
            regime_label = self._determine_regime_label(regime_context)
            explanation = self._generate_explanation(regime_context)
            
            return RegimeContextOutput(
                regime_label=regime_label,
                explanation=explanation,
                index_alignment=regime_context.index_alignment,
                volume_state=regime_context.volume_state,
                volatility_state=regime_context.volatility_state,
                time_of_day=regime_context.time_regime,
                timestamp=regime_context.timestamp
            )
            
        except Exception as e:
            logger.warning(f"Failed to fetch regime context: {e}")
            return self._neutral_regime()
    
    def _determine_regime_label(self, context: FactoryRegimeContext) -> str:
        """Determine primary regime label from context"""
        
        # Priority: volatility > volume > index > time
        if context.volatility_state == "expanding":
            return "VOLATILITY_EXPANSION"
        elif context.volume_state == "expansion":
            return "VOLUME_BREAKOUT"
        elif context.volume_state == "dry":
            return "LOW_LIQUIDITY_CHOP"
        elif context.index_alignment == "aligned":
            return "INDEX_LED_MOVE"
        elif context.index_alignment == "diverging":
            return "STOCK_SPECIFIC_MOVE"
        elif context.time_regime == "open":
            return "OPENING_VOLATILITY"
        elif context.time_regime == "close":
            return "CLOSING_PRESSURE"
        else:
            return "NEUTRAL_REGIME"
    
    def _generate_explanation(self, context: FactoryRegimeContext) -> str:
        """Generate plain-English explanation"""
        
        parts = []
        
        # Volume
        if context.volume_state == "expansion":
            parts.append("Volume is expanding")
        elif context.volume_state == "dry":
            parts.append("Volume is low")
        
        # Index
        if context.index_alignment == "aligned":
            parts.append("moving with index")
        elif context.index_alignment == "diverging":
            parts.append("diverging from index")
        
        # Volatility
        if context.volatility_state == "expanding":
            parts.append("volatility rising")
        elif context.volatility_state == "compressed":
            parts.append("volatility compressed")
        
        if not parts:
            return "No clear pattern right now."
        
        return f"{', '.join(parts)}."
    
    def _neutral_regime(self) -> RegimeContextOutput:
        """Return neutral regime when disabled or failed"""
        return RegimeContextOutput(
            regime_label="NEUTRAL_REGIME",
            explanation="No regime context available.",
            index_alignment="neutral",
            volume_state="normal",
            volatility_state="normal",
            time_of_day="unknown",
            timestamp=datetime.utcnow()
        )


# Legacy alias for backward compatibility
MarketContextAgent = MarketRegimeProvider
