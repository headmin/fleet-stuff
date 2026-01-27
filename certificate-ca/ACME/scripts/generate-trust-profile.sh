#!/bin/bash
#
# Generate trust mobileconfig profile from current CA certificates
# This script reads the CA certs from data/certs/ and creates a fresh
# local-ca-trust.mobileconfig with embedded base64-encoded certificates
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
CERTS_DIR="$BASE_DIR/data/certs"
PROFILES_DIR="$BASE_DIR/profiles"
OUTPUT_FILE="$PROFILES_DIR/local-ca-trust.mobileconfig"

# Check if cert files exist
if [ ! -f "$CERTS_DIR/root_ca.crt" ]; then
    echo "Error: Root CA certificate not found at $CERTS_DIR/root_ca.crt"
    echo "Make sure the CA container has been initialized first."
    exit 1
fi

if [ ! -f "$CERTS_DIR/intermediate_ca.crt" ]; then
    echo "Error: Intermediate CA certificate not found at $CERTS_DIR/intermediate_ca.crt"
    echo "Make sure the CA container has been initialized first."
    exit 1
fi

# Create profiles directory if it doesn't exist
mkdir -p "$PROFILES_DIR"

# Read and base64 encode the certificates
# The certs are already PEM format, we base64 encode the entire PEM
ROOT_CA_B64=$(base64 < "$CERTS_DIR/root_ca.crt" | tr -d '\n')
INTERMEDIATE_CA_B64=$(base64 < "$CERTS_DIR/intermediate_ca.crt" | tr -d '\n')

# Generate unique-ish UUIDs based on timestamp (or use uuidgen if available)
if command -v uuidgen &> /dev/null; then
    PROFILE_UUID=$(uuidgen | tr '[:lower:]' '[:upper:]')
    ROOT_UUID=$(uuidgen | tr '[:lower:]' '[:upper:]')
    INTM_UUID=$(uuidgen | tr '[:lower:]' '[:upper:]')
else
    # Fallback to static UUIDs with timestamp suffix
    TS=$(date +%s)
    PROFILE_UUID="LOCAL-TRST-CNFG-0001-$(printf '%012d' $TS | tail -c 12)"
    ROOT_UUID="LOCAL-ROOT-CA01-0001-$(printf '%012d' $TS | tail -c 12)"
    INTM_UUID="LOCAL-INTM-CA01-0001-$(printf '%012d' $TS | tail -c 12)"
fi

# Write the mobileconfig file
cat > "$OUTPUT_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <array>
        <dict>
            <key>PayloadCertificateFileName</key>
            <string>local-acme-root-ca.cer</string>
            <key>PayloadContent</key>
            <data>${ROOT_CA_B64}</data>
            <key>PayloadDisplayName</key>
            <string>Local ACME CA Root</string>
            <key>PayloadIdentifier</key>
            <string>com.local.acme-ca.root</string>
            <key>PayloadType</key>
            <string>com.apple.security.root</string>
            <key>PayloadUUID</key>
            <string>${ROOT_UUID}</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
        </dict>
        <dict>
            <key>PayloadCertificateFileName</key>
            <string>local-acme-intermediate-ca.cer</string>
            <key>PayloadContent</key>
            <data>${INTERMEDIATE_CA_B64}</data>
            <key>PayloadDisplayName</key>
            <string>Local ACME CA Intermediate</string>
            <key>PayloadIdentifier</key>
            <string>com.local.acme-ca.intermediate</string>
            <key>PayloadType</key>
            <string>com.apple.security.pkcs1</string>
            <key>PayloadUUID</key>
            <string>${INTM_UUID}</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
        </dict>
    </array>
    <key>PayloadDisplayName</key>
    <string>Local ACME CA Trust</string>
    <key>PayloadDescription</key>
    <string>Trust certificates for local step-ca ACME instance</string>
    <key>PayloadIdentifier</key>
    <string>com.local.acme-ca.trust.profile</string>
    <key>PayloadOrganization</key>
    <string>Local Test</string>
    <key>PayloadScope</key>
    <string>System</string>
    <key>PayloadType</key>
    <string>Configuration</string>
    <key>PayloadUUID</key>
    <string>${PROFILE_UUID}</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
    <key>PayloadRemovalDisallowed</key>
    <false/>
</dict>
</plist>
EOF

echo "Generated trust profile: $OUTPUT_FILE"
echo ""
echo "Certificate info:"
echo "  Root CA:         $(openssl x509 -in "$CERTS_DIR/root_ca.crt" -noout -subject 2>/dev/null | sed 's/subject=/  /')"
echo "  Intermediate CA: $(openssl x509 -in "$CERTS_DIR/intermediate_ca.crt" -noout -subject 2>/dev/null | sed 's/subject=/  /')"
echo ""
echo "Install this profile on your device before installing ACME certificate profiles."
