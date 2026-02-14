#!/bin/bash
# Quick Fix Script for Production Login Issue
# Run this on the production server

set -e

echo "=========================================="
echo "PRODUCTION LOGIN FIX"
echo "=========================================="
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Step 1: Create Admin User
echo -e "${YELLOW}[1/3] Creating/Verifying admin user...${NC}"

# Try Docker first, then direct
if command -v docker &> /dev/null && docker compose ps backend &> /dev/null 2>&1; then
    echo "Using Docker container..."
    # Copy script into container and run it
    docker compose exec backend bash -c "
    cat > /tmp/create_admin_user.py << 'EOFPYTHON'
$(cat "$SCRIPT_DIR/create_admin_user.py")
EOFPYTHON
    python3 /tmp/create_admin_user.py
    rm /tmp/create_admin_user.py
    "
elif [ -f /.dockerenv ]; then
    echo "Running inside container..."
    python3 "$SCRIPT_DIR/create_admin_user.py"
else
    echo "Running directly..."
    export MONGO_URL="${MONGO_URL:-mongodb://mongo:b5a7adcac8107c867aa1@31.97.207.166:27017/?tls=false}"
    export DB_NAME="${DB_NAME:-maharashtra_edu}"
    python3 "$SCRIPT_DIR/create_admin_user.py"
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Admin user ready${NC}"
else
    echo -e "${RED}✗ Failed to create admin user${NC}"
    exit 1
fi
echo ""

# Step 2: Test Login
echo -e "${YELLOW}[2/3] Testing login...${NC}"

# Determine backend URL
BACKEND_URL="${REACT_APP_BACKEND_URL:-http://localhost:8002}"
if [[ "$BACKEND_URL" != *"/api"* ]]; then
    BACKEND_URL="${BACKEND_URL}/api"
fi

echo "Testing: $BACKEND_URL/auth/login"

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BACKEND_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email": "admin@mahaedume.gov.in", "password": "admin123"}')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Login successful!${NC}"
    TOKEN=$(echo "$BODY" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    if [ -n "$TOKEN" ]; then
        echo "Token received: ${TOKEN:0:20}..."
    fi
else
    echo -e "${RED}✗ Login failed (HTTP $HTTP_CODE)${NC}"
    echo "Response: $BODY"
fi
echo ""

# Step 3: Check Logs
echo -e "${YELLOW}[3/3] Checking backend logs...${NC}"

if command -v docker &> /dev/null && docker compose ps backend &> /dev/null 2>&1; then
    echo "Recent errors/warnings:"
    docker compose logs --tail=30 backend | grep -i -E "(error|warning|exception|login|auth)" | tail -10 || echo "No errors found"
else
    echo "Docker not available. Check logs manually."
fi
echo ""

echo "=========================================="
echo "FIX COMPLETE"
echo "=========================================="
echo ""
echo "Default credentials:"
echo "  Email: admin@mahaedume.gov.in"
echo "  Password: admin123"
echo ""

