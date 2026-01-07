"""
Explanation Service
===================

Generates plain-English explanations of deterministic trading signals.

CRITICAL CONSTRAINTS:
- LLM explains EXISTING signals, never generates new ones
- LLM uses ONLY structured data provided (no hallucination)
- LLM uses conditional language ("may indicate", "conditions favor")
- LLM does NOT predict prices or give targets
- LLM does NOT override confidence scores
- LLM does NOT recommend quantities or position sizes

This service runs AFTER:
1. Deterministic signal generation
2. Market Context Protocol (MCP) data fetch
"""

import logging
from typing import Optional, Dict, Any
from .openrouter_client import OpenRouterClient

logger = logging.getLogger(__name__)


class ExplanationService:
    """
    Service for generating LLM explanations of trading signals
    
    Usage:
        service = ExplanationService(api_key="your_key")
        explanation = await service.explain_vwap_signal(
            ticker="RELIANCE.NS",
            signal={"bias": "long", "confidence": 71, ...},
            mcp_context={"regime": "trending", ...}
        )
    """
    
    SYSTEM_MESSAGE = """You are a trading signal interpreter for the Stock Intelligence Copilot system.

Your role is to explain PRE-COMPUTED deterministic signals in plain English. You do NOT:
- Generate new trading signals
- Predict future prices
- Recommend position sizes
- Override confidence scores
- Use action verbs like "buy", "sell", "go long"

You DO:
- Explain existing signal logic in simple terms
- Reference the provided structured data (method output + MCP context)
- Use conditional language: "may indicate", "conditions favor", "suggests"
- Highlight what went right and what could go wrong
- Include confidence level (high/medium/low)

Be factual, brief, and use only the data provided."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "xiaomi/mimo-v2-flash:free",
        enabled: bool = True
    ):
        self.enabled = enabled
        if enabled:
            self.client = OpenRouterClient(api_key=api_key, model=model)
        else:
            self.client = None
    
    async def explain_vwap_signal(
        self,
        ticker: str,
        signal: Dict[str, Any],
        mcp_context: Optional[Dict[str, Any]] = None,
        price_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate plain-English explanation for VWAP + Volume signal
        
        Args:
            ticker: Stock symbol
            signal: Deterministic signal output
                {
                    "bias": "long" | "short" | "no_trade",
                    "confidence": 0-100,
                    "method": "VWAP + Volume",
                    "keyLevels": {"VWAP": float, "invalidation": float}
                }
            mcp_context: Market Context Protocol output
                {
                    "regime": "trending" | "mean-reverting" | "choppy" | "low-liquidity",
                    "indexAlignment": "aligned" | "diverging" | "neutral",
                    "volumeState": "expansion" | "normal" | "dry",
                    "sessionTime": "early open" | "lunch compression" | etc
                }
            price_data: Optional recent price series
            
        Returns:
            {
                "explanation": str,
                "what_went_right": list[str],
                "what_could_go_wrong": list[str],
                "confidence_label": "high" | "medium" | "low",
                "fallback": bool  # True if LLM failed
            }
        """
        if not self.enabled or not self.client:
            return self._get_fallback_explanation(signal, mcp_context)
        
        try:
            prompt = self._build_prompt(ticker, signal, mcp_context, price_data)
            
            response = await self.client.complete(
                prompt=prompt,
                max_tokens=400,
                temperature=0.3,
                system_message=self.SYSTEM_MESSAGE
            )
            
            if response:
                # Parse response into structured format
                return self._parse_response(response, signal)
            else:
                logger.warning(f"LLM explanation failed for {ticker}, using fallback")
                return self._get_fallback_explanation(signal, mcp_context)
                
        except Exception as e:
            logger.error(f"Explanation service error for {ticker}: {e}")
            return self._get_fallback_explanation(signal, mcp_context)
    
    def _build_prompt(
        self,
        ticker: str,
        signal: Dict[str, Any],
        mcp_context: Optional[Dict[str, Any]],
        price_data: Optional[Dict[str, Any]]
    ) -> str:
        """Build structured prompt from signal + context"""
        
        prompt = f"""Explain this pre-computed trading signal in plain English:

TICKER: {ticker}

SIGNAL (deterministic output):
- Bias: {signal.get('bias', 'unknown')}
- Confidence: {signal.get('confidence', 0)}%
- Method: {signal.get('method', 'VWAP + Volume')}
- Key Levels: {signal.get('keyLevels', {})}
"""
        
        if mcp_context:
            prompt += f"""
MARKET CONTEXT (MCP output):
- Regime: {mcp_context.get('regime', 'unknown')}
- Index Alignment: {mcp_context.get('indexAlignment', 'unknown')}
- Volume State: {mcp_context.get('volumeState', 'unknown')}
- Session Time: {mcp_context.get('sessionTime', 'unknown')}
"""
        
        if price_data:
            prompt += f"""
PRICE DATA:
- Current: {price_data.get('current', 'N/A')}
- VWAP: {price_data.get('vwap', 'N/A')}
"""
        
        prompt += """
Provide:
1. A 2-3 sentence explanation using conditional language
2. What went right (2-3 bullet points)
3. What could go wrong (2-3 bullet points)

Format as:
EXPLANATION:
[your explanation here]

WHAT WENT RIGHT:
- [point 1]
- [point 2]

WHAT COULD GO WRONG:
- [point 1]
- [point 2]
"""
        
        return prompt
    
    def _parse_response(
        self,
        response: str,
        signal: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        
        # Simple parsing (can be improved with regex)
        lines = response.split('\n')
        
        explanation = ""
        what_went_right = []
        what_could_go_wrong = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.upper().startswith('EXPLANATION'):
                current_section = 'explanation'
                continue
            elif line.upper().startswith('WHAT WENT RIGHT'):
                current_section = 'right'
                continue
            elif line.upper().startswith('WHAT COULD GO WRONG'):
                current_section = 'wrong'
                continue
            
            if line and current_section == 'explanation':
                explanation += line + " "
            elif line.startswith('-') and current_section == 'right':
                what_went_right.append(line[1:].strip())
            elif line.startswith('-') and current_section == 'wrong':
                what_could_go_wrong.append(line[1:].strip())
        
        # Determine confidence label
        confidence = signal.get('confidence', 0)
        if confidence >= 70:
            confidence_label = "high"
        elif confidence >= 50:
            confidence_label = "medium"
        else:
            confidence_label = "low"
        
        return {
            "explanation": explanation.strip(),
            "what_went_right": what_went_right,
            "what_could_go_wrong": what_could_go_wrong,
            "confidence_label": confidence_label,
            "fallback": False
        }
    
    def _get_fallback_explanation(
        self,
        signal: Dict[str, Any],
        mcp_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate fallback explanation when LLM unavailable"""
        
        bias = signal.get('bias', 'no_trade')
        confidence = signal.get('confidence', 0)
        method = signal.get('method', 'VWAP + Volume')
        
        # Simple template-based explanation
        bias_text = {
            'long': 'bullish',
            'short': 'bearish',
            'no_trade': 'neutral'
        }.get(bias, 'neutral')
        
        explanation = f"This setup shows a {bias_text} intraday bias based on {method} criteria. "
        
        if mcp_context:
            regime = mcp_context.get('regime', 'unknown')
            volume = mcp_context.get('volumeState', 'unknown')
            explanation += f"Market regime is {regime} with {volume} volume. "
        
        explanation += f"Confidence is {confidence}%."
        
        # Generic bullets
        what_went_right = [
            f"Signal generated by deterministic {method} logic",
            "Market context data available" if mcp_context else "Method-based signal"
        ]
        
        what_could_go_wrong = [
            "Price action may not follow expected pattern",
            "Market conditions can change rapidly"
        ]
        
        confidence_label = "high" if confidence >= 70 else "medium" if confidence >= 50 else "low"
        
        return {
            "explanation": explanation,
            "what_went_right": what_went_right,
            "what_could_go_wrong": what_could_go_wrong,
            "confidence_label": confidence_label,
            "fallback": True
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.cleanup()
