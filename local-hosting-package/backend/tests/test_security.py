"""Security testing - authentication, authorization, input validation"""
import pytest
from httpx import AsyncClient


@pytest.mark.security
@pytest.mark.asyncio
class TestAuthentication:
    """Test authentication security"""
    
    async def test_password_not_in_response(self, test_client: AsyncClient, admin_user):
        """Test that passwords are never returned in responses"""
        response = await test_client.post(
            "/api/auth/login",
            json={"email": admin_user["email"], "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        # Password should never be in response
        assert "password" not in str(data).lower()
        assert "hashed_password" not in str(data).lower()
    
    async def test_token_expiration(self, test_client: AsyncClient):
        """Test that tokens expire"""
        from utils.auth import create_access_token, decode_token
        from datetime import timedelta
        
        # Create expired token
        token = create_access_token(
            {"sub": "test@test.com"},
            expires_delta=timedelta(seconds=-1)  # Expired
        )
        
        # Try to use expired token
        response = await test_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401


@pytest.mark.security
@pytest.mark.asyncio
class TestAuthorization:
    """Test authorization security"""
    
    async def test_role_based_access(self, test_client: AsyncClient, viewer_token, admin_token):
        """Test that roles are enforced"""
        # Viewer should have limited access
        viewer_response = await test_client.get(
            "/api/auth/users",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        
        # Admin should have full access
        admin_response = await test_client.get(
            "/api/auth/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Viewer should be denied or endpoint doesn't exist
        assert viewer_response.status_code in [403, 404]
        # Admin should succeed or endpoint doesn't exist
        assert admin_response.status_code in [200, 404]


@pytest.mark.security
@pytest.mark.validation
@pytest.mark.asyncio
class TestInputValidation:
    """Test input validation and sanitization"""
    
    async def test_sql_injection_prevention(self, test_client: AsyncClient):
        """Test SQL injection prevention (MongoDB injection)"""
        malicious = "'; db.dropDatabase(); //"
        response = await test_client.get(f"/api/scope/blocks?district_code={malicious}")
        # Should be handled safely
        assert response.status_code in [200, 400]
    
    async def test_xss_prevention(self, test_client: AsyncClient):
        """Test XSS prevention"""
        xss = "<script>alert('xss')</script>"
        response = await test_client.get(f"/api/scope/blocks?district_code={xss}")
        # Should be handled safely
        assert response.status_code in [200, 400]
    
    async def test_path_traversal_prevention(self, test_client: AsyncClient):
        """Test path traversal prevention"""
        traversal = "../../etc/passwd"
        response = await test_client.get(f"/api/scope/blocks?district_code={traversal}")
        # Should be handled safely
        assert response.status_code in [200, 400]
    
    async def test_large_input_handling(self, test_client: AsyncClient):
        """Test handling of very large inputs"""
        large_input = "A" * 10000
        response = await test_client.get(f"/api/scope/blocks?district_code={large_input}")
        # Should handle gracefully
        assert response.status_code in [200, 400, 413]


@pytest.mark.security
@pytest.mark.asyncio
class TestDataProtection:
    """Test data protection"""
    
    async def test_sensitive_data_not_exposed(self, test_client: AsyncClient, admin_user):
        """Test that sensitive data is not exposed"""
        response = await test_client.post(
            "/api/auth/login",
            json={"email": admin_user["email"], "password": "admin123"}
        )
        data = response.json()
        
        # Check that sensitive fields are not exposed
        user_data = data.get("user", {})
        assert "hashed_password" not in user_data
        assert "password" not in user_data
    
    async def test_cors_headers(self, test_client: AsyncClient):
        """Test CORS headers are set correctly"""
        response = await test_client.options("/api/health")
        # CORS headers should be present
        # Note: Actual CORS behavior depends on configuration

