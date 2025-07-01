"""
Base SQLAlchemy model with common functionality using SQLAlchemy 2.0 patterns.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar

from sqlalchemy import DateTime, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
)

# Type variable for generic model types
T = TypeVar("T", bound="Base")

class Base(DeclarativeBase):
    """Base model class with common fields and methods."""
    
    # Type annotations for columns
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp of when the record was created"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Timestamp of when the record was last updated"
    )
    
    # Table configuration
    __mapper_args__ = {"eager_defaults": True}
    
    def to_dict(self, exclude: Optional[set[str]] = None) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.
        
        Args:
            exclude: Set of field names to exclude from the result
            
        Returns:
            Dictionary representation of the model
        """
        if exclude is None:
            exclude = set()
            
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns  # type: ignore
            if column.name not in exclude
        }
    
    def save(self, db: Session) -> Base:
        """
        Save the instance to the database synchronously.
        
        Args:
            db: SQLAlchemy session
            
        Returns:
            The saved instance
        """
        db.add(self)
        db.commit()
        db.refresh(self)
        return self
    
    async def async_save(self, db: AsyncSession) -> Base:
        """
        Save the instance to the database asynchronously.
        
        Args:
            db: Async SQLAlchemy session
            
        Returns:
            The saved instance
        """
        db.add(self)
        await db.commit()
        await db.refresh(self)
        return self
    
    def update(self, db: Session, **kwargs: Any) -> Base:
        """
        Update the instance with the given attributes.
        
        Args:
            db: SQLAlchemy session
            **kwargs: Attributes to update
            
        Returns:
            The updated instance
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self.save(db)
    
    async def async_update(self, db: AsyncSession, **kwargs: Any) -> Base:
        """
        Update the instance with the given attributes asynchronously.
        
        Args:
            db: Async SQLAlchemy session
            **kwargs: Attributes to update
            
        Returns:
            The updated instance
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return await self.async_save(db)
    
    def delete(self, db: Session) -> None:
        """
        Delete the instance from the database synchronously.
        
        Args:
            db: SQLAlchemy session
        """
        db.delete(self)
        db.commit()
    
    async def async_delete(self, db: AsyncSession) -> None:
        """
        Delete the instance from the database asynchronously.
        
        Args:
            db: Async SQLAlchemy session
        """
        await db.delete(self)
        await db.commit()
    
    @classmethod
    def get(cls: Type[T], db: Session, id: Any) -> Optional[T]:
        """
        Get a model instance by ID synchronously.
        
        Args:
            db: SQLAlchemy session
            id: The ID of the instance to retrieve
            
        Returns:
            The instance if found, None otherwise
        """
        stmt = select(cls).where(cls.id == id)
        return db.execute(stmt).scalar_one_or_none()
    
    @classmethod
    async def async_get(cls: Type[T], db: AsyncSession, id: Any) -> Optional[T]:
        """
        Get a model instance by ID asynchronously.
        
        Args:
            db: Async SQLAlchemy session
            id: The ID of the instance to retrieve
            
        Returns:
            The instance if found, None otherwise
        """
        stmt = select(cls).where(cls.id == id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @classmethod
    def get_all(
        cls: Type[T],
        db: Session,
        skip: int = 0,
        limit: int = 100,
        **filters: Any
    ) -> List[T]:
        """
        Get all instances of the model synchronously with optional filtering.
        
        Args:
            db: SQLAlchemy session
            skip: Number of records to skip
            limit: Maximum number of records to return
            **filters: Filter conditions as keyword arguments
            
        Returns:
            List of model instances
        """
        stmt = select(cls)
        
        # Apply filters
        for key, value in filters.items():
            if hasattr(cls, key):
                stmt = stmt.where(getattr(cls, key) == value)
                
        stmt = stmt.offset(skip).limit(limit)
        result = db.execute(stmt)
        return result.scalars().all()
    
    @classmethod
    async def async_get_all(
        cls: Type[T],
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        **filters: Any
    ) -> List[T]:
        """
        Get all instances of the model asynchronously with optional filtering.
        
        Args:
            db: Async SQLAlchemy session
            skip: Number of records to skip
            limit: Maximum number of records to return
            **filters: Filter conditions as keyword arguments
            
        Returns:
            List of model instances
        """
        stmt = select(cls)
        
        # Apply filters
        for key, value in filters.items():
            if hasattr(cls, key):
                stmt = stmt.where(getattr(cls, key) == value)
                
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @classmethod
    def count(cls, db: Session, **filters: Any) -> int:
        """
        Count the number of records matching the given filters.
        
        Args:
            db: SQLAlchemy session
            **filters: Filter conditions as keyword arguments
            
        Returns:
            Number of matching records
        """
        stmt = select(func.count()).select_from(cls)
        
        # Apply filters
        for key, value in filters.items():
            if hasattr(cls, key):
                stmt = stmt.where(getattr(cls, key) == value)
                
        return db.execute(stmt).scalar_one()
    
    @classmethod
    async def async_count(cls, db: AsyncSession, **filters: Any) -> int:
        """
        Asynchronously count the number of records matching the given filters.
        
        Args:
            db: Async SQLAlchemy session
            **filters: Filter conditions as keyword arguments
            
        Returns:
            Number of matching records
        """
        stmt = select(func.count()).select_from(cls)
        
        # Apply filters
        for key, value in filters.items():
            if hasattr(cls, key):
                stmt = stmt.where(getattr(cls, key) == value)
                
        result = await db.execute(stmt)
        return result.scalar_one()
    
    def __repr__(self) -> str:
        """Return a string representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
