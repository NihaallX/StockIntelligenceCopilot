"""Database connection and utilities for Supabase"""

from supabase import create_client, Client
from app.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Database:
    """Supabase database client singleton"""
    
    _client: Optional[Client] = None
    _service_client: Optional[Client] = None
    
    @classmethod
    def get_client(cls, use_service_role: bool = False) -> Client:
        """
        Get Supabase client
        
        Args:
            use_service_role: If True, returns client with service role key (bypasses RLS)
        
        Returns:
            Supabase client instance
        """
        if use_service_role:
            if cls._service_client is None:
                cls._service_client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_SERVICE_ROLE_KEY
                )
                logger.info("Initialized Supabase service role client")
            return cls._service_client
        else:
            if cls._client is None:
                cls._client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_ANON_KEY
                )
                logger.info("Initialized Supabase anon client")
            return cls._client
    
    @classmethod
    def close(cls):
        """Close database connections"""
        cls._client = None
        cls._service_client = None
        logger.info("Closed Supabase clients")


# Convenience function
def get_db() -> Client:
    """Get database client"""
    return Database.get_client()


def get_service_db() -> Client:
    """Get database client with service role (for audit logs, etc.)"""
    return Database.get_client(use_service_role=True)
