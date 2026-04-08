#!/bin/bash
# DEPRECATED — Use contour instead:
#   contour profile validate <file>.mobileconfig
# contour provides full Apple schema validation, deprecated type detection,
# and convention checks. This script is kept for environments without contour.
#
# Usage: ./validate-profile.sh <file.mobileconfig>

set -euo pipefail

FILE="${1:?Usage: validate-profile.sh <file.mobileconfig>}"
ERRORS=0

echo "Validating: $FILE"
echo "---"

# 1. Check plist validity
if ! plutil -lint "$FILE" > /dev/null 2>&1; then
  echo "FAIL: Invalid plist XML"
  plutil -lint "$FILE" 2>&1 || true
  ERRORS=$((ERRORS + 1))
fi

# 2. Check PayloadVersion exists
VERSION_COUNT=$(grep -c '<key>PayloadVersion</key>' "$FILE" || echo 0)
DICT_COUNT=$(grep -c '<dict>' "$FILE" || echo 0)
# Rough check: should have at least as many PayloadVersion as inner dicts
# (outer dict + each inner payload should have one)
if [ "$VERSION_COUNT" -lt 2 ]; then
  echo "WARN: Only $VERSION_COUNT PayloadVersion found — expected at least 2 (outer + inner)"
  ERRORS=$((ERRORS + 1))
fi

# 3. Check for bare UUID PayloadIdentifiers
if grep -A1 '<key>PayloadIdentifier</key>' "$FILE" | grep -E '<string>[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}</string>' > /dev/null 2>&1; then
  echo "FAIL: PayloadIdentifier uses bare UUID instead of reverse-DNS format"
  grep -B1 -A1 '<key>PayloadIdentifier</key>' "$FILE" | grep -E '<string>[0-9A-Fa-f]{8}-' || true
  ERRORS=$((ERRORS + 1))
fi

# 4. Check for <real> where <integer> expected (PayloadVersion)
if grep -A1 '<key>PayloadVersion</key>' "$FILE" | grep '<real>' > /dev/null 2>&1; then
  echo "FAIL: PayloadVersion uses <real> instead of <integer>"
  ERRORS=$((ERRORS + 1))
fi

# 5. Check for invalid hex in UUIDs
if grep -A1 '<key>PayloadUUID</key>' "$FILE" | grep -E '<string>[^<]*[G-Zg-z][^<]*</string>' > /dev/null 2>&1; then
  echo "FAIL: PayloadUUID contains non-hex characters"
  grep -A1 '<key>PayloadUUID</key>' "$FILE" | grep '<string>' || true
  ERRORS=$((ERRORS + 1))
fi

# 6. Check for deprecated PayloadTypes (macOS 13+ baseline)
DEPRECATED_TYPES="com.apple.systempreferences"
for dtype in $DEPRECATED_TYPES; do
  if grep -A1 '<key>PayloadType</key>' "$FILE" | grep -q "<string>${dtype}</string>" 2>/dev/null; then
    echo "FAIL: Deprecated PayloadType '${dtype}' — banned on macOS 13+. See references/common-payload-types.md for modern replacements."
    ERRORS=$((ERRORS + 1))
  fi
done

# 7. Check for duplicate UUIDs
UUIDS=$(grep -A1 '<key>PayloadUUID</key>' "$FILE" | grep '<string>' | sed 's/.*<string>\(.*\)<\/string>.*/\1/' | sort)
UNIQUE_UUIDS=$(echo "$UUIDS" | sort -u)
if [ "$(echo "$UUIDS" | wc -l)" -ne "$(echo "$UNIQUE_UUIDS" | wc -l)" ]; then
  echo "FAIL: Duplicate PayloadUUID found"
  echo "$UUIDS" | uniq -d | while read -r dup; do
    echo "  Duplicate: $dup"
  done
  ERRORS=$((ERRORS + 1))
fi

echo "---"
if [ "$ERRORS" -eq 0 ]; then
  echo "PASS: No issues found"
else
  echo "FOUND: $ERRORS issue(s)"
fi

exit "$ERRORS"
