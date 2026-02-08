#!/usr/bin/env python3
"""Check if all requirements for testing are met"""
import sys
import subprocess
import os

def check_command(command, name):
    """Check if a command exists"""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        print(f"✓ {name} is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"✗ {name} is NOT installed")
        return False

def check_python_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
        print(f"✓ {package_name} is installed")
        return True
    except ImportError:
        print(f"✗ {package_name} is NOT installed")
        return False

def check_mongodb():
    """Check if MongoDB is accessible"""
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        import asyncio
        
        async def check():
            try:
                client = AsyncIOMotorClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
                await client.admin.command('ping')
                client.close()
                return True
            except Exception:
                return False
        
        if asyncio.run(check()):
            print("✓ MongoDB is running and accessible")
            return True
        else:
            print("✗ MongoDB is NOT accessible (may not be running)")
            return False
    except ImportError:
        print("✗ motor package not installed (cannot check MongoDB)")
        return False

def main():
    print("=" * 50)
    print("Checking Test Requirements")
    print("=" * 50)
    print()
    
    all_ok = True
    
    # Check Python
    print("Python:")
    python_version = sys.version_info
    print(f"  Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 9):
        print("  ✗ Python 3.9+ required")
        all_ok = False
    else:
        print("  ✓ Python version OK")
    print()
    
    # Check commands
    print("Commands:")
    check_command("pytest", "pytest")
    print()
    
    # Check Python packages
    print("Python Packages:")
    packages = [
        ("pytest", "pytest"),
        ("pytest-asyncio", "pytest_asyncio"),
        ("httpx", "httpx"),
        ("motor", "motor"),
        ("fastapi", "fastapi"),
        ("pymongo", "pymongo"),
    ]
    
    for package, import_name in packages:
        if not check_python_package(package, import_name):
            all_ok = False
    print()
    
    # Check MongoDB
    print("MongoDB:")
    if not check_mongodb():
        all_ok = False
    print()
    
    # Check environment variables
    print("Environment Variables:")
    test_mongo_url = os.environ.get("TEST_MONGO_URL", "mongodb://localhost:27017")
    test_db_name = os.environ.get("TEST_DB_NAME", "test_maharashtra_edu")
    print(f"  TEST_MONGO_URL: {test_mongo_url}")
    print(f"  TEST_DB_NAME: {test_db_name}")
    print()
    
    # Check directories
    print("Directories:")
    dirs = ["tests", "uploads"]
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"  ✓ {dir_name}/ exists")
        else:
            print(f"  ✗ {dir_name}/ does NOT exist")
            all_ok = False
    print()
    
    print("=" * 50)
    if all_ok:
        print("✓ All requirements met! Ready to run tests.")
        return 0
    else:
        print("✗ Some requirements are missing. Please install them.")
        print()
        print("To install missing packages:")
        print("  pip install -r requirements.txt")
        print()
        print("To start MongoDB:")
        print("  docker-compose up -d mongodb")
        print("  OR")
        print("  mongod --dbpath /path/to/data")
        return 1

if __name__ == "__main__":
    sys.exit(main())

