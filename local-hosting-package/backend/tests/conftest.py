"""Pytest configuration and fixtures"""
import pytest
import pytest_asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.testclient import TestClient
from httpx import AsyncClient
import asyncio
from typing import AsyncGenerator

# Test database configuration
TEST_DB_NAME = "test_maharashtra_edu"
# Use MONGO_URL from environment if available (for Docker), otherwise default to localhost
TEST_MONGO_URL = os.environ.get("TEST_MONGO_URL") or os.environ.get("MONGO_URL") or "mongodb://mongodb:27017"


# pytest-asyncio will handle event loop creation
# Remove custom event_loop fixture to use pytest-asyncio's default


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Create a test database connection"""
    # Get MongoDB URL at runtime, not at import time
    # In Docker, use the service name 'mongodb', otherwise use localhost
    mongo_url = os.environ.get("TEST_MONGO_URL") or os.environ.get("MONGO_URL") or "mongodb://mongodb:27017"
    print(f"DEBUG: Connecting to MongoDB at {mongo_url}")  # Debug output
    
    # Create client with server selection timeout
    client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
    
    # Test connection
    try:
        await client.admin.command('ping')
        print("DEBUG: MongoDB connection successful")
    except Exception as e:
        print(f"DEBUG: MongoDB connection failed: {e}")
        raise
    
    db = client[TEST_DB_NAME]
    try:
        yield db
    finally:
        # Cleanup: drop test database
        try:
            await client.drop_database(TEST_DB_NAME)
        except Exception:
            pass  # Ignore cleanup errors
        client.close()


@pytest_asyncio.fixture(scope="function")
async def clean_db(test_db):
    """Clean all collections before each test"""
    collections = await test_db.list_collection_names()
    for collection_name in collections:
        await test_db[collection_name].delete_many({})
    yield test_db


@pytest_asyncio.fixture(scope="function")
async def test_client(clean_db):
    """Create a test client with test database"""
    # Save original env vars
    original_mongo_url = os.environ.get("MONGO_URL")
    original_db_name = os.environ.get("DB_NAME")
    
    try:
        # Set environment variables for test BEFORE importing server
        # Get MongoDB URL at runtime, not at import time
        mongo_url = os.environ.get("TEST_MONGO_URL") or os.environ.get("MONGO_URL") or "mongodb://mongodb:27017"
        os.environ["MONGO_URL"] = mongo_url
        os.environ["DB_NAME"] = TEST_DB_NAME
        
        # Import and create app with test database
        from fastapi import FastAPI
        from pathlib import Path
        
        # Create a new app instance for testing
        test_app = FastAPI(title="Test API")
        
        # Import routers
        from routers.auth import router as auth_router, init_db as init_auth_db
        from routers.scope import router as scope_router, init_db as init_scope_db
        from routers.executive import router as executive_router, init_db as init_executive_db
        from routers.ctteacher import router as ctteacher_router, init_db as init_ctteacher_db
        from routers.classrooms_toilets import router as ct_router, init_db as init_ct_db
        from routers.apaar import router as apaar_router, init_db as init_apaar_db
        from routers.aadhaar import router as aadhaar_router, init_db as init_aadhaar_db
        from routers.enrolment import router as enrolment_router, init_db as init_enrolment_db
        from routers.teacher import router as teacher_router, init_db as init_teacher_db
        from routers.data_entry import router as data_entry_router, init_db as init_data_entry_db
        from routers.age_enrolment import router as age_enrolment_router, init_db as init_age_enrolment_db
        from routers.dropbox import router as dropbox_router, init_db as init_dropbox_db
        from routers.infrastructure import router as infrastructure_router, init_db as init_infrastructure_db
        from routers.analytics import router as analytics_router, init_db as init_analytics_db
        from routers.export import router as export_router, init_db as init_export_db
        
        # Initialize all routers with test database
        ROOT_DIR = Path(__file__).parent.parent
        UPLOADS_DIR = ROOT_DIR / "uploads"
        UPLOADS_DIR.mkdir(exist_ok=True)
        
        init_auth_db(clean_db)
        init_scope_db(clean_db)
        init_executive_db(clean_db)
        init_ctteacher_db(clean_db, UPLOADS_DIR)
        init_ct_db(clean_db, UPLOADS_DIR)
        init_apaar_db(clean_db, UPLOADS_DIR)
        init_aadhaar_db(clean_db, UPLOADS_DIR)
        init_enrolment_db(clean_db, UPLOADS_DIR)
        init_teacher_db(clean_db, UPLOADS_DIR)
        init_data_entry_db(clean_db, UPLOADS_DIR)
        init_age_enrolment_db(clean_db, UPLOADS_DIR)
        init_dropbox_db(clean_db, UPLOADS_DIR)
        init_infrastructure_db(clean_db, UPLOADS_DIR)
        init_analytics_db(clean_db)
        init_export_db(clean_db)
        
        # Register routers
        test_app.include_router(auth_router, prefix="/api")
        test_app.include_router(scope_router, prefix="/api")
        test_app.include_router(executive_router, prefix="/api")
        test_app.include_router(ctteacher_router, prefix="/api")
        test_app.include_router(ct_router, prefix="/api")
        test_app.include_router(apaar_router, prefix="/api")
        test_app.include_router(aadhaar_router, prefix="/api")
        test_app.include_router(enrolment_router, prefix="/api")
        test_app.include_router(teacher_router, prefix="/api")
        test_app.include_router(data_entry_router, prefix="/api")
        test_app.include_router(age_enrolment_router, prefix="/api")
        test_app.include_router(dropbox_router, prefix="/api")
        test_app.include_router(infrastructure_router, prefix="/api")
        test_app.include_router(analytics_router, prefix="/api")
        test_app.include_router(export_router, prefix="/api")
        
        # Add basic routes
        from fastapi import APIRouter
        api_router = APIRouter(prefix="/api")
        
        @api_router.get("/")
        async def root():
            return {"message": "Maharashtra Education Dashboard API", "version": "1.0.0"}
        
        @api_router.get("/health")
        async def health_check():
            from datetime import datetime, timezone
            return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
        
        test_app.include_router(api_router)
        
        # Create async client using ASGITransport
        from httpx import ASGITransport
        transport = ASGITransport(app=test_app)
        client = AsyncClient(transport=transport, base_url="http://test")
        yield client
        await client.aclose()
    finally:
        # Restore original env vars
        if original_mongo_url:
            os.environ["MONGO_URL"] = original_mongo_url
        if original_db_name:
            os.environ["DB_NAME"] = original_db_name


@pytest_asyncio.fixture
async def admin_user(clean_db):
    """Create an admin user for testing"""
    from utils.auth import get_password_hash
    from datetime import datetime, timezone
    import uuid
    
    user = {
        "id": str(uuid.uuid4()),
        "email": "admin@test.com",
        "full_name": "Test Admin",
        "hashed_password": get_password_hash("admin123"),
        "role": "admin",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    await clean_db.users.insert_one(user)
    return user


@pytest_asyncio.fixture
async def viewer_user(clean_db):
    """Create a viewer user for testing"""
    from utils.auth import get_password_hash
    from datetime import datetime, timezone
    import uuid
    
    user = {
        "id": str(uuid.uuid4()),
        "email": "viewer@test.com",
        "full_name": "Test Viewer",
        "hashed_password": get_password_hash("viewer123"),
        "role": "viewer",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    await clean_db.users.insert_one(user)
    return user


@pytest_asyncio.fixture
async def admin_token(test_client, admin_user):
    """Get admin authentication token"""
    response = await test_client.post(
        "/api/auth/login",
        json={"email": admin_user["email"], "password": "admin123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def viewer_token(test_client, viewer_user):
    """Get viewer authentication token"""
    response = await test_client.post(
        "/api/auth/login",
        json={"email": viewer_user["email"], "password": "viewer123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

