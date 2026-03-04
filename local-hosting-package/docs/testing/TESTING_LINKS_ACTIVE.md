# 🚀 Active Testing Links - Pune School Dashboard

## ✅ Services Status

**Backend API**: ✅ RUNNING on port 8002  
**Frontend**: ⏳ Starting (may take 30-60 seconds)  
**MongoDB**: ✅ Connected (backend health check working)

---

## 🌐 Testing Links

### Main Application Links

#### Frontend Dashboard
- **URL**: http://localhost:3000 (or check ports 3005, 3006)
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

## 🔧 Quick Test Commands

```bash
# Health Check
curl http://localhost:8002/api/health

# API Root
curl http://localhost:8002/api/

# Get Districts
curl http://localhost:8002/api/scope/districts

# Login
curl -X POST http://localhost:8002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@mahaedume.gov.in","password":"admin123"}'
```

---

## 🔑 Default Login Credentials

```
Email:    admin@mahaedume.gov.in
Password: admin123
```

---

## 📊 Service Status

| Service | Port | Status | URL |
|---------|------|--------|-----|
| Backend API | 8002 | ✅ Running | http://localhost:8002 |
| Frontend | 3000+ | ⏳ Starting | http://localhost:3000 |
| API Docs | 8002 | ✅ Available | http://localhost:8002/docs |
| Health | 8002 | ✅ Working | http://localhost:8002/api/health |

---

## 🎯 Browser Testing

1. **Open Frontend**: http://localhost:3000
   - Wait for React app to compile (30-60 seconds)
   - Login with default credentials
   - Navigate through dashboards

2. **Open API Docs**: http://localhost:8002/docs
   - Explore all endpoints
   - Test endpoints directly from Swagger UI
   - View request/response schemas

---

**Last Updated**: $(date)
**Status**: Backend running, Frontend starting
