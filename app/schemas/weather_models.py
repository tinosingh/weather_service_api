"""
Weather data models and enums.
"""
from enum import Enum
from typing import Optional

from pydantic import Field

from .base import BaseSchema

class WeatherCondition(str, Enum):
    """Standardized weather conditions."""
    CLEAR = "clear"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    FOG = "fog"
    DRIZZLE = "drizzle"
    RAIN = "rain"
    SNOW = "snow"
    THUNDERSTORM = "thunderstorm"
    HAIL = "hail"
    SLEET = "sleet"
    WINDY = "windy"
    TORNADO = "tornado"
    HURRICANE = "hurricane"
    DUST = "dust"
    SMOKE = "smoke"
    HAZE = "haze"
    MIST = "mist"

class PrecipitationType(str, Enum):
    """Types of precipitation."""
    NONE = "none"
    RAIN = "rain"
    SNOW = "snow"
    SLEET = "sleet"
    HAIL = "hail"
    FREEZING_RAIN = "freezing_rain"
    DRIZZLE = "drizzle"

class WindDirection(str, Enum):
    """Cardinal wind directions."""
    N = "N"
    NNE = "NNE"
    NE = "NE"
    ENE = "ENE"
    E = "E"
    ESE = "ESE"
    SE = "SE"
    SSE = "SSE"
    S = "S"
    SSW = "SSW"
    SW = "SW"
    WSW = "WSW"
    W = "W"
    WNW = "WNW"
    NW = "NW"
    NNW = "NNW"

class WeatherDataBase(BaseSchema):
    """Base schema for weather data."""
    location_id: str = Field(..., description="ID of the location")
    timestamp: str = Field(..., description="Observation timestamp")
    temperature: Optional[float] = Field(
        None, 
        ge=-100, 
        le=100, 
        description="Temperature in degrees Celsius"
    )
    temperature_unit: str = Field("celsius", description="Temperature unit (celsius/fahrenheit)")
    humidity: Optional[float] = Field(
        None, 
        ge=0, 
        le=100, 
        description="Relative humidity in percentage (0-100)"
    )
    pressure: Optional[float] = Field(
        None, 
        ge=800, 
        le=1100, 
        description="Atmospheric pressure in hPa (hectopascals)"
    )
    wind_speed: Optional[float] = Field(
        None, 
        ge=0, 
        le=150, 
        description="Wind speed in meters per second"
    )
    wind_direction: Optional[float] = Field(
        None, 
        ge=0, 
        lt=360, 
        description="Wind direction in degrees (0-359)"
    )
    wind_gust: Optional[float] = Field(
        None, 
        ge=0, 
        le=200, 
        description="Wind gust speed in meters per second"
    )
    precipitation_amount: Optional[float] = Field(
        None, 
        ge=0, 
        description="Precipitation amount in millimeters"
    )
    precipitation_type: Optional[PrecipitationType] = Field(
        None, 
        description="Type of precipitation"
    )
    cloud_cover: Optional[int] = Field(
        None, 
        ge=0, 
        le=100, 
        description="Cloud cover percentage (0-100)"
    )
    visibility: Optional[float] = Field(
        None, 
        ge=0, 
        description="Visibility in meters"
    )
    weather_code: Optional[str] = Field(
        None,
        description="Weather condition code from the data provider"
    )
    weather_description: Optional[str] = Field(
        None,
        description="Human-readable weather description"
    )
    source: str = Field(
        "fmi",
        description="Data source identifier (e.g., 'fmi', 'openweathermap')"
    )
