# Quick Start - Docker Deployment

## ⚠️ Important: Start Docker Desktop First

Before running the project, ensure **Docker Desktop is running** on your system.

### Step 1: Start Docker Desktop
1. Open Docker Desktop application
2. Wait for it to fully start (whale icon in menu bar should be steady)
3. Verify it's running: `docker ps` should work without errors

### Step 2: Run the Project

#### Option A: Using the Start Script (Recommended)
```bash
cd local-hosting-package
./scripts/START_SERVICES.sh
```

#### Option B: Manual Commands
```bash
cd local-hosting-package

# Build and start services
docker compose up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### Step 3: Access the Application

Once services are running (wait 30-60 seconds for startup):

🌐 **Frontend Dashboard**: http://localhost  
🔧 **Backend API**: http://localhost:8002  
📚 **API Documentation**: http://localhost:8002/docs  

### Default Login
```
Email: admin@mahaedume.gov.in
Password: admin123
```

## Troubleshooting

### Docker Desktop Not Starting
1. Restart your computer
2. Check Docker Desktop system requirements
3. Ensure virtualization is enabled (for Windows/Linux)

### Port Conflicts
If ports 80, 8002, or 27017 are in use:
```bash
# Check what's using the ports
lsof -i :80
lsof -i :8002
lsof -i :27017

# Stop conflicting services or modify ports in docker-compose.yml
```

### Build Issues
```bash
# Clean and rebuild
docker compose down
docker compose build --no-cache
docker compose up -d
```

## Service Management

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
docker compose logs -f
```

### Restart Services
```bash
docker compose restart
```

## Health Checks

```bash
# Backend
curl http://localhost:8002/api/health

# Frontend
curl http://localhost/health

# MongoDB
docker compose exec mongodb mongosh --eval "db.adminCommand('ping')"
```

---

**Once Docker Desktop is running, execute the commands above to start the project!**

