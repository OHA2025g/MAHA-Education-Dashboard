#!/bin/bash
# Comprehensive Test Runner Script

set -e

echo "=========================================="
echo "Pune School Dashboard - Test Suite"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if MongoDB is running
echo "Checking MongoDB connection..."
if ! python -c "from motor.motor_asyncio import AsyncIOMotorClient; import asyncio; asyncio.run(AsyncIOMotorClient('mongodb://localhost:27017').admin.command('ping'))" 2>/dev/null; then
    echo -e "${YELLOW}Warning: MongoDB might not be running. Tests may fail.${NC}"
    echo "Start MongoDB with: docker-compose up -d mongodb"
    echo ""
fi

# Test categories
TESTS_PASSED=0
TESTS_FAILED=0

run_test_category() {
    local category=$1
    local marker=$2
    local description=$3
    
    echo ""
    echo -e "${YELLOW}Running $description...${NC}"
    echo "----------------------------------------"
    
    if pytest -m "$marker" -v --tb=short 2>&1 | tee /tmp/test_${category}.log; then
        echo -e "${GREEN}✓ $description: PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ $description: FAILED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# 1. Smoke/Sanity Tests
run_test_category "smoke" "smoke" "Smoke/Sanity Tests"

# 2. Unit Tests
run_test_category "unit" "unit" "Unit Tests"

# 3. API/Functional Tests
run_test_category "api" "api" "API/Functional Tests"

# 4. Integration Tests
run_test_category "integration" "integration" "Integration Tests"

# 5. Security Tests
run_test_category "security" "security" "Security Tests"

# 6. Database Tests
run_test_category "database" "database" "Database Tests"

# 7. Validation Tests
run_test_category "validation" "validation" "Validation/Boundary Tests"

# 8. Regression Tests
run_test_category "regression" "regression" "Regression Tests"

# 9. Performance Tests (optional, can be slow)
echo ""
read -p "Run performance tests? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    run_test_category "performance" "performance" "Performance Tests"
fi

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Check logs above.${NC}"
    exit 1
fi
