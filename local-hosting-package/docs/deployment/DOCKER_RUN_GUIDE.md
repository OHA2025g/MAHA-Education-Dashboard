# Docker Run Guide - Pune School Dashboard

## Quick Start

### Prerequisites
1. **Docker Desktop** must be running
2. **Docker Compose** v2.0+ installed
3. At least **4GB RAM** available
4. At least **10GB** free disk space

### Step 1: Start Docker Desktop
Ensure Docker Desktop is running on your system.

### Step 2: Navigate to Project
```bash
cd local-hosting-package
```

### Step 3: Configure Environment
```bash
# Copy environment file if not exists
cp config/env.example .env

# Edit .env if needed (defaults work for local)
# nano .env
```

### Step 4: Build and Start Services
```bash
# Build images
docker compose build

# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### Step 5: Access the Application

Once services are running:

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8002
- **API Documentation**: http://localhost:8002/docs
- **MongoDB**: localhost:27017

## Troubleshooting Docker Issues

### Issue: Docker Desktop Not Starting
**Solution**:
1. Restart Docker Desktop application
2. Check system requirements
3. Ensure virtualization is enabled in BIOS (if on Windows/Linux)

### Issue: Build Context Too Large
**Solution**:
```bash
# Clean Docker build cache
docker builder prune -a

# Rebuild without cache
docker compose build --no-cache
```

### Issue: Port Already in Use
**Solution**:
```bash
# Check what's using the ports
lsof -i :80
lsof -i :8002
lsof -i :27017

# Stop conflicting services or change ports in docker-compose.yml
```

### Issue: MongoDB Connection Error
**Solution**:
```bash
# Check MongoDB container
docker compose logs mongodb

# Restart MongoDB
docker compose restart mongodb
```

## Alternative: Manual Setup (If Docker Fails)

If Docker is not working, you can run the project manually:

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export MONGO_URL=mongodb://localhost:27017
export DB_NAME=maharashtra_edu

# Start backend
uvicorn server:app --host 0.0.0.0 --port 8002
```

### Frontend Setup
```bash
cd frontend
yarn install

# Set backend URL
export REACT_APP_BACKEND_URL=http://localhost:8002

# Start frontend
yarn start
```

### MongoDB Setup
```bash
# Using Docker (just MongoDB)
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# Or install MongoDB locally
# macOS: brew install mongodb-community
# Linux: sudo apt-get install mongodb
```

## Service URLs

Once running, access:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost | Main dashboard UI |
| Backend API | http://localhost:8002 | REST API |
| API Docs | http://localhost:8002/docs | Swagger documentation |
| Health Check | http://localhost:8002/api/health | API health status |
| MongoDB | localhost:27017 | Database connection |

## Default Login Credentials

```
Email: admin@mahaedume.gov.in
Password: admin123
```

## Managing Services

### Start Services
```bash
docker compose up -d
```

### Stop Services
```bash
docker compose down
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f mongodb
```

### Restart Services
```bash
docker compose restart
```

### Rebuild After Code Changes
```bash
docker compose up -d --build
```

## Health Checks

### Check Backend
```bash
curl http://localhost:8002/api/health
```

### Check Frontend
```bash
curl http://localhost/health
```

### Check MongoDB
```bash
docker compose exec mongodb mongosh --eval "db.adminCommand('ping')"
```

## Production Deployment

For production, update `.env`:
```env
REACT_APP_BACKEND_URL=http://your-domain.com:8002
MONGO_URL=mongodb://your-mongodb-host:27017
```

Then rebuild:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

---

**Note**: If Docker Desktop is not working, please restart it and try again. The project can also be run manually as shown in the Alternative section above.

