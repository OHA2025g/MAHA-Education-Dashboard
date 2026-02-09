# Testing Documentation

This directory contains all testing-related documentation for the Pune School Dashboard backend.

## 📋 Available Documentation

### Quick Start
- **[QUICK_START_TESTING.md](./QUICK_START_TESTING.md)** - Get started with testing in 5 minutes

### Main Guides
- **[TESTING.md](./TESTING.md)** - Complete testing overview and guide
- **[README_TESTING.md](./README_TESTING.md)** - Testing documentation index

### Test Results
- **[TEST_RESULTS_SUMMARY.md](./TEST_RESULTS_SUMMARY.md)** - Summary of all test results
- **[TEST_EXECUTION_REPORT_FINAL.md](./TEST_EXECUTION_REPORT_FINAL.md)** - Final test execution report
- **[TEST_EXECUTION_REPORT.md](./TEST_EXECUTION_REPORT.md)** - Detailed test execution report

### Setup & Configuration
- **[TEST_SETUP_COMPLETE.md](./TEST_SETUP_COMPLETE.md)** - Test environment setup guide
- **[VENV_SETUP_COMPLETE.md](./VENV_SETUP_COMPLETE.md)** - Virtual environment setup

### Testing Resources
- **[TESTING_LINKS.md](./TESTING_LINKS.md)** - API testing endpoints reference
- **[TESTING_LINKS_ACTIVE.md](./TESTING_LINKS_ACTIVE.md)** - Active testing links
- **[ACTIVE_TESTING_LINKS.txt](./ACTIVE_TESTING_LINKS.txt)** - Current testing URLs

### Fixes & Issues
- **[FIXES_APPLIED.md](./FIXES_APPLIED.md)** - Test fixes and resolutions

## 🚀 Quick Start

```bash
# Navigate to backend directory
cd ../../backend

# Run all tests
pytest

# Run specific test category
pytest -m smoke
pytest -m api
pytest -m security

# Generate coverage report
pytest --cov=. --cov-report=html
```

## 📊 Test Categories

- **Smoke/Sanity**: Basic health checks
- **Unit**: Individual function testing
- **API**: Endpoint testing
- **Integration**: Service interaction testing
- **Performance**: Load and stress testing
- **Security**: Authentication and authorization
- **Database**: Data consistency and integrity
- **Validation**: Input validation and boundary testing
- **Regression**: Backward compatibility

## 📚 Related Documentation

- [Main README](../../README.md)
- [Deployment Documentation](../deployment/README.md)
- [Project Structure](../../PROJECT_STRUCTURE.md)

