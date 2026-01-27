#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

cd "$BASE_DIR"

# Load .env
if [ -f ".env" ]; then
    source ".env"
fi

ACME_PORT="${ACME_PORT:-9443}"

echo "=== Starting Local ACME CA (Docker) ==="

# Check if initialized
if [ ! -f "data/config/ca.json" ]; then
    echo "CA not initialized. Run './scripts/init.sh' first."
    exit 1
fi

# Start with docker compose
docker compose up -d

echo ""
echo "Waiting for CA to start..."
sleep 3

# Health check
for i in {1..30}; do
    if curl -sk "https://localhost:${ACME_PORT}/health" 2>/dev/null | grep -q "ok"; then
        echo ""
        echo "=== CA Started Successfully ==="
        echo ""
        echo "Health:               https://localhost:${ACME_PORT}/health"
        echo "ACME Directory:       https://localhost:${ACME_PORT}/acme/acme/directory"
        echo "ACME MDA Directory:   https://localhost:${ACME_PORT}/acme/acme-mda/directory"
        echo "Root CA:              https://localhost:${ACME_PORT}/roots.pem"
        echo ""
        echo "Commands:"
        echo "  View logs:  docker compose logs -f"
        echo "  Stop:       docker compose down"
        exit 0
    fi
    echo -n "."
    sleep 1
done

echo ""
echo "Error: CA failed to become healthy"
echo "Check logs: docker compose logs"
exit 1
