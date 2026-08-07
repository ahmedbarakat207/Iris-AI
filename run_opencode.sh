#!/bin/bash
set -e

# Resolve target directory (default to current directory if not provided)
TARGET_DIR="${1:-$(pwd)}"
if [[ "$TARGET_DIR" != /* ]]; then
    TARGET_DIR="$(pwd)/$TARGET_DIR"
fi

# Get the directory of this script and cd to it to run api.py
IRIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$IRIS_DIR"

# Start the Iris API server in the background
echo "Starting Iris API Server..."
python3 api.py &
API_PID=$!

# Wait for the server to actually be up instead of blindly sleeping
echo "Waiting for Iris API to come online..."
for i in $(seq 1 30); do
    if curl -s -o /dev/null "http://localhost:8000/v1/models"; then
        echo "Iris API is up."
        break
    fi
    sleep 0.5
done

# Export the correct environment variable for OpenCode
# Note: OpenCode uses OPENAI_BASE_URL, not OPENAI_API_BASE!
export OPENAI_BASE_URL="http://localhost:8000/v1"
export OPENAI_API_KEY="dummy-key"

echo ""
echo "========================================================"
echo " Iris is ready! Launching OpenCode in $TARGET_DIR..."
echo " Select 'GPT-3.5-turbo' to talk to Iris."
echo "========================================================"
echo ""

# Launch opencode in the target directory
cd "$TARGET_DIR"
opencode

# When you exit opencode, clean up the background API server
echo "Stopping Iris API Server..."
kill $API_PID 2>/dev/null || true
