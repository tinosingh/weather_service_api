"""
Pydantic models for request/response validation.

This module contains all the Pydantic models used for request validation
and response serialization in the API.
"""
from __future__ import annotations

# Import base schemas
from .base import BaseSchema, ResponseModel, IDSchema, TimestampSchema, EmptyResponse, ErrorResponse, MessageResponse, DateTimeTZ

# Import and re-export location schemas
from .location import LocationBase, LocationCreate, LocationUpdate, LocationInDB, Location, LocationResponse

# Import and re-export weather schemas
from .weather_schema import (
    WeatherCondition,
    PrecipitationType,
    WindDirection,
    WeatherDataBase,
    WeatherDataCreate,
    WeatherDataUpdate,
    WeatherDataInDB,
    WeatherData,
    WeatherDataResponse,
    WeatherDataListResponse,
    AggregationPeriod,
    AggregatedWeatherData,
    AggregatedWeatherResponse,
)

# Import and re-export forecast schemas
from .forecast_schema import (
    ForecastInterval,
    ForecastModel,
    ForecastProvider,
    ForecastBase,
    ForecastCreate,
    ForecastUpdate,
    ForecastInDB,
    Forecast,
    ForecastResponse,
    ForecastListResponse,
    ForecastSummary,
    ForecastSummaryResponse,
)

# Import and re-export pagination schemas
from .pagination import PaginationParams, PaginatedResponse

# Define __all__ to explicitly export all public API
__all__ = [
    # Base schemas
    'BaseSchema',
    'ResponseModel',
    'IDSchema',
    'TimestampSchema',
    'EmptyResponse',
    'ErrorResponse',
    'MessageResponse',
    'DateTimeTZ',
    
    # Location schemas
    'LocationBase',
    'LocationCreate',
    'LocationUpdate',
    'LocationInDB',
    'Location',
    'LocationResponse',
    
    # Weather schemas
    'WeatherCondition',
    'PrecipitationType',
    'WindDirection',
    'WeatherDataBase',
    'WeatherDataCreate',
    'WeatherDataUpdate',
    'WeatherDataInDB',
    'WeatherData',
    'WeatherDataResponse',
    'WeatherDataListResponse',
    'AggregationPeriod',
    'AggregatedWeatherData',
    'AggregatedWeatherResponse',
    
    # Forecast schemas
    'ForecastInterval',
    'ForecastModel',
    'ForecastProvider',
    'ForecastBase',
    'ForecastCreate',
    'ForecastUpdate',
    'ForecastInDB',
    'Forecast',
    'ForecastResponse',
    'ForecastListResponse',
    'ForecastSummary',
    'ForecastSummaryResponse',
    
    # Pagination schemas
    'PaginationParams',
    'PaginatedResponse',
]
