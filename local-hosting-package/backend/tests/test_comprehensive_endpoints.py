"""Comprehensive API endpoint tests for all routers"""
import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.asyncio
class TestExecutiveEndpoints:
    """Test Executive Dashboard endpoints"""
    
    async def test_executive_overview(self, test_client: AsyncClient, clean_db):
        """Test executive overview"""
        response = await test_client.get("/api/executive/overview")
        assert response.status_code == 200
    
    async def test_student_identity(self, test_client: AsyncClient, clean_db):
        """Test student identity endpoint"""
        response = await test_client.get("/api/executive/student-identity")
        assert response.status_code == 200
    
    async def test_infrastructure_facilities(self, test_client: AsyncClient, clean_db):
        """Test infrastructure facilities endpoint"""
        response = await test_client.get("/api/executive/infrastructure-facilities")
        assert response.status_code == 200
    
    async def test_teacher_staffing(self, test_client: AsyncClient, clean_db):
        """Test teacher staffing endpoint"""
        response = await test_client.get("/api/executive/teacher-staffing")
        assert response.status_code == 200
    
    async def test_operational_performance(self, test_client: AsyncClient, clean_db):
        """Test operational performance endpoint"""
        response = await test_client.get("/api/executive/operational-performance")
        assert response.status_code == 200
    
    async def test_school_health_index(self, test_client: AsyncClient, clean_db):
        """Test school health index endpoint"""
        response = await test_client.get("/api/executive/school-health-index")
        assert response.status_code == 200
    
    async def test_district_map_data(self, test_client: AsyncClient, clean_db):
        """Test district map data endpoint"""
        response = await test_client.get("/api/executive/district-map-data")
        assert response.status_code == 200


@pytest.mark.api
@pytest.mark.asyncio
class TestCTTeacherEndpoints:
    """Test CTTeacher Analytics endpoints"""
    
    async def test_ctteacher_overview(self, test_client: AsyncClient, clean_db):
        """Test CTTeacher overview"""
        await clean_db.ctteacher_analytics.insert_one({
            "district_code": "2725",
            "teacher_code": "T001",
            "total_teachers": 1
        })
        response = await test_client.get("/api/ctteacher/overview")
        assert response.status_code == 200
    
    async def test_ctteacher_block_wise(self, test_client: AsyncClient, clean_db):
        """Test CTTeacher block-wise data"""
        await clean_db.ctteacher_analytics.insert_one({
            "district_code": "2725",
            "block_code": "123",
            "teacher_code": "T001"
        })
        response = await test_client.get("/api/ctteacher/block-wise")
        assert response.status_code == 200
    
    async def test_ctteacher_gender_distribution(self, test_client: AsyncClient, clean_db):
        """Test gender distribution"""
        await clean_db.ctteacher_analytics.insert_one({
            "district_code": "2725",
            "gender": "Male",
            "teacher_code": "T001"
        })
        response = await test_client.get("/api/ctteacher/gender-distribution")
        assert response.status_code == 200
    
    async def test_ctteacher_qualification(self, test_client: AsyncClient, clean_db):
        """Test qualification endpoint"""
        await clean_db.ctteacher_analytics.insert_one({
            "district_code": "2725",
            "teacher_code": "T001"
        })
        response = await test_client.get("/api/ctteacher/qualification")
        assert response.status_code == 200
    
    async def test_ctteacher_age_distribution(self, test_client: AsyncClient, clean_db):
        """Test age distribution"""
        await clean_db.ctteacher_analytics.insert_one({
            "district_code": "2725",
            "teacher_code": "T001",
            "age": 30
        })
        response = await test_client.get("/api/ctteacher/age-distribution")
        assert response.status_code == 200


