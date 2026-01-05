"""
EXPERIMENTAL PERSONAL TRADING AGENT
====================================

⚠️ WARNING: EXPERIMENTAL USE ONLY
- This is for personal experimentation
- NOT compliant with SEBI regulations
- NOT for public use or distribution
- User assumes ALL responsibility
- Can and WILL be wrong
- No guarantees or warranties

This agent generates tactical trading hypotheses using:
- Price action analysis
- Momentum indicators
- Volume patterns
- Regime detection
- Probabilistic reasoning
"""

import logging
from typing import Dict, Any, Optional, List, Literal
from datetime import datetime
from dataclasses import dataclass
import uuid

logger = logging.getLogger(__name__)


@dataclass
class TradingThesis:
    """Experimental trading hypothesis"""
    
    # Core thesis
    thesis: str  # Blunt, no hedging
    
    # Price prediction
    price_range_low: float
    price_range_high: float
    
    # Trade bias
    bias: Literal["long", "short", "no_trade", "scalp_only", "wait"]
    
    # Risk management
    invalidation_reason: str
    
    # Risk notes (blunt)
    risk_notes: List[str]
    
    # Confidence
    confidence: int  # 0-100, uncapped
    
    # Regime
    regime: Literal["trending", "mean_reverting", "choppy", "event_driven", "index_led", "sector_led"]
    
    # Supporting analysis
    volume_analysis: str
    
    # Metadata
    ticker: str
    
    # Optional fields with defaults
    time_horizon: str = "intraday"
    entry_timing: str = "now"
    confidence_adjustments: List[str] = None  # Track why confidence was adjusted
    index_alignment: str = ""  # Index vs stock direction
    signal_age_minutes: Optional[int] = None  # Signal freshness
    analysis_id: Optional[str] = None  # For feedback tracking
    
    def __post_init__(self):
        """Initialize mutable defaults"""
        if self.confidence_adjustments is None:
            self.confidence_adjustments = []


