#!/bin/bash
# Setup script for testing environment
# Usage: Run from project root or backend directory

set -e

# Navigate to backend directory if not already there
if [ ! -f "backend/pytest.ini" ]; then
    if [ -f "pytest.ini" ]; then
        # Already in backend directory
        BACKEND_DIR="."
    else
        # Need to navigate to backend
        cd "$(dirname "$0")/../backend" || exit 1
        BACKEND_DIR="."
    fi
else
    BACKEND_DIR="backend"
    cd "$BACKEND_DIR" || exit 1
fi

echo "=========================================="
echo "Setting up Test Environment"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv "$BACKEND_DIR/venv"
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source "$BACKEND_DIR/venv/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install -r "$BACKEND_DIR/requirements.txt"

# Check MongoDB connection
echo ""
echo -e "${YELLOW}Checking MongoDB connection...${NC}"
if python3 -c "from motor.motor_asyncio import AsyncIOMotorClient; import asyncio; asyncio.run(AsyncIOMotorClient('mongodb://localhost:27017').admin.command('ping'))" 2>/dev/null; then
    echo -e "${GREEN}✓ MongoDB is running${NC}"
else
    echo -e "${RED}✗ MongoDB is not running${NC}"
    echo "Please start MongoDB:"
    echo "  - Using Docker: docker-compose up -d mongodb"
    echo "  - Or locally: mongod --dbpath /path/to/data"
    exit 1
fi

# Create test uploads directory
echo ""
echo "Creating test directories..."
mkdir -p "$BACKEND_DIR/uploads"
mkdir -p "$BACKEND_DIR/tests/__pycache__"

# Set test environment variables
export TEST_MONGO_URL=${TEST_MONGO_URL:-mongodb://localhost:27017}
export TEST_DB_NAME=${TEST_DB_NAME:-test_maharashtra_edu}

echo ""
echo -e "${GREEN}=========================================="
echo "Test Environment Setup Complete!"
echo "==========================================${NC}"
echo ""
echo "To run tests:"
echo "  1. Activate venv: source venv/bin/activate"
echo "  2. Run tests: pytest"
echo "  3. Or use: ./run_tests.sh"
echo ""

