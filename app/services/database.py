"""Database service for the weather application."""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.forecast import Forecast as ForecastModel
from app.schemas.forecast import Forecast, ForecastCreate


class DatabaseService:
    """Service for handling database operations."""

    def __init__(self, session: AsyncSession):
        """Initialize the database service."""
        self.session = session

    async def save_forecast(self, forecast: ForecastCreate) -> Forecast:
        """
        Save a new forecast to the database.

        Args:
            forecast: The forecast data to save.

        Returns:
            The saved forecast.
        """
        db_forecast = ForecastModel(**forecast.dict())
        self.session.add(db_forecast)
        await self.session.commit()
        await self.session.refresh(db_forecast)
        return Forecast.from_orm(db_forecast)

    async def get_forecast(self, forecast_id: UUID) -> Optional[Forecast]:
        """
        Retrieve a forecast by its ID.

        Args:
            forecast_id: The ID of the forecast to retrieve.

        Returns:
            The forecast if found, None otherwise.
        """
        result = await self.session.execute(
            select(ForecastModel).where(ForecastModel.id == forecast_id)
        )
        db_forecast = result.scalars().first()
        return Forecast.from_orm(db_forecast) if db_forecast else None

    async def list_forecasts(
        self,
        location_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Forecast]:
        """
        List forecasts with optional filtering.

        Args:
            location_id: Filter by location ID.
            start_date: Filter forecasts after this date.
            end_date: Filter forecasts before this date.
            limit: Maximum number of forecasts to return.
            offset: Number of forecasts to skip.

        Returns:
            A list of forecasts matching the criteria.
        """
        query = select(ForecastModel)

        if location_id:
            query = query.where(ForecastModel.location_id == location_id)

        if start_date:
            query = query.where(ForecastModel.timestamp >= start_date)

        if end_date:
            query = query.where(ForecastModel.timestamp <= end_date)

        query = query.order_by(ForecastModel.timestamp.desc())
        query = query.limit(limit).offset(offset)

        result = await self.session.execute(query)
        forecasts = result.scalars().all()
        return [Forecast.from_orm(f) for f in forecasts]

    async def update_forecast(
        self,
        forecast_id: UUID,
        forecast_update: ForecastCreate
    ) -> Optional[Forecast]:
        """
        Update an existing forecast.

        Args:
            forecast_id: The ID of the forecast to update.
            forecast_update: The updated forecast data.

        Returns:
            The updated forecast if found, None otherwise.
        """
        result = await self.session.execute(
            update(ForecastModel)
            .where(ForecastModel.id == forecast_id)
            .values(**forecast_update.dict(exclude_unset=True))
            .returning(ForecastModel)
        )
        db_forecast = result.scalars().first()
        if db_forecast:
            await self.session.commit()
            return Forecast.from_orm(db_forecast)
        return None

    async def delete_forecast(self, forecast_id: UUID) -> bool:
        """
        Delete a forecast by its ID.

        Args:
            forecast_id: The ID of the forecast to delete.

        Returns:
            True if the forecast was deleted, False otherwise.
        """
        result = await self.session.execute(
            delete(ForecastModel)
            .where(ForecastModel.id == forecast_id)
            .returning(ForecastModel.id)
        )
        if result.scalars().first():
            await self.session.commit()
            return True
        return False

    async def get_forecasts(
        self,
        location_id: UUID,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Forecast]:
        """
        Get forecasts for a location within a time range.

        Args:
            location_id: The location ID to get forecasts for
            start_time: Optional start time filter
            end_time: Optional end time filter
            limit: Maximum number of results to return

        Returns:
            List of matching forecasts
        """
        query = select(ForecastModel).where(
            ForecastModel.location_id == location_id
        )

        if start_time:
            query = query.where(ForecastModel.timestamp >= start_time)
        if end_time:
            query = query.where(ForecastModel.timestamp <= end_time)

        query = query.order_by(ForecastModel.timestamp.asc()).limit(limit)

        result = await self.session.execute(query)
        forecasts = result.scalars().all()

        return [Forecast.from_orm(f) for f in forecasts]

    async def delete_old_forecasts(self, cutoff: datetime) -> int:
        """
        Delete forecasts older than the specified cutoff.

        Args:
            cutoff: Delete forecasts older than this timestamp

        Returns:
            Number of forecasts deleted
        """
        result = await self.session.execute(
            delete(ForecastModel)
            .where(ForecastModel.timestamp < cutoff)
        )
        await self.session.commit()
        return result.rowcount

    async def get_latest_forecast(self, location_id: UUID) -> Optional[Forecast]:
        """
        Get the most recent forecast for a location.

        Args:
            location_id: The location ID

        Returns:
            The latest forecast or None if none found
        """
        query = (
            select(ForecastModel)
            .where(ForecastModel.location_id == location_id)
            .order_by(ForecastModel.timestamp.desc())
            .limit(1)
        )

        result = await self.session.execute(query)
        forecast = result.scalar_one_or_none()

        return Forecast.from_orm(forecast) if forecast else None
