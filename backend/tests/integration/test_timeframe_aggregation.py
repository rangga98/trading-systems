"""Integration tests for OHLCV timeframe aggregation."""

import pytest
import uuid
from datetime import date, timedelta
from decimal import Decimal
from httpx import AsyncClient, ASGITransport
from fastapi import status

from app.main import app
from app.database import get_db
from app.models.stock import Stock
from app.models.ohlcv import OHLCVData


class TestTimeframeAggregation:
    """Test suite for OHLCV timeframe aggregation."""

    @pytest.fixture
    async def async_client(self, test_db_session):
        """Create an async test client."""
        async def override_get_db():
            yield test_db_session

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client

        app.dependency_overrides.clear()

    @pytest.fixture
    async def stock_with_daily_data(self, test_db_session):
        """Create a stock with 30 days of daily OHLCV data."""
        stock_id = uuid.uuid4()
        stock = Stock(
            id=stock_id,
            ticker="BBCA.JK",
            name="Bank Central Asia",
        )
        test_db_session.add(stock)

        # Create 30 days of data (January 2024)
        base_price = Decimal("7500.00")
        for i in range(30):
            current_date = date(2024, 1, 1 + i)
            # Simulate price movement
            open_price = base_price + Decimal(str(i * 10))
            close_price = open_price + Decimal(str((i % 3 - 1) * 50))
            high_price = max(open_price, close_price) + Decimal("25.00")
            low_price = min(open_price, close_price) - Decimal("25.00")

            ohlcv = OHLCVData(
                stock_id=stock_id,
                date=current_date,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                adj_close=close_price,
                volume=10000000 + i * 100000,
            )
            test_db_session.add(ohlcv)

        await test_db_session.commit()
        return stock

    async def test_get_daily_timeframe(self, async_client, stock_with_daily_data):
        """Test retrieving daily timeframe data."""
        response = await async_client.get(
            "/api/v1/stocks/BBCA.JK/ohlcv?timeframe=daily&start_date=2024-01-01&end_date=2024-01-05"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["timeframe"] == "daily"
        assert data["count"] == 5
        # Verify daily data points
        assert data["data"][0]["date"] == "2024-01-01"
        assert data["data"][4]["date"] == "2024-01-05"

    async def test_get_weekly_timeframe(self, async_client, stock_with_daily_data):
        """Test retrieving weekly aggregated data."""
        response = await async_client.get(
            "/api/v1/stocks/BBCA.JK/ohlcv?timeframe=weekly&start_date=2024-01-01&end_date=2024-01-31"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["timeframe"] == "weekly"
        # January 2024 has ~5 weeks
        assert data["count"] >= 4

        # Verify weekly aggregation logic
        first_week = data["data"][0]
        assert "open" in first_week
        assert "high" in first_week
        assert "low" in first_week
        assert "close" in first_week
        assert "volume" in first_week

    async def test_get_monthly_timeframe(self, async_client, stock_with_daily_data):
        """Test retrieving monthly aggregated data."""
        response = await async_client.get(
            "/api/v1/stocks/BBCA.JK/ohlcv?timeframe=monthly&start_date=2024-01-01&end_date=2024-01-31"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["timeframe"] == "monthly"
        assert data["count"] == 1

        # Verify monthly aggregation
        jan_data = data["data"][0]
        assert jan_data["date"] == "2024-01-01" or "2024-01" in jan_data["date"]
        # Open should be first day of month's open
        # Close should be last day of month's close
        # High should be max of all highs
        # Low should be min of all lows

    async def test_weekly_aggregation_correctness(self, async_client, test_db_session):
        """Test that weekly aggregation calculations are correct."""
        # Create specific data to verify calculations
        stock_id = uuid.uuid4()
        stock = Stock(
            id=stock_id,
            ticker="BBRI.JK",
            name="Bank Rakyat Indonesia",
        )
        test_db_session.add(stock)

        # Week 1: Jan 1-7, 2024
        week1_data = [
            (date(2024, 1, 1), Decimal("100.00"), Decimal("110.00"), Decimal("95.00"), Decimal("105.00"), 1000000),
            (date(2024, 1, 2), Decimal("105.00"), Decimal("115.00"), Decimal("100.00"), Decimal("110.00"), 1200000),
            (date(2024, 1, 3), Decimal("110.00"), Decimal("120.00"), Decimal("105.00"), Decimal("115.00"), 1500000),
            (date(2024, 1, 4), Decimal("115.00"), Decimal("125.00"), Decimal("110.00"), Decimal("120.00"), 1100000),
            (date(2024, 1, 5), Decimal("120.00"), Decimal("130.00"), Decimal("115.00"), Decimal("125.00"), 1300000),
        ]

        for d, o, h, l, c, v in week1_data:
            ohlcv = OHLCVData(
                stock_id=stock_id,
                date=d,
                open=o,
                high=h,
                low=l,
                close=c,
                adj_close=c,
                volume=v,
            )
            test_db_session.add(ohlcv)

        await test_db_session.commit()

        response = await async_client.get(
            "/api/v1/stocks/BBRI.JK/ohlcv?timeframe=weekly&start_date=2024-01-01&end_date=2024-01-05"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 1

        week_data = data["data"][0]
        # Verify aggregation:
        # Open = first day's open = 100.00
        assert week_data["open"] == "100.00"
        # Close = last day's close = 125.00
        assert week_data["close"] == "125.00"
        # High = max of all highs = 130.00
        assert week_data["high"] == "130.00"
        # Low = min of all lows = 95.00
        assert week_data["low"] == "95.00"
        # Volume = sum of all volumes = 6100000
        assert week_data["volume"] == 6100000

    async def test_invalid_timeframe(self, async_client, stock_with_daily_data):
        """Test request with invalid timeframe."""
        response = await async_client.get(
            "/api/v1/stocks/BBCA.JK/ohlcv?timeframe=invalid"
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_pagination_large_dataset(self, async_client, test_db_session):
        """Test pagination for large datasets."""
        # Create stock with 2000 data points
        stock_id = uuid.uuid4()
        stock = Stock(
            id=stock_id,
            ticker="TLKM.JK",
            name="Telkom Indonesia",
        )
        test_db_session.add(stock)

        start_date = date(2020, 1, 1)
        for i in range(2000):
            current_date = start_date + timedelta(days=i)
            ohlcv = OHLCVData(
                stock_id=stock_id,
                date=current_date,
                open=Decimal("4000.00"),
                high=Decimal("4100.00"),
                low=Decimal("3900.00"),
                close=Decimal("4050.00"),
                adj_close=Decimal("4050.00"),
                volume=10000000,
            )
            test_db_session.add(ohlcv)

        await test_db_session.commit()

        # Request with limit
        response = await async_client.get(
            "/api/v1/stocks/TLKM.JK/ohlcv?limit=100"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 100
        assert len(data["data"]) == 100

    async def test_timeframe_with_date_range(self, async_client, stock_with_daily_data):
        """Test timeframe aggregation with date range filtering."""
        response = await async_client.get(
            "/api/v1/stocks/BBCA.JK/ohlcv?timeframe=weekly&start_date=2024-01-08&end_date=2024-01-14"
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["timeframe"] == "weekly"
        # Should return week 2 data (may include partial weeks)
        assert data["count"] >= 1
