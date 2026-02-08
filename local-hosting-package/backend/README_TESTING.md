# Quick Start Testing Guide

## Prerequisites Check

Run the requirements checker:
```bash
python check_test_requirements.py
```

## Setup Test Environment

### Option 1: Automated Setup (Recommended)
```bash
./setup_test_env.sh
```

### Option 2: Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Ensure MongoDB is running
# Using Docker:
docker-compose up -d mongodb

# Or locally:
mongod --dbpath /path/to/data
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Smoke tests (quick checks)
pytest -m smoke

# API tests
pytest -m api

# Unit tests
pytest -m unit

# Security tests
pytest -m security

# All except slow tests
pytest -m "not slow"
```

### Run Specific Test Files
```bash
pytest tests/test_health.py
pytest tests/test_auth.py
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html
```

## Using Test Runner Script
```bash
./run_tests.sh
```

## Troubleshooting

### MongoDB Not Running
```bash
# Check if MongoDB is running
docker ps | grep mongo
# OR
ps aux | grep mongod

# Start MongoDB
docker-compose up -d mongodb
```

### Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Test Database Issues
```bash
# Manually drop test database if needed
mongosh test_maharashtra_edu --eval "db.dropDatabase()"
```

## Test Structure

- `tests/test_health.py` - Basic health checks
- `tests/test_auth.py` - Authentication tests
- `tests/test_api_endpoints.py` - API endpoint tests
- `tests/test_comprehensive_endpoints.py` - Comprehensive API tests
- `tests/test_security.py` - Security tests
- `tests/test_database.py` - Database tests
- `tests/test_integration.py` - Integration tests
- `tests/test_validation.py` - Validation tests
- `tests/test_performance.py` - Performance tests
- `tests/test_regression.py` - Regression tests
- `tests/test_scope_utils.py` - Unit tests

## For More Details

See [TESTING.md](TESTING.md) for comprehensive testing documentation.