@pytest.mark.api
@pytest.mark.asyncio
class TestClassroomsToiletsEndpoints:
    """Test Classrooms & Toilets endpoints"""
    
    async def test_classrooms_overview(self, test_client: AsyncClient, clean_db):
        """Test classrooms overview"""
        await clean_db.classrooms_toilets.insert_one({
            "district_code": "2725",
            "udise_code": "123456",
            "total_classrooms": 10,
            "good_classrooms": 8
        })
        response = await test_client.get("/api/classrooms-toilets/overview")
        assert response.status_code == 200
    
    async def test_classrooms_block_wise(self, test_client: AsyncClient, clean_db):
        """Test block-wise classrooms data"""
        await clean_db.classrooms_toilets.insert_one({
            "district_code": "2725",
            "block_code": "123",
            "total_classrooms": 10
        })
        response = await test_client.get("/api/classrooms-toilets/block-wise")
        assert response.status_code == 200
    
    async def test_classroom_condition(self, test_client: AsyncClient, clean_db):
        """Test classroom condition endpoint"""
        await clean_db.classrooms_toilets.insert_one({
            "district_code": "2725",
            "good_classrooms": 8,
            "minor_repair": 2
        })
        response = await test_client.get("/api/classrooms-toilets/classroom-condition")
        assert response.status_code == 200
    
    async def test_toilet_distribution(self, test_client: AsyncClient, clean_db):
        """Test toilet distribution"""
        await clean_db.classrooms_toilets.insert_one({
            "district_code": "2725",
            "functional_toilets": 5,
            "total_toilets": 6
        })
        response = await test_client.get("/api/classrooms-toilets/toilet-distribution")
        assert response.status_code == 200
    
    async def test_hygiene_metrics(self, test_client: AsyncClient, clean_db):
        """Test hygiene metrics"""
        await clean_db.classrooms_toilets.insert_one({
            "district_code": "2725",
            "handwash_available": "Yes"
        })
        response = await test_client.get("/api/classrooms-toilets/hygiene-metrics")
        assert response.status_code == 200


@pytest.mark.api
@pytest.mark.asyncio
class TestScopeFiltering:
    """Test scope filtering across endpoints"""
    
    async def test_scope_with_district_code(self, test_client: AsyncClient, clean_db):
        """Test filtering with district code"""
        await clean_db.aadhaar_analytics.insert_one({
            "district_code": "2725",
            "district_name": "PUNE",
            "total_students": 100
        })
        response = await test_client.get("/api/aadhaar/overview?district_code=2725")
        assert response.status_code == 200
    
    async def test_scope_with_district_name(self, test_client: AsyncClient, clean_db):
        """Test filtering with district name"""
        await clean_db.aadhaar_analytics.insert_one({
            "district_code": "2725",
            "district_name": "PUNE",
            "total_students": 100
        })
        response = await test_client.get("/api/aadhaar/overview?district_name=PUNE")
        assert response.status_code == 200
    
    async def test_scope_with_block_code(self, test_client: AsyncClient, clean_db):
        """Test filtering with block code"""
        await clean_db.aadhaar_analytics.insert_one({
            "district_code": "2725",
            "block_code": "123",
            "total_students": 100
        })
        response = await test_client.get("/api/aadhaar/overview?district_code=2725&block_code=123")
        assert response.status_code == 200
    
    async def test_scope_with_udise_code(self, test_client: AsyncClient, clean_db):
        """Test filtering with UDISE code"""
        await clean_db.aadhaar_analytics.insert_one({
            "district_code": "2725",
            "block_code": "123",
            "udise_code": "123456",
            "total_students": 100
        })
        response = await test_client.get("/api/aadhaar/overview?udise_code=123456")
        assert response.status_code == 200


@pytest.mark.api
@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling"""
    
    async def test_404_for_invalid_endpoint(self, test_client: AsyncClient):
        """Test 404 for invalid endpoint"""
        response = await test_client.get("/api/invalid-endpoint")
        assert response.status_code == 404
    
    async def test_422_for_invalid_data(self, test_client: AsyncClient):
        """Test 422 for invalid request data"""
        response = await test_client.post(
            "/api/auth/login",
            json={"invalid": "data"}
        )
        assert response.status_code == 422
    
    async def test_401_for_unauthorized(self, test_client: AsyncClient):
        """Test 401 for unauthorized access"""
        response = await test_client.get("/api/auth/me")
        assert response.status_code == 401

