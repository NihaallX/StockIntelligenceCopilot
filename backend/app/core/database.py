"""Database connection and utilities (replacing Supabase)"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Create Async Engine
# echo=True will log SQL queries (useful for debugging)
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO_LOGS,
    future=True
)

# Async Session Factory
async_session_maker = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def init_db():
    """
    Initialize database tables.
    In a real production app, use Alembic for migrations.
    For this transition, we'll auto-create tables if they don't exist.
    """
    try:
        from app.models.sql_tables import User, UserRiskProfile, PortfolioPosition
        async with engine.begin() as conn:
            # await conn.run_sync(SQLModel.metadata.drop_all) # WARNING: Uncomment only to reset DB
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes to get a database session.
    """
    async with async_session_maker() as session:
        yield session

# Helper aliases to maintain some backward compatibility awareness
# though the API is changing from synchronous/supabase to async/sqlalchemy
get_service_db = get_session
get_db = get_session
