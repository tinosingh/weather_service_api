"""Weather prediction service for the weather application."""
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.schemas.forecast import Forecast, ForecastCreate
from app.services.database import DatabaseService

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for handling weather predictions."""

    def __init__(self, db_service: DatabaseService):
        """Initialize the prediction service."""
        self.db = db_service
        self.base_url = settings.FMI_API_BASE_URL
        self.api_key = settings.FMI_API_KEY

    async def fetch_forecast(
        self,
        location_id: UUID,
        days: int = 7,
        force_refresh: bool = False
    ) -> List[Forecast]:
        """
        Fetch weather forecast for a location.

        Args:
            location_id: The ID of the location to get forecast for
            days: Number of days to forecast (1-10)
            force_refresh: If True, ignore cached data and fetch fresh

        Returns:
            List of forecast data points
        """
        # First check if we have recent data in the database
        if not force_refresh:
            cached = await self._get_cached_forecast(location_id, hours=1)
            if cached:
                logger.info(
                    "Returning cached forecast for location %s",
                    location_id
                )
                return cached

        # If no cache or force_refresh, fetch from API
        logger.info("Fetching fresh forecast for location %s", location_id)
        try:
            async with httpx.AsyncClient() as client:
                # This is a simplified example - real implementation would use actual FMI API
                response = await client.get(
                    f"{self.base_url}/forecast",
                    params={
                        "location_id": str(location_id),
                        # Clamp between 1-10 days
                        "days": min(max(days, 1), 10),
                        "api_key": self.api_key
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                # Convert API response to our schema and save to database
                forecasts = []
                for item in data.get("forecasts", []):
                    forecast = ForecastCreate(
                        timestamp=datetime.fromisoformat(item["timestamp"]),
                        location_id=location_id,
                        temperature=item["temperature"],
                        condition=item["condition"],
                        humidity=item["humidity"],
                        precipitation_probability=item["precipitation_probability"]
                    )
                    # Save to database
                    db_forecast = await self.db.save_forecast(forecast)
                    forecasts.append(db_forecast)

                return forecasts

        except httpx.HTTPStatusError as e:
            logger.error("Error fetching forecast: %s", e)
            # Fall back to cached data if available
            cached = await self._get_cached_forecast(location_id, hours=24)
            if cached:
                logger.info("Falling back to cached forecast")
                return cached
            raise HTTPException(
                status_code=502,
                detail="Failed to fetch forecast from weather service"
            )

    async def _get_cached_forecast(
        self,
        location_id: UUID,
        hours: int = 24
    ) -> Optional[List[Forecast]]:
        """
        Get cached forecast data from the database.

        Args:
            location_id: The location ID to get cached data for
            hours: Maximum age of cached data in hours

        Returns:
            List of cached forecasts or None if no recent data
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cached = await self.db.get_forecasts(
            location_id=location_id,
            start_time=cutoff,
            limit=24  # Max 24 data points (hourly for a day)
        )

        return cached if cached else None

    async def get_forecast_summary(
        self,
        location_id: UUID
    ) -> dict:
        """
        Get a summary of the weather forecast for a location.

        Args:
            location_id: The location ID to get summary for

        Returns:
            Dictionary with forecast summary
        """
        forecasts = await self.fetch_forecast(location_id)

        if not forecasts:
            return {"message": "No forecast data available"}

        # Calculate daily summaries
        daily = {}
        for forecast in forecasts:
            date = forecast.timestamp.date()
            if date not in daily:
                daily[date] = {
                    "date": date,
                    "min_temp": forecast.temperature,
                    "max_temp": forecast.temperature,
                    "conditions": {forecast.condition},
                    "precipitation_chance": forecast.precipitation_probability,
                    "hourly": []
                }
            else:
                day = daily[date]
                day["min_temp"] = min(day["min_temp"], forecast.temperature)
                day["max_temp"] = max(day["max_temp"], forecast.temperature)
                day["conditions"].add(forecast.condition)
                day["precipitation_chance"] = max(
                    day["precipitation_chance"],
                    forecast.precipitation_probability
                )

            # Add to hourly data
            daily[date]["hourly"].append({
                "time": forecast.timestamp.time(),
                "temperature": forecast.temperature,
                "condition": forecast.condition,
                "precipitation_chance": forecast.precipitation_probability
            })

        # Convert sets to lists for JSON serialization
        for day in daily.values():
            day["conditions"] = list(day["conditions"])

        return {
            "location_id": location_id,
            "days": list(daily.values()),
            "current": {
                "temperature": forecasts[0].temperature,
                "condition": forecasts[0].condition,
                # Simplified for now
                "feels_like": forecasts[0].temperature,
                "humidity": forecasts[0].humidity,
                "precipitation_chance": forecasts[0].precipitation_probability
            }
        }
