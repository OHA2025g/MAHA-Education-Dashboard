#!/usr/bin/env python3
"""
Comprehensive Test Suite
Covers all testing types: Functional, Non-Functional, Unit, Integration, System, etc.
"""
import asyncio
import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Test configuration
BASE_URL = "http://localhost:8002"
FRONTEND_URL = "http://localhost"
TEST_RESULTS = []


class TestResult:
    def __init__(self, category: str, test_name: str, passed: bool, 
                 message: str = "", duration: float = 0):
        self.category = category
        self.test_name = test_name
        self.passed = passed
        self.message = message
        self.duration = duration
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "category": self.category,
            "test_name": self.test_name,
            "passed": self.passed,
            "message": self.message,
            "duration": self.duration,
            "timestamp": self.timestamp
        }


def log_test(category: str, test_name: str, passed: bool, message: str = "", duration: float = 0):
    """Log test result"""
    result = TestResult(category, test_name, passed, message, duration)
    TEST_RESULTS.append(result)
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: [{category}] {test_name}")
    if message:
        print(f"         {message}")
    return result


# ============= SMOKE TESTING =============

async def test_smoke_backend_health():
    """Smoke Test: Backend health endpoint"""
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/api/health")
            duration = time.time() - start
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    log_test("Smoke", "Backend Health", True, 
                            f"Response: {data.get('status')}", duration)
                    return True
            log_test("Smoke", "Backend Health", False, 
                    f"Status: {response.status_code}", duration)
            return False
    except Exception as e:
        duration = time.time() - start
        log_test("Smoke", "Backend Health", False, str(e), duration)
        return False


async def test_smoke_frontend_health():
    """Smoke Test: Frontend health endpoint"""
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{FRONTEND_URL}/health")
            duration = time.time() - start
            if response.status_code == 200:
                log_test("Smoke", "Frontend Health", True, "", duration)
                return True
            log_test("Smoke", "Frontend Health", False, 
                    f"Status: {response.status_code}", duration)
            return False
    except Exception as e:
        duration = time.time() - start
        log_test("Smoke", "Frontend Health", False, str(e), duration)
        return False


async def test_smoke_backend_root():
    """Smoke Test: Backend root endpoint"""
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/api/")
            duration = time.time() - start
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "version" in data:
                    log_test("Smoke", "Backend Root", True, "", duration)
                    return True
            log_test("Smoke", "Backend Root", False, 
                    f"Status: {response.status_code}", duration)
            return False
    except Exception as e:
        duration = time.time() - start
        log_test("Smoke", "Backend Root", False, str(e), duration)
        return False


# ============= FUNCTIONAL TESTING =============

