"""Pytest fixtures and configuration."""

import asyncio
import pytest
from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.config import settings

# Use test database
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/trading_simulator", "/test_trading_simulator")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_db_session(test_engine):
    """Create a test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        # Rollback after each test
        await session.rollback()


@pytest.fixture
def mock_yfinance_data():
    """Sample yfinance OHLCV data for testing."""
    return {
        "date": date(2024, 1, 15),
        "open": Decimal("7500.00"),
        "high": Decimal("7650.00"),
        "low": Decimal("7480.00"),
        "close": Decimal("7600.00"),
        "adj_close": Decimal("7600.00"),
        "volume": 15000000,
    }


@pytest.fixture
def mock_stock_info():
    """Sample stock info for testing."""
    return {
        "ticker": "BBCA.JK",
        "name": "Bank Central Asia Tbk",
        "sector": "Financial Services",
    }
