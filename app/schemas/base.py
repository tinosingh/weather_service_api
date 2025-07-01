"""
Base Pydantic models and shared utilities.
"""
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic_core import CoreSchema
from pydantic.json_schema import JsonSchemaValue

# Type variables for generic models
T = TypeVar('T')

class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
        }
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Convert model to dictionary with enhanced datetime handling."""
        return super().model_dump(
            by_alias=True,
            exclude_unset=True,
            exclude_none=True,
            **kwargs
        )

class IDSchema(BaseSchema):
    """Base schema with ID field."""
    id: UUID = Field(..., description="Unique identifier")

class TimestampSchema(BaseSchema):
    """Base schema with created_at and updated_at timestamps."""
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class ResponseModel(BaseSchema, Generic[T]):
    """Standard response model for API responses."""
    success: bool = Field(True, description="Indicates if the request was successful")
    data: Optional[T] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if success is False")
    
    @classmethod
    def success_response(cls, data: T) -> 'ResponseModel[T]':
        """Create a successful response with data."""
        return cls(success=True, data=data)
    
    @classmethod
    def error_response(cls, error: str, data: Optional[T] = None) -> 'ResponseModel[T]':
        """Create an error response with an error message."""
        return cls(success=False, error=error, data=data)

class EmptyResponse(ResponseModel[None]):
    """Response model for empty responses."""
    data: None = Field(None, description="No data")

class ErrorResponse(BaseSchema):
    """Standard error response model."""
    detail: Union[str, List[Dict[str, Any]]] = Field(..., description="Error details")
    status_code: int = Field(..., description="HTTP status code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Error message",
                "status_code": 400
            }
        }

class MessageResponse(BaseSchema):
    """Standard message response model."""
    message: str = Field(..., description="Response message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully"
            }
        }

class DateTimeTZ(datetime):
    """
    Custom datetime type that ensures timezone-aware datetimes.
    If no timezone is provided, UTC is assumed.
    """
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> CoreSchema:
        from pydantic_core import core_schema
        
        def validate(value: Any) -> datetime:
            if isinstance(value, str):
                # Parse string to datetime
                try:
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except (ValueError, AttributeError) as e:
                    raise ValueError("Invalid datetime format") from e
            elif isinstance(value, (int, float)):
                # Convert timestamp to datetime
                dt = datetime.fromtimestamp(value)
            elif isinstance(value, datetime):
                dt = value
            else:
                raise ValueError("Invalid datetime value")
            
            # Ensure timezone awareness
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.utcnow().astimezone().tzinfo)
            
            return dt
        
        return core_schema.no_info_plain_validator_function(
            function=validate,
            serialization=core_schema.format_ser_schema("date-time"),
        )
    
    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, _handler: Any
    ) -> JsonSchemaValue:
        return {"type": "string", "format": "date-time"}
