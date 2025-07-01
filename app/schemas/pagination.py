"""Simple pagination schemas for the weather service."""
from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Simple pagination parameters."""
    page: int = Field(1, ge=1, description="Page number (1-based)")
    page_size: int = Field(10, ge=1, le=100, alias="pageSize", description="Items per page (max 100)")

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: List[T]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")
    total_pages: int = Field(alias="totalPages")
