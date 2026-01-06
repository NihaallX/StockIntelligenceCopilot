"""Language & UX Layer - Beginner-Friendly, Conditional Phrasing

Converts technical detections into calm, diplomatic language.

NEVER use:
- "BUY NOW" / "SELL IMMEDIATELY"
- Price targets
- Time guarantees
- Urgency language

ALWAYS use:
- Conditional phrasing ("if", "may", "looks like")
- Calm tone
- Beginner-readable explanations
- No jargon without context
"""

from typing import Dict, List
from .method_layer import Detection, DetectionTag
from .regime_mcp import MarketContext, RegimeContext
from .data_layer import IntradayMetrics


class LanguageFormatter:
    """
    Formats technical data into beginner-friendly language.
    
    All output is:
    - Conditional (never directive)
    - Calm (never urgent)
    - Readable (minimal jargon)
    """
    
    def __init__(self):
        self.forbidden_words = [
            "buy now", "sell now", "immediately", "must", 
            "will", "guaranteed", "target", "stop loss",
            "get in", "get out", "act now"
        ]
    
    def format_daily_overview(self, detection: Detection) -> Dict:
        """
        Format for "Today's Watch" homepage card.
        
        Output:
        {
            "ticker": "RELIANCE.NS",
            "tags": ["⚠️ Weak vs index", "📊 High exposure"],
            "one_line": "This stock looks weak today and represents large portfolio exposure."
        }
        """
        tags_display = []
        
        # Convert technical tags to beginner-friendly labels
        if DetectionTag.WEAK_TREND in detection.tags:
            tags_display.append("⚠️ Weak vs index")
        
        if DetectionTag.EXTENDED_MOVE in detection.tags:
            tags_display.append("📈 Extended move")
        
        if DetectionTag.PORTFOLIO_RISK in detection.tags:
            tags_display.append("📊 High exposure")
        
        # Generate one-line summary
        one_line = self._generate_one_liner(detection)
        
        return {
            "ticker": detection.ticker,
            "tags": tags_display,
            "one_line": one_line,
            "severity": detection.severity
        }
    
    def format_detailed_view(
        self,
        detection: Detection,
        metrics: IntradayMetrics,
        market_context: MarketContext
    ) -> Dict:
        """
        Format for detailed stock view page.
        
        Output includes:
        - Explanation paragraphs
        - Conditional notes
        - Market context badge
        - Risk levels (not recommendations)
        """
        # Main explanation
        explanation = self._build_explanation(detection, metrics)
        
        # Conditional note
        conditional_note = self._build_conditional_note(detection, metrics)
        
        # Context badge
        context_badge = self._format_context_badge(market_context)
        
        # Risk summary
        risk_summary = self._build_risk_summary(detection)
        
        return {
            "ticker": detection.ticker,
            "explanation": explanation,
            "conditional_note": conditional_note,
            "context_badge": context_badge,
            "risk_summary": risk_summary,
            "severity": detection.severity,
            "detected_at": metrics.timestamp.isoformat()
        }
    
    def _generate_one_liner(self, detection: Detection) -> str:
        """Generate a single-line summary"""
        
        if not detection.tags:
            return "No significant patterns detected today."
        
        descriptors = []
        
        if DetectionTag.WEAK_TREND in detection.tags:
            descriptors.append("showing weakness")
        
        if DetectionTag.EXTENDED_MOVE in detection.tags:
            descriptors.append("has moved sharply")
        
        if DetectionTag.PORTFOLIO_RISK in detection.tags:
            descriptors.append("represents significant portfolio exposure")
        
        # Combine with "and"
        if len(descriptors) == 1:
            return f"This stock {descriptors[0]}."
        elif len(descriptors) == 2:
            return f"This stock {descriptors[0]} and {descriptors[1]}."
        else:
            all_but_last = ", ".join(descriptors[:-1])
            return f"This stock {all_but_last}, and {descriptors[-1]}."
    
    def _build_explanation(
        self, 
        detection: Detection, 
        metrics: IntradayMetrics
    ) -> str:
        """
        Build detailed explanation paragraph.
        
        Uses actual triggered conditions for transparency.
        """
        if not detection.tags:
            return (
                f"{metrics.ticker} appears to be trading normally today. "
                "No significant risk patterns detected at this time."
            )
        
        paragraphs = []
        
        # Trend stress explanation
        if DetectionTag.WEAK_TREND in detection.tags:
            conditions = detection.triggered_conditions[DetectionTag.WEAK_TREND]
            para = (
                f"**Trend Weakness Detected**: {metrics.ticker} is showing signs of "
                "weakness today. "
            )
            # Add specific conditions
            bullets = "\n".join([f"• {c}" for c in conditions])
            para += f"\n\n{bullets}"
            paragraphs.append(para)
        
        # Mean reversion explanation
        if DetectionTag.EXTENDED_MOVE in detection.tags:
            conditions = detection.triggered_conditions[DetectionTag.EXTENDED_MOVE]
            para = (
                "**Extended Move Detected**: The stock has made a sharp move "
                "that may be nearing exhaustion. "
            )
            bullets = "\n".join([f"• {c}" for c in conditions])
            para += f"\n\n{bullets}"
            paragraphs.append(para)
        
        # Portfolio risk explanation
        if DetectionTag.PORTFOLIO_RISK in detection.tags:
            conditions = detection.triggered_conditions[DetectionTag.PORTFOLIO_RISK]
            para = (
                "**Portfolio Concentration**: This position represents a significant "
                "portion of your portfolio. "
            )
            bullets = "\n".join([f"• {c}" for c in conditions])
            para += f"\n\n{bullets}"
            paragraphs.append(para)
        
        return "\n\n".join(paragraphs)
    
    def _build_conditional_note(
        self, 
        detection: Detection, 
        metrics: IntradayMetrics
    ) -> str:
        """
        Build conditional "if-then" note.
        
        NEVER directive. ALWAYS conditional.
        """
        if not detection.tags:
            return ""
        
        notes = []
        
        if DetectionTag.WEAK_TREND in detection.tags:
            # Use VWAP as reference point
            notes.append(
                f"If price stays below ₹{metrics.vwap:.2f} (VWAP), "
                "downside risk may increase."
            )
        
        if DetectionTag.EXTENDED_MOVE in detection.tags:
            # Use recent high/low as reference
            if metrics.stock_change_pct > 0:
                notes.append(
                    f"If price fails to hold above ₹{metrics.sma_20:.2f}, "
                    "the move may reverse."
                )
            else:
                notes.append(
                    f"If price recovers above ₹{metrics.sma_20:.2f}, "
                    "selling pressure may ease."
                )
        
        if DetectionTag.PORTFOLIO_RISK in detection.tags:
            notes.append(
                "Consider whether this concentration aligns with your risk comfort level."
            )
        
        return " ".join(notes)
    
    def _format_context_badge(self, context: MarketContext) -> Dict:
        """
        Format market context for badge display.
        
        Returns:
        {
            "labels": ["Index-Led", "Post-Lunch"],
            "tooltip": "Stock movement is driven by index-level pressure..."
        }
        """
        # Human-readable labels
        label_map = {
            RegimeContext.INDEX_LED_MOVE: "Index-Led",
            RegimeContext.LOW_LIQUIDITY_CHOP: "Low Liquidity",
            RegimeContext.POST_LUNCH_VOLATILITY: "Post-Lunch",
            RegimeContext.EXPIRY_PRESSURE: "Expiry Week",
            RegimeContext.SECTOR_BASKET_MOVE: "Sector Move",
            RegimeContext.PRE_MARKET_GAP: "Gap Move",
            RegimeContext.LAST_HOUR_VOLATILITY: "Last Hour",
        }
        
        labels = [label_map.get(c, str(c)) for c in context.contexts]
        
        return {
            "labels": labels,
            "tooltip": context.explanation
        }
    
    def _build_risk_summary(self, detection: Detection) -> str:
        """
        Build risk level summary (NOT a recommendation).
        
        Returns calm assessment of risk factors.
        """
        severity_text = {
            "watch": "⚪ Normal monitoring recommended",
            "caution": "🟡 Elevated factors present",
            "alert": "🔴 Multiple factors detected"
        }
        
        return severity_text.get(detection.severity, "⚪ Normal")
    
    def validate_output(self, text: str) -> bool:
        """
        Validate that output doesn't contain forbidden words/phrases.
        
        Returns True if clean, False if violations found.
        """
        text_lower = text.lower()
        
        for forbidden in self.forbidden_words:
            if forbidden in text_lower:
                return False
        
        return True
    
    def format_batch_overview(
        self, 
        detections: List[Detection]
    ) -> List[Dict]:
        """
        Format multiple detections for daily overview page.
        
        Sorted by severity (alert > caution > watch).
        """
        # Sort by severity
        severity_order = {"alert": 0, "caution": 1, "watch": 2}
        sorted_detections = sorted(
            detections,
            key=lambda d: severity_order.get(d.severity, 3)
        )
        
        return [
            self.format_daily_overview(d) 
            for d in sorted_detections
        ]
