#!/usr/bin/env bash
# Launch the orchestrator for RunPod-based distributed crawling.
#
# Usage:
#   ./run_runpod.sh                    # default: 8 hours max
#   ./run_runpod.sh --max-hours 12     # 12 hour run
#   ./run_runpod.sh --no-tunnel        # skip ngrok (workers on same network)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Check for .env
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo ""
    echo "  *** WARNING: .env file not found in $SCRIPT_DIR ***"
    echo ""
    echo "  Create a .env file with:"
    echo ""
    echo "    NGROK_AUTH_TOKEN=your_ngrok_token"
    echo "    QUERIES_FILE=./queries.txt"
    echo "    OUTPUT_FILE=./final_leads.csv"
    echo ""
    echo "  Aborting."
    exit 1
fi

# Install orchestrator deps if needed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "[setup] Installing orchestrator dependencies..."
    pip install -r "$SCRIPT_DIR/requirements-orchestrator.txt"
fi

echo "[$(date '+%H:%M:%S')] Starting RunPod orchestrator..."
echo ""

python3 "$SCRIPT_DIR/runpod_orchestrator.py" "$@"
