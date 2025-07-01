"""
Weather forecast Pydantic models and schemas.
"""
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import Field, model_validator

from .base import BaseSchema, IDSchema, TimestampSchema, DateTimeTZ
from .weather_schema import WeatherCondition, WeatherDataBase

class ForecastInterval(str, Enum):
    """Time intervals for forecast data."""
    HOURLY = "hourly"
    DAILY = "daily"
    THREE_HOURLY = "3hourly"
    SIX_HOURLY = "6hourly"
    TWELVE_HOURLY = "12hourly"

class ForecastModel(str, Enum):
    """Weather forecast models."""
    GFS = "gfs"
    ECMWF = "ecmwf"
    UKMO = "ukmo"
    ICON = "icon"
    HIRLAM = "hirlam"
    HARMONIE = "harmonie"
    NAM = "nam"
    HRRR = "hrrr"
    NBM = "nbm"
    NDFD = "ndfd"
    FMI = "fmi"

class ForecastProvider(str, Enum):
    """Weather forecast data providers."""
    FMI = "fmi"
    OPENWEATHER = "openweather"
    WEATHERAPI = "weatherapi"
    WEATHERBIT = "weatherbit"
    VISUALCROSSING = "visualcrossing"
    CLIMACELL = "climacell"
    DARKSKY = "darksky"
    METEOBLUE = "meteoblue"
    WEATHERUNLOCKED = "weatherunlocked"

class ForecastBase(WeatherDataBase):
    """Base schema for weather forecast data."""
    forecast_timestamp: DateTimeTZ = Field(..., description="Timestamp when the forecast was generated")
    valid_from: DateTimeTZ = Field(..., description="Start of the forecast validity period")
    valid_to: DateTimeTZ = Field(..., description="End of the forecast validity period")
    interval: ForecastInterval = Field(..., description="Time interval for this forecast")
    model: ForecastModel = Field(..., description="Forecast model used")
    provider: ForecastProvider = Field(..., description="Data provider")
    confidence: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Confidence score of the forecast (0-1)"
    )
    
    @model_validator(mode='after')
    def validate_forecast_period(self) -> 'ForecastBase':
        """Validate that valid_to is after valid_from."""
        if self.valid_to <= self.valid_from:
            raise ValueError("valid_to must be after valid_from")
        return self

class ForecastCreate(ForecastBase):
    """Schema for creating a new forecast."""
    pass

class ForecastUpdate(BaseSchema):
    """Schema for updating an existing forecast."""
    temperature: Optional[float] = Field(
        None, 
        ge=-100, 
        le=100, 
        description="Forecasted temperature in degrees Celsius"
    )
    precipitation_amount: Optional[float] = Field(
        None, 
        ge=0, 
        description="Forecasted precipitation amount in millimeters"
    )
    precipitation_probability: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Probability of precipitation (0-1)"
    )
    wind_speed: Optional[float] = Field(
        None,
        ge=0,
        le=150,
        description="Forecasted wind speed in meters per second"
    )
    wind_gust: Optional[float] = Field(
        None,
        ge=0,
        le=200,
        description="Forecasted wind gust speed in meters per second"
    )
    wind_direction: Optional[float] = Field(
        None,
        ge=0,
        lt=360,
        description="Forecasted wind direction in degrees (0-359)"
    )
    cloud_cover: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="Forecasted cloud cover percentage (0-100)"
    )
    confidence: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Confidence score of the forecast (0-1)"
    )
    
    @model_validator(mode='after')
    def check_at_least_one_field_provided(self) -> 'ForecastUpdate':
        """Ensure at least one field is provided for update."""
        if not any([
            self.temperature is not None,
            self.precipitation_amount is not None,
            self.precipitation_probability is not None,
            self.wind_speed is not None,
            self.wind_gust is not None,
            self.wind_direction is not None,
            self.cloud_cover is not None,
            self.confidence is not None
        ]):
            raise ValueError('At least one field must be provided for update')
        return self

class ForecastInDB(ForecastBase, IDSchema, TimestampSchema):
    """Schema for forecast data in the database."""
    location_name: Optional[str] = Field(
        None,
        description="Name of the location (denormalized for query performance)"
    )
    
    class Config:
        from_attributes = True

class Forecast(ForecastInDB):
    """Schema for forecast data returned by the API."""
    pass

class ForecastResponse(BaseSchema):
    """Response model for a single forecast."""
    data: 'Forecast' = Field(..., description="Forecast data")

class ForecastListResponse(BaseSchema):
    """Response model for a list of forecasts."""
    data: List['Forecast'] = Field(..., description="List of forecast data points")
    location_id: UUID = Field(..., description="Location ID")
    model: ForecastModel = Field(..., description="Forecast model used")
    provider: ForecastProvider = Field(..., description="Data provider")
    interval: ForecastInterval = Field(..., description="Forecast interval")
    valid_from: DateTimeTZ = Field(..., description="Start of the forecast period")
    valid_to: DateTimeTZ = Field(..., description="End of the forecast period")
    count: int = Field(..., description="Number of forecast data points")

class ForecastSummary(BaseSchema):
    """Summary of forecast data for a time period."""
    valid_from: DateTimeTZ = Field(..., description="Start of the period")
    valid_to: DateTimeTZ = Field(..., description="End of the period")
    temperature_avg: Optional[float] = Field(None, description="Average temperature")
    temperature_min: Optional[float] = Field(None, description="Minimum temperature")
    temperature_max: Optional[float] = Field(None, description="Maximum temperature")
    precipitation_sum: Optional[float] = Field(None, description="Total precipitation")
    precipitation_probability_max: Optional[float] = Field(
        None,
        description="Maximum probability of precipitation"
    )
    wind_speed_avg: Optional[float] = Field(None, description="Average wind speed")
    wind_gust_max: Optional[float] = Field(None, description="Maximum wind gust")
    condition: Optional[WeatherCondition] = Field(None, description="Dominant weather condition")

class ForecastSummaryResponse(BaseSchema):
    """Response model for forecast summaries."""
    data: List[ForecastSummary] = Field(..., description="List of forecast summaries")
    location_id: UUID = Field(..., description="Location ID")
    model: ForecastModel = Field(..., description="Forecast model used")
    provider: ForecastProvider = Field(..., description="Data provider")
    interval: ForecastInterval = Field(..., description="Forecast interval")
    valid_from: DateTimeTZ = Field(..., description="Start of the forecast period")
    valid_to: DateTimeTZ = Field(..., description="End of the forecast period")
