"""
Database models package for the weather application using SQLAlchemy 2.0 patterns.

This package contains all the SQLAlchemy models for the application.
"""
from __future__ import annotations

from .base import Base
from .forecast import Forecast

# Re-export models for easier imports
__all__ = [
    'Base',
    'Forecast',
]
