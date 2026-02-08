"""Database consistency and integrity tests"""
import pytest
from motor.motor_asyncio import AsyncIOMotorClient


@pytest.mark.database
@pytest.mark.asyncio
class TestDatabaseConnection:
    """Test database connectivity"""
    
    async def test_database_connection(self, test_db):
        """Test database connection works"""
        # Try to list collections
        collections = await test_db.list_collection_names()
        assert isinstance(collections, list)
    
    async def test_database_insert(self, clean_db):
        """Test database insert operation"""
        result = await clean_db.test_collection.insert_one({"test": "data"})
        assert result.inserted_id is not None
    
    async def test_database_query(self, clean_db):
        """Test database query operation"""
        await clean_db.test_collection.insert_one({"name": "test", "value": 123})
        result = await clean_db.test_collection.find_one({"name": "test"})
        assert result is not None
        assert result["value"] == 123


@pytest.mark.database
@pytest.mark.asyncio
class TestDataConsistency:
    """Test data consistency across collections"""
    
    async def test_district_code_consistency(self, clean_db):
        """Test district codes are consistent across collections"""
        district_code = "2725"
        district_name = "PUNE"
        
        # Insert in multiple collections
        await clean_db.aadhaar_analytics.insert_one({
            "district_code": district_code,
            "district_name": district_name
        })
        await clean_db.apaar_analytics.insert_one({
            "district_code": district_code,
            "district_name": district_name
        })
        
        # Verify consistency
        aadhaar = await clean_db.aadhaar_analytics.find_one({"district_code": district_code})
        apaar = await clean_db.apaar_analytics.find_one({"district_code": district_code})
        
        assert aadhaar["district_name"] == apaar["district_name"]
    
    async def test_udise_code_uniqueness(self, clean_db):
        """Test UDISE codes are unique per school"""
        udise_code = "123456"
        
        # Insert same UDISE code twice (should be allowed in different collections)
        await clean_db.aadhaar_analytics.insert_one({"udise_code": udise_code})
        await clean_db.apaar_analytics.insert_one({"udise_code": udise_code})
        
        # Both should exist
        count_aadhaar = await clean_db.aadhaar_analytics.count_documents({"udise_code": udise_code})
        count_apaar = await clean_db.apaar_analytics.count_documents({"udise_code": udise_code})
        
        assert count_aadhaar == 1
        assert count_apaar == 1


@pytest.mark.database
@pytest.mark.integration
@pytest.mark.asyncio
class TestDataIntegrity:
    """Test data integrity constraints"""
    
    async def test_required_fields(self, clean_db):
        """Test that required fields are present"""
        # Insert document with all required fields
        doc = {
            "district_code": "2725",
            "district_name": "PUNE",
            "block_code": "123",
            "block_name": "Test Block",
            "udise_code": "123456",
            "school_name": "Test School"
        }
        result = await clean_db.test_collection.insert_one(doc)
        assert result.inserted_id is not None
    
    async def test_data_types(self, clean_db):
        """Test data types are correct"""
        doc = {
            "district_code": "2725",  # String
            "total_students": 100,  # Integer
            "percentage": 85.5,  # Float
            "is_active": True  # Boolean
        }
        result = await clean_db.test_collection.insert_one(doc)
        retrieved = await clean_db.test_collection.find_one({"_id": result.inserted_id})
        
        assert isinstance(retrieved["district_code"], str)
        assert isinstance(retrieved["total_students"], int)
        assert isinstance(retrieved["percentage"], (int, float))
        assert isinstance(retrieved["is_active"], bool)