async def test_functional_api_endpoints():
    """Functional Test: API endpoints return correct structure"""
    start = time.time()
    endpoints = [
        ("/api/health", {"status", "timestamp"}),
        ("/api/", {"message", "version"}),
    ]
    
    passed = 0
    failed = 0
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint, expected_keys in endpoints:
            try:
                response = await client.get(f"{BASE_URL}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    if all(key in data for key in expected_keys):
                        passed += 1
                    else:
                        failed += 1
                else:
                    failed += 1
            except Exception:
                failed += 1
    
    duration = time.time() - start
    success = failed == 0
    log_test("Functional", "API Endpoints Structure", success, 
            f"Passed: {passed}, Failed: {failed}", duration)
    return success


async def test_functional_api_docs():
    """Functional Test: API documentation accessible"""
    start = time.time()
    endpoints = ["/docs", "/redoc", "/openapi.json"]
    passed = 0
    failed = 0
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint in endpoints:
            try:
                response = await client.get(f"{BASE_URL}{endpoint}")
                if response.status_code == 200:
                    passed += 1
                else:
                    failed += 1
            except Exception:
                failed += 1
    
    duration = time.time() - start
    success = failed == 0
    log_test("Functional", "API Documentation", success, 
            f"Passed: {passed}, Failed: {failed}", duration)
    return success


# ============= INTEGRATION TESTING =============

async def test_integration_backend_frontend():
    """Integration Test: Backend and Frontend connectivity"""
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test backend
            backend_response = await client.get(f"{BASE_URL}/api/health")
            # Test frontend
            frontend_response = await client.get(f"{FRONTEND_URL}/health")
            
            duration = time.time() - start
            if backend_response.status_code == 200 and frontend_response.status_code == 200:
                log_test("Integration", "Backend-Frontend Connectivity", True, "", duration)
                return True
            log_test("Integration", "Backend-Frontend Connectivity", False, 
                    f"Backend: {backend_response.status_code}, Frontend: {frontend_response.status_code}", 
                    duration)
            return False
    except Exception as e:
        duration = time.time() - start
        log_test("Integration", "Backend-Frontend Connectivity", False, str(e), duration)
        return False


async def test_integration_api_response_format():
    """Integration Test: API response format consistency"""
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/api/health")
            duration = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    log_test("Integration", "API Response Format", True, "", duration)
                    return True
            log_test("Integration", "API Response Format", False, 
                    "Response is not valid JSON object", duration)
            return False
    except Exception as e:
        duration = time.time() - start
        log_test("Integration", "API Response Format", False, str(e), duration)
        return False


# ============= SYSTEM TESTING =============

async def test_system_end_to_end():
    """System Test: End-to-end system functionality"""
    start = time.time()
    steps_passed = 0
    steps_total = 3
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Step 1: Backend health
            response = await client.get(f"{BASE_URL}/api/health")
            if response.status_code == 200:
                steps_passed += 1
            
            # Step 2: Frontend health
            response = await client.get(f"{FRONTEND_URL}/health")
            if response.status_code == 200:
                steps_passed += 1
            
            # Step 3: API root
            response = await client.get(f"{BASE_URL}/api/")
            if response.status_code == 200:
                steps_passed += 1
        
        duration = time.time() - start
        success = steps_passed == steps_total
        log_test("System", "End-to-End Functionality", success, 
                f"Steps passed: {steps_passed}/{steps_total}", duration)
        return success
    except Exception as e:
        duration = time.time() - start
        log_test("System", "End-to-End Functionality", False, str(e), duration)
        return False


# ============= PERFORMANCE TESTING =============

async def test_performance_response_time():
    """Performance Test: Response time"""
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            request_start = time.time()
            response = await client.get(f"{BASE_URL}/api/health")
            request_duration = time.time() - request_start
        
        duration = time.time() - start
        if request_duration < 1.0:  # Should respond in under 1 second
            log_test("Performance", "Response Time", True, 
                    f"Response time: {request_duration*1000:.2f}ms", duration)
            return True
        else:
            log_test("Performance", "Response Time", False, 
                    f"Response time too slow: {request_duration*1000:.2f}ms", duration)
            return False
    except Exception as e:
        duration = time.time() - start
        log_test("Performance", "Response Time", False, str(e), duration)
        return False


async def test_performance_load():
    """Performance Test: Load testing (10 concurrent requests)"""
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            tasks = [client.get(f"{BASE_URL}/api/health") for _ in range(10)]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful = sum(1 for r in responses if not isinstance(r, Exception) and r.status_code == 200)
        duration = time.time() - start
        
        if successful == 10 and duration < 5.0:
            log_test("Performance", "Load Test (10 requests)", True, 
                    f"All {successful} requests successful in {duration*1000:.2f}ms", duration)
            return True
        else:
            log_test("Performance", "Load Test (10 requests)", False, 
                    f"Only {successful}/10 successful in {duration*1000:.2f}ms", duration)
            return False
    except Exception as e:
        duration = time.time() - start
        log_test("Performance", "Load Test (10 requests)", False, str(e), duration)
        return False


# ============= SECURITY TESTING =============

async def test_security_sql_injection():
    """Security Test: SQL/MongoDB injection protection"""
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try MongoDB injection
            response = await client.get(f"{BASE_URL}/api/health", 
                                       params={"test": {"$ne": "test"}})
            duration = time.time() - start
            
            # Should not crash or expose internal errors
            if response.status_code in [200, 400, 422]:
                log_test("Security", "Injection Protection", True, "", duration)
                return True
            log_test("Security", "Injection Protection", False, 
                    f"Unexpected status: {response.status_code}", duration)
            return False
    except Exception as e:
        duration = time.time() - start
        log_test("Security", "Injection Protection", False, str(e), duration)
        return False


async def test_security_xss():
    """Security Test: XSS protection"""
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/api/health", 
                                       params={"test": "<script>alert('xss')</script>"})
            duration = time.time() - start
            
            # Check response doesn't contain script tags
            content = response.text
            if "<script>" not in content.lower():
                log_test("Security", "XSS Protection", True, "", duration)
                return True
            log_test("Security", "XSS Protection", False, "Script tags found in response", duration)
            return False
    except Exception as e:
        duration = time.time() - start
        log_test("Security", "XSS Protection", False, str(e), duration)
        return False


