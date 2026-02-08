# Docker Deployment Guide

This guide explains how to deploy the Pune School Dashboard using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+ installed
- Docker Compose 2.0+ installed
- At least 4GB of available RAM
- At least 10GB of available disk space

## Quick Start

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/OHA2025g/Pune_School_Dashboard.git
   cd Pune_School_Dashboard/local-hosting-package
   ```

2. **Create environment file**:
   ```bash
   cp env.example .env
   ```

3. **Edit `.env` file** with your configuration:
   ```env
   DB_NAME=maharashtra_edu
   MONGO_URL=mongodb://mongodb:27017
   OPENAI_API_KEY=sk-your-openai-key-here  # Optional
   OPENAI_MODEL=gpt-4o-mini
   REACT_APP_BACKEND_URL=http://localhost:8002
   ```

4. **Build and start all services**:
   ```bash
   docker-compose up -d
   ```

5. **Check service status**:
   ```bash
   docker-compose ps
   ```

6. **View logs**:
   ```bash
   docker-compose logs -f
   ```

## Accessing the Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8002
- **API Documentation**: http://localhost:8002/docs
- **MongoDB**: localhost:27017

## Services

### 1. MongoDB (`mongodb`)
- **Image**: `mongo:7.0`
- **Port**: `27017`
- **Data Volume**: `mongodb_data` (persistent)
- **Config Volume**: `mongodb_config` (persistent)

### 2. Backend API (`backend`)
- **Port**: `8002`
- **Environment Variables**:
  - `MONGO_URL`: MongoDB connection string
  - `DB_NAME`: Database name
  - `OPENAI_API_KEY`: OpenAI API key (optional, for AI insights)
  - `OPENAI_MODEL`: OpenAI model to use
- **Volumes**:
  - `./backend/uploads`: File uploads directory

### 3. Frontend (`frontend`)
- **Port**: `80`
- **Build Args**:
  - `REACT_APP_BACKEND_URL`: Backend API URL
- **Serves**: Built React application via nginx

## Production Deployment

### 1. Update Environment Variables

For production, update `.env`:

```env
# Use your domain or server IP
REACT_APP_BACKEND_URL=http://your-domain.com:8002

# Or if using reverse proxy
REACT_APP_BACKEND_URL=https://api.your-domain.com
```

### 2. Build for Production

```bash
# Build images
docker-compose build --no-cache

# Start services
docker-compose up -d
```

### 3. Using External MongoDB

If you have an external MongoDB instance:

```env
MONGO_URL=mongodb://username:password@your-mongodb-host:27017
```

Then comment out the `mongodb` service in `docker-compose.yml`:

```yaml
# mongodb:
#   image: mongo:7.0
#   ...
```

### 4. Using Reverse Proxy (Nginx/Traefik)

For production, it's recommended to use a reverse proxy. Example nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 5. SSL/HTTPS Setup

Use Let's Encrypt with Certbot:

```bash
sudo certbot --nginx -d your-domain.com
```

## Managing Services

### Start services
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### Stop and remove volumes (⚠️ deletes data)
```bash
docker-compose down -v
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

### Restart a service
```bash
docker-compose restart backend
```

### Rebuild after code changes
```bash
docker-compose up -d --build
```

## Data Management

### Backup MongoDB

```bash
# Create backup
docker-compose exec mongodb mongodump --out /data/backup

# Copy backup from container
docker cp pune-dashboard-mongodb:/data/backup ./backup
```

### Restore MongoDB

```bash
# Copy backup to container
docker cp ./backup pune-dashboard-mongodb:/data/backup

# Restore
docker-compose exec mongodb mongorestore /data/backup
```

### Access MongoDB Shell

```bash
docker-compose exec mongodb mongosh
```

## Troubleshooting

### Services not starting

1. **Check logs**:
   ```bash
   docker-compose logs
   ```

2. **Check port availability**:
   ```bash
   # Check if ports are in use
   lsof -i :80
   lsof -i :8002
   lsof -i :27017
   ```

3. **Verify Docker resources**:
   ```bash
   docker system df
   docker stats
   ```

### Frontend not connecting to backend

1. **Check `REACT_APP_BACKEND_URL`** in `.env`
2. **Rebuild frontend**:
   ```bash
   docker-compose up -d --build frontend
   ```

### MongoDB connection issues

1. **Check MongoDB is running**:
   ```bash
   docker-compose ps mongodb
   ```

2. **Check connection string** in `.env`:
   ```env
   MONGO_URL=mongodb://mongodb:27017
   ```

3. **Check MongoDB logs**:
   ```bash
   docker-compose logs mongodb
   ```

### Out of disk space

```bash
# Clean up unused Docker resources
docker system prune -a

# Remove old images
docker image prune -a
```

## Development Mode

For development with hot-reload:

### Backend (separate terminal)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8002 --reload
```

### Frontend (separate terminal)
```bash
cd frontend
yarn install
yarn start
```

### MongoDB (Docker)
```bash
docker-compose up -d mongodb
```

## Security Considerations

1. **Change default passwords** if using MongoDB authentication
2. **Use environment variables** for sensitive data (never commit `.env`)
3. **Enable MongoDB authentication** in production
4. **Use HTTPS** in production
5. **Set up firewall rules** to restrict access
6. **Regular backups** of MongoDB data
7. **Keep Docker images updated**

## Monitoring

### Health Checks

All services have health checks configured. Check status:

```bash
docker-compose ps
```

### Resource Usage

```bash
docker stats
```

## Scaling

To scale services (if needed):

```bash
# Scale backend (requires load balancer)
docker-compose up -d --scale backend=3
```

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Review this guide
- Check GitHub issues: https://github.com/OHA2025g/Pune_School_Dashboard/issues

