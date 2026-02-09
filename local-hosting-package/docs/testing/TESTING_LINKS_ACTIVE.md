# 🚀 Active Testing Links - Pune School Dashboard

## ✅ Services Status

**Backend API**: ✅ RUNNING  
**Frontend**: ⏳ Starting (may take 30-60 seconds)  
**MongoDB**: ✅ Running (based on backend health check)

---

## 🌐 Testing Links

### Main Application Links

#### Frontend Dashboard
- **URL**: http://localhost:3000
- **Status**: Starting (React development server)
- **Note**: May take 30-60 seconds to compile

#### Backend API
- **URL**: http://localhost:8002
- **Status**: ✅ RUNNING
- **Health Check**: http://localhost:8002/api/health ✅

#### API Documentation
- **Swagger UI**: http://localhost:8002/docs
- **ReDoc**: http://localhost:8002/redoc
- **OpenAPI JSON**: http://localhost:8002/openapi.json

---

## 🔧 API Endpoints for Testing

### Health & Status
```bash
# Health check
curl http://localhost:8002/api/health

# API root
curl http://localhost:8002/api/
```

### Authentication
```bash
# Login
curl -X POST http://localhost:8002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@mahaedume.gov.in","password":"admin123"}'

# Get current user (requires token)
curl http://localhost:8002/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Scope Endpoints
```bash
# Get districts
curl http://localhost:8002/api/scope/districts

# Get blocks for a district
curl http://localhost:8002/api/scope/districts/2725/blocks

# Get schools for a block
curl http://localhost:8002/api/scope/blocks/123/schools
```

### Executive Dashboard
```bash
# Overview
curl http://localhost:8002/api/executive/overview

# Student Identity
curl http://localhost:8002/api/executive/student-identity

# Infrastructure Facilities
curl http://localhost:8002/api/executive/infrastructure-facilities

# Teacher Staffing
curl http://localhost:8002/api/executive/teacher-staffing

# Operational Performance
curl http://localhost:8002/api/executive/operational-performance

# School Health Index
curl http://localhost:8002/api/executive/school-health-index

# District Map Data
curl http://localhost:8002/api/executive/district-map-data
```

### CTTeacher Analytics
```bash
# Overview
curl http://localhost:8002/api/ctteacher/overview

# Block-wise
curl http://localhost:8002/api/ctteacher/block-wise

# Gender Distribution
curl http://localhost:8002/api/ctteacher/gender-distribution

# Qualification
curl http://localhost:8002/api/ctteacher/qualification

# Age Distribution
curl http://localhost:8002/api/ctteacher/age-distribution
```

### Classrooms & Toilets
```bash
# Overview
curl http://localhost:8002/api/classrooms-toilets/overview

# Block-wise
curl http://localhost:8002/api/classrooms-toilets/block-wise

# Classroom Condition
curl http://localhost:8002/api/classrooms-toilets/classroom-condition

# Toilet Distribution
curl http://localhost:8002/api/classrooms-toilets/toilet-distribution

# Hygiene Metrics
curl http://localhost:8002/api/classrooms-toilets/hygiene-metrics
```

### Other Dashboards
```bash
# Aadhaar Overview
curl http://localhost:8002/api/aadhaar/overview

# APAAR Overview
curl http://localhost:8002/api/apaar/overview

# Enrolment Overview
curl http://localhost:8002/api/enrolment/overview

# Teacher Overview
curl http://localhost:8002/api/teacher/overview

# Infrastructure Overview
curl http://localhost:8002/api/infrastructure/overview
```

---

## 🔑 Default Login Credentials

```
Email: admin@mahaedume.gov.in
Password: admin123
```

---

## 📊 Quick Test Commands

### Test Backend Health
```bash
curl http://localhost:8002/api/health
```
**Expected**: `{"status":"healthy","timestamp":"..."}`

### Test API Root
```bash
curl http://localhost:8002/api/
```
**Expected**: `{"message":"Maharashtra Education Dashboard API","version":"1.0.0"}`

### Test Login
```bash
curl -X POST http://localhost:8002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@mahaedume.gov.in","password":"admin123"}'
```
**Expected**: JSON with `access_token` and `user` object

### Test Scope Endpoints
```bash
# Districts
curl http://localhost:8002/api/scope/districts

# Blocks (replace 2725 with actual district code)
curl http://localhost:8002/api/scope/districts/2725/blocks
```

---

## 🌐 Browser Testing

### Frontend
1. Open browser: http://localhost:3000
2. Wait for React app to load (may take 30-60 seconds)
3. Login with default credentials
4. Navigate through dashboards

### API Documentation
1. Open: http://localhost:8002/docs
2. Explore all endpoints
3. Test endpoints directly from Swagger UI
4. Use "Try it out" feature

---

## 🔍 Service Status Check

### Check Backend
```bash
curl http://localhost:8002/api/health
ps aux | grep uvicorn
```

### Check Frontend
```bash
curl http://localhost:3000
ps aux | grep -E "(node|yarn)"
```

### Check MongoDB
```bash
# If MongoDB is running locally
mongosh --eval "db.adminCommand('ping')"

# Or check if backend can connect (if health check works, MongoDB is accessible)
```

---

## 📝 Service Information

| Service | Port | URL | Status |
|---------|------|-----|--------|
| Backend API | 8002 | http://localhost:8002 | ✅ RUNNING |
| Frontend | 3000 | http://localhost:3000 | ⏳ Starting |
| API Docs | 8002 | http://localhost:8002/docs | ✅ Available |
| Health | 8002 | http://localhost:8002/api/health | ✅ Working |

---

## 🎯 Quick Access

**Copy and paste these URLs in your browser:**

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8002
- **API Docs**: http://localhost:8002/docs
- **Health Check**: http://localhost:8002/api/health

---

**Status**: Backend is running! Frontend is compiling and will be available shortly at http://localhost:3000

