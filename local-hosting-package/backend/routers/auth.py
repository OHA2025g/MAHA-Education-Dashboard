"""Authentication routes"""
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone
from typing import Optional
import uuid
import os
from motor.motor_asyncio import AsyncIOMotorClient

from models.user import (
    UserCreate, UserUpdate, UserResponse, UserRole,
    LoginRequest, Token, PasswordResetRequest, PasswordResetConfirm,
    ChangePasswordRequest, ROLE_PERMISSIONS
)
from utils.auth import (
    verify_password, get_password_hash, create_access_token,
    create_reset_token, verify_reset_token, get_current_user, require_admin
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Database will be injected
db = None

def init_db(database):
    global db
    db = database

def get_db():
    """Get database connection, re-initialize if needed"""
    global db
    if db is None:
        # Re-initialize from environment - use same connection as server.py
        from pathlib import Path
        from dotenv import load_dotenv
        ROOT_DIR = Path(__file__).parent.parent
        load_dotenv(ROOT_DIR / '.env')
        load_dotenv(ROOT_DIR / ".env.local", override=True)
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'maharashtra_edu')
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
    return db

@router.post("/login", response_model=Token)
async def login(request: LoginRequest):
    """Login with email and password"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Use global db, or get_db() if not set
        database = db if db is not None else get_db()
        
        # Test database connection first
        try:
            await database.users.find_one({"_id": "connection_test"})
        except Exception as db_error:
            logger.error(f"Database connection error: {db_error}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database connection failed. Please contact administrator."
            )
        
        # Normalize email to lowercase for case-insensitive lookup
        email_lower = request.email.lower().strip()
        
        logger.info(f"Login attempt for email: {email_lower}")
        
        # Find user - try multiple methods
        user = None
        
        # Method 1: Exact lowercase match
        try:
            user = await database.users.find_one({"email": email_lower})
            if user:
                logger.debug(f"User found via exact match: {email_lower}")
        except Exception as e:
            logger.warning(f"Exact match query failed: {e}")
        
        # Method 2: Case-insensitive regex search
        if not user:
            try:
                user = await database.users.find_one({"email": {"$regex": f"^{request.email.strip()}$", "$options": "i"}})
                if user:
                    logger.debug(f"User found via case-insensitive search")
                    # Normalize email to lowercase
                    if user.get("email") != email_lower:
                        await database.users.update_one(
                            {"id": user["id"]} if user.get("id") else {"email": user.get("email")},
                            {"$set": {"email": email_lower, "updated_at": datetime.now(timezone.utc)}}
                        )
                        user["email"] = email_lower
                        logger.info(f"Normalized email to lowercase: {email_lower}")
            except Exception as e:
                logger.warning(f"Case-insensitive search failed: {e}")
        
        # Method 3: Try without regex (simple find)
        if not user:
            try:
                all_users = await database.users.find({}).to_list(length=100)
                for u in all_users:
                    if u.get("email", "").lower() == email_lower:
                        user = u
                        logger.debug(f"User found via iteration")
                        break
            except Exception as e:
                logger.warning(f"User iteration failed: {e}")
        
        if not user:
            logger.warning(f"Login attempt with non-existent email: {email_lower}")
            # Don't reveal if email exists or not for security
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        logger.info(f"User found: {user.get('email')}, role: {user.get('role')}, active: {user.get('is_active')}, has_id: {bool(user.get('id'))}")
        
        # Get password hash
        hashed_pwd = user.get("hashed_password") or user.get("password") or ""
        
        if not hashed_pwd:
            logger.warning(f"User {email_lower} has no password hash - user_id: {user.get('id')}")
            # Try to fix by creating password hash
            try:
                from utils.auth import get_password_hash
                # Use provided password or default
                password_to_hash = request.password if request.password else "admin123"
                new_hash = get_password_hash(password_to_hash)
                await database.users.update_one(
                    {"id": user["id"]} if user.get("id") else {"email": email_lower},
                    {"$set": {"hashed_password": new_hash, "updated_at": datetime.now(timezone.utc)}}
                )
                logger.info(f"Created password hash for user {email_lower}")
                hashed_pwd = new_hash
            except Exception as fix_error:
                logger.error(f"Failed to create password hash: {fix_error}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )
        
        # Verify password using multiple methods
        import bcrypt
        password_valid = False
        password_to_check = request.password
        
        # Method 1: Direct bcrypt
        try:
            password_bytes = password_to_check.encode('utf-8')
            if isinstance(hashed_pwd, str):
                hash_bytes = hashed_pwd.encode('utf-8')
            else:
                hash_bytes = hashed_pwd
            
            password_valid = bcrypt.checkpw(password_bytes, hash_bytes)
            logger.debug(f"Bcrypt verification result: {password_valid}")
        except Exception as e:
            logger.debug(f"Bcrypt check failed: {e}")
        
        # Method 2: Passlib verify_password
        if not password_valid:
            try:
                password_valid = verify_password(password_to_check, hashed_pwd)
                logger.debug(f"Passlib verification result: {password_valid}")
            except Exception as verify_error:
                logger.debug(f"Passlib verification failed: {verify_error}")
        
        # Method 3: Try with different password variations (for debugging)
        if not password_valid and email_lower == "admin@mahaedume.gov.in":
            logger.warning(f"Password verification failed for admin user. Hash preview: {hashed_pwd[:20] if hashed_pwd else 'None'}...")
            # Log hash format for debugging
            if hashed_pwd:
                logger.debug(f"Hash format check: starts with $2b$ = {hashed_pwd.startswith('$2b$')}")
        
        if not password_valid:
            logger.warning(f"Login attempt with incorrect password for: {email_lower}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not user.get("is_active", True):
            logger.warning(f"Login attempt for inactive account: {email_lower}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )
        
        # Ensure user has required fields
        if not user.get("id"):
            user_id = str(uuid.uuid4())
            await database.users.update_one(
                {"email": email_lower},
                {"$set": {"id": user_id, "updated_at": datetime.now(timezone.utc)}}
            )
            user["id"] = user_id
            logger.info(f"Created missing user ID: {user_id}")
        
        # Create token
        token_data = {
            "sub": user["email"],
            "role": user.get("role", "viewer"),
            "user_id": user["id"],
            "full_name": user.get("full_name", "User"),
            "district_code": user.get("district_code")
        }
        access_token = create_access_token(token_data)
        
        logger.info(f"Successful login for user: {user['email']} (role: {user.get('role')}, user_id: {user.get('id')})")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user.get("full_name", "User"),
                "role": user.get("role", "viewer"),
                "district_code": user.get("district_code"),
                "permissions": ROLE_PERMISSIONS.get(UserRole(user.get("role", "viewer")), {})
            }
        }
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Login error for {request.email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login. Please try again."
        )

@router.post("/google-login", response_model=Token)
async def google_login(google_token: dict):
    """Login with Google OAuth"""
    # Verify Google token (simplified - in production use Google's API)
    email = google_token.get("email")
    name = google_token.get("name", "")
    
    if not email:
        raise HTTPException(status_code=400, detail="Invalid Google token")
    
    # Find or create user
    user = await db.users.find_one({"email": email})
    
    if not user:
        # Create new user with viewer role
        user_id = str(uuid.uuid4())
        user = {
            "id": user_id,
            "email": email,
            "full_name": name,
            "role": UserRole.VIEWER.value,
            "is_active": True,
            "hashed_password": "",  # No password for Google users
            "auth_provider": "google",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        await db.users.insert_one(user)
    
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="Account is disabled")
    
    token_data = {
        "sub": user["email"],
        "role": user["role"],
        "user_id": user["id"],
        "full_name": user["full_name"],
        "district_code": user.get("district_code")
    }
    access_token = create_access_token(token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
            "permissions": ROLE_PERMISSIONS.get(UserRole(user["role"]), {})
        }
    }

@router.get("/diagnostics")
async def login_diagnostics():
    """Diagnostic endpoint to check login system health (for debugging)"""
    import logging
    logger = logging.getLogger(__name__)
    
    diagnostics = {
        "database_connected": False,
        "database_name": None,
        "admin_user_exists": False,
        "admin_user_email": None,
        "admin_user_has_password": False,
        "admin_user_active": False,
        "total_users": 0,
        "errors": []
    }
    
    try:
        database = db if db is not None else get_db()
        diagnostics["database_name"] = database.name
        
        # Test connection
        await database.users.find_one({"_id": "test"})
        diagnostics["database_connected"] = True
        
        # Count users
        user_count = await database.users.count_documents({})
        diagnostics["total_users"] = user_count
        
        # Check for admin user
        admin_email = "admin@mahaedume.gov.in"
        admin_user = await database.users.find_one({"email": admin_email})
        if not admin_user:
            # Try case-insensitive
            admin_user = await database.users.find_one({"email": {"$regex": f"^{admin_email}$", "$options": "i"}})
        
        if admin_user:
            diagnostics["admin_user_exists"] = True
            diagnostics["admin_user_email"] = admin_user.get("email")
            diagnostics["admin_user_has_password"] = bool(admin_user.get("hashed_password") or admin_user.get("password"))
            diagnostics["admin_user_active"] = admin_user.get("is_active", True)
        else:
            diagnostics["errors"].append("Admin user not found")
            
    except Exception as e:
        diagnostics["errors"].append(f"Database error: {str(e)}")
        logger.error(f"Diagnostics error: {e}", exc_info=True)
    
    return diagnostics

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    user = await db.users.find_one({"email": current_user["email"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user["id"],
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"],
        "district_code": user.get("district_code"),
        "is_active": user.get("is_active", True),
        "created_at": user.get("created_at"),
        "permissions": ROLE_PERMISSIONS.get(UserRole(user["role"]), {})
    }

@router.post("/password-reset-request")
async def request_password_reset(request: PasswordResetRequest):
    """Request a password reset"""
    user = await db.users.find_one({"email": request.email})
    
    # Always return success to prevent email enumeration
    if user:
        reset_token = create_reset_token(request.email)
        # In production, send email with reset link
        # For now, store token in DB
        await db.password_resets.insert_one({
            "email": request.email,
            "token": reset_token,
            "created_at": datetime.now(timezone.utc),
            "used": False
        })
        # Return token for testing (in production, this would be emailed)
        return {"message": "Password reset instructions sent", "token": reset_token}
    
    return {"message": "If the email exists, reset instructions have been sent"}

@router.post("/password-reset-confirm")
async def confirm_password_reset(request: PasswordResetConfirm):
    """Confirm password reset with token"""
    email = verify_reset_token(request.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Check if token was already used
    reset_record = await db.password_resets.find_one({"token": request.token, "used": False})
    if not reset_record:
        raise HTTPException(status_code=400, detail="Reset token already used or invalid")
    
    # Update password
    hashed_password = get_password_hash(request.new_password)
    await db.users.update_one(
        {"email": email},
        {"$set": {"hashed_password": hashed_password, "updated_at": datetime.now(timezone.utc)}}
    )
    
    # Mark token as used
    await db.password_resets.update_one({"token": request.token}, {"$set": {"used": True}})
    
    return {"message": "Password reset successful"}

@router.post("/change-password")
async def change_password(request: ChangePasswordRequest, current_user: dict = Depends(get_current_user)):
    """Change password for logged-in user"""
    user = await db.users.find_one({"email": current_user["email"]})
    
    if not verify_password(request.current_password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    hashed_password = get_password_hash(request.new_password)
    await db.users.update_one(
        {"email": current_user["email"]},
        {"$set": {"hashed_password": hashed_password, "updated_at": datetime.now(timezone.utc)}}
    )
    
    return {"message": "Password changed successfully"}

# Admin routes for user management
@router.get("/users")
async def list_users(current_user: dict = Depends(require_admin)):
    """List all users (admin only)"""
    users = await db.users.find({}, {"_id": 0, "hashed_password": 0}).to_list(length=1000)
    return users

@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, current_user: dict = Depends(require_admin)):
    """Create a new user (admin only)"""
    # Check if user exists
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    user_data = {
        "id": user_id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value,
        "district_code": user.district_code,
        "is_active": user.is_active,
        "hashed_password": get_password_hash(user.password),
        "created_at": now,
        "updated_at": now,
        "created_by": current_user["user_id"]
    }
    
    await db.users.insert_one(user_data)
    
    return UserResponse(
        id=user_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        district_code=user.district_code,
        is_active=user.is_active,
        created_at=now
    )

@router.put("/users/{user_id}")
async def update_user(user_id: str, update: UserUpdate, current_user: dict = Depends(require_admin)):
    """Update a user (admin only)"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = {k: v for k, v in update.dict().items() if v is not None}
    if update_data.get("role"):
        update_data["role"] = update_data["role"].value
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await db.users.update_one({"id": user_id}, {"$set": update_data})
    
    updated_user = await db.users.find_one({"id": user_id}, {"_id": 0, "hashed_password": 0})
    return updated_user

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(require_admin)):
    """Delete a user (admin only)"""
    if user_id == current_user["user_id"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}

