"""Pytest fixtures and configuration."""

import pytest
from datetime import date
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.config import settings

# Use test database - replace the actual DB name in the URL
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/trading_sim", "/test_trading_sim")


def _get_default_db_url():
    """Get URL for the default postgres database to create test DB."""
    return TEST_DATABASE_URL.replace("/test_trading_sim", "/postgres")


async def _ensure_test_db_exists():
    """Create test database if it doesn't exist."""
    default_url = _get_default_db_url()
    engine = create_async_engine(default_url, echo=False, isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = 'test_trading_sim'")
            )
            if not result.fetchone():
                await conn.execute(text("CREATE DATABASE test_trading_sim"))
    finally:
        await engine.dispose()


@pytest.fixture
async def test_engine():
    """Create a test database engine."""
    await _ensure_test_db_exists()

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