class ExperimentalTradingAgent:
    """
    Personal experimental trading intelligence agent
    
    ⚠️ EXPERIMENTAL - NOT FOR PRODUCTION
    
    This agent:
    - Generates predictions
    - Suggests tactical trades
    - Uses aggressive language
    - Can be wrong
    - Optimizes for short-term opportunities
    
    This agent does NOT:
    - Place trades automatically
    - Care about compliance
    - Protect feelings
    - Guarantee success
    """
    
    def __init__(self, enabled: bool = False):
        """
        Initialize experimental agent
        
        Args:
            enabled: Master kill switch (default: False for safety)
        """
        self.enabled = enabled
        self.analysis_count = {}  # Track analysis frequency per ticker
        self.last_analysis_time = {}  # Track signal freshness
        
        if enabled:
            logger.warning(
                "⚠️ EXPERIMENTAL TRADING AGENT ENABLED - "
                "Personal use only. Not compliant. User assumes all risk."
            )
        else:
            logger.info("Experimental trading agent disabled (safe mode)")
    
    def analyze_setup(
        self,
        ticker: str,
        current_price: float,
        ohlcv: Dict[str, Any],
        indicators: Dict[str, Any],
        portfolio_context: Optional[Dict[str, Any]] = None,
        index_context: Optional[Dict[str, Any]] = None,
        time_of_day: Optional[str] = None
    ) -> Optional[TradingThesis]:
        """
        Generate experimental trading thesis
        
        Args:
            ticker: Stock ticker
            current_price: Current market price
            ohlcv: OHLCV data
            indicators: Technical indicators (RSI, MACD, etc.)
            portfolio_context: User's portfolio info
            index_context: Index data (NIFTY, etc.)
            time_of_day: "pre_market", "open", "mid_day", "close"
        
        Returns:
            TradingThesis or None if agent disabled
        """
        if not self.enabled:
            logger.debug("Experimental agent disabled, skipping analysis")
            return None
        
        logger.info(f"🔬 Generating experimental thesis for {ticker}")
        
        # Detect regime
        regime = self._detect_regime(indicators, ohlcv, index_context)
        
        # No regime = no trade
        if regime == "choppy":
            return self._generate_no_trade_thesis(
                ticker=ticker,
                current_price=current_price,
                reason="Choppy conditions. No clear directional bias.",
                regime=regime
            )
        
        # Analyze price action
        price_action = self._analyze_price_action(ohlcv, current_price)
        
        # Analyze momentum
        momentum = self._analyze_momentum(indicators)
        
        # Analyze volume
        volume_analysis = self._analyze_volume(ohlcv)
        
        # Check intraday context
        if time_of_day:
            intraday_filter = self._intraday_filter(
                time_of_day=time_of_day,
                volume_analysis=volume_analysis,
                price_action=price_action
            )
            if intraday_filter:
                return intraday_filter
        
        # Check portfolio concentration risk
        if portfolio_context:
            concentration_warning = self._check_concentration_risk(
                ticker=ticker,
                portfolio=portfolio_context
            )
            if concentration_warning:
                logger.warning(f"⚠️ Portfolio concentration risk: {concentration_warning}")
        
        # Generate thesis
        thesis = self._generate_thesis(
            ticker=ticker,
            current_price=current_price,
            regime=regime,
            price_action=price_action,
            momentum=momentum,
            volume_analysis=volume_analysis,
            indicators=indicators,
            ohlcv=ohlcv
        )
        
        # Apply improvements (index override, liquidity filter, freshness, frequency)
        volume_ratio = ohlcv.get('volume_ratio', 1.0)  # Current vol / avg vol
        timeframe = "intraday"  # Default to intraday
        thesis = self._enhance_thesis_with_improvements(
            thesis=thesis,
            index_context=index_context,
            volume_ratio=volume_ratio,
            timeframe=timeframe
        )
        
        # Log for review
        self._log_thesis(thesis)
        
        return thesis
    
    def _detect_regime(
        self,
        indicators: Dict[str, Any],
        ohlcv: Dict[str, Any],
        index_context: Optional[Dict[str, Any]]
    ) -> str:
        """Detect market regime"""
        
        # Check for trending
        rsi = indicators.get('rsi', 50)
        macd_slope = indicators.get('macd_slope', 0)
        volume_ratio = ohlcv.get('volume_vs_avg', 1.0)
        
        # Strong trend conditions
        if abs(macd_slope) > 0.5 and volume_ratio > 1.2:
            if rsi > 60 or rsi < 40:
                return "trending"
        
        # Mean reversion conditions
        if rsi > 70 or rsi < 30:
            if volume_ratio < 0.8:
                return "mean_reverting"
        
        # Index-led
        if index_context and index_context.get('strength', 0) > 0.7:
            return "index_led"
        
        # Default to choppy if unclear
        return "choppy"
    
    def _analyze_price_action(self, ohlcv: Dict[str, Any], current_price: float) -> str:
        """Analyze price action structure"""
        
        # Get recent highs/lows
        recent_high = ohlcv.get('recent_high', current_price)
        recent_low = ohlcv.get('recent_low', current_price)
        
        # Check trend structure
        if current_price > recent_high * 0.98:
            return "Breaking resistance. Buyers in control."
        elif current_price < recent_low * 1.02:
            return "Breaking support. Sellers in control."
        else:
            return "Range-bound. No clear direction."
    
    def _analyze_momentum(self, indicators: Dict[str, Any]) -> str:
        """Analyze momentum indicators"""
        
        rsi = indicators.get('rsi', 50)
        macd = indicators.get('macd', 0)
        macd_signal = indicators.get('macd_signal', 0)
        
        # Check for divergences
        if rsi > 70:
            return "Overbought. Watch for exhaustion."
        elif rsi < 30:
            return "Oversold. Watch for bounce."
        elif macd > macd_signal and macd > 0:
            return "Momentum building. Upside favored."
        elif macd < macd_signal and macd < 0:
            return "Momentum fading. Downside risk."
        else:
            return "Neutral momentum. Wait for confirmation."
    
    def _analyze_volume(self, ohlcv: Dict[str, Any]) -> str:
        """Analyze volume patterns"""
        
        volume_ratio = ohlcv.get('volume_vs_avg', 1.0)
        
        if volume_ratio > 2.0:
            return "High volume. Strong conviction."
        elif volume_ratio > 1.5:
            return "Above-average volume. Decent participation."
        elif volume_ratio < 0.7:
            return "Low volume. Fake move likely."
        else:
            return "Average volume. Neutral signal."
    
    def _intraday_filter(
        self,
        time_of_day: str,
        volume_analysis: str,
        price_action: str
    ) -> Optional[TradingThesis]:
        """Filter out bad intraday setups"""
        
        # Early spike with low volume = fade candidate
        if time_of_day == "open" and "Low volume" in volume_analysis:
            return TradingThesis(
                thesis="Early spike lacks volume. High chance of fade. Wait for 11:30.",
                price_range_low=0,
                price_range_high=0,
                timeframe="wait",
                probability=0,
                bias="wait",
                invalidation_level=0,
                invalidation_reason="Volume confirms move",
                risk_notes=["Fake breakouts common in first 30 minutes"],
                confidence=0,
                regime="choppy",
                price_action=price_action,
                momentum="Unknown",
                volume_analysis=volume_analysis,
                generated_at=datetime.now(),
                ticker=""
            )
        
        return None
    
    def _check_concentration_risk(
        self,
        ticker: str,
        portfolio: Dict[str, Any]
    ) -> Optional[str]:
        """Check for portfolio concentration risk"""
        
        position_pct = portfolio.get('position_percentage', 0)
        
        if position_pct > 40:
            return f"{ticker} is {position_pct:.0f}% of portfolio. Overconcentrated."
        
        return None
    
    def _generate_thesis(
        self,
        ticker: str,
        current_price: float,
        regime: str,
        price_action: str,
        momentum: str,
        volume_analysis: str,
        indicators: Dict[str, Any],
        ohlcv: Dict[str, Any]
    ) -> TradingThesis:
        """Generate complete trading thesis"""
        
        # Determine bias
        if "Buyers in control" in price_action and "Upside favored" in momentum:
            bias = "long"
            thesis = f"Momentum is building after price broke resistance. {momentum}"
        elif "Sellers in control" in price_action and "Downside risk" in momentum:
            bias = "short"
            thesis = f"Price breaking down with momentum confirmation. {momentum}"
        else:
            bias = "no_trade"
            thesis = "No clear setup. Wait for confirmation."
        
        # Calculate price range (simple ±3-5% for demo)
        if bias == "long":
            range_low = current_price * 0.98
            range_high = current_price * 1.05
            invalidation = current_price * 0.97
            invalidation_reason = f"Below ₹{invalidation:.2f}, setup fails"
        elif bias == "short":
            range_low = current_price * 0.95
            range_high = current_price * 1.02
            invalidation = current_price * 1.03
            invalidation_reason = f"Above ₹{invalidation:.2f}, setup fails"
        else:
            range_low = current_price * 0.98
            range_high = current_price * 1.02
            invalidation = 0
            invalidation_reason = "N/A"
        
        # Risk notes
        risk_notes = []
        if "Low volume" in volume_analysis:
            risk_notes.append("Low volume increases reversal risk.")
        if regime == "index_led":
            risk_notes.append("This move depends on index strength.")
        
        # Confidence score
        confidence = self._calculate_confidence(
            bias=bias,
            volume_analysis=volume_analysis,
            regime=regime
        )
        
        return TradingThesis(
            thesis=thesis,
            price_range_low=range_low,
            price_range_high=range_high,
            bias=bias,
            invalidation_reason=invalidation_reason,
            risk_notes=risk_notes if risk_notes else ["Standard volatility risk"],
            confidence=confidence,
            regime=regime,
            volume_analysis=volume_analysis,
            ticker=ticker,
            time_horizon="1-3 sessions",
            entry_timing="now",
            analysis_id=str(uuid.uuid4())  # Generate unique ID for feedback tracking
        )
    
    def _generate_no_trade_thesis(
        self,
        ticker: str,
        current_price: float,
        reason: str,
        regime: str
    ) -> TradingThesis:
        """Generate explicit no-trade thesis"""
        
        return TradingThesis(
            thesis=f"No trade. {reason}",
            price_range_low=0,
            price_range_high=0,
            bias="no_trade",
            invalidation_reason="N/A",
            risk_notes=[reason],
            confidence=0,
            regime=regime,
            volume_analysis="N/A",
            ticker=ticker,
            time_horizon="wait",
            entry_timing="hold",
            analysis_id=str(uuid.uuid4())  # Generate unique ID
        )
    
    def _calculate_confidence(
        self,
        bias: str,
        volume_analysis: str,
        regime: str
    ) -> int:
        """Calculate confidence score (0-100, uncapped)"""
        
        if bias == "no_trade":
            return 0
        
        confidence = 50  # Base
        
        # Volume bonus
        if "High volume" in volume_analysis:
            confidence += 20
        elif "Above-average" in volume_analysis:
            confidence += 10
        elif "Low volume" in volume_analysis:
            confidence -= 20
        
        # Regime bonus
        if regime == "trending":
            confidence += 15
        elif regime == "choppy":
            confidence -= 30
        
        return max(0, min(100, confidence))
    
    def _log_thesis(self, thesis: TradingThesis):
        """Log thesis for review"""
        
        logger.warning(
            f"🔬 EXPERIMENTAL THESIS - {thesis.ticker}\n"
            f"   Thesis: {thesis.thesis}\n"
            f"   Bias: {thesis.bias.upper()}\n"
            f"   Range: ₹{thesis.price_range_low:.2f}-₹{thesis.price_range_high:.2f}\n"
            f"   Confidence: {thesis.confidence}%\n"
            f"   Invalidation: {thesis.invalidation_reason}"
        )
    
    # ============================================================================
    # NEW IMPROVEMENTS (Task D)
    # ============================================================================
    
    def _check_index_override(
        self,
        stock_bias: str,
        index_context: Optional[Dict[str, Any]]
    ) -> tuple[int, str]:
        """
        Check if index trend contradicts stock signal
        
        Returns:
            (confidence_adjustment, alignment_note)
        """
        if not index_context:
            return (0, "No index data available")
        
        index_trend = index_context.get('trend', 'neutral')  # 'up', 'down', 'neutral'
        index_strength = index_context.get('strength', 0.5)  # 0-1
        
        # Check for conflict
        if stock_bias == "long" and index_trend == "down" and index_strength > 0.6:
            return (-20, "Stock signal conflicts with index direction (bearish index)")
        elif stock_bias == "short" and index_trend == "up" and index_strength > 0.6:
            return (-20, "Stock signal conflicts with index direction (bullish index)")
        elif stock_bias in ["long", "short"] and index_trend == stock_bias.replace("long", "up").replace("short", "down"):
            return (10, f"Index supports {stock_bias} bias")
        else:
            return (0, "Index neutral to stock signal")
    
    def _apply_liquidity_filter(
        self,
        volume_analysis: str,
        volume_ratio: float,
        bias: str
    ) -> tuple[str, str]:
        """
        Force scalp/no trade if volume too low
        
        Returns:
            (new_bias, reason)
        """
        if volume_ratio < 0.6:  # Less than 60% of average
            if bias in ["long", "short"]:
                return ("scalp_only", "Low volume (<60% avg). Only scalp trades viable.")
            else:
                return ("no_trade", "Volume too low for reliable signals.")
        
        return (bias, "")
    
    def _check_signal_freshness(
        self,
        ticker: str,
        timeframe: str
    ) -> tuple[int, Optional[str]]:
        """
        Check if signal is stale and add warning
        
        Returns:
            (age_minutes, warning_message)
        """
        now = datetime.now()
        
        if ticker in self.last_analysis_time:
            last_time = self.last_analysis_time[ticker]
            age_minutes = int((now - last_time).total_seconds() / 60)
            
            # Intraday signals stale after 30 min
            if timeframe == "intraday" and age_minutes > 30:
                return (age_minutes, f"Signal freshness degraded ({age_minutes} minutes old)")
            
            # Swing signals stale after 1 day
            elif timeframe in ["1-3 sessions", "swing"] and age_minutes > 1440:  # 24 hours
                return (age_minutes, f"Signal freshness degraded ({age_minutes // 60} hours old)")
        
        # Update last analysis time
        self.last_analysis_time[ticker] = now
        return (0, None)
    
    def _check_analysis_frequency(
        self,
        ticker: str
    ) -> Optional[str]:
        """
        Track and warn about over-analysis
        
        Returns:
            Warning message if user is over-analyzing
        """
        # Increment count
        self.analysis_count[ticker] = self.analysis_count.get(ticker, 0) + 1
        
        # Warn after 5+ analyses in same session
        if self.analysis_count[ticker] >= 5:
            return "Over-analysis increases false conviction. Trust your first read."
        
        return None
    
    def _enhance_thesis_with_improvements(
        self,
        thesis: TradingThesis,
        index_context: Optional[Dict[str, Any]],
        volume_ratio: float,
        timeframe: str
    ) -> TradingThesis:
        """
        Apply all improvement checks to thesis
        
        This is called after initial thesis generation to add:
        - Index override
        - Liquidity filter
        - Signal freshness
        - Analysis frequency warning
        """
        confidence_adjustments = []
        
        # 1. Index Override
        if index_context:
            index_adj, index_note = self._check_index_override(thesis.bias, index_context)
            if index_adj != 0:
                thesis.confidence += index_adj
                confidence_adjustments.append(f"Index: {index_adj:+d}%")
                thesis.risk_notes.append(index_note)
                thesis.index_alignment = index_note
        
        # 2. Liquidity Filter
        new_bias, liquidity_reason = self._apply_liquidity_filter(
            thesis.volume_analysis,
            volume_ratio,
            thesis.bias
        )
        if new_bias != thesis.bias:
            thesis.bias = new_bias
            thesis.risk_notes.append(liquidity_reason)
            confidence_adjustments.append("Liquidity: Downgraded to scalp/no trade")
        
        # 3. Signal Freshness
        age_minutes, freshness_warning = self._check_signal_freshness(
            thesis.ticker,
            timeframe
        )
        if freshness_warning:
            thesis.risk_notes.append(freshness_warning)
            thesis.signal_age_minutes = age_minutes
        
        # 4. Analysis Frequency Guard
        freq_warning = self._check_analysis_frequency(thesis.ticker)
        if freq_warning:
            thesis.risk_notes.append(freq_warning)
        
        # Store adjustments
        thesis.confidence_adjustments = confidence_adjustments
        
        # Ensure confidence stays in bounds
        thesis.confidence = max(0, min(100, thesis.confidence))
        
        return thesis


