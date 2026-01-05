"""MCP Trigger Logic - Controls when Market Context Agent runs

This module implements intelligent triggering for MCP to avoid excessive API calls.
MCP does NOT run on every price tick - only when meaningful context is needed.

Design Principles:
- Debounce calls (minimum cooldown per ticker)
- Trigger only on significant events
- Never block core analysis
- Track trigger history for monitoring
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TriggerState:
    """Track MCP trigger state for a ticker"""
    last_triggered: datetime
    last_opportunity_type: Optional[str]
    last_volatility: Optional[float]
    trigger_count: int
    last_signal_hash: Optional[str] = None  # Hash of signal to detect changes
    last_user_id: Optional[str] = None      # User who last triggered


@dataclass
class UserSession:
    """Track user's daily MCP usage"""
    user_id: str
    last_login_mcp_run: datetime
    daily_mcp_count: int
    session_date: str  # YYYY-MM-DD


class MCPTriggerManager:
    """
    Manages when MCP should run based on intelligent triggers
    
    MCP Trigger Rules (UPDATED for Task 2):
    1. **On Login**: Once per day per user, only for changed signals
    2. **On Explicit Click**: Immediate execution (bypasses cooldown)
    3. **Automatic**: New opportunity detected → Trigger
    4. **Automatic**: Opportunity type changed → Trigger
    5. **Automatic**: Volatility crossed threshold → Trigger
    6. **Cooldown**: Minimum 5 minutes between auto-triggers (doesn't apply to clicks)
    7. **Caching**: MCP results cached for 5 minutes
    
    Example:
        trigger_mgr = MCPTriggerManager(cooldown_minutes=5)
        
        # User logs in - triggers MCP for portfolio signals (once per day)
        if trigger_mgr.should_trigger_on_login(user_id="user123", ticker="RELIANCE.NS"):
            context = await agent.enrich_opportunity(...)
        
        # User clicks "Why does this matter?" - immediate trigger
        if trigger_mgr.should_trigger("RELIANCE.NS", explicit_user_click=True):
            context = await agent.enrich_opportunity(...)
        
        # Automatic analysis - respects cooldown
        if trigger_mgr.should_trigger("RELIANCE.NS", "BREAKOUT", volatility=0.15):
            context = await agent.enrich_opportunity(...)
    """
    
    def __init__(
        self,
        cooldown_minutes: int = 5,
        volatility_threshold: float = 0.05,
        enabled: bool = True,
        cache_ttl_seconds: int = 300  # 5 minutes
    ):
        """
        Initialize MCP trigger manager
        
        Args:
            cooldown_minutes: Minimum time between MCP calls for same ticker
            volatility_threshold: Volatility change that triggers MCP (5% default)
            enabled: Master switch for MCP triggering
            cache_ttl_seconds: TTL for MCP result cache (default 300s = 5min)
        """
        self.cooldown_minutes = cooldown_minutes
        self.volatility_threshold = volatility_threshold
        self.enabled = enabled
        self.cache_ttl_seconds = cache_ttl_seconds
        
        # Track state per ticker
        self._state: Dict[str, TriggerState] = {}
        
        # Track user sessions for daily limits
        self._user_sessions: Dict[str, UserSession] = {}
        
        logger.info(
            f"MCP Trigger Manager initialized: "
            f"cooldown={cooldown_minutes}min, "
            f"volatility_threshold={volatility_threshold:.1%}, "
            f"enabled={enabled}"
        )
    
    def should_trigger(
        self,
        ticker: str,
        opportunity_type: Optional[str] = None,
        volatility: Optional[float] = None,
        force: bool = False,
        explicit_user_click: bool = False,
        signal_hash: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Determine if MCP should run for this analysis
        
        Args:
            ticker: Stock ticker (e.g., RELIANCE.NS)
            opportunity_type: Type of opportunity (BREAKOUT, REVERSAL, etc.)
            volatility: Current volatility metric (0-1 scale)
            force: Override all rules and trigger MCP
            explicit_user_click: User clicked "Why does this matter?" button
            signal_hash: Hash of current signal (to detect changes)
            user_id: User ID (for session tracking)
        
        Returns:
            True if MCP should run, False otherwise
        
        Trigger Logic:
        1. If MCP disabled → False
        2. If explicit_user_click=True → True (bypass cooldown, bypass cache)
        3. If force=True → True
        4. If first time for ticker → True
        5. If signal changed (different hash) → True
        6. If in cooldown period → False (unless overridden by rules below)
        7. If opportunity type changed → True
        8. If volatility crossed threshold → True
        9. Otherwise → False
        """
        
        if not self.enabled:
            logger.debug(f"MCP disabled globally - no trigger for {ticker}")
            return False
        
        # Explicit user click ALWAYS triggers (bypass everything)
        if explicit_user_click:
            logger.info(f"👆 Explicit user click for {ticker} - trigger MCP (bypass cooldown)")
            self._update_state(ticker, opportunity_type, volatility, signal_hash, user_id)
            return True
        
        if force:
            logger.info(f"🔥 Force trigger MCP for {ticker}")
            self._update_state(ticker, opportunity_type, volatility, signal_hash, user_id)
            return True
        
        # Get or create state
        state = self._state.get(ticker)
        
        if state is None:
            # First time seeing this ticker → trigger
            logger.info(f"✅ New ticker {ticker} - trigger MCP (first analysis)")
            self._update_state(ticker, opportunity_type, volatility, signal_hash, user_id)
            return True
        
        # Check if signal changed (new hash)
        if signal_hash and state.last_signal_hash != signal_hash:
            logger.info(
                f"✅ Signal changed for {ticker} "
                f"(hash: {state.last_signal_hash[:8] if state.last_signal_hash else 'None'} → {signal_hash[:8]}) "
                f"- trigger MCP"
            )
            self._update_state(ticker, opportunity_type, volatility, signal_hash, user_id)
            return True
        
        # Check cooldown
        time_since_last = datetime.now() - state.last_triggered
        in_cooldown = time_since_last < timedelta(minutes=self.cooldown_minutes)
        
        if in_cooldown:
            # Check if any override conditions met
            type_changed = state.last_opportunity_type != opportunity_type
            
            volatility_spiked = False
            if volatility is not None and state.last_volatility is not None:
                volatility_change = abs(volatility - state.last_volatility)
                volatility_spiked = volatility_change > self.volatility_threshold
            
            if type_changed:
                logger.info(
                    f"✅ Opportunity type changed for {ticker}: "
                    f"{state.last_opportunity_type} → {opportunity_type} "
                    f"- trigger MCP (override cooldown)"
                )
                self._update_state(ticker, opportunity_type, volatility, signal_hash, user_id)
                return True
            
            if volatility_spiked:
                logger.info(
                    f"✅ Volatility crossed threshold for {ticker}: "
                    f"{state.last_volatility:.2%} → {volatility:.2%} "
                    f"- trigger MCP (override cooldown)"
                )
                self._update_state(ticker, opportunity_type, volatility, signal_hash, user_id)
                return True
            
            # In cooldown, no overrides
            logger.debug(
                f"⏳ {ticker} in cooldown: "
                f"{time_since_last.total_seconds():.0f}s / "
                f"{self.cooldown_minutes * 60}s - no trigger"
            )
            return False
        
        # Cooldown expired → trigger
        logger.info(
            f"✅ Cooldown expired for {ticker} "
            f"({time_since_last.total_seconds():.0f}s) - trigger MCP"
        )
        self._update_state(ticker, opportunity_type, volatility, signal_hash, user_id)
        return True
    
    def _update_state(
        self,
        ticker: str,
        opportunity_type: Optional[str],
        volatility: Optional[float],
        signal_hash: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """Update trigger state after MCP runs"""
        existing_state = self._state.get(ticker)
        trigger_count = existing_state.trigger_count + 1 if existing_state else 1
        
        self._state[ticker] = TriggerState(
            last_triggered=datetime.now(),
            last_opportunity_type=opportunity_type,
            last_volatility=volatility,
            trigger_count=trigger_count,
            last_signal_hash=signal_hash,
            last_user_id=user_id
        )
    
    def should_trigger_on_login(
        self,
        user_id: str,
        ticker: str,
        signal_hash: str,
        max_daily_triggers: int = 10
    ) -> bool:
        """
        Determine if MCP should run on user login for portfolio stocks
        
        Rules:
        - Once per day per user per ticker
        - Only if signal changed since last login
        - Respect daily limit (prevent abuse)
        
        Args:
            user_id: User ID
            ticker: Stock ticker
            signal_hash: Hash of current signal
            max_daily_triggers: Maximum MCP triggers per day per user
        
        Returns:
            True if MCP should run on login
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get or create user session
        session = self._user_sessions.get(user_id)
        
        if session is None or session.session_date != today:
            # New day or first login - create fresh session
            self._user_sessions[user_id] = UserSession(
                user_id=user_id,
                last_login_mcp_run=datetime.now(),
                daily_mcp_count=0,
                session_date=today
            )
            session = self._user_sessions[user_id]
            logger.info(f"📅 New session for user {user_id} on {today}")
        
        # Check daily limit
        if session.daily_mcp_count >= max_daily_triggers:
            logger.warning(
                f"⚠️ User {user_id} exceeded daily MCP limit "
                f"({session.daily_mcp_count}/{max_daily_triggers}) - no trigger"
            )
            return False
        
        # Check if signal changed since last login
        ticker_state = self._state.get(ticker)
        
        if ticker_state is None:
            # First time - trigger and update state
            logger.info(f"✅ Login trigger for {ticker} (first time for user {user_id})")
            session.daily_mcp_count += 1
            session.last_login_mcp_run = datetime.now()
            self._update_state(ticker, None, None, signal_hash, user_id)  # Save signal hash
            return True
        
        if ticker_state.last_signal_hash != signal_hash:
            # Signal changed - trigger and update state
            logger.info(
                f"✅ Login trigger for {ticker} "
                f"(signal changed for user {user_id})"
            )
            session.daily_mcp_count += 1
            session.last_login_mcp_run = datetime.now()
            self._update_state(ticker, None, None, signal_hash, user_id)  # Update signal hash
            return True
        
        # Signal unchanged - no trigger
        logger.debug(
            f"⏭️ Login skip for {ticker} "
            f"(signal unchanged for user {user_id})"
        )
        return False
    
    def get_cache_key(self, ticker: str, signal_hash: str) -> str:
        """
        Generate cache key for MCP results
        
        Args:
            ticker: Stock ticker
            signal_hash: Hash of signal (to invalidate on change)
        
        Returns:
            Cache key string
        """
        return f"mcp_context:{ticker}:{signal_hash}"
    
    def reset_ticker(self, ticker: str):
        """Reset trigger state for a ticker (useful for testing)"""
        if ticker in self._state:
            del self._state[ticker]
            logger.info(f"Reset trigger state for {ticker}")
    
    def reset_user_session(self, user_id: str):
        """Reset user session (useful for testing)"""
        if user_id in self._user_sessions:
            del self._user_sessions[user_id]
            logger.info(f"Reset session for user {user_id}")
    
    def get_stats(self) -> Dict[str, any]:
        """Get trigger statistics for monitoring"""
        total_tickers = len(self._state)
        total_triggers = sum(state.trigger_count for state in self._state.values())
        
        return {
            "enabled": self.enabled,
            "cooldown_minutes": self.cooldown_minutes,
            "volatility_threshold": self.volatility_threshold,
            "tracked_tickers": total_tickers,
            "total_triggers": total_triggers,
            "avg_triggers_per_ticker": (
                total_triggers / total_tickers if total_tickers > 0 else 0
            )
        }


# Global singleton instance
_trigger_manager: Optional[MCPTriggerManager] = None


def get_trigger_manager(
    cooldown_minutes: int = 5,
    volatility_threshold: float = 0.05,
    enabled: bool = True
) -> MCPTriggerManager:
    """
    Get or create the global MCP trigger manager
    
    Args:
        cooldown_minutes: Minimum time between MCP calls for same ticker
        volatility_threshold: Volatility change that triggers MCP
        enabled: Master switch for MCP triggering
    
    Returns:
        MCPTriggerManager singleton instance
    """
    global _trigger_manager
    
    if _trigger_manager is None:
        _trigger_manager = MCPTriggerManager(
            cooldown_minutes=cooldown_minutes,
            volatility_threshold=volatility_threshold,
            enabled=enabled
        )
    
    return _trigger_manager
