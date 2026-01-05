"""Market hours service for Phase 2D"""

from datetime import datetime, time
from typing import Dict
import pytz
import logging

from app.models.enums import ExchangeEnum, MarketStatusEnum

logger = logging.getLogger(__name__)


class MarketHoursService:
    """
    Track market open/closed status across exchanges.
    
    Handles:
    - Timezone conversions
    - Market hours checking
    - Holiday detection (basic)
    """
    
    MARKET_HOURS = {
        ExchangeEnum.NYSE: {
            "timezone": "America/New_York",
            "open_time": time(9, 30),
            "close_time": time(16, 0),
            "trading_days": [0, 1, 2, 3, 4],  # Monday-Friday
        },
        ExchangeEnum.NASDAQ: {
            "timezone": "America/New_York",
            "open_time": time(9, 30),
            "close_time": time(16, 0),
            "trading_days": [0, 1, 2, 3, 4],
        },
        ExchangeEnum.NSE: {
            "timezone": "Asia/Kolkata",
            "open_time": time(9, 15),
            "close_time": time(15, 30),
            "trading_days": [0, 1, 2, 3, 4],
        },
        ExchangeEnum.BSE: {
            "timezone": "Asia/Kolkata",
            "open_time": time(9, 15),
            "close_time": time(15, 30),
            "trading_days": [0, 1, 2, 3, 4],
        }
    }
    
    def get_market_status(self, exchange: ExchangeEnum) -> Dict:
        """
        Get current market status.
        
        Returns:
            Dict with is_open, timezone, local_time, etc.
        """
        if exchange not in self.MARKET_HOURS:
            raise ValueError(f"Unsupported exchange: {exchange}")
        
        config = self.MARKET_HOURS[exchange]
        tz = pytz.timezone(config["timezone"])
        
        # Get current time in market timezone
        now = datetime.now(tz)
        current_time = now.time()
        current_day = now.weekday()
        
        # Check if trading day
        is_trading_day = current_day in config["trading_days"]
        
        # Check if within trading hours
        is_within_hours = (
            config["open_time"] <= current_time <= config["close_time"]
        )
        
        is_open = is_trading_day and is_within_hours
        
        # Calculate next open/close (simplified - doesn't handle holidays)
        next_open = None
        next_close = None
        
        if is_open:
            # Market is open, next event is close
            next_close = now.replace(
                hour=config["close_time"].hour,
                minute=config["close_time"].minute,
                second=0
            ).isoformat()
        else:
            # Market is closed, calculate next open
            if is_trading_day and current_time < config["open_time"]:
                # Today before open
                next_open = now.replace(
                    hour=config["open_time"].hour,
                    minute=config["open_time"].minute,
                    second=0
                ).isoformat()
            else:
                # After close or weekend - next trading day
                next_open = "Next trading day"  # Simplified
        
        return {
            "is_open": is_open,
            "timezone": config["timezone"],
            "local_time": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "next_open": next_open,
            "next_close": next_close
        }
    
    def is_market_open(self, exchange: ExchangeEnum) -> bool:
        """Quick check if market is currently open"""
        status = self.get_market_status(exchange)
        return status["is_open"]
