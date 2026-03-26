#!/bin/bash
# validate-endpoints.sh
#
# Validates the endpoint index against a live Fleet instance.
# Checks that endpoints return non-404 responses.
#
# Usage: FLEET_API_TOKEN=<token> ./validate-endpoints.sh <fleet-url>
# Example: FLEET_API_TOKEN=abc123 ./validate-endpoints.sh https://fleet.example.com
#
# Output: Lists endpoints that return 404 (likely removed/changed).

set -euo pipefail

FLEET_URL="${1:?Usage: FLEET_API_TOKEN=<token> ./validate-endpoints.sh <fleet-url>}"
API_TOKEN="${FLEET_API_TOKEN:?Set FLEET_API_TOKEN environment variable}"

# Remove trailing slash
FLEET_URL="${FLEET_URL%/}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
INDEX="$SKILL_DIR/references/endpoint-index.md"

if [ ! -f "$INDEX" ]; then
  echo "ERROR: $INDEX not found. Run update-endpoint-index.sh first."
  exit 1
fi

echo "Validating endpoints against: $FLEET_URL"
echo "---"

TOTAL=0
OK=0
NOT_FOUND=0
ERRORS=0

# Extract GET endpoints (safe to probe) — use process substitution to avoid subshell
while IFS='|' read -r _ name _ path _; do
  path=$(echo "$path" | sed 's/`//g' | xargs)

  # Skip endpoints with path params (:id, :token, etc.)
  if echo "$path" | grep -q '/:'; then
    continue
  fi

  TOTAL=$((TOTAL + 1))
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $API_TOKEN" \
    "${FLEET_URL}${path}" 2>/dev/null || echo "000")

  if [ "$STATUS" = "404" ]; then
    echo "MISSING: $path (404)"
    NOT_FOUND=$((NOT_FOUND + 1))
  elif [ "$STATUS" = "000" ]; then
    echo "ERROR:   $path (connection failed)"
    ERRORS=$((ERRORS + 1))
  else
    OK=$((OK + 1))
  fi
done < <(grep -E '^\| .+ \| `GET` \| `(/api/v1/[^`]+)` \|$' "$INDEX")

echo "---"
echo "Results: $TOTAL checked, $OK ok, $NOT_FOUND missing, $ERRORS errors"
echo ""
echo "Endpoints with :id/:token params were skipped (need specific IDs)."
echo ""
echo "To fully validate, also check the Fleet changelog for removed endpoints:"
echo "  https://github.com/fleetdm/fleet/blob/main/CHANGELOG.md"
