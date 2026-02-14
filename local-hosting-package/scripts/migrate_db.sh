#!/bin/bash
# Database Migration Script Wrapper

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Database Migration Tool"
echo "========================"
echo ""

# Set default values
LOCAL_MONGO_URL="${LOCAL_MONGO_URL:-mongodb://localhost:27017}"
REMOTE_MONGO_URL="${REMOTE_MONGO_URL:-mongodb://mongo:b5a7adcac8107c867aa1@31.97.207.166:27017/?tls=false}"
DB_NAME="${DB_NAME:-maharashtra_edu}"

# Check if running in Docker
if [ -f /.dockerenv ] || [ -n "$DOCKER_CONTAINER" ]; then
    echo "Running inside Docker container..."
    python3 "$SCRIPT_DIR/migrate_to_production_db.py"
else
    # Check if local MongoDB is accessible
    echo "Checking local MongoDB connection..."
    if command -v mongosh &> /dev/null; then
        if mongosh "$LOCAL_MONGO_URL" --eval "db.adminCommand('ping')" --quiet &> /dev/null; then
            echo "✓ Local MongoDB is accessible"
        else
            echo "⚠️  Local MongoDB may not be accessible"
        fi
    fi
    
    # Run migration script
    echo "Starting migration..."
    cd "$PROJECT_DIR"
    
    # Use Python from backend if available, otherwise system Python
    if [ -d "backend/venv" ]; then
        source backend/venv/bin/activate
        python "$SCRIPT_DIR/migrate_to_production_db.py"
    elif command -v python3 &> /dev/null; then
        python3 "$SCRIPT_DIR/migrate_to_production_db.py"
    else
        echo "❌ Python 3 not found. Please install Python 3."
        exit 1
    fi
fi

