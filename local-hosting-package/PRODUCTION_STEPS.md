# Production Deployment Steps - Complete Guide

## Step-by-Step Instructions for Production Server

### Prerequisites
- SSH access to production server
- Docker and Docker Compose installed
- Git access to repository

---

## Step 1: Pull Latest Code

```bash
# SSH into production server
ssh user@production-server

# Navigate to project directory
cd /path/to/project

# Pull latest code
git pull origin main

# Navigate to local-hosting-package
cd local-hosting-package
```

**Expected Output:**
```
Already up to date.
```
or
```
Updating 130ef97..4f574a4
Fast-forward
...
```

---

## Step 2: Create Admin User

The admin user needs to exist in the production database. Run one of these methods:

### Method A: Using the Automated Script (Recommended)

```bash
cd local-hosting-package

# Set MongoDB connection
export MONGO_URL="mongodb://mongo:b5a7adcac8107c867aa1@31.97.207.166:27017/?tls=false"
export DB_NAME="maharashtra_edu"

# Run the script
./scripts/production_fix_login.sh
```

### Method B: Using Docker Container

```bash
cd local-hosting-package

# Copy script into container and run
docker compose exec backend bash -c "
cat > /tmp/create_admin_user.py << 'EOFPYTHON'
$(cat scripts/create_admin_user.py)
EOFPYTHON
python3 /tmp/create_admin_user.py
rm /tmp/create_admin_user.py
"
```

### Method C: Direct Python (if MongoDB is accessible)

```bash
export MONGO_URL="mongodb://mongo:b5a7adcac8107c867aa1@31.97.207.166:27017/?tls=false"
export DB_NAME="maharashtra_edu"
python3 scripts/create_admin_user.py
```

**Expected Output:**
```
============================================================
CREATE ADMIN USER
============================================================
MongoDB: 31.97.207.166:27017
Database: maharashtra_edu
Admin Email: admin@mahaedume.gov.in
============================================================

Connecting to MongoDB...
✓ MongoDB connection successful

Checking for existing admin user...
✓ Admin user already exists: admin@mahaedume.gov.in
  User ID: ...
  Full Name: System Administrator
  Role: admin
  Is Active: True
  Password: Hashed (exists)
```

---

## Step 3: Test Login

Test the login endpoint to verify it works:

```bash
# Test login
curl -X POST https://schooldashboard.demo.agrayianailabs.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@mahaedume.gov.in", "password": "admin123"}'
```

**Expected Response (Success):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "email": "admin@mahaedume.gov.in",
    "full_name": "System Administrator",
    "role": "admin",
    "permissions": {...}
  }
}
```

**If it fails, you'll see:**
```json
{
  "detail": "Incorrect email or password"
}
```

---

## Step 4: Check Backend Logs

Check for any errors or warnings:

```bash
# View recent logs
docker compose logs --tail=50 backend

# Filter for errors
docker compose logs backend | grep -i error

# Filter for login/auth issues
docker compose logs backend | grep -i -E "(login|auth|exception|warning)"
```

**What to look for:**
- Database connection errors
- User lookup errors
- Password verification errors
- Authentication token errors

---

## Complete Automated Script

For convenience, run the complete deployment script:

```bash
cd local-hosting-package
./scripts/deploy_production.sh
```

This will execute all steps automatically.

---

## Troubleshooting

### Issue: Git pull fails
**Solution:** Check git credentials and repository access

### Issue: Admin user script fails
**Solution:** 
1. Verify MongoDB connection string
2. Check network connectivity
3. Verify MongoDB credentials
4. Check if database exists

### Issue: Login still fails after creating user
**Solution:**
1. Check backend logs for detailed errors
2. Verify password hash was created correctly
3. Test password verification manually
4. Check if JWT_SECRET_KEY is set

### Issue: Backend not running
**Solution:**
```bash
# Restart backend
docker compose restart backend

# Check status
docker compose ps

# View logs
docker compose logs backend
```

---

## Verification Checklist

After completing all steps:

- [ ] Code pulled from GitHub
- [ ] Admin user exists in database
- [ ] Login endpoint returns 200 status
- [ ] Access token received
- [ ] Can login via web interface
- [ ] Backend logs show no errors
- [ ] All services are running

---

## Default Credentials

- **Email:** admin@mahaedume.gov.in
- **Password:** admin123

**⚠️ IMPORTANT:** Change the default password after first login in production!

---

## Next Steps After Fix

1. Test all dashboard features
2. Verify data is loading
3. Check API endpoints
4. Monitor application logs
5. Set up regular backups
6. Change default admin password

