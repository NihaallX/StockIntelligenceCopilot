"""Method Layer - Deterministic Logic

Implements 3 rule-based detection methods:
1. Trend Stress Detection
2. Mean Reversion Risk
3. Portfolio Risk Exposure

Output: Tags per stock (NOT scores)
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional
from .data_layer import IntradayMetrics, PortfolioPosition


class DetectionTag(str, Enum):
    """Possible detection tags"""
    WEAK_TREND = "WEAK_TREND"
    EXTENDED_MOVE = "EXTENDED_MOVE"
    PORTFOLIO_RISK = "PORTFOLIO_RISK"


@dataclass
class Detection:
    """A detected condition on a stock"""
    ticker: str
    tags: List[DetectionTag]
    triggered_conditions: Dict[DetectionTag, List[str]]
    severity: str  # "watch", "caution", "alert"


class MethodDetector:
    """Rule-based detection methods - fully deterministic"""
    
    def __init__(
        self, 
        trend_stress_threshold: int = 2,
        mean_reversion_threshold: int = 2,
        portfolio_risk_threshold: int = 1
    ):
        """
        Initialize detector with thresholds.
        
        Args:
            trend_stress_threshold: Min conditions for WEAK_TREND (default 2)
            mean_reversion_threshold: Min conditions for EXTENDED_MOVE (default 2)
            portfolio_risk_threshold: Min conditions for PORTFOLIO_RISK (default 1)
        """
        self.trend_stress_threshold = trend_stress_threshold
        self.mean_reversion_threshold = mean_reversion_threshold
        self.portfolio_risk_threshold = portfolio_risk_threshold
    
    def detect_all(
        self,
        metrics: IntradayMetrics,
        position: Optional[PortfolioPosition] = None,
        all_positions: Optional[List[PortfolioPosition]] = None,
        red_candles_count: int = 0
    ) -> Detection:
        """
        Run all detection methods on a stock.
        
        Args:
            metrics: Intraday metrics for the stock
            position: User's position (if they hold it)
            all_positions: All portfolio positions (for correlation)
            red_candles_count: Count of red candles with volume
            
        Returns:
            Detection object with tags and explanations
        """
        tags = []
        triggered_conditions = {}
        
        # Method A: Trend Stress Detection
        trend_conditions = self._detect_trend_stress(metrics, red_candles_count)
        if len(trend_conditions) >= self.trend_stress_threshold:
            tags.append(DetectionTag.WEAK_TREND)
            triggered_conditions[DetectionTag.WEAK_TREND] = trend_conditions
        
        # Method B: Mean Reversion Risk
        reversion_conditions = self._detect_mean_reversion(metrics)
        if len(reversion_conditions) >= self.mean_reversion_threshold:
            tags.append(DetectionTag.EXTENDED_MOVE)
            triggered_conditions[DetectionTag.EXTENDED_MOVE] = reversion_conditions
        
        # Method C: Portfolio Risk Exposure (only if user holds it)
        if position and all_positions:
            risk_conditions = self._detect_portfolio_risk(
                position, 
                all_positions
            )
            if len(risk_conditions) >= self.portfolio_risk_threshold:
                tags.append(DetectionTag.PORTFOLIO_RISK)
                triggered_conditions[DetectionTag.PORTFOLIO_RISK] = risk_conditions
        
        # Determine severity
        severity = self._calculate_severity(tags, triggered_conditions)
        
        return Detection(
            ticker=metrics.ticker,
            tags=tags,
            triggered_conditions=triggered_conditions,
            severity=severity
        )
    
    def _detect_trend_stress(
        self, 
        metrics: IntradayMetrics,
        red_candles_count: int
    ) -> List[str]:
        """
        Method A: Trend Stress Detection
        
        Triggers if ≥2 conditions true:
        1. Price below VWAP
        2. Stock underperforms index by >1%
        3. Red candles with rising volume
        4. Below short-term MA (20/50)
        
        Returns list of triggered condition descriptions.
        """
        conditions = []
        
        # Condition 1: Price below VWAP
        if metrics.current_price < metrics.vwap:
            pct_below = ((metrics.vwap - metrics.current_price) / metrics.vwap) * 100
            conditions.append(f"Price below VWAP by {pct_below:.1f}%")
        
        # Condition 2: Underperforms index by >1%
        if metrics.relative_performance < -1.0:
            conditions.append(
                f"Underperforming index by {abs(metrics.relative_performance):.1f}%"
            )
        
        # Condition 3: Red candles with volume (passed from data layer)
        if red_candles_count >= 3:
            conditions.append(f"{red_candles_count} recent red candles with volume")
        
        # Condition 4: Below MAs
        if metrics.current_price < metrics.sma_20:
            conditions.append("Price below 20-day average")
        if metrics.current_price < metrics.sma_50:
            conditions.append("Price below 50-day average")
        
        return conditions
    
    def _detect_mean_reversion(
        self, 
        metrics: IntradayMetrics
    ) -> List[str]:
        """
        Method B: Mean Reversion Risk
        
        Triggers if ≥2 conditions true:
        1. Sharp drop (>2%) in short time
        2. RSI extreme (<30 or >70)
        3. Near recent support/resistance
        
        Returns list of triggered condition descriptions.
        """
        conditions = []
        
        # Condition 1: Sharp intraday move (>2%)
        move_threshold = 2.0
        if abs(metrics.stock_change_pct) > move_threshold:
            direction = "drop" if metrics.stock_change_pct < 0 else "surge"
            conditions.append(
                f"Sharp {direction} of {abs(metrics.stock_change_pct):.1f}% today"
            )
        
        # Condition 2: RSI extreme
        if metrics.rsi_14 < 30:
            conditions.append(f"RSI oversold at {metrics.rsi_14:.1f}")
        elif metrics.rsi_14 > 70:
            conditions.append(f"RSI overbought at {metrics.rsi_14:.1f}")
        
        # Condition 3: Near support/resistance (within 2%)
        proximity_threshold = 0.02  # 2%
        
        if metrics.recent_high_20d > 0:
            distance_to_high = (metrics.recent_high_20d - metrics.current_price) / metrics.recent_high_20d
            if distance_to_high <= proximity_threshold:
                conditions.append(
                    f"Near 20-day high of ₹{metrics.recent_high_20d:.2f}"
                )
        
        if metrics.recent_low_20d > 0:
            distance_to_low = (metrics.current_price - metrics.recent_low_20d) / metrics.recent_low_20d
            if distance_to_low <= proximity_threshold:
                conditions.append(
                    f"Near 20-day low of ₹{metrics.recent_low_20d:.2f}"
                )
        
        return conditions
    
    def _detect_portfolio_risk(
        self,
        position: PortfolioPosition,
        all_positions: List[PortfolioPosition]
    ) -> List[str]:
        """
        Method C: Portfolio Risk Exposure
        
        Triggers if ≥1 condition true:
        1. Position >25% of portfolio
        2. Highly correlated holdings moving together
        3. Single stock driving >40% of daily P&L
        
        Returns list of triggered condition descriptions.
        """
        conditions = []
        
        # Condition 1: Large position
        if position.portfolio_weight_pct > 25.0:
            conditions.append(
                f"Position size is {position.portfolio_weight_pct:.1f}% of portfolio"
            )
        
        # Condition 2: Correlated holdings (simplified)
        # Check if multiple large positions (>15%) exist
        large_positions = [p for p in all_positions if p.portfolio_weight_pct > 15.0]
        if len(large_positions) >= 2:
            tickers = [p.ticker for p in large_positions]
            conditions.append(
                f"Multiple large positions: {', '.join(tickers)}"
            )
        
        # Condition 3: Single stock driving P&L
        if all_positions:
            total_daily_pnl = sum(p.daily_pnl for p in all_positions)
            if total_daily_pnl != 0:
                pnl_contribution = abs(position.daily_pnl / total_daily_pnl) * 100
                if pnl_contribution > 40.0:
                    conditions.append(
                        f"Driving {pnl_contribution:.1f}% of today's P&L"
                    )
        
        return conditions
    
    def _calculate_severity(
        self, 
        tags: List[DetectionTag],
        triggered_conditions: Dict[DetectionTag, List[str]]
    ) -> str:
        """
        Determine severity level based on tags and conditions.
        
        Returns: "watch", "caution", or "alert"
        """
        if not tags:
            return "watch"
        
        # Count total triggered conditions
        total_conditions = sum(len(conds) for conds in triggered_conditions.values())
        
        # Multiple tags = alert
        if len(tags) >= 2:
            return "alert"
        
        # Single tag with many conditions = caution
        if total_conditions >= 3:
            return "caution"
        
        return "watch"
    
    def filter_by_severity(
        self, 
        detections: List[Detection],
        min_severity: str = "watch"
    ) -> List[Detection]:
        """
        Filter detections by minimum severity level.
        
        Args:
            detections: List of Detection objects
            min_severity: Minimum severity ("watch", "caution", "alert")
            
        Returns:
            Filtered list
        """
        severity_levels = {"watch": 0, "caution": 1, "alert": 2}
        min_level = severity_levels.get(min_severity, 0)
        
        return [
            d for d in detections 
            if severity_levels.get(d.severity, 0) >= min_level
        ]
