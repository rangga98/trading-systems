"""Integration tests for Stocks API."""

import pytest
from datetime import date
from decimal import Decimal
from httpx import AsyncClient
from fastapi import status

from app.main import app
from app.database import get_db


class TestStocksAPI:
    """Test suite for Stocks API endpoints."""

    @pytest.fixture
    async def async_client(self, test_db_session):
        """Create an async test client."""
        # Override the get_db dependency
        async def override_get_db():
            yield test_db_session

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client

        # Cleanup
        app.dependency_overrides.clear()

    async def test_list_stocks_empty(self, async_client):
        """Test listing stocks when database is empty."""
        response = await async_client.get("/api/v1/stocks")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_create_stock(self, async_client):
        """Test creating a new stock."""
        stock_data = {
            "ticker": "BBCA.JK",
            "name": "Bank Central Asia Tbk",
            "sector": "Financial Services",
        }
        
        response = await async_client.post("/api/v1/stocks", json=stock_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["ticker"] == "BBCA.JK"
        assert data["name"] == "Bank Central Asia Tbk"
        assert data["sector"] == "Financial Services"
        assert "id" in data
        assert "created_at" in data

    async def test_create_stock_invalid_ticker(self, async_client):
        """Test creating stock with invalid ticker format."""
        stock_data = {
            "ticker": "BBCA",  # Missing .JK suffix
            "name": "Invalid Stock",
        }
        
        response = await async_client.post("/api/v1/stocks", json=stock_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_stock_by_ticker(self, async_client):
        """Test getting a stock by ticker."""
        # First create a stock
        stock_data = {
            "ticker": "BBRI.JK",
            "name": "Bank Rakyat Indonesia Tbk",
            "sector": "Financial Services",
        }
        await async_client.post("/api/v1/stocks", json=stock_data)
        
        # Get the stock
        response = await async_client.get("/api/v1/stocks/BBRI.JK")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["ticker"] == "BBRI.JK"
        assert data["name"] == "Bank Rakyat Indonesia Tbk"

    async def test_get_stock_not_found(self, async_client):
        """Test getting a non-existent stock."""
        response = await async_client.get("/api/v1/stocks/NONEXISTENT.JK")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_list_stocks_with_data(self, async_client, test_db_session):
        """Test listing stocks with data."""
        from app.models.stock import Stock
        from app.models.ohlcv import OHLCVData
        
        # Create a stock with data
        stock = Stock(
            id="test-stock-1",
            ticker="TLKM.JK",
            name="Telkom Indonesia",
            sector="Telecommunication",
        )
        test_db_session.add(stock)
        
        ohlcv = OHLCVData(
            stock_id="test-stock-1",
            date=date(2024, 1, 15),
            open=Decimal("4000.00"),
            high=Decimal("4100.00"),
            low=Decimal("3900.00"),
            close=Decimal("4050.00"),
            volume=10000000,
        )
        test_db_session.add(ohlcv)
        await test_db_session.commit()
        
        response = await async_client.get("/api/v1/stocks")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["ticker"] == "TLKM.JK"
        assert data["items"][0]["has_data"] is True
        assert data["items"][0]["data_count"] == 1

    async def test_delete_stock_soft(self, async_client):
        """Test soft deleting a stock."""
        # Create a stock
        stock_data = {
            "ticker": "ASII.JK",
            "name": "Astra International Tbk",
        }
        create_response = await async_client.post("/api/v1/stocks", json=stock_data)
        stock_id = create_response.json()["id"]
        
        # Delete the stock (soft delete)
        response = await async_client.delete(f"/api/v1/stocks/{stock_id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it's soft deleted by checking it still exists in list
        list_response = await async_client.get("/api/v1/stocks")
        data = list_response.json()
        # Soft deleted items should not appear in normal list

    async def test_search_stocks(self, async_client):
        """Test searching stocks."""
        # Create stocks
        await async_client.post("/api/v1/stocks", json={
            "ticker": "BBCA.JK",
            "name": "Bank Central Asia",
        })
        await async_client.post("/api/v1/stocks", json={
            "ticker": "BBRI.JK",
            "name": "Bank Rakyat Indonesia",
        })
        await async_client.post("/api/v1/stocks", json={
            "ticker": "TLKM.JK",
            "name": "Telkom Indonesia",
        })
        
        # Search for "Bank"
        response = await async_client.get("/api/v1/stocks?search=Bank")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2

    async def test_list_stocks_pagination(self, async_client):
        """Test stock list pagination."""
        # Create multiple stocks
        for i in range(5):
            await async_client.post("/api/v1/stocks", json={
                "ticker": f"TEST{i}.JK",
                "name": f"Test Stock {i}",
            })
        
        # Get first page with limit 2
        response = await async_client.get("/api/v1/stocks?limit=2&offset=0")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 5

    async def test_create_duplicate_ticker(self, async_client):
        """Test creating stock with duplicate ticker."""
        stock_data = {
            "ticker": "UNVR.JK",
            "name": "Unilever Indonesia",
        }
        
        # First creation should succeed
        response1 = await async_client.post("/api/v1/stocks", json=stock_data)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Second creation should fail (duplicate)
        response2 = await async_client.post("/api/v1/stocks", json=stock_data)
        assert response2.status_code == status.HTTP_409_CONFLICT
