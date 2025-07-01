"""
Weather data Pydantic models and schemas.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from .base import BaseSchema, IDSchema, TimestampSchema, DateTimeTZ


# Enums for weather parameters
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
    location_id: UUID = Field(..., description="ID of the location")
    timestamp: DateTimeTZ = Field(..., description="Observation timestamp")
    temperature: Optional[float] = Field(
        None,
        ge=-100,
        le=100,
        description="Temperature in degrees Celsius"
    )
    temperature_unit: str = Field(
        "celsius",
        description="Temperature unit (celsius/fahrenheit)"
    )
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
    
    @field_validator('temperature_unit')
    def validate_temperature_unit(cls, v: str) -> str:
        """Validate temperature unit."""
        if v.lower() not in ["celsius", "fahrenheit"]:
            raise ValueError(
                "Temperature unit must be either 'celsius' or 'fahrenheit'"
            )
        return v.lower()

    @field_validator('wind_direction')
    def validate_wind_direction(cls, v: Optional[float]) -> Optional[float]:
        """Normalize wind direction to 0-359 degrees."""
        if v is None:
            return None
        return v % 360

    @model_validator(mode='before')
    def normalize_precipitation_type(cls, v: Any) -> Any:
        """Normalize precipitation type."""
        if (isinstance(v, dict) and
                'precipitation_type' in v and
                v['precipitation_type'] is not None):
            v['precipitation_type'] = v['precipitation_type'].lower()
        return v

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, handling special types."""
        result = self.model_dump()
        if ('precipitation_type' in result and
                result['precipitation_type'] is not None):
            result['precipitation_type'] = result['precipitation_type'].value
        return result

class WeatherDataCreate(WeatherDataBase):
    """Schema for creating new weather data."""
    pass

class WeatherDataUpdate(BaseSchema):
    """Schema for updating existing weather data."""
    temperature: Optional[float] = Field(
        None,
        ge=-100,
        le=100,
        description="Temperature in degrees Celsius"
    )
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
        description="Atmospheric pressure in hPa"
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
    source: Optional[str] = Field(
        None,
        description="Data source identifier"
    )
    
    @model_validator(mode='after')
    def check_at_least_one_field_provided(self) -> 'WeatherDataUpdate':
        """Ensure at least one field is provided for update."""
        if not any([
            self.temperature is not None,
            self.humidity is not None,
            self.pressure is not None,
            self.wind_speed is not None,
            self.wind_direction is not None,
            self.wind_gust is not None,
            self.precipitation_amount is not None,
            self.precipitation_type is not None,
            self.cloud_cover is not None,
            self.visibility is not None,
            self.weather_code is not None,
            self.weather_description is not None,
            self.source is not None
        ]):
            raise ValueError('At least one field must be provided for update')
        return self



class WeatherDataInDB(WeatherDataBase, IDSchema, TimestampSchema):
    """Schema for weather data in the database."""
    location_name: Optional[str] = Field(
        None,
        description="Name of the location (denormalized for query performance)"
    )
    
    class Config:
        from_attributes = True



class WeatherData(WeatherDataInDB):
    """Schema for weather data returned by the API."""
    pass



class WeatherDataResponse(BaseSchema):
    """Response model for a single weather data point."""
    data: 'WeatherData' = Field(..., description="Weather data")



class WeatherDataListResponse(BaseSchema):
    """Response model for a list of weather data points."""
    data: List['WeatherData'] = Field(
        ...,
        description="List of weather data points"
    )
    count: int = Field(
        ...,
        description="Total number of data points"
    )
    location_id: Optional[UUID] = Field(
        None,
        description="Location ID if filtered by location"
    )
    start_date: Optional[datetime] = Field(
        None,
        description="Start date of the data range"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="End date of the data range"
    )

# Aggregated weather data models


class AggregationPeriod(str, Enum):
    """Time periods for data aggregation."""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"

class AggregatedWeatherData(BaseSchema):
    """Schema for aggregated weather data."""
    period_start: datetime = Field(
        ...,
        description="Start of the aggregation period"
    )
    period_end: datetime = Field(
        ...,
        description="End of the aggregation period"
    )
    location_id: UUID = Field(
        ...,
        description="Location ID"
    )
    temperature_avg: Optional[float] = Field(
        None,
        description="Average temperature"
    )
    temperature_min: Optional[float] = Field(
        None,
        description="Minimum temperature"
    )
    temperature_max: Optional[float] = Field(
        None,
        description="Maximum temperature"
    )
    humidity_avg: Optional[float] = Field(
        None,
        description="Average humidity"
    )
    pressure_avg: Optional[float] = Field(
        None,
        description="Average pressure"
    )
    wind_speed_avg: Optional[float] = Field(
        None,
        description="Average wind speed"
    )
    wind_gust_max: Optional[float] = Field(
        None,
        description="Maximum wind gust"
    )
    precipitation_sum: Optional[float] = Field(
        None,
        description="Total precipitation"
    )
    sample_count: int = Field(
        ...,
        description="Number of samples in this aggregation"
    )

class AggregatedWeatherResponse(BaseSchema):
    """Response model for aggregated weather data."""
    data: List[AggregatedWeatherData] = Field(
        ...,
        description="Aggregated weather data"
    )
    location_id: UUID = Field(
        ...,
        description="Location ID"
    )
    period: AggregationPeriod = Field(
        ...,
        description="Aggregation period"
    )
    start_date: datetime = Field(
        ...,
        description="Start of the data range"
    )
    end_date: datetime = Field(
        ...,
        description="End of the data range"
    )
    sample_count: int = Field(
        ...,
        description="Total number of data points aggregated"
    )
