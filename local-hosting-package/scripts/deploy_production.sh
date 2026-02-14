#!/bin/bash
# Production Deployment Script
# This script handles: code pull, admin user creation, testing, and log checking

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================="
echo "PRODUCTION DEPLOYMENT SCRIPT"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Pull latest code
echo -e "${YELLOW}Step 1: Pulling latest code from GitHub...${NC}"
cd "$PROJECT_DIR/.."
if [ -d ".git" ]; then
    echo "Pulling latest changes..."
    git pull origin main || {
        echo -e "${RED}✗ Failed to pull code${NC}"
        exit 1
    }
    echo -e "${GREEN}✓ Code pulled successfully${NC}"
else
    echo -e "${YELLOW}⚠ Not a git repository, skipping pull${NC}"
fi
echo ""

# Step 2: Create admin user
echo -e "${YELLOW}Step 2: Creating/Verifying admin user...${NC}"
cd "$PROJECT_DIR"

# Check if running in Docker
if [ -f /.dockerenv ] || [ -n "$DOCKER_CONTAINER" ]; then
    echo "Running inside Docker container..."
    python3 "$SCRIPT_DIR/create_admin_user.py"
elif command -v docker &> /dev/null && docker compose ps backend &> /dev/null; then
    echo "Running admin user creation script via Docker..."
    docker compose exec -T backend python scripts/create_admin_user.py || {
        echo -e "${YELLOW}⚠ Docker exec failed, trying direct connection...${NC}"
        python3 "$SCRIPT_DIR/create_admin_user.py"
    }
else
    echo "Running admin user creation script directly..."
    python3 "$SCRIPT_DIR/create_admin_user.py"
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Admin user verified/created${NC}"
else
    echo -e "${RED}✗ Failed to create admin user${NC}"
    exit 1
fi
echo ""

# Step 3: Test login
echo -e "${YELLOW}Step 3: Testing login endpoint...${NC}"

# Determine backend URL
if [ -n "$REACT_APP_BACKEND_URL" ]; then
    BACKEND_URL="$REACT_APP_BACKEND_URL"
elif [ -n "$PRODUCTION_URL" ]; then
    BACKEND_URL="$PRODUCTION_URL/api"
else
    BACKEND_URL="http://localhost:8002"
fi

echo "Testing login at: $BACKEND_URL/api/auth/login"

# Test login
LOGIN_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email": "admin@mahaedume.gov.in", "password": "admin123"}' \
    -w "\nHTTP_CODE:%{http_code}")

HTTP_CODE=$(echo "$LOGIN_RESPONSE" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)
RESPONSE_BODY=$(echo "$LOGIN_RESPONSE" | sed 's/HTTP_CODE:[0-9]*$//')

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Login test successful!${NC}"
    echo "Response: $(echo "$RESPONSE_BODY" | head -c 100)..."
else
    echo -e "${RED}✗ Login test failed (HTTP $HTTP_CODE)${NC}"
    echo "Response: $RESPONSE_BODY"
    echo ""
    echo "Checking backend logs for errors..."
fi
echo ""

# Step 4: Check backend logs
echo -e "${YELLOW}Step 4: Checking backend logs (last 20 lines)...${NC}"

if command -v docker &> /dev/null && docker compose ps backend &> /dev/null; then
    echo "Recent backend logs:"
    docker compose logs --tail=20 backend | grep -i -E "(error|warning|login|auth|exception)" || {
        echo "No errors found in recent logs"
        echo ""
        echo "Full recent logs:"
        docker compose logs --tail=20 backend
    }
else
    echo -e "${YELLOW}⚠ Docker not available or backend not running${NC}"
    echo "To check logs manually, run:"
    echo "  docker compose logs backend"
fi
echo ""

# Summary
echo "=========================================="
echo "DEPLOYMENT SUMMARY"
echo "=========================================="
echo -e "Code Pull: ${GREEN}✓${NC}"
echo -e "Admin User: ${GREEN}✓${NC}"
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "Login Test: ${GREEN}✓ PASSED${NC}"
    echo ""
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo ""
    echo "You can now login with:"
    echo "  Email: admin@mahaedume.gov.in"
    echo "  Password: admin123"
else
    echo -e "Login Test: ${RED}✗ FAILED (HTTP $HTTP_CODE)${NC}"
    echo ""
    echo -e "${YELLOW}⚠ Login test failed. Please check:${NC}"
    echo "  1. Backend is running: docker compose ps"
    echo "  2. Backend logs: docker compose logs backend"
    echo "  3. Database connection: Check MONGO_URL environment variable"
    echo "  4. Admin user exists: Run create_admin_user.py script"
fi
echo "=========================================="