def format_experimental_output(thesis: TradingThesis) -> str:
    """Format thesis for display"""
    
    output = f"""
╔═══════════════════════════════════════════════════════════════════╗
║  🔬 EXPERIMENTAL TRADING THESIS - {thesis.ticker}
╚═══════════════════════════════════════════════════════════════════╝

1️⃣ MARKET THESIS
   {thesis.thesis}

2️⃣ PROBABILISTIC PRICE RANGE
   Next {thesis.timeframe}: ₹{thesis.price_range_low:.2f}–₹{thesis.price_range_high:.2f}
   (≈{thesis.probability}% probability)

3️⃣ TRADE BIAS
   {thesis.bias.upper().replace('_', ' ')}

4️⃣ INVALIDATION ZONE
   {thesis.invalidation_reason}

5️⃣ RISK NOTES
"""
    
    for note in thesis.risk_notes:
        output += f"   • {note}\n"
    
    output += f"""
6️⃣ CONFIDENCE SCORE
   {thesis.confidence}/100

📊 SUPPORTING ANALYSIS
   Regime: {thesis.regime.upper()}
   Price Action: {thesis.price_action}
   Momentum: {thesis.momentum}
   Volume: {thesis.volume_analysis}

⚠️  DISCLAIMER: Experimental analysis for personal use only.
    Not financial advice. Can and will be wrong. User assumes all risk.

Generated: {thesis.generated_at.strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return output
