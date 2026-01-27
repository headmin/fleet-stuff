#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

ROOT_CA="$BASE_DIR/data/certs/root_ca.crt"

if [ ! -f "$ROOT_CA" ]; then
    echo "Error: Root CA not found at $ROOT_CA"
    exit 1
fi

echo "=== Installing Root CA Trust ==="
echo ""
echo "This will add the local ACME CA root certificate to your system trust store."
echo "Root CA: $ROOT_CA"
echo ""

# Show certificate info
echo "Certificate details:"
openssl x509 -in "$ROOT_CA" -noout -subject -issuer -fingerprint -sha256 | sed 's/^/  /'
echo ""

read -p "Install this certificate as a trusted root? [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing certificate (requires sudo)..."
    sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain "$ROOT_CA"
    echo ""
    echo "Root CA installed successfully!"
    echo ""
    echo "You can now install the ACME profile from:"
    echo "  $BASE_DIR/profiles/local-acme-mda-device.mobileconfig"
else
    echo "Cancelled."
    exit 1
fi
