""
Weather data models.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base

class WeatherStation(Base):
    """Weather station information."""
    
    __tablename__ = "weather_stations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    fmisid = Column(Integer, unique=True, index=True, nullable=False)  # FMI station ID
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Float, nullable=True)
    region = Column(String, nullable=True)
    country = Column(String, nullable=True, default="Finland")
    active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    
    # Relationships
    observations = relationship("WeatherObservation", back_populates="station")
    
    def __repr__(self) -> str:
        return f"<WeatherStation {self.name} ({self.fmisid})>"
    
    @classmethod
    def get_by_fmisid(cls, db, fmisid: int) -> Optional['WeatherStation']:
        """Get a station by its FMI ID."""
        return db.query(cls).filter(cls.fmisid == fmisid).first()


class WeatherObservation(Base):
    """Weather observation data."""
    
    __tablename__ = "weather_observations"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    station_id = Column(Integer, ForeignKey("weather_stations.id"), nullable=False, index=True)
    
    # Weather parameters
    temperature = Column(Float, nullable=True)  # Celsius
    humidity = Column(Float, nullable=True)     # %
    wind_speed = Column(Float, nullable=True)   # m/s
    wind_direction = Column(Float, nullable=True)  # degrees
    pressure = Column(Float, nullable=True)     # hPa
    precipitation = Column(Float, nullable=True)  # mm
    cloud_cover = Column(Float, nullable=True)   # %
    
    # Raw data from API
    raw_data = Column(JSONB, nullable=True)
    
    # Relationships
    station = relationship("WeatherStation", back_populates="observations")
    
    # Composite index on station_id and timestamp for faster time-based queries
    __table_args__ = (
        Index('idx_observation_station_time', 'station_id', 'timestamp'),
    )
    
    def __repr__(self) -> str:
        return f"<WeatherObservation {self.station_id} @ {self.timestamp}>"
    
    @classmethod
    def get_latest_observation(cls, db, station_id: int) -> Optional['WeatherObservation']:
        """Get the latest observation for a station."""
        return (
            db.query(cls)
            .filter(cls.station_id == station_id)
            .order_by(cls.timestamp.desc())
            .first()
        )
    
    @classmethod
    def get_observations_in_range(
        cls,
        db,
        station_id: int,
        start_time: datetime,
        end_time: datetime,
        parameters: Optional[List[str]] = None
    ) -> List['WeatherObservation']:
        """Get observations for a station within a time range."""
        query = (
            db.query(cls)
            .filter(
                cls.station_id == station_id,
                cls.timestamp >= start_time,
                cls.timestamp <= end_time
            )
            .order_by(cls.timestamp)
        )
        
        # Filter by requested parameters if specified
        if parameters:
            columns = [getattr(cls, param) for param in parameters if hasattr(cls, param)]
            query = query.with_entities(*columns)
            
        return query.all()


class WeatherForecast(Base):
    """Weather forecast data."""
    
    __tablename__ = "weather_forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(Integer, ForeignKey("weather_stations.id"), index=True)
    forecast_time = Column(DateTime, nullable=False, index=True)  # When the forecast was made
    valid_from = Column(DateTime, nullable=False, index=True)     # Start of forecast period
    valid_to = Column(DateTime, nullable=False, index=True)       # End of forecast period
    
    # Forecast parameters
    temperature_min = Column(Float, nullable=True)  # Celsius
    temperature_max = Column(Float, nullable=True)  # Celsius
    temperature_mean = Column(Float, nullable=True)  # Celsius
    precipitation = Column(Float, nullable=True)     # mm
    wind_speed = Column(Float, nullable=True)        # m/s
    wind_direction = Column(Float, nullable=True)    # degrees
    
    # Raw forecast data
    raw_data = Column(JSONB, nullable=True)
    
    # Relationships
    station = relationship("WeatherStation")
    
    def __repr__(self) -> str:
        return f"<WeatherForecast {self.station_id} {self.valid_from} to {self.valid_to}>"
    
    @classmethod
    def get_latest_forecast(
        cls,
        db,
        station_id: int,
        valid_from: datetime = None,
        valid_to: datetime = None
    ) -> List['WeatherForecast']:
        """Get the latest forecast for a station."""
        query = db.query(cls).filter(cls.station_id == station_id)
        
        if valid_from:
            query = query.filter(cls.valid_from >= valid_from)
        if valid_to:
            query = query.filter(cls.valid_to <= valid_to)
            
        return query.order_by(cls.forecast_time.desc(), cls.valid_from).all()