async def test_security_cors():
    """Security Test: CORS headers"""
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/api/health", 
                                       headers={"Origin": "https://school_dashboard.demo.agrayianailabs.com"})
            duration = time.time() - start
            
            headers = dict(response.headers)
            if "access-control-allow-origin" in str(headers).lower():
                log_test("Security", "CORS Headers", True, "", duration)
                return True
            log_test("Security", "CORS Headers", False, "CORS headers not found", duration)
            return False
    except Exception as e:
        duration = time.time() - start
        log_test("Security", "CORS Headers", False, str(e), duration)
        return False


# ============= REGRESSION TESTING =============

async def test_regression_existing_endpoints():
    """Regression Test: Existing endpoints still work"""
    start = time.time()
    endpoints = ["/api/health", "/api/", "/docs", "/redoc"]
    passed = 0
    failed = 0
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for endpoint in endpoints:
            try:
                response = await client.get(f"{BASE_URL}{endpoint}")
                if response.status_code == 200:
                    passed += 1
                else:
                    failed += 1
            except Exception:
                failed += 1
    
    duration = time.time() - start
    success = failed == 0
    log_test("Regression", "Existing Endpoints", success, 
            f"Passed: {passed}, Failed: {failed}", duration)
    return success


# ============= MAIN TEST RUNNER =============

async def run_all_tests():
    """Run all test suites"""
    print("=" * 60)
    print("COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"Started at: {datetime.now().isoformat()}")
    print("=" * 60)
    print()
    
    # Smoke Tests
    print("=== SMOKE TESTING ===")
    await test_smoke_backend_health()
    await test_smoke_frontend_health()
    await test_smoke_backend_root()
    print()
    
    # Functional Tests
    print("=== FUNCTIONAL TESTING ===")
    await test_functional_api_endpoints()
    await test_functional_api_docs()
    print()
    
    # Integration Tests
    print("=== INTEGRATION TESTING ===")
    await test_integration_backend_frontend()
    await test_integration_api_response_format()
    print()
    
    # System Tests
    print("=== SYSTEM TESTING ===")
    await test_system_end_to_end()
    print()
    
    # Performance Tests
    print("=== PERFORMANCE TESTING ===")
    await test_performance_response_time()
    await test_performance_load()
    print()
    
    # Security Tests
    print("=== SECURITY TESTING ===")
    await test_security_sql_injection()
    await test_security_xss()
    await test_security_cors()
    print()
    
    # Regression Tests
    print("=== REGRESSION TESTING ===")
    await test_regression_existing_endpoints()
    print()
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    total = len(TEST_RESULTS)
    passed = sum(1 for r in TEST_RESULTS if r.passed)
    failed = total - passed
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed*100/total:.2f}%")
    print()
    
    # Group by category
    categories = {}
    for result in TEST_RESULTS:
        if result.category not in categories:
            categories[result.category] = {"total": 0, "passed": 0}
        categories[result.category]["total"] += 1
        if result.passed:
            categories[result.category]["passed"] += 1
    
    print("Results by Category:")
    for category, stats in categories.items():
        rate = stats["passed"] * 100 / stats["total"]
        print(f"  {category}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
    
    print()
    print(f"Completed at: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Save results to file
    results_file = Path(__file__).parent.parent / "comprehensive_test_results.json"
    with open(results_file, "w") as f:
        json.dump([r.to_dict() for r in TEST_RESULTS], f, indent=2)
    print(f"\nResults saved to: {results_file}")
    
    return failed == 0


if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Tests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

