"""Integration tests for OHLCV API."""

import pytest
import uuid
from datetime import date
from decimal import Decimal
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport
from fastapi import status

from app.main import app
from app.database import get_db
import pandas as pd
from app.models.stock import Stock
from app.models.ohlcv import OHLCVData


class TestOHLCVAPI:
    """Test suite for OHLCV API endpoints."""

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
    def mock_yfinance_data(self):
        """Mock yfinance data for testing."""
        return pd.DataFrame([
            {
                "date": date(2024, 1, 15),
                "open": 7500.00,
                "high": 7650.00,
                "low": 7480.00,
                "close": 7600.00,
                "adj_close": 7600.00,
                "volume": 15000000,
            },
            {
                "date": date(2024, 1, 16),
                "open": 7600.00,
                "high": 7700.00,
                "low": 7550.00,
                "close": 7650.00,
                "adj_close": 7650.00,
                "volume": 12000000,
            },
        ])

    async def test_import_ohlcv_data(self, async_client, test_db_session, mock_yfinance_data):
        """Test importing OHLCV data."""
        # Create stock first
        stock_id = uuid.uuid4()
        stock = Stock(
            id=stock_id,
            ticker="BBCA.JK",
            name="Bank Central Asia",
        )
        test_db_session.add(stock)
        await test_db_session.commit()
        
        # Mock yfinance client
        with patch("app.services.yfinance_client.YFinanceClient.fetch_ohlcv") as mock_fetch:
            mock_fetch.return_value = mock_yfinance_data
            
            import_data = {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "on_conflict": "skip",
            }
            
            response = await async_client.post(
                "/api/v1/stocks/BBCA.JK/ohlcv/import",
                json=import_data,
            )
            
            assert response.status_code == status.HTTP_202_ACCEPTED
            data = response.json()
            assert data["status"] == "completed"
            assert data["ticker"] == "BBCA.JK"
            assert data["records_imported"] == 2

    async def test_get_ohlcv_data(self, async_client, test_db_session):
        """Test retrieving OHLCV data."""
        # Create stock and OHLCV data
        stock_id = uuid.uuid4()
        stock = Stock(
            id=stock_id,
            ticker="BBRI.JK",
            name="Bank Rakyat Indonesia",
        )
        test_db_session.add(stock)
        
        for i in range(3):
            ohlcv = OHLCVData(
                stock_id=stock_id,
                date=date(2024, 1, 15 + i),
                open=Decimal("7500.00") + i * 100,
                high=Decimal("7650.00") + i * 100,
                low=Decimal("7480.00") + i * 100,
                close=Decimal("7600.00") + i * 100,
                adj_close=Decimal("7600.00") + i * 100,
                volume=10000000 + i * 1000000,
            )
            test_db_session.add(ohlcv)
        
        await test_db_session.commit()
        
        response = await async_client.get("/api/v1/stocks/BBRI.JK/ohlcv")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["ticker"] == "BBRI.JK"
        assert data["count"] == 3
        assert len(data["data"]) == 3
        assert data["data"][0]["open"] == "7500.00"

    async def test_get_ohlcv_with_date_range(self, async_client, test_db_session):
        """Test retrieving OHLCV data with date range filter."""
        # Create stock and OHLCV data
        stock_id = uuid.uuid4()
        stock = Stock(
            id=stock_id,
            ticker="TLKM.JK",
            name="Telkom Indonesia",
        )
        test_db_session.add(stock)
        
        for i in range(5):
            ohlcv = OHLCVData(
                stock_id=stock_id,
                date=date(2024, 1, 10 + i),
                open=Decimal("4000.00"),
                high=Decimal("4100.00"),
                low=Decimal("3900.00"),
                close=Decimal("4050.00"),
                adj_close=Decimal("4050.00"),
                volume=10000000,
            )
            test_db_session.add(ohlcv)
        
        await test_db_session.commit()
        
        response = await async_client.get(
            "/api/v1/stocks/TLKM.JK/ohlcv?start_date=2024-01-12&end_date=2024-01-13"
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 2
        assert data["data"][0]["date"] == "2024-01-12"
        assert data["data"][1]["date"] == "2024-01-13"

    async def test_get_ohlcv_stock_not_found(self, async_client):
        """Test retrieving OHLCV for non-existent stock."""
        response = await async_client.get("/api/v1/stocks/NONEXISTENT.JK/ohlcv")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_import_ohlcv_stock_not_found(self, async_client):
        """Test importing OHLCV for non-existent stock creates it automatically."""
        import_data = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
        }

        with patch("app.services.yfinance_client.YFinanceClient.fetch_ohlcv") as mock_fetch:
            mock_fetch.return_value = pd.DataFrame()
            with patch("app.services.yfinance_client.YFinanceClient.get_stock_info", return_value={
                "ticker": "NONEXISTENT.JK", "name": "Test Stock", "sector": None,
            }):
                response = await async_client.post(
                    "/api/v1/stocks/NONEXISTENT.JK/ohlcv/import",
                    json=import_data,
                )

        # Stock is auto-created, import succeeds
        assert response.status_code == status.HTTP_202_ACCEPTED

    async def test_import_ohlcv_invalid_date_range(self, async_client, test_db_session):
        """Test importing with invalid date range."""
        stock_id = uuid.uuid4()
        stock = Stock(
            id=stock_id,
            ticker="ASII.JK",
            name="Astra International",
        )
        test_db_session.add(stock)
        await test_db_session.commit()
        
        import_data = {
            "start_date": "2024-01-31",  # End before start
            "end_date": "2024-01-01",
        }
        
        response = await async_client.post(
            "/api/v1/stocks/ASII.JK/ohlcv/import",
            json=import_data,
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_import_ohlcv_overwrite_mode(self, async_client, test_db_session, mock_yfinance_data):
        """Test importing with overwrite conflict mode."""
        stock_id = uuid.uuid4()
        stock = Stock(
            id=stock_id,
            ticker="ICBP.JK",
            name="Indofood CBP",
        )
        test_db_session.add(stock)
        
        # Add existing data
        existing = OHLCVData(
            stock_id=stock_id,
            date=date(2024, 1, 15),
            open=Decimal("7000.00"),
            high=Decimal("7100.00"),
            low=Decimal("6900.00"),
            close=Decimal("7050.00"),
            adj_close=Decimal("7050.00"),
            volume=5000000,
        )
        test_db_session.add(existing)
        await test_db_session.commit()
        
        with patch("app.services.yfinance_client.YFinanceClient.fetch_ohlcv") as mock_fetch:
            mock_fetch.return_value = mock_yfinance_data
            
            import_data = {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "on_conflict": "overwrite",
            }
            
            response = await async_client.post(
                "/api/v1/stocks/ICBP.JK/ohlcv/import",
                json=import_data,
            )
            
            assert response.status_code == status.HTTP_202_ACCEPTED
            data = response.json()
            assert data["records_imported"] == 2

    async def test_get_ohlcv_empty_data(self, async_client, test_db_session):
        """Test retrieving OHLCV when no data exists."""
        stock_id = uuid.uuid4()
        stock = Stock(
            id=stock_id,
            ticker="PGAS.JK",
            name="Perusahaan Gas Negara",
        )
        test_db_session.add(stock)
        await test_db_session.commit()
        
        response = await async_client.get("/api/v1/stocks/PGAS.JK/ohlcv")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 0
        assert data["data"] == []

    async def test_get_import_job_status(self, async_client, test_db_session):
        """Test retrieving import job status."""
        from app.models.import_job import ImportJob
        from app.services.import_job_service import ImportJobService
        
        # Create an import job
        job_service = ImportJobService(test_db_session)
        job = await job_service.create("BBCA.JK", date(2024, 1, 1), date(2024, 1, 31))
        
        response = await async_client.get(f"/api/v1/import-jobs/{job.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(job.id)
        assert data["ticker"] == "BBCA.JK"
        assert data["status"] == "PENDING"

    async def test_get_import_job_not_found(self, async_client):
        """Test retrieving non-existent import job."""
        response = await async_client.get("/api/v1/import-jobs/00000000-0000-0000-0000-000000000000")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
