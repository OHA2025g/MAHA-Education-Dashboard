# Quick Fix: Login Issue in Production

## Problem
Login fails with "Login failed. Please check your credentials" error.

## Most Likely Cause
The admin user doesn't exist in the production database.

## Quick Fix (Run on Production Server)

### Option 1: Using Docker Container

```bash
# SSH into production server
# Navigate to project directory
cd /path/to/project/local-hosting-package

# Run the script inside backend container
docker compose exec backend python scripts/create_admin_user.py
```

### Option 2: Direct Python Script

```bash
# Set environment variables
export MONGO_URL="mongodb://mongo:b5a7adcac8107c867aa1@31.97.207.166:27017/?tls=false"
export DB_NAME="maharashtra_edu"

# Run script
cd local-hosting-package
python3 scripts/create_admin_user.py
```

### Option 3: Using MongoDB Shell

```bash
# Connect to MongoDB
mongosh "mongodb://mongo:b5a7adcac8107c867aa1@31.97.207.166:27017/?tls=false"

# Switch to database
use maharashtra_edu

# Create admin user manually
db.users.insertOne({
  "id": "admin-001",
  "email": "admin@mahaedume.gov.in",
  "full_name": "System Administrator",
  "role": "admin",
  "is_active": true,
  "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyY5Y5Y5Y5Y5Y",  # This is a placeholder - use the script to generate proper hash
  "created_at": new Date(),
  "updated_at": new Date()
})
```

**Note:** For Option 3, you need to generate the password hash properly. Use Option 1 or 2 instead.

## Verify Fix

After running the script, test login:

```bash
curl -X POST https://schooldashboard.demo.agrayianailabs.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@mahaedume.gov.in", "password": "admin123"}'
```

You should get a response with `access_token`.

## Default Credentials

- **Email:** admin@mahaedume.gov.in
- **Password:** admin123

## Check Backend Logs

If login still fails, check logs:

```bash
docker compose logs backend | tail -50
```

Look for:
- Database connection errors
- User lookup errors
- Password verification errors

## Additional Troubleshooting

1. **Check if database is accessible:**
   ```bash
   docker compose exec backend python -c "
   from motor.motor_asyncio import AsyncIOMotorClient
   import asyncio
   import os
   async def test():
       client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
       await client.admin.command('ping')
       print('Database connection OK')
   asyncio.run(test())
   "
   ```

2. **Check if users collection exists:**
   ```bash
   mongosh "mongodb://mongo:***@31.97.207.166:27017/?tls=false"
   use maharashtra_edu
   db.users.countDocuments()
   ```

3. **List all users:**
   ```bash
   db.users.find({}, {email: 1, role: 1, is_active: 1})
   ```

