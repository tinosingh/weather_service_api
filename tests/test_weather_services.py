"""Tests for weather services."""
from datetime import datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.forecast import ForecastCreate
from app.services.database import DatabaseService
from app.services.prediction import PredictionService

# Test data
TEST_LOCATION_ID = uuid4()
NOW = datetime.utcnow()


def create_test_forecast(
    hours_ago: int = 0,
    temp: float = 20.0,
    condition: str = "clear",
    humidity: float = 50.0,
    precip_prob: float = 0.0
) -> ForecastCreate:
    """Helper to create a test forecast."""
    return ForecastCreate(
        timestamp=NOW - timedelta(hours=hours_ago),
        location_id=TEST_LOCATION_ID,
        temperature=temp,
        condition=condition,
        humidity=humidity,
        precipitation_probability=precip_prob
    )


@pytest.mark.asyncio
async def test_save_and_retrieve_forecast(db_session: AsyncSession):
    """Test saving and retrieving a forecast from the database."""
    # Setup
    db_service = DatabaseService(db_session)
    forecast = create_test_forecast()

    # Test save
    saved = await db_service.save_forecast(forecast)
    assert saved.id is not None
    assert saved.temperature == forecast.temperature

    # Test retrieve
    retrieved = await db_service.get_latest_forecast(TEST_LOCATION_ID)
    assert retrieved is not None
    assert retrieved.id == saved.id
    assert retrieved.temperature == forecast.temperature

@pytest.mark.asyncio
async def test_fetch_forecast(db_session: AsyncSession, mocker):
    """Test fetching forecast from the prediction service."""
    # Setup
    db_service = DatabaseService(db_session)
    prediction_service = PredictionService(db_service)
    
    # Mock the HTTP client
    mock_response = {
        "forecasts": [
            {
                "timestamp": (NOW + timedelta(hours=i)).isoformat(),
                "temperature": 20.0 + i,
                "condition": "clear",
                "humidity": 50.0,
                "precipitation_probability": 0.0
            }
            for i in range(24)  # 24 hours of forecast
        ]
    }
    
    # Patch the HTTP client
    mock_client = mocker.AsyncMock()
    mock_client.get.return_value.json.return_value = mock_response
    mock_client.get.return_value.raise_for_status.return_value = None
    
    with mocker.patch('httpx.AsyncClient', return_value=mock_client):
        # Test fetch
        forecasts = await prediction_service.fetch_forecast(TEST_LOCATION_ID)
        
        # Verify
        assert len(forecasts) == 24
        assert all(isinstance(f.temperature, float) for f in forecasts)
        assert all(f.location_id == TEST_LOCATION_ID for f in forecasts)
        
        # Verify the forecasts were saved to the database
        db_forecasts = await db_service.get_forecasts(TEST_LOCATION_ID)
        assert len(db_forecasts) == 24

@pytest.mark.asyncio
async def test_forecast_summary(db_session: AsyncSession):
    """Test generating a forecast summary."""
    # Setup
    db_service = DatabaseService(db_session)
    prediction_service = PredictionService(db_service)
    
    # Create test data - 3 days of hourly data
    for day in range(3):
        for hour in range(24):
            temp = 15.0 + day * 2  # Warmer each day
            forecast = create_test_forecast(
                hours_ago=(2 - day) * 24 + (23 - hour),  # Most recent first
                temp=temp,
                condition=["clear", "clouds", "rain"][(day + hour) % 3],
                humidity=50.0 + hour,
                precip_prob=0.0 if hour < 12 else 0.5
            )
            await db_service.save_forecast(forecast)
    
    # Test summary
    summary = await prediction_service.get_forecast_summary(TEST_LOCATION_ID)
    
    # Verify
    assert summary["location_id"] == TEST_LOCATION_ID
    assert len(summary["days"]) == 3
    
    # Check first day (most recent) has the highest temperature
    assert summary["days"][0]["max_temp"] > summary["days"][-1]["max_temp"]
    
    # Check we have 24 hourly entries for each day
    assert all(len(day["hourly"]) == 24 for day in summary["days"])
