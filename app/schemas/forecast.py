"""Forecast data schemas for the weather service."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from app.schemas.weather import WeatherCondition

class ForecastBase(BaseModel):
    """Base forecast data model."""
    location_id: UUID
    forecast_time: datetime
    valid_from: datetime
    valid_to: datetime
    temperature_min: float = Field(..., ge=-50, le=60)
    temperature_max: float = Field(..., ge=-50, le=60)
    condition: WeatherCondition
    precipitation_probability: float = Field(..., ge=0, le=100)
    precipitation_amount: float = Field(..., ge=0)
    wind_speed: float = Field(..., ge=0)
    wind_direction: int = Field(..., ge=0, le=360)  # degrees
    
    class Config:
        from_attributes = True
        populate_by_name = True

class ForecastCreate(ForecastBase):
    """Schema for creating forecast data."""
    pass

class ForecastUpdate(BaseModel):
    """Schema for updating forecast data."""
    temperature_min: Optional[float] = None
    temperature_max: Optional[float] = None
    condition: Optional[WeatherCondition] = None
    precipitation_probability: Optional[float] = None
    precipitation_amount: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[int] = None

class Forecast(ForecastBase):
    """Full forecast data model with ID and timestamps."""
    id: UUID
    created_at: datetime
    updated_at: datetime

class ForecastResponse(BaseModel):
    """Standard API response for a single forecast."""
    data: 'Forecast'
    success: bool = True

class ForecastListResponse(BaseModel):
    """Standard API response for multiple forecasts."""
    data: List[Forecast]
    count: int
    success: bool = True