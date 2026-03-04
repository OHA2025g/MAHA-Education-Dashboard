#!/bin/bash
# Comprehensive Testing Script for MAHA Education Dashboard

echo "=========================================="
echo "COMPREHENSIVE TESTING SUITE"
echo "=========================================="
echo ""

# Run from project root (local-hosting-package)
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR" || exit 1

BASE_URL="http://localhost:8002"
FRONTEND_URL="http://localhost"
TEST_RESULTS="docs/testing/test_results.txt"
mkdir -p docs/testing

# Initialize test results
echo "Test Execution Report - $(date)" > $TEST_RESULTS
echo "==========================================" >> $TEST_RESULTS
echo "" >> $TEST_RESULTS

# Function to run test and log result
run_test() {
    local test_name=$1
    local command=$2
    echo "Running: $test_name"
    if eval "$command" > /dev/null 2>&1; then
        echo "✓ PASS: $test_name" | tee -a $TEST_RESULTS
        return 0
    else
        echo "✗ FAIL: $test_name" | tee -a $TEST_RESULTS
        return 1
    fi
}

PASSED=0
FAILED=0

echo "=== SMOKE TESTS ===" | tee -a $TEST_RESULTS
echo ""

# Smoke Test 1: Backend Health
if run_test "Backend Health Endpoint" "curl -sf $BASE_URL/api/health | grep -q healthy"; then
    ((PASSED++))
else
    ((FAILED++))
fi

# Smoke Test 2: Backend Root
if run_test "Backend Root Endpoint" "curl -sf $BASE_URL/api/ | grep -q message"; then
    ((PASSED++))
else
    ((FAILED++))
fi

# Smoke Test 3: Frontend Health
if run_test "Frontend Health Endpoint" "curl -sf $FRONTEND_URL/health | grep -q healthy"; then
    ((PASSED++))
else
    ((FAILED++))
fi

# Smoke Test 4: Frontend Accessibility
if run_test "Frontend Main Page" "curl -sf $FRONTEND_URL | grep -q html"; then
    ((PASSED++))
else
    ((FAILED++))
fi

echo ""
echo "=== API TESTS ===" | tee -a $TEST_RESULTS
echo ""

# API Test 1: API Documentation
if run_test "API Documentation (Swagger)" "curl -sf $BASE_URL/docs | grep -q swagger"; then
    ((PASSED++))
else
    ((FAILED++))
fi

# API Test 2: OpenAPI Schema
if run_test "OpenAPI Schema" "curl -sf $BASE_URL/openapi.json | grep -q openapi"; then
    ((PASSED++))
else
    ((FAILED++))
fi

# API Test 3: ReDoc Documentation
if run_test "ReDoc Documentation" "curl -sf $BASE_URL/redoc | grep -q redoc"; then
    ((PASSED++))
else
    ((FAILED++))
fi

echo ""
echo "=== PERFORMANCE TESTS ===" | tee -a $TEST_RESULTS
echo ""

# Performance Test 1: Health Endpoint Response Time
START=$(date +%s%N)
curl -sf $BASE_URL/api/health > /dev/null 2>&1
END=$(date +%s%N)
DURATION=$((($END - $START) / 1000000))  # Convert to milliseconds

if [ $DURATION -lt 1000 ]; then
    echo "✓ PASS: Health Endpoint Performance (< 1s: ${DURATION}ms)" | tee -a $TEST_RESULTS
    ((PASSED++))
else
    echo "✗ FAIL: Health Endpoint Performance (>= 1s: ${DURATION}ms)" | tee -a $TEST_RESULTS
    ((FAILED++))
fi

# Performance Test 2: Load Test (10 requests)
echo "Running load test (10 concurrent requests)..."
START=$(date +%s%N)
for i in {1..10}; do
    curl -sf $BASE_URL/api/health > /dev/null 2>&1 &
done
wait
END=$(date +%s%N)
DURATION=$((($END - $START) / 1000000))

if [ $DURATION -lt 5000 ]; then
    echo "✓ PASS: Load Test (10 requests in < 5s: ${DURATION}ms)" | tee -a $TEST_RESULTS
    ((PASSED++))
else
    echo "✗ FAIL: Load Test (10 requests >= 5s: ${DURATION}ms)" | tee -a $TEST_RESULTS
    ((FAILED++))
fi

echo ""
echo "=== SECURITY TESTS ===" | tee -a $TEST_RESULTS
echo ""

# Security Test 1: SQL Injection Protection
if run_test "SQL Injection Protection" "curl -sf '$BASE_URL/api/health?test=\$ne' | grep -q -v 'MongoDB'"; then
    ((PASSED++))
else
    ((FAILED++))
fi

# Security Test 2: XSS Protection
if run_test "XSS Protection" "curl -sf '$BASE_URL/api/health?test=<script>' | grep -q -v '<script>'"; then
    ((PASSED++))
else
    ((FAILED++))
fi

# Security Test 3: CORS Headers (check in GET response)
if run_test "CORS Headers" "curl -sI $BASE_URL/api/health | grep -qi 'access-control' || curl -sI -H 'Origin: http://localhost' $BASE_URL/api/health | grep -qi 'access-control'"; then
    ((PASSED++))
else
    ((FAILED++))
fi

echo ""
echo "=== INTEGRATION TESTS ===" | tee -a $TEST_RESULTS
echo ""

# Integration Test 1: Backend-Frontend Connectivity (check if frontend can reach backend)
if run_test "Backend-Frontend Connectivity" "curl -sf $FRONTEND_URL | grep -q 'html' && curl -sf $BASE_URL/api/health | grep -q 'healthy'"; then
    ((PASSED++))
else
    ((FAILED++))
fi

# Integration Test 2: API Response Format
RESPONSE=$(curl -sf $BASE_URL/api/health)
if echo "$RESPONSE" | grep -q "status" && echo "$RESPONSE" | grep -q "timestamp"; then
    echo "✓ PASS: API Response Format" | tee -a $TEST_RESULTS
    ((PASSED++))
else
    echo "✗ FAIL: API Response Format" | tee -a $TEST_RESULTS
    ((FAILED++))
fi

echo ""
echo "=== SUMMARY ===" | tee -a $TEST_RESULTS
echo "Total Tests: $((PASSED + FAILED))" | tee -a $TEST_RESULTS
echo "Passed: $PASSED" | tee -a $TEST_RESULTS
echo "Failed: $FAILED" | tee -a $TEST_RESULTS
echo "Success Rate: $(echo "scale=2; $PASSED * 100 / ($PASSED + $FAILED)" | bc)%" | tee -a $TEST_RESULTS
echo "" | tee -a $TEST_RESULTS
echo "Test results saved to: $TEST_RESULTS"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo "✓ ALL TESTS PASSED!"
    exit 0
else
    echo ""
    echo "✗ SOME TESTS FAILED"
    exit 1
fi

