"""
Forecast model for the weather application using SQLAlchemy 2.0 patterns.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

if TYPE_CHECKING:
    from app.schemas.forecast import ForecastCreate  # noqa: F401

class Forecast(Base):
    """SQLAlchemy model for weather forecasts with SQLAlchemy 2.0 patterns."""
    
    __tablename__ = "forecasts"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
        doc="Unique identifier for the forecast"
    )
    
    # Required fields
    location_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        index=True,
        doc="Reference to the location this forecast is for"
    )
    
    forecast_time: Mapped[datetime] = mapped_column(
        nullable=False,
        index=True,
        server_default=func.now(),
        doc="When this forecast was generated"
    )
    
    valid_from: Mapped[datetime] = mapped_column(
        nullable=False,
        index=True,
        doc="Start time for the forecast period"
    )
    
    valid_to: Mapped[datetime] = mapped_column(
        nullable=False,
        index=True,
        doc="End time for the forecast period"
    )
    
    temperature_min: Mapped[float] = mapped_column(
        nullable=False,
        doc="Minimum temperature in degrees Celsius"
    )
    
    temperature_max: Mapped[float] = mapped_column(
        nullable=False,
        doc="Maximum temperature in degrees Celsius"
    )
    
    condition: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Weather condition (e.g., 'sunny', 'rainy')"
    )
    
    precipitation_probability: Mapped[float] = mapped_column(
        nullable=False,
        doc="Probability of precipitation (0-1)"
    )
    
    precipitation_amount: Mapped[float] = mapped_column(
        nullable=False,
        doc="Expected precipitation amount in mm"
    )
    
    wind_speed: Mapped[float] = mapped_column(
        nullable=False,
        doc="Wind speed in m/s"
    )
    
    wind_direction: Mapped[int] = mapped_column(
        nullable=False,
        doc="Wind direction in degrees (0-360)"
    )
    
    # Optional fields
    source: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        doc="Data source (e.g., 'openweathermap', 'accuweather')"
    )
    
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Additional notes or metadata"
    )
    
    # Indexes
    __table_args__ = (
        # Composite index for common query patterns
        Index('idx_forecast_location_valid', 'location_id', 'valid_from', 'valid_to'),
        Index('idx_forecast_time_range', 'valid_from', 'valid_to'),
    )
    
    @classmethod
    def from_schema(cls, forecast_create: 'ForecastCreate') -> 'Forecast':
        """
        Create a Forecast instance from a Pydantic schema.
        
        Args:
            forecast_create: The Pydantic model containing forecast data
            
        Returns:
            A new Forecast instance
        """
        return cls(
            id=uuid4(),
            location_id=forecast_create.location_id,
            forecast_time=forecast_create.forecast_time or datetime.now(timezone.utc),
            valid_from=forecast_create.valid_from,
            valid_to=forecast_create.valid_to,
            temperature_min=forecast_create.temperature_min,
            temperature_max=forecast_create.temperature_max,
            condition=forecast_create.condition,
            precipitation_probability=forecast_create.precipitation_probability,
            precipitation_amount=forecast_create.precipitation_amount,
            wind_speed=forecast_create.wind_speed,
            wind_direction=forecast_create.wind_direction,
            source=getattr(forecast_create, 'source', None),
            notes=getattr(forecast_create, 'notes', None),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the forecast to a dictionary.
        
        Returns:
            Dictionary representation of the forecast
        """
        return {
            "id": str(self.id),
            "location_id": str(self.location_id),
            "forecast_time": self.forecast_time.isoformat(),
            "valid_from": self.valid_from.isoformat(),
            "valid_to": self.valid_to.isoformat(),
            "temperature_min": self.temperature_min,
            "temperature_max": self.temperature_max,
            "condition": self.condition,
            "precipitation_probability": self.precipitation_probability,
            "precipitation_amount": self.precipitation_amount,
            "wind_speed": self.wind_speed,
            "wind_direction": self.wind_direction,
            "source": self.source,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
