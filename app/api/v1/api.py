"""
API v1 router configuration.

This module defines the API router and includes all endpoint routers.
"""
from fastapi import APIRouter

# Import all endpoint routers
from app.api.endpoints import weather as weather_endpoints

# Create API router
api_router = APIRouter()

# Include routers
api_router.include_router(
    weather_endpoints.router,
    prefix="/weather",
    tags=["weather"]
)

# Add more routers here as needed
# api_router.include_router(
#     another_router,
#     prefix="/another",
#     tags=["another"]
# )
