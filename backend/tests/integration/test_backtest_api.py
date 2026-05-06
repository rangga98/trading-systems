"""Integration tests for Backtest API."""

import pytest
import uuid
from datetime import date
from decimal import Decimal
from httpx import AsyncClient, ASGITransport
from fastapi import status

from app.main import app
from app.database import get_db


class TestBacktestAPI:
    """Test suite for Backtest API endpoints."""

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
    async def stock_with_data(self, test_db_session):
        """Create stock with OHLCV data for backtesting."""
        from app.models.stock import Stock
        from app.models.ohlcv import OHLCVData

        stock_id = uuid.uuid4()
        stock = Stock(
            id=stock_id,
            ticker="BBCA.JK",
            name="Bank Central Asia",
        )
        test_db_session.add(stock)

        # Add OHLCV data
        for i in range(10):
            ohlcv = OHLCVData(
                stock_id=stock_id,
                date=date(2024, 1, 1 + i),
                open=Decimal("100.00") + i * Decimal("5.00"),
                high=Decimal("110.00") + i * Decimal("5.00"),
                low=Decimal("95.00") + i * Decimal("5.00"),
                close=Decimal("105.00") + i * Decimal("5.00"),
                adj_close=Decimal("105.00") + i * Decimal("5.00"),
                volume=1000000 + i * 100000,
            )
            test_db_session.add(ohlcv)

        await test_db_session.commit()
        return stock

    async def test_create_backtest_config(self, async_client):
        """Test creating a backtest configuration."""
        config_data = {
            "name": "Test Strategy",
            "ticker": "BBCA.JK",
            "initial_capital": "100000000.00",
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": "100000000.00",
            "stop_loss_pct": 5.0,
            "take_profit_pct": 10.0,
            "date_range_start": "2024-01-01",
            "date_range_end": "2024-01-31",
        }

        response = await async_client.post("/api/v1/backtests", json=config_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "Test Strategy"
        assert data["ticker"] == "BBCA.JK"
        assert data["initial_capital"] == "100000000.00"
        assert "id" in data

    async def test_list_backtest_configs(self, async_client):
        """Test listing backtest configurations."""
        # Create configs
        configs = [
            {
                "name": f"Strategy {i}",
                "ticker": "BBCA.JK",
                "initial_capital": "100000000.00",
                "position_sizing_type": "FIXED_AMOUNT",
                "position_size_value": "100000000.00",
                "date_range_start": "2024-01-01",
                "date_range_end": "2024-01-31",
            }
            for i in range(3)
        ]

        for config in configs:
            await async_client.post("/api/v1/backtests", json=config)

        response = await async_client.get("/api/v1/backtests")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    async def test_get_backtest_config(self, async_client):
        """Test getting a specific backtest configuration."""
        config_data = {
            "name": "My Strategy",
            "ticker": "BBRI.JK",
            "initial_capital": "50000000.00",
            "position_sizing_type": "FIXED_PCT",
            "position_size_value": "50.00",
            "date_range_start": "2024-01-01",
            "date_range_end": "2024-01-31",
        }

        create_response = await async_client.post("/api/v1/backtests", json=config_data)
        config_id = create_response.json()["id"]

        response = await async_client.get(f"/api/v1/backtests/{config_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "My Strategy"
        assert data["ticker"] == "BBRI.JK"

    async def test_update_backtest_config(self, async_client):
        """Test updating a backtest configuration."""
        config_data = {
            "name": "Original Name",
            "ticker": "TLKM.JK",
            "initial_capital": "100000000.00",
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": "100000000.00",
            "date_range_start": "2024-01-01",
            "date_range_end": "2024-01-31",
        }

        create_response = await async_client.post("/api/v1/backtests", json=config_data)
        config_id = create_response.json()["id"]

        update_data = {"name": "Updated Name"}
        response = await async_client.patch(f"/api/v1/backtests/{config_id}", json=update_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"

    async def test_delete_backtest_config(self, async_client):
        """Test deleting a backtest configuration."""
        config_data = {
            "name": "To Delete",
            "ticker": "ASII.JK",
            "initial_capital": "100000000.00",
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": "100000000.00",
            "date_range_start": "2024-01-01",
            "date_range_end": "2024-01-31",
        }

        create_response = await async_client.post("/api/v1/backtests", json=config_data)
        config_id = create_response.json()["id"]

        response = await async_client.delete(f"/api/v1/backtests/{config_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify deleted
        get_response = await async_client.get(f"/api/v1/backtests/{config_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_execute_backtest(self, async_client, stock_with_data):
        """Test executing a backtest."""
        config_data = {
            "name": "Buy and Hold Test",
            "ticker": "BBCA.JK",
            "initial_capital": "100000000.00",
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": "100000000.00",
            "stop_loss_pct": 5.0,
            "take_profit_pct": 10.0,
            "date_range_start": "2024-01-01",
            "date_range_end": "2024-01-10",
        }

        create_response = await async_client.post("/api/v1/backtests", json=config_data)
        config_id = create_response.json()["id"]

        response = await async_client.post(f"/api/v1/backtests/{config_id}/execute")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "COMPLETED"
        assert "result_id" in data

    async def test_get_backtest_result(self, async_client, stock_with_data):
        """Test getting backtest result with trades."""
        config_data = {
            "name": "Result Test",
            "ticker": "BBCA.JK",
            "initial_capital": "100000000.00",
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": "100000000.00",
            "date_range_start": "2024-01-01",
            "date_range_end": "2024-01-10",
        }

        create_response = await async_client.post("/api/v1/backtests", json=config_data)
        config_id = create_response.json()["id"]

        execute_response = await async_client.post(f"/api/v1/backtests/{config_id}/execute")
        result_id = execute_response.json()["result_id"]

        response = await async_client.get(f"/api/v1/backtests/results/{result_id}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "trades" in data
        assert "total_return_pct" in data
        assert "equity_curve" in data

    async def test_list_backtest_results(self, async_client, stock_with_data):
        """Test listing backtest results."""
        config_data = {
            "name": "List Results Test",
            "ticker": "BBCA.JK",
            "initial_capital": "100000000.00",
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": "100000000.00",
            "date_range_start": "2024-01-01",
            "date_range_end": "2024-01-10",
        }

        create_response = await async_client.post("/api/v1/backtests", json=config_data)
        config_id = create_response.json()["id"]

        # Execute multiple times
        for _ in range(3):
            await async_client.post(f"/api/v1/backtests/{config_id}/execute")

        response = await async_client.get("/api/v1/backtests/results")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 3

    async def test_backtest_invalid_config(self, async_client):
        """Test backtest with invalid configuration."""
        config_data = {
            "name": "Invalid",
            "ticker": "BBCA.JK",
            "initial_capital": "0.00",  # Invalid: zero capital
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": "100000000.00",
            "date_range_start": "2024-01-01",
            "date_range_end": "2024-01-31",
        }

        response = await async_client.post("/api/v1/backtests", json=config_data)

        # Should be rejected
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_backtest_stop_loss_greater_than_take_profit(self, async_client):
        """Test validation: stop_loss > take_profit."""
        config_data = {
            "name": "Invalid SL/TP",
            "ticker": "BBCA.JK",
            "initial_capital": "100000000.00",
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": "100000000.00",
            "stop_loss_pct": 15.0,
            "take_profit_pct": 5.0,  # SL > TP
            "date_range_start": "2024-01-01",
            "date_range_end": "2024-01-31",
        }

        response = await async_client.post("/api/v1/backtests", json=config_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_backtest_date_range_invalid(self, async_client):
        """Test validation: end_date before start_date."""
        config_data = {
            "name": "Invalid Dates",
            "ticker": "BBCA.JK",
            "initial_capital": "100000000.00",
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": "100000000.00",
            "date_range_start": "2024-01-31",
            "date_range_end": "2024-01-01",  # End before start
        }

        response = await async_client.post("/api/v1/backtests", json=config_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_backtest_nonexistent_stock(self, async_client):
        """Test backtest for non-existent stock."""
        config_data = {
            "name": "No Stock",
            "ticker": "NONEXISTENT.JK",
            "initial_capital": "100000000.00",
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": "100000000.00",
            "date_range_start": "2024-01-01",
            "date_range_end": "2024-01-31",
        }

        create_response = await async_client.post("/api/v1/backtests", json=config_data)
        config_id = create_response.json()["id"]

        response = await async_client.post(f"/api/v1/backtests/{config_id}/execute")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "FAILED"

    async def test_backtest_no_data_for_period(self, async_client, stock_with_data):
        """Test backtest with no data in date range."""
        config_data = {
            "name": "No Data",
            "ticker": "BBCA.JK",
            "initial_capital": "100000000.00",
            "position_sizing_type": "FIXED_AMOUNT",
            "position_size_value": "100000000.00",
            "date_range_start": "2025-01-01",  # Future date with no data
            "date_range_end": "2025-01-31",
        }

        create_response = await async_client.post("/api/v1/backtests", json=config_data)
        config_id = create_response.json()["id"]

        response = await async_client.post(f"/api/v1/backtests/{config_id}/execute")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "COMPLETED"
        # Should have empty trades
