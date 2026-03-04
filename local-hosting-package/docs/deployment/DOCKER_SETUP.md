# Docker Setup Guide - Complete Project

This guide provides instructions for running the complete MAHA Education Dashboard project using Docker.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM available
- 10GB free disk space

## Quick Start

### Development Environment

1. **Clone and navigate to the project:**
   ```bash
   cd local-hosting-package
   ```

2. **Create environment file:**
   ```bash
   cp config/env.example .env
   ```

3. **Edit `.env` file with your configuration:**
   ```env
   DB_NAME=maharashtra_edu
   REACT_APP_BACKEND_URL=http://localhost:8002
   OPENAI_API_KEY=your-api-key-here
   JWT_SECRET_KEY=your-secret-key-here
   ```

4. **Build and start all services:**
   ```bash
   docker compose up -d --build
   ```

5. **Check service status:**
   ```bash
   docker compose ps
   ```

6. **View logs:**
   ```bash
   docker compose logs -f
   ```

7. **Access the application:**
   - Frontend: http://localhost
   - Backend API: http://localhost:8002
   - API Docs: http://localhost:8002/docs

### Production Environment

1. **Use production compose file:**
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```

2. **Set production environment variables:**
   ```bash
   export JWT_SECRET_KEY=strong-secret-key
   export OPENAI_API_KEY=your-production-key
   export DB_NAME=maharashtra_edu_prod
   ```

## Services

### MongoDB
- **Port:** 27017
- **Data Volume:** `mongodb_data`
- **Config Volume:** `mongodb_config`
- **Health Check:** Automatic ping test

### Backend API
- **Port:** 8002
- **Framework:** FastAPI
- **Health Endpoint:** `/api/health`
- **Dependencies:** All Python packages from `requirements.txt`

### Frontend
- **Port:** 80 (configurable via `FRONTEND_PORT`)
- **Framework:** React with Tailwind CSS
- **Build Tool:** Create React App (CRA) with CRACO
- **Web Server:** Nginx

## Project Structure

```
local-hosting-package/
├── backend/
│   ├── Dockerfile              # Backend container definition
│   ├── requirements.txt        # Python dependencies
│   ├── server.py               # FastAPI application
│   ├── routers/                # API route modules
│   │   ├── executive.py        # Executive dashboard endpoints
│   │   ├── teacher.py          # Teacher analytics endpoints
│   │   ├── aadhaar.py          # Aadhaar analytics endpoints
│   │   ├── apaar.py            # APAAR endpoints
│   │   └── ...                 # Other route modules
│   ├── utils/                  # Utility modules
│   ├── models/                 # Data models
│   └── tests/                  # Test suite
├── frontend/
│   ├── Dockerfile              # Frontend container definition
│   ├── package.json            # Node.js dependencies
│   ├── nginx.conf              # Nginx configuration
│   └── src/                    # React source code
├── docker-compose.yml          # Development compose file
├── docker-compose.prod.yml     # Production compose file
└── .dockerignore              # Docker ignore patterns
```

## Dependencies Included

### Backend Dependencies
- **FastAPI** - Web framework
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation
- **JWT** - Authentication
- **Pandas** - Data processing
- **OpenPyXL** - Excel file handling
- **WeasyPrint** - PDF generation
- **OpenAI** - AI integration
- **Pytest** - Testing framework
- And 100+ other dependencies

### Frontend Dependencies
- **React 19** - UI framework
- **React Router** - Routing
- **Axios** - HTTP client
- **Recharts** - Charting library
- **Radix UI** - UI components
- **Tailwind CSS** - Styling
- **Next Themes** - Theme management
- **Sonner** - Toast notifications
- And 50+ other dependencies

## Common Commands

### Start Services
```bash
docker compose up -d
```

### Stop Services
```bash
docker compose down
```

### Rebuild Services
```bash
docker compose up -d --build
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

### Execute Commands in Containers
```bash
# Backend shell
docker compose exec backend bash

# Run tests
docker compose exec backend pytest

# MongoDB shell
docker compose exec mongodb mongosh
```

### Database Backup
```bash
# Backup MongoDB
docker compose exec mongodb mongodump --out /data/backup

# Restore MongoDB
docker compose exec mongodb mongorestore /data/backup
```

### Clean Up
```bash
# Stop and remove containers
docker compose down

# Remove volumes (WARNING: Deletes data)
docker compose down -v

# Remove images
docker compose down --rmi all
```

## Health Checks

All services include health checks:

- **MongoDB:** Ping test every 10s
- **Backend:** HTTP health endpoint every 30s
- **Frontend:** HTTP health endpoint every 30s

Check health status:
```bash
docker compose ps
```

## Troubleshooting

### Port Already in Use
```bash
# Change ports in docker-compose.yml
ports:
  - "8003:8002"  # Use different host port
```

### Out of Memory
```bash
# Increase Docker memory limit in Docker Desktop settings
# Or use production compose file with resource limits
```

### Build Failures
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker compose build --no-cache
```

### Database Connection Issues
```bash
# Check MongoDB is healthy
docker compose ps mongodb

# Check backend logs
docker compose logs backend
```

## Environment Variables

### Required
- `DB_NAME` - MongoDB database name
- `MONGO_URL` - MongoDB connection string (auto-set in compose)

### Optional
- `REACT_APP_BACKEND_URL` - Frontend backend URL
- `OPENAI_API_KEY` - OpenAI API key for AI features
- `JWT_SECRET_KEY` - JWT secret for authentication
- `JWT_ALGORITHM` - JWT algorithm (default: HS256)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiry (default: 1440)
- `FRONTEND_PORT` - Frontend port (default: 80)

## Production Deployment

1. **Use production compose file:**
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```

2. **Set strong secrets:**
   ```bash
   export JWT_SECRET_KEY=$(openssl rand -hex 32)
   ```

3. **Enable HTTPS** (recommended):
   - Use reverse proxy (Nginx/Traefik)
   - Configure SSL certificates
   - Update `REACT_APP_BACKEND_URL` to HTTPS

4. **Monitor resources:**
   ```bash
   docker stats
   ```

5. **Set up backups:**
   ```bash
   # Add cron job for MongoDB backups
   0 2 * * * docker compose exec -T mongodb mongodump --out /data/backup
   ```

## Support

For issues or questions:
1. Check logs: `docker compose logs`
2. Verify health: `docker compose ps`
3. Review this documentation
4. Check GitHub issues



