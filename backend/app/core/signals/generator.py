"""Signal generation engine - Rule-based trading signal logic"""

from typing import List, Dict, Tuple
from datetime import datetime

from app.models.schemas import (
    Signal,
    SignalType,
    SignalStrength,
    SignalReasoning,
    TimeHorizon,
    TechnicalIndicators,
    MarketData,
)


class SignalGenerator:
    """
    Generate trading signals based on technical indicators.
    
    Uses rule-based logic to evaluate market conditions and generate
    bullish, bearish, or neutral signals with confidence scores.
    
    Key principles:
    - Multiple confirming signals increase confidence
    - Contradicting signals reduce confidence
    - Maximum confidence capped at 95% (epistemic humility)
    - "Neutral" is a valid and common outcome
    """
    
    def generate_signal(
        self,
        market_data: MarketData,
        indicators: TechnicalIndicators,
        time_horizon: TimeHorizon = TimeHorizon.LONG_TERM
    ) -> Signal:
        """
        Generate a trading signal based on market data and indicators.
        
        Args:
            market_data: Historical price and fundamental data
            indicators: Calculated technical indicators
            time_horizon: Investment time horizon
            
        Returns:
            Signal with type, confidence, and reasoning
        """
        # Evaluate individual signals
        signals_data = self._evaluate_indicators(indicators)
        
        # Aggregate signals
        signal_type, confidence = self._aggregate_signals(signals_data)
        
        # Determine signal strength
        strength = self._determine_strength(confidence)
        
        # Build reasoning
        reasoning = self._build_reasoning(signals_data, signal_type, indicators)
        
        return Signal(
            ticker=indicators.ticker,
            timestamp=datetime.now(),
            strength=SignalStrength(
                signal_type=signal_type,
                confidence=confidence,
                strength=strength
            ),
            reasoning=reasoning,
            time_horizon=time_horizon
        )
    
    def _evaluate_indicators(
        self,
        indicators: TechnicalIndicators
    ) -> Dict[str, Tuple[SignalType, float, str]]:
        """
        Evaluate each technical indicator and return individual signals.
        
        Returns:
            Dict mapping indicator name to (signal_type, weight, explanation)
        """
        signals = {}
        
        # 1. Moving Average Crossover (Trend)
        if indicators.sma_20 and indicators.sma_50:
            if indicators.sma_20 > indicators.sma_50:
                diff_pct = (indicators.sma_20 - indicators.sma_50) / indicators.sma_50
                weight = min(0.3, diff_pct * 10)  # Up to 0.3 weight
                signals["ma_crossover"] = (
                    SignalType.BULLISH,
                    weight,
                    f"20-day SMA (${indicators.sma_20:.2f}) above 50-day SMA (${indicators.sma_50:.2f})"
                )
            elif indicators.sma_50 > indicators.sma_20:
                diff_pct = (indicators.sma_50 - indicators.sma_20) / indicators.sma_20
                weight = min(0.3, diff_pct * 10)
                signals["ma_crossover"] = (
                    SignalType.BEARISH,
                    weight,
                    f"20-day SMA (${indicators.sma_20:.2f}) below 50-day SMA (${indicators.sma_50:.2f})"
                )
        
        # 2. RSI (Momentum)
        if indicators.rsi is not None:
            if indicators.rsi < 30:
                # Oversold - potential buy
                weight = (30 - indicators.rsi) / 30 * 0.25  # Up to 0.25
                signals["rsi"] = (
                    SignalType.BULLISH,
                    weight,
                    f"RSI at {indicators.rsi:.1f} suggests oversold conditions"
                )
            elif indicators.rsi > 70:
                # Overbought - potential sell
                weight = (indicators.rsi - 70) / 30 * 0.25
                signals["rsi"] = (
                    SignalType.BEARISH,
                    weight,
                    f"RSI at {indicators.rsi:.1f} suggests overbought conditions"
                )
            else:
                # Neutral zone
                signals["rsi"] = (
                    SignalType.NEUTRAL,
                    0.1,
                    f"RSI at {indicators.rsi:.1f} in neutral range"
                )
        
        # 3. MACD (Trend and Momentum)
        if indicators.macd is not None and indicators.macd_signal is not None:
            if indicators.macd > indicators.macd_signal:
                diff = abs(indicators.macd - indicators.macd_signal)
                weight = min(0.25, diff / indicators.current_price * 10)
                signals["macd"] = (
                    SignalType.BULLISH,
                    weight,
                    f"MACD ({indicators.macd:.2f}) above signal line ({indicators.macd_signal:.2f})"
                )
            else:
                diff = abs(indicators.macd_signal - indicators.macd)
                weight = min(0.25, diff / indicators.current_price * 10)
                signals["macd"] = (
                    SignalType.BEARISH,
                    weight,
                    f"MACD ({indicators.macd:.2f}) below signal line ({indicators.macd_signal:.2f})"
                )
        
        # 4. Bollinger Bands (Volatility and Mean Reversion)
        if all([indicators.bollinger_upper, indicators.bollinger_lower, indicators.bollinger_middle]):
            price = indicators.current_price
            upper = indicators.bollinger_upper
            lower = indicators.bollinger_lower
            middle = indicators.bollinger_middle
            
            if price < lower:
                # Below lower band - oversold
                distance = (lower - price) / middle
                weight = min(0.2, distance * 2)
                signals["bollinger"] = (
                    SignalType.BULLISH,
                    weight,
                    f"Price (${price:.2f}) below lower Bollinger Band (${lower:.2f})"
                )
            elif price > upper:
                # Above upper band - overbought
                distance = (price - upper) / middle
                weight = min(0.2, distance * 2)
                signals["bollinger"] = (
                    SignalType.BEARISH,
                    weight,
                    f"Price (${price:.2f}) above upper Bollinger Band (${upper:.2f})"
                )
            else:
                signals["bollinger"] = (
                    SignalType.NEUTRAL,
                    0.05,
                    f"Price within Bollinger Bands"
                )
        
        return signals
    
    def _aggregate_signals(
        self,
        signals_data: Dict[str, Tuple[SignalType, float, str]]
    ) -> Tuple[SignalType, float]:
        """
        Aggregate individual signals into an overall signal with confidence.
        
        Returns:
            (signal_type, confidence_score)
        """
        bullish_score = 0.0
        bearish_score = 0.0
        neutral_score = 0.0
        
        for signal_type, weight, _ in signals_data.values():
            if signal_type == SignalType.BULLISH:
                bullish_score += weight
            elif signal_type == SignalType.BEARISH:
                bearish_score += weight
            else:
                neutral_score += weight
        
        # Determine dominant signal
        max_score = max(bullish_score, bearish_score, neutral_score)
        
        if max_score == bullish_score and bullish_score > 0.3:
            # Need at least 0.3 to be actionable
            signal_type = SignalType.BULLISH
            confidence = min(bullish_score / (bullish_score + bearish_score + neutral_score), 0.95)
        elif max_score == bearish_score and bearish_score > 0.3:
            signal_type = SignalType.BEARISH
            confidence = min(bearish_score / (bullish_score + bearish_score + neutral_score), 0.95)
        else:
            # Default to neutral if signals are mixed or weak
            signal_type = SignalType.NEUTRAL
            confidence = 0.5 + (neutral_score * 0.2)  # Neutral confidence 0.5-0.7
        
        # Cap confidence at 95%
        confidence = min(confidence, 0.95)
        
        return signal_type, confidence
    
    def _determine_strength(self, confidence: float) -> str:
        """Determine signal strength based on confidence"""
        if confidence < 0.6:
            return "weak"
        elif confidence < 0.75:
            return "moderate"
        else:
            return "strong"
    
    def _build_reasoning(
        self,
        signals_data: Dict[str, Tuple[SignalType, float, str]],
        final_signal: SignalType,
        indicators: TechnicalIndicators
    ) -> SignalReasoning:
        """Build detailed reasoning for the signal"""
        
        primary_factors = []
        contradicting_factors = []
        supporting_indicators = {}
        
        for indicator_name, (signal_type, weight, explanation) in signals_data.items():
            if signal_type == final_signal:
                primary_factors.append(explanation)
            elif signal_type != SignalType.NEUTRAL and signal_type != final_signal:
                contradicting_factors.append(explanation)
            
            # Add indicator values
            if indicator_name == "rsi" and indicators.rsi:
                supporting_indicators["RSI"] = indicators.rsi
            elif indicator_name == "macd" and indicators.macd:
                supporting_indicators["MACD"] = indicators.macd
            elif indicator_name == "ma_crossover" and indicators.sma_20:
                supporting_indicators["SMA_20"] = indicators.sma_20
        
        # Assumptions
        assumptions = [
            "Historical price patterns are indicative of future behavior",
            "Technical indicators are calculated correctly from market data",
            "Market conditions remain relatively stable",
            f"Analysis is based on {indicators.ticker} closing prices"
        ]
        
        # Limitations
        limitations = [
            "Does not account for fundamental company changes or news",
            "Based solely on technical analysis",
            "Past performance does not guarantee future results",
            "External market shocks can invalidate technical signals",
            "Confidence scores are probabilistic estimates, not certainties"
        ]
        
        return SignalReasoning(
            primary_factors=primary_factors if primary_factors else ["No strong signals detected"],
            supporting_indicators=supporting_indicators,
            contradicting_factors=contradicting_factors,
            assumptions=assumptions,
            limitations=limitations
        )


# Singleton instance
signal_generator = SignalGenerator()
