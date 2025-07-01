"""
API v1 package initialization.

This module initializes the API v1 package and makes the router available.
"""

from .api import api_router

__all__ = ["api_router"]
