#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

# Load .env
if [ -f "$BASE_DIR/.env" ]; then
    source "$BASE_DIR/.env"
fi

CONTAINER_NAME="${CONTAINER_NAME:-local-acme-ca}"

echo "=== Stopping Local ACME CA ==="

# Try Apple Container first
if command -v container &> /dev/null; then
    container kill "$CONTAINER_NAME" 2>/dev/null && echo "Stopped (Apple Container)" || true
    container rm "$CONTAINER_NAME" 2>/dev/null || true
fi

# Try Docker
if command -v docker &> /dev/null; then
    cd "$BASE_DIR"
    docker compose down 2>/dev/null && echo "Stopped (Docker)" || true
fi

echo "Done"
