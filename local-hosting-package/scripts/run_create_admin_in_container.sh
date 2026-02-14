#!/bin/bash
# Script to create admin user inside Docker container
# This copies the script into the container and runs it

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Creating admin user in Docker container..."

# Copy script to container and run it
docker compose exec backend bash -c "
cat > /tmp/create_admin_user.py << 'EOFPYTHON'
$(cat "$SCRIPT_DIR/create_admin_user.py")
EOFPYTHON
python3 /tmp/create_admin_user.py
rm /tmp/create_admin_user.py
"

echo "Done!"

