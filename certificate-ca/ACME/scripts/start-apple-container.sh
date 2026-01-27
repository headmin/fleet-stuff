#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

# Load .env
if [ -f "$BASE_DIR/.env" ]; then
    source "$BASE_DIR/.env"
fi

CONTAINER_NAME="${CONTAINER_NAME:-local-acme-ca}"
ACME_PORT="${ACME_PORT:-9443}"

echo "=== Starting Local ACME CA (Apple Container) ==="

# Check for container CLI
if ! command -v container &> /dev/null; then
    echo "Error: 'container' CLI not found"
    echo "Install from: https://github.com/apple/containerization"
    exit 1
fi

# Ensure container system is started
echo "Ensuring container system is running..."
if ! container system info &>/dev/null; then
    echo "Starting container system service..."
    container system start
fi

# Check if initialized
if [ ! -f "$BASE_DIR/data/config/ca.json" ]; then
    echo "CA not initialized. Run './scripts/init.sh' first."
    exit 1
fi

# Stop existing container
echo "Stopping existing container..."
container kill "$CONTAINER_NAME" 2>/dev/null || true
container rm "$CONTAINER_NAME" 2>/dev/null || true
sleep 1

# Pull image if needed
echo "Pulling step-ca image..."
container image pull smallstep/step-ca:latest 2>/dev/null || true

# Start container
echo "Starting step-ca container..."
container run \
    --name "$CONTAINER_NAME" \
    --detach \
    --publish "${ACME_PORT}:9000" \
    --volume "$BASE_DIR/data:/home/step" \
    smallstep/step-ca:latest

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
        echo "Container: $CONTAINER_NAME"
        echo ""
        echo "Commands:"
        echo "  View logs:  container logs $CONTAINER_NAME"
        echo "  Stop:       container kill $CONTAINER_NAME"
        echo "  Remove:     container rm $CONTAINER_NAME"
        exit 0
    fi
    echo -n "."
    sleep 1
done

echo ""
echo "Error: CA failed to become healthy"
echo "Check logs: container logs $CONTAINER_NAME"
exit 1
