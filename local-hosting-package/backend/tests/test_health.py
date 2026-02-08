"""Smoke/Sanity tests - Basic health and connectivity"""
import pytest
from httpx import AsyncClient


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_root_endpoint(test_client: AsyncClient):
    """Test root endpoint returns API info"""
    response = await test_client.get("/api/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_health_endpoint(test_client: AsyncClient):
    """Test health check endpoint"""
    response = await test_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

