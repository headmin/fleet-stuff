#!/bin/bash
# Validate a Windows CSP profile XML file for Fleet compatibility
# Usage: ./validate-windows-profile.sh <file.xml>

set -euo pipefail

FILE="${1:?Usage: validate-windows-profile.sh <file.xml>}"
ERRORS=0

echo "Validating: $FILE"
echo "---"

CONTENT=$(cat "$FILE")

# 1. Check for XML declaration (forbidden — makes Fleet think it's macOS)
if echo "$CONTENT" | head -5 | grep -q '<?xml'; then
  echo "FAIL: File starts with <?xml?> declaration — Fleet will classify this as macOS, not Windows"
  ERRORS=$((ERRORS + 1))
fi

# 2. Check for SyncML envelope (forbidden)
if grep -qi '<SyncML\|<SyncHdr\|<SyncBody' "$FILE" 2>/dev/null; then
  echo "FAIL: Contains SyncML envelope elements — Fleet wraps the fragment itself"
  ERRORS=$((ERRORS + 1))
fi

# 3. Check for processing instructions (forbidden)
if grep -q '<?' "$FILE" 2>/dev/null | grep -v '<?xml' 2>/dev/null; then
  # More precise check: any PI that isn't on line 1
  if grep -n '<?' "$FILE" | grep -v '<?xml' | grep -q '.'; then
    echo "FAIL: Contains XML processing instructions (forbidden by Fleet)"
    ERRORS=$((ERRORS + 1))
  fi
fi

# 4. Check well-formed XML
if ! xmllint --noout "$FILE" 2>/dev/null; then
  echo "FAIL: Not well-formed XML"
  xmllint --noout "$FILE" 2>&1 | head -5 || true
  ERRORS=$((ERRORS + 1))
fi

# 5. Check top-level elements are valid
# Extract top-level element names
TOP_ELEMENTS=$(grep -oE '^ *<(Replace|Add|Exec|Atomic|Delete)' "$FILE" | sed 's/.*<//;s/[> ].*//' | sort -u)
INVALID_TOP=$(echo "$TOP_ELEMENTS" | grep -v -E '^(Replace|Add|Exec|Atomic)$' | grep -v '^$' || true)
if [ -n "$INVALID_TOP" ]; then
  echo "FAIL: Invalid top-level element(s): $INVALID_TOP"
  ERRORS=$((ERRORS + 1))
fi

# 6. Check for <Delete> (not valid in Fleet profiles)
if grep -q '<Delete' "$FILE" 2>/dev/null; then
  echo "FAIL: <Delete> is not a valid element in Fleet profiles"
  ERRORS=$((ERRORS + 1))
fi

# 7. Check Atomic rules — if Atomic is first top-level, must be only one
FIRST_ELEMENT=$(grep -oE '^ *<(Replace|Add|Exec|Atomic)' "$FILE" | head -1 | sed 's/.*<//')
if [ "$FIRST_ELEMENT" = "Atomic" ]; then
  NON_ATOMIC_TOP=$(grep -cE '^ *<(Replace|Add|Exec)' "$FILE" || echo 0)
  if [ "$NON_ATOMIC_TOP" -gt 0 ]; then
    # Check if these are inside Atomic or at top level
    # Simple heuristic: if there's a Replace/Add AFTER </Atomic>, it's a violation
    if sed -n '/<\/Atomic>/,$ p' "$FILE" | grep -qE '<(Replace|Add|Exec)'; then
      echo "FAIL: <Atomic> is first element but other elements exist outside it — Atomic must be sole top-level element"
      ERRORS=$((ERRORS + 1))
    fi
  fi
fi

# 8. Check for reserved Fleet LocURIs
if grep -q '/Vendor/MSFT/BitLocker' "$FILE" 2>/dev/null; then
  echo "FAIL: Contains reserved BitLocker LocURI — use Fleet's built-in BitLocker settings"
  ERRORS=$((ERRORS + 1))
fi
if grep -q '/Vendor/MSFT/Policy/Config/Update' "$FILE" 2>/dev/null; then
  echo "WARN: Contains Windows Update LocURI — reserved by Fleet unless enableCustomOSUpdates is set"
fi

# 9. Check that <Exec> is only in SCEP profiles
if grep -q '<Exec' "$FILE" 2>/dev/null; then
  if ! grep -q 'SCEP\|ClientCertificateInstall' "$FILE" 2>/dev/null; then
    echo "FAIL: <Exec> is only valid in SCEP certificate enrollment profiles"
    ERRORS=$((ERRORS + 1))
  fi
fi

# 10. Check LocURI format
BAD_URIS=$(grep '<LocURI>' "$FILE" | grep -v './Device/Vendor/MSFT\|./User/Vendor/MSFT\|./Vendor/MSFT' | grep -v '^\s*$' || true)
if [ -n "$BAD_URIS" ]; then
  echo "WARN: LocURI(s) don't follow expected path format (./Device/Vendor/MSFT/ or ./User/Vendor/MSFT/):"
  echo "$BAD_URIS" | head -3
fi

echo "---"
if [ "$ERRORS" -eq 0 ]; then
  echo "PASS: No issues found"
else
  echo "FOUND: $ERRORS issue(s)"
fi

exit "$ERRORS"
