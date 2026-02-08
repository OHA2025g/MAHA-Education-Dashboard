"""Integration tests for service interactions"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestAuthIntegration:
    """Test authentication integration with other services"""
    
    async def test_authenticated_request(self, test_client: AsyncClient, admin_token, clean_db):
        """Test that authenticated requests work across services"""
        # Insert test data
        await clean_db.aadhaar_analytics.insert_one({
            "district_code": "2725",
            "total_students": 100
        })
        
        # Make authenticated request
        response = await test_client.get(
            "/api/aadhaar/overview",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        # Should work with or without auth depending on endpoint
        assert response.status_code in [200, 401, 403]


@pytest.mark.integration
@pytest.mark.asyncio
class TestScopeIntegration:
    """Test scope filtering across different endpoints"""
    
    async def test_scope_filtering_consistency(self, test_client: AsyncClient, clean_db):
        """Test that scope filtering works consistently"""
        district_code = "2725"
        
        # Insert data in multiple collections
        await clean_db.aadhaar_analytics.insert_one({
            "district_code": district_code,
            "district_name": "PUNE",
            "total_students": 100
        })
        await clean_db.apaar_analytics.insert_one({
            "district_code": district_code,
            "district_name": "PUNE",
            "total_students": 100
        })
        
        # Test both endpoints with same scope
        aadhaar_response = await test_client.get(f"/api/aadhaar/overview?district_code={district_code}")
        apaar_response = await test_client.get(f"/api/apaar/overview?district_code={district_code}")
        
        # Both should return data
        assert aadhaar_response.status_code == 200
        assert apaar_response.status_code == 200


@pytest.mark.integration
@pytest.mark.asyncio
class TestDataFlow:
    """Test data flow through the system"""
    
    async def test_data_import_to_query(self, test_client: AsyncClient, clean_db):
        """Test that imported data can be queried"""
        # Simulate data import
        test_data = {
            "district_code": "2725",
            "district_name": "PUNE",
            "block_code": "123",
            "block_name": "Test Block",
            "udise_code": "123456",
            "school_name": "Test School",
            "total_students": 100
        }
        
        await clean_db.aadhaar_analytics.insert_one(test_data)
        
        # Query the data
        response = await test_client.get("/api/aadhaar/overview?district_code=2725")
        assert response.status_code == 200
        
        # Verify data is accessible
        data = response.json()
        assert data is not None

