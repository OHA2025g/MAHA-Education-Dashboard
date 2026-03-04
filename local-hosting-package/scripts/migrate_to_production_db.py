#!/usr/bin/env python3
"""
Database Migration Script
Migrates data from local MongoDB to remote production MongoDB
"""
import asyncio
import sys
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Connection strings
LOCAL_MONGO_URL = os.environ.get("LOCAL_MONGO_URL", "mongodb://localhost:27017")
REMOTE_MONGO_URL = os.environ.get("REMOTE_MONGO_URL", "mongodb://mongo:b5a7adcac8107c867aa1@31.97.207.166:27017")
DB_NAME = os.environ.get("DB_NAME", "maharashtra_edu")

# Collections to migrate
COLLECTIONS_TO_MIGRATE = [
    "users",
    "districts",
    "blocks",
    "schools",
    "aadhaar_analytics",
    "apaar_analytics",
    "teacher_analytics",
    "infrastructure_analytics",
    "enrolment_analytics",
    "dropbox_analytics",
    "data_entry_analytics",
    "age_enrolment",
    "ctteacher_analytics",
    "classrooms_toilets",
    "districts_summary",
    "blocks_summary",
]


async def test_connection(client, url_name):
    """Test MongoDB connection"""
    try:
        await client.admin.command('ping')
        print(f"✓ {url_name} connection successful")
        return True
    except ServerSelectionTimeoutError as e:
        print(f"✗ {url_name} connection failed: {e}")
        return False
    except Exception as e:
        print(f"✗ {url_name} connection error: {e}")
        return False


async def get_collection_count(db, collection_name):
    """Get count of documents in collection"""
    try:
        count = await db[collection_name].count_documents({})
        return count
    except Exception:
        return 0


async def migrate_collection(source_db, target_db, collection_name, batch_size=1000):
    """Migrate a single collection"""
    print(f"\n📦 Migrating collection: {collection_name}")
    
    # Get source count
    source_count = await get_collection_count(source_db, collection_name)
    print(f"   Source documents: {source_count}")
    
    if source_count == 0:
        print(f"   ⚠️  Collection is empty, skipping...")
        return 0
    
    # Clear target collection
    target_count_before = await get_collection_count(target_db, collection_name)
    if target_count_before > 0:
        print(f"   ⚠️  Target has {target_count_before} documents, clearing...")
        await target_db[collection_name].delete_many({})
    
    # Migrate in batches
    migrated = 0
    cursor = source_db[collection_name].find({})
    
    batch = []
    async for doc in cursor:
        # Remove _id to let MongoDB generate new ones (or keep if you want to preserve)
        # doc.pop('_id', None)
        batch.append(doc)
        
        if len(batch) >= batch_size:
            await target_db[collection_name].insert_many(batch)
            migrated += len(batch)
            print(f"   ✓ Migrated {migrated}/{source_count} documents...", end='\r')
            batch = []
    
    # Insert remaining documents
    if batch:
        await target_db[collection_name].insert_many(batch)
        migrated += len(batch)
    
    # Verify
    target_count_after = await get_collection_count(target_db, collection_name)
    print(f"\n   ✓ Migration complete: {migrated} documents migrated")
    print(f"   ✓ Target now has: {target_count_after} documents")
    
    if target_count_after != source_count:
        print(f"   ⚠️  WARNING: Count mismatch! Source: {source_count}, Target: {target_count_after}")
    
    return migrated


async def main():
    """Main migration function"""
    print("=" * 60)
    print("DATABASE MIGRATION TOOL")
    print("=" * 60)
    print(f"Local MongoDB: {LOCAL_MONGO_URL}")
    print(f"Remote MongoDB: {REMOTE_MONGO_URL}")
    print(f"Database: {DB_NAME}")
    print(f"Started at: {datetime.now()}")
    print("=" * 60)
    
    # Connect to local MongoDB
    print("\n🔌 Connecting to local MongoDB...")
    local_client = AsyncIOMotorClient(LOCAL_MONGO_URL, serverSelectionTimeoutMS=5000)
    if not await test_connection(local_client, "Local"):
        print("\n❌ Cannot connect to local MongoDB. Exiting.")
        return 1
    local_db = local_client[DB_NAME]
    
    # Connect to remote MongoDB
    print("\n🔌 Connecting to remote MongoDB...")
    remote_client = AsyncIOMotorClient(REMOTE_MONGO_URL, serverSelectionTimeoutMS=10000)
    if not await test_connection(remote_client, "Remote"):
        print("\n❌ Cannot connect to remote MongoDB. Exiting.")
        local_client.close()
        return 1
    remote_db = remote_client[DB_NAME]
    
    # List available collections in source
    print("\n📋 Checking source collections...")
    local_collections = await local_db.list_collection_names()
    print(f"   Found {len(local_collections)} collections in source")
    
    # Filter collections that exist
    collections_to_migrate = [c for c in COLLECTIONS_TO_MIGRATE if c in local_collections]
    print(f"   Will migrate {len(collections_to_migrate)} collections")
    
    if not collections_to_migrate:
        print("\n⚠️  No collections to migrate!")
        local_client.close()
        remote_client.close()
        return 0
    
    # Ask for confirmation
    print("\n⚠️  WARNING: This will overwrite data in the remote database!")
    print(f"   Collections to migrate: {', '.join(collections_to_migrate)}")
    response = input("\n   Continue? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\n❌ Migration cancelled by user.")
        local_client.close()
        remote_client.close()
        return 0
    
    # Migrate each collection
    total_migrated = 0
    start_time = datetime.now()
    
    for collection_name in collections_to_migrate:
        try:
            migrated = await migrate_collection(local_db, remote_db, collection_name)
            total_migrated += migrated
        except Exception as e:
            print(f"\n   ✗ Error migrating {collection_name}: {e}")
            continue
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    print(f"Collections migrated: {len(collections_to_migrate)}")
    print(f"Total documents migrated: {total_migrated}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Completed at: {end_time}")
    print("=" * 60)
    
    # Close connections
    local_client.close()
    remote_client.close()
    
    print("\n✅ Migration completed successfully!")
    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Migration interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

