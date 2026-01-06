"""Market Regime MCP - Context WITHOUT News Scraping

Provides market context based on:
- Time of day
- Index correlation
- Volume patterns
- Session behavior

NO NEWS SCRAPING. NO OPINIONS. JUST REGIME LABELS.
"""

from dataclasses import dataclass
from datetime import datetime, time
from enum import Enum
from typing import List, Optional
from .data_layer import IntradayMetrics


class RegimeContext(str, Enum):
    """Market regime labels"""
    INDEX_LED_MOVE = "INDEX_LED_MOVE"
    LOW_LIQUIDITY_CHOP = "LOW_LIQUIDITY_CHOP"
    POST_LUNCH_VOLATILITY = "POST_LUNCH_VOLATILITY"
    EXPIRY_PRESSURE = "EXPIRY_PRESSURE"
    SECTOR_BASKET_MOVE = "SECTOR_BASKET_MOVE"
    PRE_MARKET_GAP = "PRE_MARKET_GAP"
    LAST_HOUR_VOLATILITY = "LAST_HOUR_VOLATILITY"


@dataclass
class MarketContext:
    """Market regime context output"""
    contexts: List[RegimeContext]
    explanation: str
    timestamp: datetime


class MarketRegimeContext:
    """
    Determines market regime using ONLY market data.
    
    NO news scraping.
    NO sentiment analysis.
    NO LLM predictions.
    
    Returns context labels that explain market behavior.
    """
    
    def __init__(self):
        # Indian market hours (IST)
        self.market_open = time(9, 15)
        self.post_lunch_start = time(13, 30)
        self.last_hour_start = time(14, 30)
        self.market_close = time(15, 30)
    
    def detect_regime(
        self, 
        metrics: IntradayMetrics,
        current_time: Optional[datetime] = None
    ) -> MarketContext:
        """
        Detect market regime based on data patterns.
        
        Args:
            metrics: Intraday metrics for stock
            current_time: Current time (defaults to now)
            
        Returns:
            MarketContext with regime labels
        """
        if current_time is None:
            current_time = datetime.now()
        
        contexts = []
        explanations = []
        
        # Check each regime condition
        
        # 1. INDEX_LED_MOVE
        if self._is_index_led(metrics):
            contexts.append(RegimeContext.INDEX_LED_MOVE)
            explanations.append("Stock movement is driven by index-level pressure")
        
        # 2. LOW_LIQUIDITY_CHOP
        if self._is_low_liquidity(metrics):
            contexts.append(RegimeContext.LOW_LIQUIDITY_CHOP)
            explanations.append("Low liquidity causing choppy price action")
        
        # 3. POST_LUNCH_VOLATILITY
        if self._is_post_lunch_session(current_time):
            contexts.append(RegimeContext.POST_LUNCH_VOLATILITY)
            explanations.append("Post-lunch session with typical volatility")
        
        # 4. EXPIRY_PRESSURE (check if near expiry day)
        if self._is_expiry_pressure(current_time):
            contexts.append(RegimeContext.EXPIRY_PRESSURE)
            explanations.append("Weekly/monthly expiry creating pressure")
        
        # 5. SECTOR_BASKET_MOVE (simplified)
        if self._is_sector_move(metrics):
            contexts.append(RegimeContext.SECTOR_BASKET_MOVE)
            explanations.append("Sector-wide movement detected")
        
        # 6. PRE_MARKET_GAP
        if self._is_gap_move(metrics):
            contexts.append(RegimeContext.PRE_MARKET_GAP)
            explanations.append("Significant gap from previous close")
        
        # 7. LAST_HOUR_VOLATILITY
        if self._is_last_hour(current_time):
            contexts.append(RegimeContext.LAST_HOUR_VOLATILITY)
            explanations.append("Last hour volatility typical of day-end positioning")
        
        # Generate combined explanation
        if not explanations:
            explanation = "Normal market conditions. No specific regime detected."
        else:
            explanation = ". ".join(explanations) + "."
        
        return MarketContext(
            contexts=contexts,
            explanation=explanation,
            timestamp=current_time
        )
    
    def _is_index_led(self, metrics: IntradayMetrics) -> bool:
        """
        Check if move is index-led.
        
        Criteria:
        - Stock moves in same direction as index
        - Correlation is high (both move >1%)
        - Stock's relative performance is small (<0.5%)
        """
        same_direction = (
            (metrics.stock_change_pct > 0 and metrics.index_change_pct > 0) or
            (metrics.stock_change_pct < 0 and metrics.index_change_pct < 0)
        )
        
        both_significant = (
            abs(metrics.stock_change_pct) > 1.0 and 
            abs(metrics.index_change_pct) > 1.0
        )
        
        low_relative_performance = abs(metrics.relative_performance) < 0.5
        
        return same_direction and both_significant and low_relative_performance
    
    def _is_low_liquidity(self, metrics: IntradayMetrics) -> bool:
        """
        Check if liquidity is low.
        
        Criteria:
        - Volume ratio < 0.5 (current volume is half of average)
        - Price not moving much despite time passed
        """
        low_volume = metrics.volume_ratio < 0.5
        low_volatility = abs(metrics.stock_change_pct) < 0.5
        
        return low_volume and low_volatility
    
    def _is_post_lunch_session(self, current_time: datetime) -> bool:
        """Check if in post-lunch session (1:30 PM - 2:30 PM IST)"""
        current = current_time.time()
        return self.post_lunch_start <= current < self.last_hour_start
    
    def _is_last_hour(self, current_time: datetime) -> bool:
        """Check if in last hour (2:30 PM - 3:30 PM IST)"""
        current = current_time.time()
        return self.last_hour_start <= current <= self.market_close
    
    def _is_expiry_pressure(self, current_time: datetime) -> bool:
        """
        Check if near expiry.
        
        Weekly expiry: Every Thursday
        Monthly expiry: Last Thursday of month
        """
        # Weekly expiry (Thursday)
        is_thursday = current_time.weekday() == 3
        
        # Monthly expiry (last Thursday)
        is_last_week = current_time.day > 24
        is_monthly_expiry = is_thursday and is_last_week
        
        return is_monthly_expiry or is_thursday
    
    def _is_sector_move(self, metrics: IntradayMetrics) -> bool:
        """
        Check if sector-wide move.
        
        Simplified: If sector data available and moving similarly
        """
        if metrics.sector_change_pct is None:
            return False
        
        # Stock and sector moving in same direction significantly
        same_direction = (
            (metrics.stock_change_pct > 0 and metrics.sector_change_pct > 0) or
            (metrics.stock_change_pct < 0 and metrics.sector_change_pct < 0)
        )
        
        both_significant = (
            abs(metrics.stock_change_pct) > 1.0 and
            abs(metrics.sector_change_pct) > 0.5
        )
        
        return same_direction and both_significant
    
    def _is_gap_move(self, metrics: IntradayMetrics) -> bool:
        """
        Check if significant gap from open.
        
        Criteria: Gap >2% from previous close implied by open
        """
        # If current price is >2% away from open
        gap_pct = abs(
            (metrics.current_price - metrics.open_price) / metrics.open_price * 100
        )
        
        return gap_pct > 2.0
    
    def detect_regime_batch(
        self,
        metrics_list: List[IntradayMetrics],
        current_time: Optional[datetime] = None
    ) -> List[MarketContext]:
        """
        Detect regime for multiple stocks.
        
        Useful for portfolio-wide context.
        """
        return [
            self.detect_regime(metrics, current_time)
            for metrics in metrics_list
        ]
