"""Simple weather data schemas for the weather service."""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Any, Dict
from uuid import UUID
from pydantic import Field, ConfigDict

from .base import BaseSchema, ResponseModel, IDSchema, TimestampSchema

class WeatherCondition(str, Enum):
    """Simplified weather conditions."""
    CLEAR = "clear"
    CLOUDS = "clouds"
    RAIN = "rain"
    SNOW = "snow"
    THUNDERSTORM = "thunderstorm"
    FOG = "fog"
    WIND = "wind"

class WeatherBase(BaseSchema):
    """Base weather data model."""
    timestamp: datetime
    location_id: UUID
    temperature: float = Field(..., ge=-50, le=60)
    condition: WeatherCondition
    humidity: float = Field(..., ge=0, le=100)
    pressure: float = Field(..., gt=800, lt=1100)
    wind_speed: float = Field(..., ge=0)
    wind_direction: int = Field(..., ge=0, le=360)  # degrees

class WeatherCreate(WeatherBase):
    """Schema for creating weather data."""
    pass

class WeatherUpdate(BaseSchema):
    """Schema for updating weather data."""
    temperature: Optional[float] = None
    condition: Optional[WeatherCondition] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[int] = None

class Weather(WeatherBase, IDSchema, TimestampSchema):
    """Full weather data model with ID and timestamps."""
    pass

class WeatherResponse(ResponseModel[Weather]):
    """Standard API response for a single weather reading."""
    pass

class WeatherListResponse(ResponseModel[List[Weather]]):
    """Standard API response for multiple weather readings."""
    count: int
