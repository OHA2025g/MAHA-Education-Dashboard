# Testing Guide

This document provides comprehensive information about testing the Pune School Dashboard backend.

## Test Categories

The test suite includes the following categories:

### 1. Smoke/Sanity Tests (`test_health.py`)
- Quick checks to ensure basic functionality
- Health endpoints
- Root API endpoint

### 2. Unit Tests (`test_scope_utils.py`, `test_auth.py`)
- Individual function testing
- Utility functions
- Authentication utilities

### 3. API/Functional Tests (`test_api_endpoints.py`, `test_comprehensive_endpoints.py`)
- All API endpoints
- Request/response validation
- Status code verification
- Data format validation

### 4. Integration Tests (`test_integration.py`)
- Service interactions
- Data flow through system
- Cross-service communication

### 5. Security Tests (`test_security.py`)
- Authentication
- Authorization
- Input validation
- SQL injection prevention
- XSS prevention

### 6. Database Tests (`test_database.py`)
- Data consistency
- Data integrity
- Connection handling
- Query operations

### 7. Validation/Boundary Tests (`test_validation.py`)
- Input validation
- Boundary conditions
- Edge cases
- Error handling

### 8. Performance Tests (`test_performance.py`)
- Response times
- Concurrent request handling
- Load testing
- Large dataset handling

### 9. Regression Tests (`test_regression.py`)
- Backward compatibility
- Existing feature verification
- Breaking change detection

## Running Tests

### Prerequisites

1. **MongoDB**: Must be running (local or Docker)
   ```bash
   # Using Docker
   docker-compose up -d mongodb
   
   # Or local MongoDB
   mongod --dbpath /path/to/data
   ```

2. **Python Environment**: Use virtual environment
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Running All Tests

```bash
cd backend
pytest
```

### Running Specific Test Categories

```bash
# Smoke tests
pytest -m smoke

# API tests
pytest -m api

# Unit tests
pytest -m unit

# Integration tests
pytest -m integration

# Security tests
pytest -m security

# Database tests
pytest -m database

# Validation tests
pytest -m validation

# Performance tests (can be slow)
pytest -m performance

# Regression tests
pytest -m regression
```

### Running Specific Test Files

```bash
# Health tests
pytest tests/test_health.py

# Auth tests
pytest tests/test_auth.py

# API endpoint tests
pytest tests/test_api_endpoints.py
```

### Running with Verbose Output

```bash
pytest -v
```

### Running with Coverage (if pytest-cov installed)

```bash
pytest --cov=. --cov-report=html
```

### Using the Test Runner Script

```bash
cd backend
chmod +x run_tests.sh
./run_tests.sh
```

## Test Configuration

Tests use a separate test database (`test_maharashtra_edu`) to avoid affecting production data.

Environment variables:
- `TEST_MONGO_URL`: MongoDB connection string (default: `mongodb://localhost:27017`)
- `TEST_DB_NAME`: Test database name (default: `test_maharashtra_edu`)

## Test Fixtures

### `test_db`
- Session-scoped database connection
- Automatically drops test database after tests

### `clean_db`
- Function-scoped clean database
- Cleans all collections before each test

### `test_client`
- Async HTTP client for API testing
- Configured with test database

### `admin_user`
- Creates admin user for testing
- Email: `admin@test.com`
- Password: `admin123`

### `viewer_user`
- Creates viewer user for testing
- Email: `viewer@test.com`
- Password: `viewer123`

### `admin_token`
- JWT token for admin user
- For authenticated requests

### `viewer_token`
- JWT token for viewer user
- For authenticated requests

## Writing New Tests

### Example: API Endpoint Test

```python
@pytest.mark.api
@pytest.mark.asyncio
async def test_my_endpoint(test_client: AsyncClient, clean_db):
    """Test my endpoint"""
    # Setup test data
    await clean_db.my_collection.insert_one({
        "field": "value"
    })
    
    # Make request
    response = await test_client.get("/api/my-endpoint")
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "field" in data
```

### Example: Unit Test

```python
@pytest.mark.unit
def test_my_function():
    """Test my function"""
    result = my_function("input")
    assert result == "expected_output"
```

### Example: Security Test

```python
@pytest.mark.security
@pytest.mark.asyncio
async def test_unauthorized_access(test_client: AsyncClient):
    """Test unauthorized access is blocked"""
    response = await test_client.get("/api/protected-endpoint")
    assert response.status_code == 401
```

## Test Markers

Tests are marked with categories for easy filtering:

- `@pytest.mark.smoke` - Smoke/sanity tests
- `@pytest.mark.api` - API/functional tests
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.security` - Security tests
- `@pytest.mark.database` - Database tests
- `@pytest.mark.validation` - Validation tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.regression` - Regression tests
- `@pytest.mark.slow` - Slow-running tests

## Continuous Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    cd backend
    pip install -r requirements.txt
    pytest
```

## Troubleshooting

### MongoDB Connection Error
- Ensure MongoDB is running
- Check `TEST_MONGO_URL` environment variable
- Verify network connectivity

### Import Errors
- Ensure virtual environment is activated
- Install all dependencies: `pip install -r requirements.txt`

### Async Test Issues
- Ensure `pytest-asyncio` is installed
- Check `@pytest.mark.asyncio` decorator is present

### Test Database Not Cleaning
- Check MongoDB connection
- Verify test database name is correct
- Manually drop test database if needed: `mongosh test_maharashtra_edu --eval "db.dropDatabase()"`

## Test Coverage Goals

- **Unit Tests**: >80% coverage
- **API Tests**: All endpoints covered
- **Integration Tests**: Critical paths covered
- **Security Tests**: All authentication/authorization paths

## Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Always clean up test data
3. **Assertions**: Use specific assertions
4. **Naming**: Use descriptive test names
5. **Documentation**: Add docstrings to tests
6. **Speed**: Keep tests fast (< 1 second each)
7. **Reliability**: Tests should be deterministic

## Test Reports

After running tests, you can generate reports:

```bash
# HTML report
pytest --html=report.html

# JUnit XML (for CI)
pytest --junitxml=report.xml
```

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

