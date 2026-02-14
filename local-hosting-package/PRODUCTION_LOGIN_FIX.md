# Production Login Fix - Step by Step Guide

## Issue
Login is failing in production with "Login failed. Please check your credentials" error.

## Quick Fix (Run on Production Server)

### Option 1: Automated Script (Recommended)

```bash
# SSH into production server
# Navigate to project directory
cd /path/to/project/local-hosting-package

# Run the automated fix script
./scripts/production_fix_login.sh
```

This script will:
1. ✅ Create/verify admin user
2. ✅ Test login endpoint
3. ✅ Check backend logs

### Option 2: Manual Steps

#### Step 1: Pull Latest Code

```bash
cd /path/to/project
git pull origin main
```

#### Step 2: Create Admin User

**Using Docker:**
```bash
cd local-hosting-package

# Set MongoDB connection (if not in environment)
export MONGO_URL="mongodb://mongo:b5a7adcac8107c867aa1@31.97.207.166:27017/?tls=false"
export DB_NAME="maharashtra_edu"

# Run script inside backend container
docker compose exec backend python /app/scripts/create_admin_user.py

# OR if scripts are mounted
docker compose exec backend python scripts/create_admin_user.py
```

**Direct Python (if MongoDB is accessible):**
```bash
export MONGO_URL="mongodb://mongo:b5a7adcac8107c867aa1@31.97.207.166:27017/?tls=false"
export DB_NAME="maharashtra_edu"
python3 scripts/create_admin_user.py
```

**Using MongoDB Shell:**
```bash
mongosh "mongodb://mongo:b5a7adcac8107c867aa1@31.97.207.166:27017/?tls=false"

use maharashtra_edu

# Check if user exists
db.users.find({"email": "admin@mahaedume.gov.in"})

# If user doesn't exist, you'll need to create it with proper password hash
# Use the Python script instead for proper hash generation
```

#### Step 3: Test Login

```bash
# Test login endpoint
curl -X POST https://school_dashboard.demo.agrayianailabs.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@mahaedume.gov.in", "password": "admin123"}'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "email": "admin@mahaedume.gov.in",
    "full_name": "System Administrator",
    "role": "admin"
  }
}
```

#### Step 4: Check Backend Logs

```bash
# View recent logs
docker compose logs --tail=50 backend

# Filter for errors
docker compose logs backend | grep -i error

# Filter for login/auth issues
docker compose logs backend | grep -i -E "(login|auth|exception)"
```

## Troubleshooting

### Issue: "User not found"
**Solution:** Admin user doesn't exist. Run `create_admin_user.py` script.

### Issue: "Incorrect password"
**Solution:** 
1. Verify password hash exists: Check database
2. Recreate user with script
3. Check if password hash format is correct

### Issue: "Database connection failed"
**Solution:**
1. Verify MONGO_URL environment variable
2. Test MongoDB connection:
   ```bash
   docker compose exec backend python -c "
   from motor.motor_asyncio import AsyncIOMotorClient
   import asyncio
   import os
   async def test():
       client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
       await client.admin.command('ping')
       print('OK')
   asyncio.run(test())
   "
   ```

### Issue: "500 Internal Server Error"
**Solution:**
1. Check backend logs for detailed error
2. Verify JWT_SECRET_KEY is set
3. Check database connection
4. Verify all dependencies are installed

## Default Credentials

- **Email:** admin@mahaedume.gov.in
- **Password:** admin123

## Verification Checklist

- [ ] Code pulled from GitHub
- [ ] Admin user exists in database
- [ ] Login endpoint returns 200 status
- [ ] Access token is received
- [ ] Backend logs show no errors
- [ ] Can login via web interface

## After Fix

Once login works:
1. Test all dashboard features
2. Verify data is loading correctly
3. Check API endpoints are accessible
4. Monitor logs for any issues

## Support

If issues persist:
1. Check `LOGIN_FIX.md` for detailed troubleshooting
2. Review backend logs: `docker compose logs backend`
3. Verify database connection
4. Check environment variables

