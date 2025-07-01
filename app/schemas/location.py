"""
Location-related Pydantic models.
"""
from typing import Optional

from pydantic import Field, field_validator, model_validator

from .base import BaseSchema, IDSchema, TimestampSchema

class LocationBase(BaseSchema):
    """Base schema for location data."""
    name: str = Field(..., min_length=2, max_length=255, description="Location name")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    elevation: Optional[float] = Field(
        None, 
        ge=-1000, 
        le=10000, 
        description="Elevation in meters above sea level"
    )
    timezone: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="IANA timezone name (e.g., 'Europe/Helsinki')"
    )

    @field_validator('name')
    def name_must_contain_letters(cls, v: str) -> str:
        """Validate that name contains letters."""
        if not any(c.isalpha() for c in v):
            raise ValueError('Name must contain at least one letter')
        return v.strip()

    @field_validator('timezone')
    def validate_timezone(cls, v: Optional[str]) -> Optional[str]:
        """Validate timezone format."""
        if v is None:
            return v
            
        # Basic validation - in a real app, you might want to use pytz or zoneinfo
        if not v or len(v) < 2 or '/' not in v:
            raise ValueError('Invalid timezone format. Use format like "Continent/City"')
        return v

class LocationCreate(LocationBase):
    """Schema for creating a new location."""
    pass

class LocationUpdate(BaseSchema):
    """Schema for updating an existing location."""
    name: Optional[str] = Field(
        None, 
        min_length=2, 
        max_length=255, 
        description="Location name"
    )
    latitude: Optional[float] = Field(
        None, 
        ge=-90, 
        le=90, 
        description="Latitude in decimal degrees"
    )
    longitude: Optional[float] = Field(
        None, 
        ge=-180, 
        le=180, 
        description="Longitude in decimal degrees"
    )
    elevation: Optional[float] = Field(
        None, 
        ge=-1000, 
        le=10000, 
        description="Elevation in meters above sea level"
    )
    timezone: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="IANA timezone name (e.g., 'Europe/Helsinki')"
    )
    
    @model_validator(mode='after')
    def check_at_least_one_field_provided(self) -> 'LocationUpdate':
        """Ensure at least one field is provided for update."""
        if not any([
            self.name is not None,
            self.latitude is not None,
            self.longitude is not None,
            self.elevation is not None,
            self.timezone is not None
        ]):
            raise ValueError('At least one field must be provided for update')
        return self

class LocationInDB(LocationBase, IDSchema, TimestampSchema):
    """Schema for location data in the database."""
    pass

class Location(LocationInDB):
    """Schema for location data returned by the API."""
    pass

class LocationResponse(BaseSchema):
    """Response model for a single location."""
    data: Location = Field(..., description="Location data")

class LocationListResponse(BaseSchema):
    """Response model for a list of locations."""
    data: list[Location] = Field(..., description="List of locations")
    count: int = Field(..., description="Total number of locations")
