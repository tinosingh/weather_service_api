"""Test configuration and fixtures."""
import asyncio
from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import Base

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine and session factory
test_engine = create_async_engine(
    TEST_DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def setup_database():
    """Set up test database."""
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def apply_migrations():
    """Apply migrations at the beginning of each test."""
    # In a real app, you would run your migrations here
    # For testing with SQLite in-memory, we just create/drop tables
    pass

@pytest.fixture
async def db_session(
    setup_database,
    apply_migrations
) -> AsyncGenerator[AsyncSession, None]:
    """Create a clean database session for testing."""
    # Create a new connection with a transaction
    connection = await test_engine.connect()
    transaction = await connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    # Clean up
    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest.fixture
def db_service(db_session):
    """Create a database service with a test session."""
    from app.services.database import DatabaseService
    return DatabaseService(db_session)


@pytest.fixture
def prediction_service(db_service):
    """Create a prediction service with a test database service."""
    from app.services.prediction import PredictionService
    return PredictionService(db_service)
