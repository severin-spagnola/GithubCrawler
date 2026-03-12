#!/usr/bin/env bash
# Run once from the Pi to set up passwordless SSH to each lab PC and
# pre-deploy crawler.py.
#
# Make executable: chmod +x setup_coordinator.sh

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration — edit these before running
# ---------------------------------------------------------------------------
PCS=(
    "192.168.1.101"
    "192.168.1.102"
    "192.168.1.103"
    "192.168.1.104"
)
USER="student"
CRAWLER_LOCAL="$(cd "$(dirname "$0")" && pwd)/crawler.py"
CRAWLER_REMOTE="/tmp/crawler.py"

# ---------------------------------------------------------------------------
# Generate SSH key if one doesn't already exist
# ---------------------------------------------------------------------------
if [ ! -f "$HOME/.ssh/id_rsa" ]; then
    echo "[setup] No SSH key found — generating ~/.ssh/id_rsa ..."
    ssh-keygen -t rsa -b 4096 -N "" -f "$HOME/.ssh/id_rsa"
    echo "[setup] SSH key generated."
else
    echo "[setup] SSH key already exists at ~/.ssh/id_rsa — skipping keygen."
fi

# ---------------------------------------------------------------------------
# For each PC: copy SSH key, then deploy crawler.py
# ---------------------------------------------------------------------------
FAILED=()

for PC in "${PCS[@]}"; do
    echo ""
    echo "--- Setting up $PC ---"

    # Copy SSH public key (will prompt for password once)
    if ssh-copy-id -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
                   "${USER}@${PC}" 2>/dev/null; then
        echo "  [ok] ssh-copy-id succeeded for $PC"
    else
        echo "  [warn] ssh-copy-id failed for $PC — skipping crawler deploy"
        FAILED+=("$PC")
        continue
    fi

    # Deploy crawler.py
    if scp -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
           "$CRAWLER_LOCAL" "${USER}@${PC}:${CRAWLER_REMOTE}"; then
        echo "  [ok] crawler.py deployed to $PC:$CRAWLER_REMOTE"
    else
        echo "  [warn] scp failed for $PC"
        FAILED+=("$PC")
    fi
done

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "=== Setup complete ==="
echo "  PCs configured : $((${#PCS[@]} - ${#FAILED[@]})) / ${#PCS[@]}"

if [ ${#FAILED[@]} -gt 0 ]; then
    echo "  Failed PCs     : ${FAILED[*]}"
    echo "  Check connectivity and SSH credentials for the above."
fi

echo ""
echo "Next step: make sure .env is configured, then run:  ./run_crawl.sh"
