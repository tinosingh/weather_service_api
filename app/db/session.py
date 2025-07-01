"""
Database session management and connection utilities using SQLAlchemy 2.0 patterns.
"""
from __future__ import annotations

from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator, Optional

from sqlalchemy import create_engine, text as sql_text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from sqlalchemy.pool import QueuePool, NullPool

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models with common functionality."""
    pass

# Synchronous engine and session factory
sync_engine = create_engine(
    str(settings.DATABASE_URL),
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    echo=settings.SQL_ECHO,
    echo_pool=settings.SQL_ECHO_POOL,
    hide_parameters=not settings.SQL_SHOW_PARAMETERS,
)

# Async engine and session factory
async_engine: Optional[AsyncEngine] = None
AsyncSessionLocal = None

if settings.ASYNC_DB_ENABLED:
    # Configure async engine
    async_engine = create_async_engine(
        settings.async_database_url,
        poolclass=NullPool if settings.ENVIRONMENT == "test" else None,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=settings.DB_POOL_TIMEOUT,
        pool_recycle=settings.DB_POOL_RECYCLE,
        pool_pre_ping=settings.DB_POOL_PRE_PING,
        echo=settings.SQL_ECHO,
        echo_pool=settings.SQL_ECHO_POOL,
        hide_parameters=not settings.SQL_SHOW_PARAMETERS,
    )
    
    # Create async session factory
    AsyncSessionLocal = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

# Create sync session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that yields database sessions for synchronous operations.
    
    Yields:
        Session: A synchronous database session
        
    Example:
        with get_db() as db:
            result = db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

@asynccontextmanager
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager that yields database sessions for async operations.
    
    Yields:
        AsyncSession: An asynchronous database session
        
    Example:
        async with get_async_db() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
    """
    if not async_engine or not AsyncSessionLocal:
        raise RuntimeError("Async database is not configured. Set ASYNC_DB_ENABLED=True in settings.")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Database error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

async def check_db_connection() -> bool:
    """
    Check if the database is accessible using SQLAlchemy 2.0 patterns.
    
    Returns:
        bool: True if the database is accessible, False otherwise
    """
    if not async_engine:
        logger.error("Async database engine not available")
        return False
        
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute(sql_text("SELECT 1"))
            return bool(await result.scalar() == 1)
    except Exception as e:
        logger.error(f"Database connection check failed: {e}", exc_info=True)
        return False

def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    This should be called during application startup.
    """
    from app.models import Base  # noqa: F401
    
    logger.info("Initializing database...")
    try:
        Base.metadata.create_all(bind=sync_engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

async def async_init_db() -> None:
    """
    Asynchronously initialize the database by creating all tables.
    
    This should be called during application startup.
    """
    from app.models import Base  # noqa: F401
    
    if not async_engine:
        raise RuntimeError("Async database is not configured. Set ASYNC_DB_ENABLED=True in settings.")
    
    logger.info("Initializing database asynchronously...")
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
