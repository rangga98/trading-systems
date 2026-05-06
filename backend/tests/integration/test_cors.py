import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from fastapi import status

from app.database import get_db

class TestCORS:
    @pytest.fixture
    async def async_client(self, test_db_session):
        # Override the get_db dependency
        async def override_get_db():
            yield test_db_session

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client
        
        app.dependency_overrides.clear()

    async def test_cors_preflight(self, async_client):
        """Test CORS preflight request."""
        headers = {
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        }
        response = await async_client.options("/api/v1/stocks", headers=headers)
        
        # This is expected to fail or not return expected headers if CORS is misconfigured
        assert response.status_code == status.HTTP_200_OK
        assert response.headers.get("access-control-allow-origin") == "*"
        assert "GET" in response.headers.get("access-control-allow-methods", "")

    async def test_cors_simple_request(self, async_client):
        """Test CORS simple request."""
        headers = {
            "Origin": "http://localhost:5173",
        }
        response = await async_client.get("/api/v1/stocks", headers=headers)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers.get("access-control-allow-origin") == "*"
