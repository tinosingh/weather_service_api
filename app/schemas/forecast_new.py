"""Simple forecast data schemas for the weather service."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from .weather import WeatherCondition

class ForecastBase(BaseModel):
    """Base forecast data model."""
    timestamp: datetime
    location_id: UUID
    temperature: float = Field(..., ge=-50, le=60)
    condition: WeatherCondition
    humidity: float = Field(..., ge=0, le=100)
    precipitation_probability: float = Field(..., ge=0, le=1, alias="precipitationProbability")
    
    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }

class ForecastCreate(ForecastBase):
    """Schema for creating forecast data."""
    pass

class ForecastUpdate(BaseModel):
    """Schema for updating forecast data."""
    temperature: Optional[float] = None
    condition: Optional[WeatherCondition] = None
    humidity: Optional[float] = None
    precipitation_probability: Optional[float] = Field(None, alias="precipitationProbability")

class Forecast(ForecastBase):
    """Full forecast data model with ID and timestamps."""
    id: UUID
    created_at: datetime
    updated_at: datetime

class ForecastResponse(BaseModel):
    """Standard API response for a single forecast."""
    data: Forecast
    success: bool = True

class ForecastListResponse(BaseModel):
    """Standard API response for multiple forecasts."""
    data: List[Forecast]
    count: int
    success: bool = True
