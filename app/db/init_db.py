""
Database initialization and management utilities.

This module provides functions to initialize and manage the database schema
and initial data for the application.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.session import Base, SessionLocal, async_engine, sync_engine
from app.models import Forecast  # noqa: F401 - Import models to ensure they're registered

logger = logging.getLogger(__name__)

# Type variable for model classes
ModelType = TypeVar("ModelType", bound=Base)

def init_db() -> None:
    """
    Initialize the database by creating all tables and any initial data.
    
    This is a synchronous version that should be used in scripts and CLI commands.
    """
    logger.info("Initializing database...")
    
    # Create all tables
    Base.metadata.create_all(bind=sync_engine)
    
    logger.info("Database initialization complete")

async def init_async_db() -> None:
    """
    Initialize the database asynchronously by creating all tables and any initial data.
    
    This is the preferred version to use in async contexts like FastAPI startup events.
    """
    logger.info("Initializing database asynchronously...")
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Asynchronous database initialization complete")

def reset_db() -> None:
    """
    Drop all tables and recreate them.
    
    WARNING: This will delete all data in the database!
    """
    logger.warning("Resetting database - THIS WILL DELETE ALL DATA!")
    
    # Drop all tables
    Base.metadata.drop_all(bind=sync_engine)
    
    # Recreate all tables
    Base.metadata.create_all(bind=sync_engine)
    
    logger.info("Database reset complete")

async def reset_async_db() -> None:
    """
    Drop all tables and recreate them asynchronously.
    
    WARNING: This will delete all data in the database!
    """
    logger.warning("Resetting database asynchronously - THIS WILL DELETE ALL DATA!")
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Asynchronous database reset complete")

def check_db_connection() -> bool:
    """
    Check if the database is accessible.
    
    Returns:
        bool: True if the database is accessible, False otherwise
    """
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False

async def check_async_db_connection() -> bool:
    """
    Check if the database is accessible asynchronously.
    
    Returns:
        bool: True if the database is accessible, False otherwise
    """
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Asynchronous database connection check failed: {e}")
        return False

# Alias for backward compatibility
init_db_sync = init_db
init_db_async = init_async_db
reset_db_sync = reset_db
reset_db_async = reset_async_db
check_db_connection_sync = check_db_connection
check_db_connection_async = check_async_db_connection

__all__ = [
    "init_db",
    "init_async_db",
    "init_db_sync",
    "init_db_async",
    "reset_db",
    "reset_async_db",
    "reset_db_sync",
    "reset_db_async",
    "check_db_connection",
    "check_async_db_connection",
    "check_db_connection_sync",
    "check_db_connection_async",
]
