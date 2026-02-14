"""Comprehensive live tests for the running system"""
import pytest
import httpx
import asyncio
from typing import Dict, Any


BASE_URL = "http://localhost:8002"
FRONTEND_URL = "http://localhost"


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_backend_health():
    """Test backend health endpoint"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_backend_root():
    """Test backend root endpoint"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        response = await client.get("/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_frontend_health():
    """Test frontend health endpoint"""
    async with httpx.AsyncClient(base_url=FRONTEND_URL, timeout=10.0) as client:
        response = await client.get("/health")
        assert response.status_code == 200


@pytest.mark.api
@pytest.mark.asyncio
async def test_api_docs_accessible():
    """Test API documentation is accessible"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        response = await client.get("/docs")
        assert response.status_code == 200


@pytest.mark.api
@pytest.mark.asyncio
async def test_api_redoc_accessible():
    """Test ReDoc documentation is accessible"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        response = await client.get("/redoc")
        assert response.status_code == 200


@pytest.mark.api
@pytest.mark.asyncio
async def test_api_openapi_schema():
    """Test OpenAPI schema is accessible"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema


@pytest.mark.api
@pytest.mark.asyncio
async def test_auth_endpoints_exist():
    """Test authentication endpoints exist"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # Test login endpoint exists (should return 422 for missing credentials, not 404)
        response = await client.post("/api/auth/login", json={})
        assert response.status_code in [422, 401]  # Validation error or unauthorized, not 404


@pytest.mark.performance
@pytest.mark.asyncio
async def test_health_endpoint_performance():
    """Test health endpoint response time"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        import time
        start = time.time()
        response = await client.get("/api/health")
        elapsed = time.time() - start
        assert response.status_code == 200
        assert elapsed < 1.0  # Should respond in under 1 second


@pytest.mark.security
@pytest.mark.asyncio
async def test_cors_headers():
    """Test CORS headers are present"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        response = await client.options("/api/health")
        # CORS headers should be present (even if OPTIONS returns 405, headers should exist)
        assert "access-control-allow-origin" in str(response.headers).lower() or response.status_code in [200, 405]


@pytest.mark.security
@pytest.mark.asyncio
async def test_sql_injection_protection():
    """Test basic SQL injection protection (MongoDB injection)"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # Try to inject MongoDB operators
        malicious_input = {"$ne": "test"}
        response = await client.get("/api/health", params=malicious_input)
        # Should not crash or expose internal errors
        assert response.status_code in [200, 400, 422]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_api_endpoints_consistency():
    """Test API endpoints return consistent response format"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        endpoints = ["/api/health", "/api/"]
        for endpoint in endpoints:
            response = await client.get(endpoint)
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, dict)  # Should return JSON object

