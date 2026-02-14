#!/usr/bin/env python3
"""
Script to create admin user in production database
Run this if login fails due to missing admin user
"""
import asyncio
import sys
import os
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auth import get_password_hash

# Get MongoDB connection from environment
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://mongo:b5a7adcac8107c867aa1@31.97.207.166:27017/?tls=false")
DB_NAME = os.environ.get("DB_NAME", "maharashtra_edu")

ADMIN_EMAIL = "admin@mahaedume.gov.in"
ADMIN_PASSWORD = "admin123"


async def create_admin_user():
    """Create admin user if it doesn't exist"""
    print("=" * 60)
    print("CREATE ADMIN USER")
    print("=" * 60)
    print(f"MongoDB: {MONGO_URL.split('@')[1] if '@' in MONGO_URL else MONGO_URL}")
    print(f"Database: {DB_NAME}")
    print(f"Admin Email: {ADMIN_EMAIL}")
    print("=" * 60)
    print()
    
    # Connect to MongoDB
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=10000)
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✓ MongoDB connection successful")
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        return 1
    
    db = client[DB_NAME]
    
    # Check if admin user exists
    print(f"\nChecking for existing admin user...")
    existing_admin = await db.users.find_one({"email": ADMIN_EMAIL})
    
    if existing_admin:
        print(f"✓ Admin user already exists: {ADMIN_EMAIL}")
        print(f"  User ID: {existing_admin.get('id')}")
        print(f"  Full Name: {existing_admin.get('full_name')}")
        print(f"  Role: {existing_admin.get('role')}")
        print(f"  Is Active: {existing_admin.get('is_active')}")
        
        # Check if password hash exists
        if existing_admin.get("hashed_password"):
            print(f"  Password: Hashed (exists)")
        else:
            print(f"  Password: Missing - will update")
            hashed_password = get_password_hash(ADMIN_PASSWORD)
            await db.users.update_one(
                {"email": ADMIN_EMAIL},
                {"$set": {"hashed_password": hashed_password, "updated_at": datetime.now(timezone.utc)}}
            )
            print(f"  ✓ Password hash updated")
        
        client.close()
        return 0
    
    # Create admin user
    print(f"\nCreating admin user...")
    admin_user = {
        "id": str(uuid.uuid4()),
        "email": ADMIN_EMAIL,
        "full_name": "System Administrator",
        "role": "admin",
        "is_active": True,
        "hashed_password": get_password_hash(ADMIN_PASSWORD),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    
    try:
        await db.users.insert_one(admin_user)
        print(f"✓ Admin user created successfully!")
        print(f"  Email: {ADMIN_EMAIL}")
        print(f"  Password: {ADMIN_PASSWORD}")
        print(f"  User ID: {admin_user['id']}")
        client.close()
        return 0
    except Exception as e:
        print(f"✗ Failed to create admin user: {e}")
        client.close()
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(create_admin_user())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Operation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

