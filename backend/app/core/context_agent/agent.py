"""Market Context Agent - Core implementation

READ-ONLY context enrichment layer.
Does NOT generate signals, predictions, or recommendations.
"""

import logging
import hashlib
import json
from typing import Optional
from datetime import datetime

from .models import (
    ContextEnrichmentInput,
    ContextEnrichmentOutput,
    SupportingPoint,
    SafeContextOutput
)
from .mcp_fetcher import MCPContextFetcher
from app.core.cache import cache_manager

logger = logging.getLogger(__name__)


class MarketContextAgent:
    """
    Market Context Agent - MCP-based context enrichment
    
    This agent is READ-ONLY and EXPLANATORY.
    It accepts structured opportunity objects and enriches them with real-world
    market context from reputable sources.
    
    HARD CONSTRAINTS:
    - Does NOT generate buy/sell recommendations
    - Does NOT predict prices or timing
    - Does NOT alter opportunity type, confidence, or risk
    - Does NOT invent data
    - Does NOT run if no opportunity object is provided
    
    Usage:
        agent = MarketContextAgent(enabled=True)
        context = await agent.enrich_opportunity(input_data)
    """
    
    def __init__(self, enabled: bool = False):
        """
        Initialize the Market Context Agent
        
        Args:
            enabled: Whether MCP context fetching is enabled (default: False)
        """
        self.enabled = enabled
        self.mcp_fetcher = MCPContextFetcher() if enabled else None
        
        logger.info(
            f"Market Context Agent initialized: "
            f"enabled={enabled}"
        )
    
    async def enrich_opportunity(
        self,
        input_data: ContextEnrichmentInput,
        use_cache: bool = True,
        cache_ttl: int = 300  # 5 minutes default
    ) -> ContextEnrichmentOutput:
        """
        Enrich an opportunity with market context (with caching)
        
        This method:
        1. Validates input (opportunity must be provided)
        2. Checks cache for recent results (if use_cache=True)
        3. Uses MCP to fetch real-world context if cache miss
        4. Caches results with TTL
        5. Returns context WITH CITATIONS
        6. Returns safe fallback if MCP fails
        
        Args:
            input_data: Structured input with opportunity and ticker info
            use_cache: Whether to use/store cache (default: True)
            cache_ttl: Cache time-to-live in seconds (default: 300 = 5min)
        
        Returns:
            ContextEnrichmentOutput with market context and citations
        """
        
        # Validation: opportunity must be provided
        if not input_data.opportunity:
            logger.warning("No opportunity provided - returning safe output")
            return self._safe_output(mcp_status="failed")
        
        # If MCP is disabled, return safe output immediately
        if not self.enabled or not self.mcp_fetcher:
            logger.info("MCP context enrichment disabled - skipping")
            return self._safe_output(mcp_status="disabled")
        
        # Generate signal hash for cache key
        signal_hash = self._generate_signal_hash(input_data)
        cache_key = f"mcp_context:{input_data.ticker}:{signal_hash}"
        
        # Check cache first (if enabled)
        if use_cache:
            cached_context = cache_manager.get(cache_key)
            if cached_context:
                logger.info(f"✅ MCP cache HIT for {input_data.ticker} (hash: {signal_hash[:8]})")
                return cached_context
            else:
                logger.debug(f"MCP cache MISS for {input_data.ticker}")
        
        # Attempt to fetch context via MCP
        try:
            logger.info(
                f"Fetching market context for {input_data.ticker} "
                f"(horizon: {input_data.time_horizon}, signal: {input_data.signal_type})"
            )
            
            context = await self.mcp_fetcher.fetch_context(
                ticker=input_data.ticker,
                market=input_data.market,
                time_horizon=input_data.time_horizon,
                signal_type=input_data.signal_type,
                signal_reasons=input_data.signal_reasons,
                confidence=input_data.confidence
            )
            
            # Validate that we got usable context
            if not context.supporting_points:
                logger.warning(
                    f"No supporting points found for {input_data.ticker} - "
                    f"returning safe output"
                )
                return self._safe_output(mcp_status="partial")
            
            logger.info(
                f"✅ Context enrichment successful: "
                f"{len(context.supporting_points)} points from "
                f"{len(context.data_sources_used)} sources"
            )
            
            # Cache the result
            if use_cache:
                cache_manager.set(cache_key, context, ttl=cache_ttl)
                logger.debug(f"Cached MCP result for {input_data.ticker} (TTL: {cache_ttl}s)")
            
            return context
            
        except Exception as e:
            logger.error(
                f"Context enrichment failed for {input_data.ticker}: {e}",
                exc_info=True
            )
            return self._safe_output(mcp_status="failed")
    
    def _safe_output(
        self,
        mcp_status: str = "disabled"
    ) -> ContextEnrichmentOutput:
        """
        Return safe fallback output when MCP fails or is disabled
        
        Args:
            mcp_status: Status to include in output
        
        Returns:
            ContextEnrichmentOutput with safe defaults
        """
        return ContextEnrichmentOutput(
            context_summary="No additional market context available at this time.",
            supporting_points=[],
            data_sources_used=[],
            disclaimer="Informational only. Not financial advice.",
            enriched_at=datetime.utcnow(),
            mcp_status=mcp_status
        )
    
    def _generate_signal_hash(self, input_data: ContextEnrichmentInput) -> str:
        """
        Generate hash of signal for cache invalidation
        
        Hash includes:
        - Ticker
        - Signal type
        - Signal reasons
        - Confidence (rounded to 2 decimals)
        
        This ensures cache is invalidated when signal changes.
        
        Args:
            input_data: Input data to hash
        
        Returns:
            SHA256 hash (first 16 chars)
        """
        hash_content = {
            "ticker": input_data.ticker,
            "signal_type": input_data.signal_type,
            "signal_reasons": sorted(input_data.signal_reasons),  # Sort for consistency
            "confidence": round(input_data.confidence, 2)
        }
        
        hash_string = json.dumps(hash_content, sort_keys=True)
        hash_obj = hashlib.sha256(hash_string.encode())
        return hash_obj.hexdigest()[:16]  # First 16 chars is enough
    
    def validate_input(self, input_data: ContextEnrichmentInput) -> bool:
        """
        Validate input data
        
        Args:
            input_data: Input to validate
        
        Returns:
            True if valid, False otherwise
        """
        if not input_data.opportunity:
            logger.warning("Validation failed: No opportunity provided")
            return False
        
        if not input_data.ticker:
            logger.warning("Validation failed: No ticker provided")
            return False
        
        return True
