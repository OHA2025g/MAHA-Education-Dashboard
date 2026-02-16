# Login Issue Fix

## Problem
Login is failing in production with error: "Login failed. Please check your credentials."

## Root Causes

1. **Missing Admin User**: The admin user (`admin@mahaedume.gov.in`) may not exist in the production database
2. **Database Connection Issues**: The database connection might not be properly initialized
3. **Password Hash Mismatch**: Password hash format might be incompatible

## Solutions

### Solution 1: Create Admin User Manually

Run the admin user creation script:

```bash
# From production server or locally with production MongoDB connection
cd local-hosting-package
export MONGO_URL="mongodb://mongo:b5a7adcac8107c867aa1@31.97.207.166:27017/?tls=false"
export DB_NAME="maharashtra_edu"
python3 scripts/create_admin_user.py
```

Or from Docker container:
```bash
docker compose exec backend python scripts/create_admin_user.py
```

### Solution 2: Verify Admin User Exists

Check if admin user exists in database:
```bash
# Connect to MongoDB
mongosh "mongodb://mongo:b5a7adcac8107c867aa1@31.97.207.166:27017/?tls=false"

# Switch to database
use maharashtra_edu

# Check for admin user
db.users.find({"email": "admin@mahaedume.gov.in"})
```

### Solution 3: Check Backend Logs

Check backend logs for detailed error messages:
```bash
docker compose logs backend | grep -i login
docker compose logs backend | grep -i error
```

## Default Credentials

- **Email:** admin@mahaedume.gov.in
- **Password:** admin123

## Verification Steps

1. **Check if user exists:**
   ```bash
   # Using the script
   python3 scripts/create_admin_user.py
   ```

2. **Test login endpoint:**
   ```bash
   curl -X POST https://schooldashboard.demo.agrayianailabs.com/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@mahaedume.gov.in", "password": "admin123"}'
   ```

3. **Check backend health:**
   ```bash
   curl https://schooldashboard.demo.agrayianailabs.com/api/health
   ```

## Code Changes Made

1. **Added logging to login endpoint** - Better error tracking
2. **Improved error handling** - More detailed error messages
3. **Created admin user script** - Easy way to create admin user

## Next Steps

1. Run the `create_admin_user.py` script on production
2. Verify the user was created
3. Test login again
4. Check backend logs if issues persist