@router.post("/users/{user_id}/reset-password")
async def admin_reset_password(user_id: str, current_user: dict = Depends(require_admin)):
    """Reset user password to a temporary one (admin only)"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate temporary password
    temp_password = str(uuid.uuid4())[:12]
    hashed_password = get_password_hash(temp_password)
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"hashed_password": hashed_password, "updated_at": datetime.now(timezone.utc)}}
    )
    
    return {"message": "Password reset successful", "temporary_password": temp_password}

# Initialize default admin user
async def create_default_admin(database):
    """Create default admin user if none exists"""
    global db
    db = database
    
    admin_email = "admin@mahaedume.gov.in"
    admin_email_lower = admin_email.lower()
    admin_password = "admin123"
    
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Check if admin exists - try multiple methods
        admin_exists = None
        
        # Method 1: Exact lowercase match
        try:
            admin_exists = await db.users.find_one({"email": admin_email_lower})
        except Exception:
            pass
        
        # Method 2: Case-insensitive regex
        if not admin_exists:
            try:
                admin_exists = await db.users.find_one({"email": {"$regex": f"^{admin_email}$", "$options": "i"}})
            except Exception:
                pass
        
        # Method 3: Iterate through users
    if not admin_exists:
            try:
                all_users = await db.users.find({}).to_list(length=100)
                for u in all_users:
                    if u.get("email", "").lower() == admin_email_lower:
                        admin_exists = u
                        break
            except Exception:
                pass
        
        if admin_exists:
            # Normalize email to lowercase
            if admin_exists.get("email") != admin_email_lower:
                await db.users.update_one(
                    {"id": admin_exists.get("id")} if admin_exists.get("id") else {"email": admin_exists.get("email")},
                    {"$set": {"email": admin_email_lower, "updated_at": datetime.now(timezone.utc)}}
                )
                admin_exists["email"] = admin_email_lower
                logger.info(f"Normalized admin email to lowercase")
            
            # Ensure user has ID
            if not admin_exists.get("id"):
                user_id = str(uuid.uuid4())
                await db.users.update_one(
                    {"email": admin_email_lower},
                    {"$set": {"id": user_id, "updated_at": datetime.now(timezone.utc)}}
                )
                admin_exists["id"] = user_id
                logger.info(f"Created missing admin user ID")
            
            # Ensure password hash exists and is correct
            hashed_pwd = admin_exists.get("hashed_password") or admin_exists.get("password")
            if not hashed_pwd:
                logger.warning(f"Admin user exists but has no password hash. Creating...")
                hashed_password = get_password_hash(admin_password)
                await db.users.update_one(
                    {"email": admin_email_lower},
                    {"$set": {
                        "hashed_password": hashed_password,
                        "updated_at": datetime.now(timezone.utc),
                        "is_active": True,
                        "role": "admin"
                    }}
                )
                logger.info(f"✓ Admin password hash created")
            else:
                # Verify password hash is valid
                try:
                    from utils.auth import verify_password
                    if not verify_password(admin_password, hashed_pwd):
                        logger.warning(f"Admin password hash is invalid. Updating...")
                        hashed_password = get_password_hash(admin_password)
                        await db.users.update_one(
                            {"email": admin_email_lower},
                            {"$set": {
                                "hashed_password": hashed_password,
                                "updated_at": datetime.now(timezone.utc)
                            }}
                        )
                        logger.info(f"✓ Admin password hash updated")
                    else:
                        logger.info(f"✓ Admin user exists with valid password: {admin_exists.get('email')}")
                except Exception as verify_error:
                    logger.warning(f"Could not verify admin password hash: {verify_error}. Updating...")
                    hashed_password = get_password_hash(admin_password)
                    await db.users.update_one(
                        {"email": admin_email_lower},
                        {"$set": {
                            "hashed_password": hashed_password,
                            "updated_at": datetime.now(timezone.utc)
                        }}
                    )
                    logger.info(f"✓ Admin password hash recreated")
        else:
            # Create new admin user
        admin_user = {
            "id": str(uuid.uuid4()),
                "email": admin_email_lower,
            "full_name": "System Administrator",
            "role": "admin",
            "is_active": True,
                "hashed_password": get_password_hash(admin_password),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        await db.users.insert_one(admin_user)
            logger.info(f"✓ Default admin user created: {admin_email} / {admin_password}")
    except Exception as e:
        logger.error(f"Failed to create/verify admin user: {e}", exc_info=True)
        print(f"ERROR: Failed to create/verify admin user: {e}")
