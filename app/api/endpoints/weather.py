"""Weather API endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.weather import WeatherResponse
from app.schemas.forecast import ForecastListResponse
from app.services.database import DatabaseService
from app.services.prediction import PredictionService

router = APIRouter()

@router.get("/current/{location_id}", response_model=WeatherResponse)
async def get_current_weather(
    location_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get current weather for a location.
    
    Args:
        location_id: The location ID to get weather for
        
    Returns:
        Current weather data
    """
    db_service = DatabaseService(db)
    prediction_service = PredictionService(db_service)
    
    # Get the most recent weather data (simplified - in a real app, 
    # we'd have a separate current_weather table)
    weather = await db_service.get_latest_forecast(location_id)
    
    if not weather:
        raise HTTPException(
            status_code=404,
            detail=f"No weather data found for location {location_id}"
        )
        
    return WeatherResponse(data=weather)

@router.get("/forecast/{location_id}", response_model=ForecastListResponse)
async def get_weather_forecast(
    location_id: UUID,
    days: int = Query(7, ge=1, le=14, description="Number of days to forecast"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get weather forecast for a location.
    
    Args:
        location_id: The location ID to get forecast for
        days: Number of days to forecast (1-14)
        
    Returns:
        Weather forecast data
    """
    db_service = DatabaseService(db)
    prediction_service = PredictionService(db_service)
    
    # Fetch forecast from the prediction service
    forecasts = await prediction_service.fetch_forecast(
        location_id=location_id,
        days=days
    )
    
    return ForecastListResponse(
        data=forecasts,
        count=len(forecasts)
    )

@router.get("/forecast/{location_id}/summary")
async def get_forecast_summary(
    location_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a summary of the weather forecast for a location.
    
    Args:
        location_id: The location ID to get forecast summary for
        
    Returns:
        Weather forecast summary
    """
    db_service = DatabaseService(db)
    prediction_service = PredictionService(db_service)
    
    return await prediction_service.get_forecast_summary(location_id)
