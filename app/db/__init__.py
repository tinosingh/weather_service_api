"""
Database package for the weather application using SQLAlchemy 2.0 patterns.

This package contains database configuration and session management.
"""
from __future__ import annotations

from .session import (
    Base,
    SessionLocal,
    AsyncSessionLocal,
    get_db,
    get_async_db,
    init_db,
    async_init_db,
    check_db_connection,
    async_engine,
    sync_engine,
)

__all__ = [
    'Base',
    'SessionLocal',
    'get_db',
    'get_async_db',
    'check_db_connection',
    'init_db',
    'async_init_db',
    'engine',
    'sync_engine',
]
