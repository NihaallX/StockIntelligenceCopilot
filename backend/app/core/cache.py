"""Simple in-memory cache manager"""

import logging
from typing import Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import threading

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with TTL"""
    key: str
    value: Any
    expires_at: datetime


class CacheManager:
    """
    Simple in-memory cache with TTL.
    
    For production, replace with Redis.
    """
    
    def __init__(self):
        self._cache: dict[str, CacheEntry] = {}
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                return None
            
            if datetime.now() > entry.expires_at:
                # Expired - remove
                del self._cache[key]
                logger.debug(f"Cache EXPIRED: {key}")
                return None
            
            logger.debug(f"Cache HIT: {key}")
            return entry.value
    
    def set(self, key: str, value: Any, ttl: int):
        """
        Set cached value with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        with self._lock:
            expires_at = datetime.now() + timedelta(seconds=ttl)
            self._cache[key] = CacheEntry(key, value, expires_at)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
    
    def delete(self, key: str):
        """Delete cached value"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Cache DELETE: {key}")
    
    def clear(self):
        """Clear all cached values"""
        with self._lock:
            self._cache.clear()
            logger.info("Cache CLEARED")
    
    def cleanup_expired(self):
        """Remove expired entries (periodic cleanup)"""
        with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key, entry in self._cache.items()
                if now > entry.expires_at
            ]
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.info(f"Cache cleanup: removed {len(expired_keys)} expired entries")


# Singleton instance
cache_manager = CacheManager()
