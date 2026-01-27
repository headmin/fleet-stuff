#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$BASE_DIR/.env"

if [ -f "$ENV_FILE" ]; then
    echo ".env file already exists at $ENV_FILE"
    echo "Remove it first if you want to recreate: rm $ENV_FILE"
    exit 1
fi

cat > "$ENV_FILE" << 'EOF'
# ACME CA Local Container Configuration
CA_NAME=local-acme-ca
ACME_PORT=9443
CA_PASSWORD=supersecret

# Container settings
CONTAINER_NAME=local-acme-ca
EOF

echo "Created $ENV_FILE"
echo ""
cat "$ENV_FILE"
