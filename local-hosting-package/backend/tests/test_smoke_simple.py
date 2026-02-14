"""Simple smoke tests that test the actual running server"""
import pytest
import httpx


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_health_endpoint_live():
    """Test health check endpoint on running server"""
    async with httpx.AsyncClient(base_url="http://localhost:8002", timeout=10.0) as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_root_endpoint_live():
    """Test root endpoint on running server"""
    async with httpx.AsyncClient(base_url="http://localhost:8002", timeout=10.0) as client:
        response = await client.get("/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

