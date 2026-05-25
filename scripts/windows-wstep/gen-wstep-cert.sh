#!/usr/bin/env bash
#
# gen-wstep-cert.sh
#
# Generates the certificate + key pair Fleet uses to authenticate and manage
# Windows hosts (MDM WSTEP), using REAL OpenSSL inside an Apple `container`.
#
# macOS ships LibreSSL, which does NOT support `openssl genrsa --traditional`.
# Running the generation inside a Linux container with genuine OpenSSL avoids
# that problem entirely. Files are written to a host-mounted ./output dir, and
# a copy-paste-friendly README.md is generated alongside them.
#
# Usage:
#   ./gen-wstep-cert.sh
#
# Override any default via env var, e.g.:
#   DAYS=730 ORG='Acme Corp' ./gen-wstep-cert.sh
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Configurable parameters (Fleet documented defaults) --------------------
KEY_BITS="${KEY_BITS:-4096}"
DAYS="${DAYS:-3652}"
CN="${CN:-Fleet Root CA}"
ORG="${ORG:-Fleet}"
COUNTRY="${COUNTRY:-US}"
KEY_FILE="${KEY_FILE:-fleet-mdm-win-wstep.key}"
CRT_FILE="${CRT_FILE:-fleet-mdm-win-wstep.crt}"
OUT_DIR="${OUT_DIR:-$SCRIPT_DIR/output}"
IMAGE="${IMAGE:-alpine:latest}"

# --- Handle pre-existing output --------------------------------------------
# DECISION POINT — implemented by you (see notes from Claude).
#
# Called before generation when $OUT_DIR already contains a key or cert.
# Regenerating silently would overwrite a key that may already be wired into a
# live Fleet server, breaking enrollment for every Windows host. Decide the
# behavior: refuse, prompt, back up, or overwrite.
#
# Args: $1 = path to existing key (may not exist), $2 = path to existing cert
# Return: 0 to proceed with (over)writing, non-zero to abort generation.
handle_existing_output() {
    local existing_key="$1"
    local existing_crt="$2"

    [ -f "$existing_key" ] && echo "  - $existing_key" >&2
    [ -f "$existing_crt" ] && echo "  - $existing_crt" >&2
    echo "Overwriting may invalidate a key already configured in a live Fleet server." >&2

    # Prompt only when attached to a terminal; refuse in non-interactive/CI use.
    if [ -t 0 ]; then
        printf "Overwrite these files? [y/N] " >&2
        read -r reply
        case "$reply" in
            [yY] | [yY][eE][sS]) return 0 ;;
            *) return 1 ;;
        esac
    fi

    echo "No TTY: refusing to overwrite. Remove the files or set OUT_DIR= to regenerate." >&2
    return 1
}

# --- Preflight --------------------------------------------------------------
echo "=== Fleet MDM Windows WSTEP cert generator (Apple container) ==="

if ! command -v container &>/dev/null; then
    echo "Error: 'container' CLI not found." >&2
    echo "Install from: https://github.com/apple/containerization" >&2
    exit 1
fi

if ! container system info &>/dev/null; then
    echo "Starting container system service..."
    container system start
fi

mkdir -p "$OUT_DIR"

if [ -f "$OUT_DIR/$KEY_FILE" ] || [ -f "$OUT_DIR/$CRT_FILE" ]; then
    echo "Existing output detected in $OUT_DIR"
    if ! handle_existing_output "$OUT_DIR/$KEY_FILE" "$OUT_DIR/$CRT_FILE"; then
        echo "Aborted: not overwriting existing files." >&2
        exit 1
    fi
fi

# --- Generate inside the container -----------------------------------------
echo "Pulling $IMAGE (if needed)..."
container image pull "$IMAGE" 2>/dev/null || true

