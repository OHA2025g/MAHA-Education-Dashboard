"""Functional/API tests for all endpoints"""
import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.asyncio
class TestScopeEndpoints:
    """Test scope-related endpoints"""
    
    async def test_get_districts(self, test_client: AsyncClient, clean_db):
        """Test getting districts list"""
        # Insert test data
        await clean_db.aadhaar_analytics.insert_one({
            "district_code": "2725",
            "district_name": "PUNE",
            "block_code": "123",
            "block_name": "Test Block"
        })
        
        response = await test_client.get("/api/scope/districts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_blocks(self, test_client: AsyncClient, clean_db):
        """Test getting blocks list"""
        await clean_db.aadhaar_analytics.insert_one({
            "district_code": "2725",
            "district_name": "PUNE",
            "block_code": "123",
            "block_name": "Test Block"
        })
        
        response = await test_client.get("/api/scope/blocks?district_code=2725")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_schools(self, test_client: AsyncClient, clean_db):
        """Test getting schools list"""
        await clean_db.aadhaar_analytics.insert_one({
            "district_code": "2725",
            "block_code": "123",
            "udise_code": "123456",
            "school_name": "Test School"
        })
        
        response = await test_client.get("/api/scope/schools?district_code=2725&block_code=123")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.api
@pytest.mark.asyncio
class TestAadhaarEndpoints:
    """Test Aadhaar analytics endpoints"""
    
    async def test_aadhaar_overview(self, test_client: AsyncClient, clean_db):
        """Test Aadhaar overview endpoint"""
        await clean_db.aadhaar_analytics.insert_one({
            "district_code": "2725",
            "total_students": 100,
            "aadhaar_verified": 80
        })
        
        response = await test_client.get("/api/aadhaar/overview")
        assert response.status_code == 200
        data = response.json()
        assert "total_students" in data or "total_schools" in data
    
    async def test_aadhaar_overview_with_scope(self, test_client: AsyncClient, clean_db):
        """Test Aadhaar overview with scope filter"""
        await clean_db.aadhaar_analytics.insert_one({
            "district_code": "2725",
            "district_name": "PUNE",
            "total_students": 100,
            "aadhaar_verified": 80
        })
        
        response = await test_client.get("/api/aadhaar/overview?district_code=2725")
        assert response.status_code == 200


@pytest.mark.api
@pytest.mark.asyncio
class TestAPAAREndpoints:
    """Test APAAR analytics endpoints"""
    
    async def test_apaar_overview(self, test_client: AsyncClient, clean_db):
        """Test APAAR overview endpoint"""
        await clean_db.apaar_analytics.insert_one({
            "district_code": "2725",
            "total_students": 100,
            "apaar_generated": 70
        })
        
        response = await test_client.get("/api/apaar/overview")
        assert response.status_code == 200


@pytest.mark.api
@pytest.mark.asyncio
class TestExecutiveEndpoints:
    """Test Executive dashboard endpoints"""
    
    async def test_executive_overview(self, test_client: AsyncClient, clean_db):
        """Test Executive overview endpoint"""
        response = await test_client.get("/api/executive/overview")
        assert response.status_code == 200


@pytest.mark.api
@pytest.mark.validation
@pytest.mark.asyncio
class TestInputValidation:
    """Test input validation and boundary cases"""
    
    async def test_invalid_district_code(self, test_client: AsyncClient):
        """Test with invalid district code"""
        response = await test_client.get("/api/scope/blocks?district_code=invalid")
        # Should handle gracefully (either 200 with empty list or 400)
        assert response.status_code in [200, 400]
    
    async def test_missing_required_params(self, test_client: AsyncClient):
        """Test endpoints with missing required parameters"""
        # Most endpoints should handle missing params gracefully
        response = await test_client.get("/api/scope/blocks")
        assert response.status_code in [200, 400]
    
    async def test_sql_injection_attempt(self, test_client: AsyncClient):
        """Test SQL injection prevention (MongoDB injection)"""
        malicious_input = "'; drop database --"
        response = await test_client.get(f"/api/scope/blocks?district_code={malicious_input}")
        # Should be handled safely
        assert response.status_code in [200, 400]
    
    async def test_xss_attempt(self, test_client: AsyncClient):
        """Test XSS prevention"""
        xss_input = "<script>alert('xss')</script>"
        response = await test_client.get(f"/api/scope/blocks?district_code={xss_input}")
        # Should be handled safely
        assert response.status_code in [200, 400]

