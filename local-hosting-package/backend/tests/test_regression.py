"""Regression tests - ensure existing functionality still works"""
import pytest
from httpx import AsyncClient


@pytest.mark.regression
@pytest.mark.asyncio
class TestBackwardCompatibility:
    """Test backward compatibility of APIs"""
    
    async def test_health_endpoint_still_works(self, test_client: AsyncClient):
        """Test health endpoint hasn't broken"""
        response = await test_client.get("/api/health")
        assert response.status_code == 200
        assert "status" in response.json()
    
    async def test_auth_endpoint_still_works(self, test_client: AsyncClient, admin_user):
        """Test auth endpoint hasn't broken"""
        response = await test_client.post(
            "/api/auth/login",
            json={"email": admin_user["email"], "password": "admin123"}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()


@pytest.mark.regression
@pytest.mark.asyncio
class TestExistingFeatures:
    """Test that existing features still work"""
    
    async def test_scope_filtering_still_works(self, test_client: AsyncClient, clean_db):
        """Test scope filtering hasn't regressed"""
        await clean_db.aadhaar_analytics.insert_one({
            "district_code": "2725",
            "district_name": "PUNE",
            "total_students": 100
        })
        
        response = await test_client.get("/api/aadhaar/overview?district_code=2725")
        assert response.status_code == 200
    
    async def test_name_based_filtering_still_works(self, test_client: AsyncClient, clean_db):
        """Test name-based filtering hasn't regressed"""
        await clean_db.aadhaar_analytics.insert_one({
            "district_code": "2725",
            "district_name": "PUNE",
            "total_students": 100
        })
        
        response = await test_client.get("/api/aadhaar/overview?district_name=PUNE")
        assert response.status_code == 200