echo "Generating key + certificate with real OpenSSL inside $IMAGE..."
container run --rm \
    --volume "$OUT_DIR:/out" \
    --env KEY_BITS="$KEY_BITS" \
    --env DAYS="$DAYS" \
    --env CN="$CN" \
    --env ORG="$ORG" \
    --env COUNTRY="$COUNTRY" \
    --env KEY_FILE="$KEY_FILE" \
    --env CRT_FILE="$CRT_FILE" \
    "$IMAGE" \
    sh -c '
        set -e
        apk add --no-cache openssl >/dev/null 2>&1
        openssl version > /out/.openssl-version
        openssl genrsa --traditional -out "/out/$KEY_FILE" "$KEY_BITS"
        openssl req -x509 -new -nodes \
            -key "/out/$KEY_FILE" \
            -sha256 -days "$DAYS" \
            -out "/out/$CRT_FILE" \
            -subj "/CN=$CN/C=$COUNTRY/O=$ORG"
        chmod 600 "/out/$KEY_FILE"
    '

# --- Verify -----------------------------------------------------------------
if [ ! -s "$OUT_DIR/$KEY_FILE" ] || [ ! -s "$OUT_DIR/$CRT_FILE" ]; then
    echo "Error: expected output files were not created." >&2
    exit 1
fi

OPENSSL_VERSION="$(cat "$OUT_DIR/.openssl-version" 2>/dev/null || echo 'unknown')"
rm -f "$OUT_DIR/.openssl-version"

# --- Generate copy-paste README.md (on the host) ----------------------------
README="$OUT_DIR/README.md"
KEY_CONTENTS="$(cat "$OUT_DIR/$KEY_FILE")"
CRT_CONTENTS="$(cat "$OUT_DIR/$CRT_FILE")"

cat > "$README" <<EOF
# Fleet MDM Windows WSTEP certificate

Generated on $(date -u '+%Y-%m-%d %H:%M:%S UTC') inside an Apple \`container\`
(image: \`$IMAGE\`) using genuine OpenSSL — **not** macOS LibreSSL, which lacks
the \`--traditional\` flag.

\`\`\`
$OPENSSL_VERSION
\`\`\`

## Step 1 — Commands run

\`\`\`sh
openssl genrsa --traditional -out $KEY_FILE $KEY_BITS
openssl req -x509 -new -nodes -key $KEY_FILE -sha256 -days $DAYS \\
  -out $CRT_FILE -subj '/CN=$CN/C=$COUNTRY/O=$ORG'
\`\`\`

## Step 2 — Configure Fleet

Set the **contents** (not file paths) of the cert and key in your Fleet server
configuration, then restart the Fleet server:

| Environment variable | Value |
|----------------------|-------|
| \`FLEET_MDM_WINDOWS_WSTEP_IDENTITY_CERT_BYTES\` | contents of \`$CRT_FILE\` (below) |
| \`FLEET_MDM_WINDOWS_WSTEP_IDENTITY_KEY_BYTES\`  | contents of \`$KEY_FILE\` (below) |

> **Note:** Any Fleet env var ending in \`_BYTES\` expects the file's actual
> content, not a path. To pass a file path instead, drop the \`_BYTES\` suffix.

### \`$CRT_FILE\` — \`FLEET_MDM_WINDOWS_WSTEP_IDENTITY_CERT_BYTES\`

\`\`\`
$CRT_CONTENTS
\`\`\`

### \`$KEY_FILE\` — \`FLEET_MDM_WINDOWS_WSTEP_IDENTITY_KEY_BYTES\`

> ⚠️ **Private key — keep secret.** Do not commit this file or this README.

\`\`\`
$KEY_CONTENTS
\`\`\`
EOF

# --- Keep secrets out of git ------------------------------------------------
GITIGNORE="$SCRIPT_DIR/.gitignore"
if [ ! -f "$GITIGNORE" ] || ! grep -qxF "output/" "$GITIGNORE" 2>/dev/null; then
    echo "output/" >> "$GITIGNORE"
fi

# --- Summary ----------------------------------------------------------------
echo ""
echo "=== Done ==="
echo "OpenSSL: $OPENSSL_VERSION"
echo "Output:"
echo "  $OUT_DIR/$KEY_FILE   (private key — keep secret)"
echo "  $OUT_DIR/$CRT_FILE"
echo "  $README              (commands + copy-paste cert blocks + Fleet steps)"
echo ""
echo "Next: open the README.md and copy the cert/key into Fleet's"
echo "FLEET_MDM_WINDOWS_WSTEP_IDENTITY_CERT_BYTES / _KEY_BYTES, then restart Fleet."
