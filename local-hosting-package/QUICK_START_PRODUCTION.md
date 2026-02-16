# Quick Start - Production Deployment

## 🚀 Quick Deployment Steps

### 1. Migrate Database (One-time)

```bash
cd local-hosting-package

# Run migration script
python3 scripts/migrate_to_production_db.py

# Or from Docker (if local MongoDB is in Docker)
docker compose exec backend python scripts/migrate_to_production_db.py
```

**This will:**
- Connect to local MongoDB (localhost:27017)
- Connect to remote MongoDB (31.97.207.166:27017)
- Migrate all collections to production database
- Show progress and ask for confirmation

### 2. Configure Environment

```bash
# Copy template
cp env.prod.example .env.prod

# Edit .env.prod with your values
# Important: Update JWT_SECRET_KEY to a strong random value!
```

### 3. Build and Deploy

```bash
# Build production images
docker compose -f docker-compose.prod.yml build

# Start services
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

### 4. Verify

```bash
# Test backend
curl http://localhost:8002/api/health

# Test frontend
curl http://localhost/health
```

## 📋 Configuration Summary

- **Production URL:** https://schooldashboard.demo.agrayianailabs.com/
- **Backend API:** https://schooldashboard.demo.agrayianailabs.com/api
- **MongoDB:** mongodb://mongo:***@31.97.207.166:27017/?tls=false
- **CORS Origins:** https://schooldashboard.demo.agrayianailabs.com

## 🔧 Important Notes

1. **MongoDB Connection:** The production setup uses remote MongoDB, so no local MongoDB container is needed
2. **CORS:** Configured to allow requests from the production domain
3. **Environment Variables:** Use `.env.prod` file (not committed to git)
4. **Reverse Proxy:** You'll need to configure Nginx/Apache to route:
   - `/` → Frontend (port 80)
   - `/api` → Backend (port 8002)

## 📚 Full Documentation

See `PRODUCTION_DEPLOYMENT.md` for detailed deployment guide including:
- Reverse proxy configuration
- SSL/TLS setup
- Monitoring and maintenance
- Troubleshooting

## 🆘 Troubleshooting

**Database migration fails:**
- Check local MongoDB is running: `docker compose ps mongodb`
- Verify remote MongoDB credentials
- Check network connectivity

**Backend cannot connect to MongoDB:**
- Verify MONGO_URL in .env.prod
- Check MongoDB server is accessible
- Verify credentials are correct

**CORS errors:**
- Verify CORS_ORIGINS includes the production domain
- Check reverse proxy is forwarding headers
- Verify frontend is using correct backend URL

