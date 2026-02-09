# Testing Links - Pune School Dashboard

## 🚀 Quick Access Links

Once the Docker services are running, access the application at:

### Main Application
- **Frontend Dashboard**: http://localhost
- **Backend API**: http://localhost:8002
- **API Documentation (Swagger)**: http://localhost:8002/docs
- **API Documentation (ReDoc)**: http://localhost:8002/redoc

### Health & Status
- **Backend Health Check**: http://localhost:8002/api/health
- **Frontend Health Check**: http://localhost/health
- **API Root**: http://localhost:8002/api/

### Test Endpoints

#### Authentication
- **Login**: POST http://localhost:8002/api/auth/login
- **Current User**: GET http://localhost:8002/api/auth/me
- **Users List** (Admin): GET http://localhost:8002/api/auth/users

#### Scope (District/Block/School)
- **Districts**: GET http://localhost:8002/api/scope/districts
- **Blocks**: GET http://localhost:8002/api/scope/districts/{district_code}/blocks
- **Schools**: GET http://localhost:8002/api/scope/blocks/{block_code}/schools

#### Executive Dashboard
- **Overview**: GET http://localhost:8002/api/executive/overview
- **Student Identity**: GET http://localhost:8002/api/executive/student-identity
- **Infrastructure**: GET http://localhost:8002/api/executive/infrastructure-facilities
- **Teacher Staffing**: GET http://localhost:8002/api/executive/teacher-staffing
- **Operational Performance**: GET http://localhost:8002/api/executive/operational-performance
- **School Health Index**: GET http://localhost:8002/api/executive/school-health-index
- **District Map Data**: GET http://localhost:8002/api/executive/district-map-data

#### CTTeacher Analytics
- **Overview**: GET http://localhost:8002/api/ctteacher/overview
- **Block-wise**: GET http://localhost:8002/api/ctteacher/block-wise
- **Gender Distribution**: GET http://localhost:8002/api/ctteacher/gender-distribution
- **Qualification**: GET http://localhost:8002/api/ctteacher/qualification
- **Age Distribution**: GET http://localhost:8002/api/ctteacher/age-distribution

#### Classrooms & Toilets
- **Overview**: GET http://localhost:8002/api/classrooms-toilets/overview
- **Block-wise**: GET http://localhost:8002/api/classrooms-toilets/block-wise
- **Classroom Condition**: GET http://localhost:8002/api/classrooms-toilets/classroom-condition
- **Toilet Distribution**: GET http://localhost:8002/api/classrooms-toilets/toilet-distribution
- **Hygiene Metrics**: GET http://localhost:8002/api/classrooms-toilets/hygiene-metrics

#### Other Dashboards
- **Aadhaar Overview**: GET http://localhost:8002/api/aadhaar/overview
- **APAAR Overview**: GET http://localhost:8002/api/apaar/overview
- **Enrolment Overview**: GET http://localhost:8002/api/enrolment/overview
- **Teacher Overview**: GET http://localhost:8002/api/teacher/overview
- **Infrastructure Overview**: GET http://localhost:8002/api/infrastructure/overview

## Default Credentials

```
Email: admin@mahaedume.gov.in
Password: admin123
```

## Testing with cURL

### Health Check
```bash
curl http://localhost:8002/api/health
```

### Get Districts
```bash
curl http://localhost:8002/api/scope/districts
```

### Login
```bash
curl -X POST http://localhost:8002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@mahaedume.gov.in","password":"admin123"}'
```

### Get Overview (with token)
```bash
# First get token from login, then:
curl http://localhost:8002/api/executive/overview \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Testing with Browser

1. Open http://localhost in your browser
2. Login with default credentials
3. Navigate through different dashboards
4. Test filters and data visualization

## Testing with Postman/Insomnia

1. Import the API collection from http://localhost:8002/docs
2. Set base URL: http://localhost:8002
3. Test all endpoints
4. Use authentication token for protected endpoints

## Service Status Check

```bash
# Check all services
docker compose ps

# Check specific service logs
docker compose logs backend
docker compose logs frontend
docker compose logs mongodb

# Check service health
curl http://localhost:8002/api/health
curl http://localhost/health
```

---

**Note**: Ensure Docker services are running before accessing these links.
Use `docker compose ps` to verify all services are up.

