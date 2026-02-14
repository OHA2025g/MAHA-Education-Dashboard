# Production Deployment Guide

## Production Environment

- **Frontend URL:** https://school_dashboard.demo.agrayianailabs.com/
- **Backend API:** Should be accessible at the same domain (via reverse proxy) or separate subdomain
- **MongoDB:** Remote MongoDB at `mongodb://mongo:b5a7adcac8107c867aa1@31.97.207.166:27017/?tls=false`

## Prerequisites

1. Docker and Docker Compose installed on production server
2. Access to the production server
3. Domain configured to point to the server
4. SSL certificate configured (for HTTPS)

## Step 1: Database Migration

### Migrate Local Database to Production MongoDB

```bash
cd local-hosting-package

# Option 1: Run migration script directly
python3 scripts/migrate_to_production_db.py

# Option 2: Use the wrapper script
./scripts/migrate_db.sh

# Option 3: Run from Docker container (if local MongoDB is in Docker)
docker compose exec backend python scripts/migrate_to_production_db.py
```

The migration script will:
- Connect to local MongoDB
- Connect to remote MongoDB
- Migrate all collections
- Show progress and summary

**Important:** The script will ask for confirmation before overwriting data in the remote database.

## Step 2: Environment Configuration

Create a `.env.prod` file (or set environment variables):

```bash
# Database
DB_NAME=maharashtra_edu
MONGO_URL=mongodb://mongo:b5a7adcac8107c867aa1@31.97.207.166:27017/?tls=false

# Backend API URL (for frontend)
# If backend is at same domain: https://school_dashboard.demo.agrayianailabs.com/api
# If backend is at separate subdomain: https://api.school_dashboard.demo.agrayianailabs.com
REACT_APP_BACKEND_URL=https://school_dashboard.demo.agrayianailabs.com/api

# CORS
CORS_ORIGINS=https://school_dashboard.demo.agrayianailabs.com
CORS_ALLOW_CREDENTIALS=true

# Security
JWT_SECRET_KEY=your-strong-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Optional: OpenAI
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o-mini
```

## Step 3: Build and Deploy

### Build Production Images

```bash
cd local-hosting-package
docker compose -f docker-compose.prod.yml build
```

### Start Production Services

```bash
# Load environment variables from .env.prod
export $(cat .env.prod | xargs)

# Start services
docker compose -f docker-compose.prod.yml up -d
```

### Check Service Status

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

## Step 4: Reverse Proxy Configuration (Nginx)

If using Nginx as reverse proxy, configure it to route requests:

```nginx
# /etc/nginx/sites-available/school_dashboard.demo.agrayianailabs.com

server {
    listen 80;
    server_name school_dashboard.demo.agrayianailabs.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name school_dashboard.demo.agrayianailabs.com;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;

    # Frontend (React app)
    location / {
        proxy_pass http://localhost:80;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # CORS headers (if needed)
        add_header 'Access-Control-Allow-Origin' 'https://school_dashboard.demo.agrayianailabs.com' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
        
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }

    # API Documentation
    location /docs {
        proxy_pass http://localhost:8002/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /redoc {
        proxy_pass http://localhost:8002/redoc;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Step 5: Verify Deployment

### Check Backend Health
```bash
curl https://school_dashboard.demo.agrayianailabs.com/api/health
```

### Check Frontend
```bash
curl https://school_dashboard.demo.agrayianailabs.com/health
```

### Test API Endpoints
```bash
# Root endpoint
curl https://school_dashboard.demo.agrayianailabs.com/api/

# API documentation
open https://school_dashboard.demo.agrayianailabs.com/docs
```

## Step 6: Monitoring and Maintenance

### View Logs
```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
```

### Restart Services
```bash
docker compose -f docker-compose.prod.yml restart
```

### Update Deployment
```bash
# Pull latest code
git pull

# Rebuild and restart
docker compose -f docker-compose.prod.yml up -d --build
```

### Backup Database
```bash
# Backup from remote MongoDB
mongodump --uri="mongodb://mongo:b5a7adcac8107c867aa1@31.97.207.166:27017/?tls=false" --db=maharashtra_edu --out=./backup_$(date +%Y%m%d)
```

## Troubleshooting

### Backend cannot connect to MongoDB
- Verify MongoDB connection string is correct
- Check network connectivity to MongoDB server
- Verify MongoDB credentials
- Check MongoDB server logs

### CORS errors
- Verify CORS_ORIGINS environment variable includes the frontend domain
- Check browser console for specific CORS errors
- Verify reverse proxy is forwarding headers correctly

### Frontend cannot reach backend
- Verify REACT_APP_BACKEND_URL is set correctly
- Check reverse proxy configuration
- Verify backend is running and accessible
- Check browser network tab for API call errors

## Security Checklist

- [ ] JWT_SECRET_KEY is set to a strong, random value
- [ ] MongoDB credentials are secure
- [ ] SSL/TLS certificates are valid
- [ ] CORS is configured for specific origins (not *)
- [ ] Environment variables are not committed to git
- [ ] Firewall rules are configured
- [ ] Regular backups are scheduled
- [ ] Logs are monitored

## Support

For issues or questions:
1. Check logs: `docker compose -f docker-compose.prod.yml logs`
2. Verify health: `docker compose -f docker-compose.prod.yml ps`
3. Review this documentation
4. Check GitHub issues

