# Deployment Documentation

This directory contains all deployment-related documentation for the Pune School Dashboard.

## 📋 Available Guides

1. **[DOCKER_DEPLOYMENT.md](./DOCKER_DEPLOYMENT.md)**
   - Complete Docker deployment guide
   - Service configuration
   - Production deployment steps
   - Troubleshooting

2. **[QUICK_START_DOCKER.md](./QUICK_START_DOCKER.md)**
   - Quick start guide for Docker
   - Minimal setup instructions
   - Common commands

3. **[DOCKER_RUN_GUIDE.md](./DOCKER_RUN_GUIDE.md)**
   - Running Docker containers
   - Service management
   - Health checks

4. **[START_DOCKER.md](./START_DOCKER.md)**
   - Starting Docker services
   - Service initialization
   - First-time setup

5. **[DOCKER_STATUS.md](./DOCKER_STATUS.md)**
   - Checking Docker service status
   - Health monitoring
   - Service logs

6. **[DEPLOYMENT_READY.md](./DEPLOYMENT_READY.md)**
   - Production deployment checklist
   - Pre-deployment verification
   - Security considerations

## 🚀 Quick Start

```bash
# Copy environment file
cp ../config/env.example ../.env

# Start all services
docker compose up -d

# Check status
docker compose ps
```

## 📚 Related Documentation

- [Main README](../../README.md)
- [Testing Documentation](../testing/README.md)
- [Project Structure](../../PROJECT_STRUCTURE.md)

