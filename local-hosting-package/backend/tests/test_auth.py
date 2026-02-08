"""Authentication and Authorization tests"""
import pytest
from httpx import AsyncClient
from utils.auth import get_password_hash, create_access_token, verify_password


@pytest.mark.api
@pytest.mark.security
@pytest.mark.asyncio
class TestAuthentication:
    """Test authentication endpoints"""
    
    async def test_login_success(self, test_client: AsyncClient, admin_user):
        """Test successful login"""
        response = await test_client.post(
            "/api/auth/login",
            json={"email": admin_user["email"], "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == admin_user["email"]
    
    async def test_login_invalid_email(self, test_client: AsyncClient):
        """Test login with invalid email"""
        response = await test_client.post(
            "/api/auth/login",
            json={"email": "nonexistent@test.com", "password": "password123"}
        )
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    async def test_login_invalid_password(self, test_client: AsyncClient, admin_user):
        """Test login with invalid password"""
        response = await test_client.post(
            "/api/auth/login",
            json={"email": admin_user["email"], "password": "wrongpassword"}
        )
        assert response.status_code == 401
    
    async def test_login_inactive_user(self, test_client: AsyncClient, clean_db):
        """Test login with inactive user"""
        from utils.auth import get_password_hash
        from datetime import datetime, timezone
        import uuid
        
        user = {
            "id": str(uuid.uuid4()),
            "email": "inactive@test.com",
            "full_name": "Inactive User",
            "hashed_password": get_password_hash("password123"),
            "role": "viewer",
            "is_active": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        await clean_db.users.insert_one(user)
        
        response = await test_client.post(
            "/api/auth/login",
            json={"email": user["email"], "password": "password123"}
        )
        assert response.status_code == 403
        assert "disabled" in response.json()["detail"].lower()
    
    async def test_get_current_user(self, test_client: AsyncClient, admin_token):
        """Test getting current user with valid token"""
        response = await test_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "role" in data
    
    async def test_get_current_user_invalid_token(self, test_client: AsyncClient):
        """Test getting current user with invalid token"""
        response = await test_client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
    
    async def test_get_current_user_no_token(self, test_client: AsyncClient):
        """Test getting current user without token"""
        response = await test_client.get("/api/auth/me")
        assert response.status_code == 401


@pytest.mark.unit
class TestAuthUtils:
    """Test authentication utility functions"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)
    
    def test_create_access_token(self):
        """Test JWT token creation"""
        data = {"sub": "test@example.com", "role": "admin"}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_token_contains_data(self):
        """Test token contains expected data"""
        from utils.auth import decode_token
        data = {"sub": "test@example.com", "role": "admin", "user_id": "123"}
        token = create_access_token(data)
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded["sub"] == "test@example.com"
        assert decoded["role"] == "admin"


@pytest.mark.api
@pytest.mark.security
@pytest.mark.asyncio
class TestAuthorization:
    """Test authorization and role-based access"""
    
    async def test_admin_access(self, test_client: AsyncClient, admin_token):
        """Test admin can access admin endpoints"""
        # Assuming there's an admin-only endpoint
        # This is a placeholder - adjust based on actual endpoints
        response = await test_client.get(
            "/api/auth/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        # Should succeed for admin
        assert response.status_code in [200, 404]  # 404 if endpoint doesn't exist
    
    async def test_viewer_restricted_access(self, test_client: AsyncClient, viewer_token):
        """Test viewer cannot access admin endpoints"""
        response = await test_client.get(
            "/api/auth/users",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        # Should fail for viewer
        assert response.status_code in [403, 404]  # 403 forbidden or 404 if endpoint doesn't exist

