"""Performance and load testing"""
import pytest
import asyncio
from httpx import AsyncClient
from time import time


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.asyncio
class TestResponseTime:
    """Test API response times"""
    
    async def test_health_endpoint_performance(self, test_client: AsyncClient):
        """Test health endpoint responds quickly"""
        start = time()
        response = await test_client.get("/api/health")
        elapsed = time() - start
        
        assert response.status_code == 200
        assert elapsed < 1.0  # Should respond in under 1 second
    
    async def test_overview_endpoint_performance(self, test_client: AsyncClient, clean_db):
        """Test overview endpoint performance"""
        # Insert test data
        for i in range(100):
            await clean_db.aadhaar_analytics.insert_one({
                "district_code": "2725",
                "total_students": 100 + i
            })
        
        start = time()
        response = await test_client.get("/api/aadhaar/overview")
        elapsed = time() - start
        
        assert response.status_code == 200
        assert elapsed < 5.0  # Should respond in under 5 seconds


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.asyncio
class TestConcurrentRequests:
    """Test handling of concurrent requests"""
    
    async def test_concurrent_health_checks(self, test_client: AsyncClient):
        """Test multiple concurrent health checks"""
        async def make_request():
            return await test_client.get("/api/health")
        
        # Make 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
    
    async def test_concurrent_data_queries(self, test_client: AsyncClient, clean_db):
        """Test concurrent data queries"""
        # Insert test data
        await clean_db.aadhaar_analytics.insert_one({
            "district_code": "2725",
            "total_students": 100
        })
        
        async def make_request():
            return await test_client.get("/api/aadhaar/overview?district_code=2725")
        
        # Make 5 concurrent requests
        tasks = [make_request() for _ in range(5)]
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.asyncio
class TestLoadHandling:
    """Test system behavior under load"""
    
    async def test_large_dataset_query(self, test_client: AsyncClient, clean_db):
        """Test querying large dataset"""
        # Insert large amount of test data
        for i in range(1000):
            await clean_db.aadhaar_analytics.insert_one({
                "district_code": "2725",
                "total_students": 100 + i
            })
        
        start = time()
        response = await test_client.get("/api/aadhaar/overview?district_code=2725")
        elapsed = time() - start
        
        assert response.status_code == 200
        # Should handle large datasets reasonably
        assert elapsed < 10.0

