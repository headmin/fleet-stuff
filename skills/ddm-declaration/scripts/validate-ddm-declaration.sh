#!/bin/bash
# Validate a DDM declaration JSON file for Fleet compatibility
# Usage: ./validate-ddm-declaration.sh <file.json>

set -euo pipefail

FILE="${1:?Usage: validate-ddm-declaration.sh <file.json>}"
ERRORS=0

echo "Validating: $FILE"
echo "---"

# 1. Check valid JSON
if ! python3 -c "import json, sys; json.load(open(sys.argv[1]))" "$FILE" 2>/dev/null; then
  echo "FAIL: Invalid JSON"
  ERRORS=$((ERRORS + 1))
fi

# 2. Check required keys
for key in Type Identifier Payload; do
  if ! python3 -c "import json, sys; d=json.load(open(sys.argv[1])); assert '$key' in d" "$FILE" 2>/dev/null; then
    echo "FAIL: Missing required key '$key'"
    ERRORS=$((ERRORS + 1))
  fi
done

# 3. Check ServerToken is NOT present
if python3 -c "import json, sys; d=json.load(open(sys.argv[1])); assert 'ServerToken' in d" "$FILE" 2>/dev/null; then
  echo "FAIL: ServerToken must not be included — Fleet generates it automatically"
  ERRORS=$((ERRORS + 1))
fi

# 4. Check Type prefix
TYPE=$(python3 -c "import json, sys; print(json.load(open(sys.argv[1])).get('Type', ''))" "$FILE" 2>/dev/null || echo "")
if [ -n "$TYPE" ]; then
  if [[ ! "$TYPE" == com.apple.configuration.* ]]; then
    echo "FAIL: Type must start with 'com.apple.configuration.' — got '$TYPE'"
    ERRORS=$((ERRORS + 1))
  fi

  # 5. Check forbidden types
  FORBIDDEN="account.caldav account.carddav account.exchange account.google account.ldap account.mail screensharing.connection security.certificate security.identity security.passkey.attestation services.configuration-files watch.enrollment"
  SUBTYPE="${TYPE#com.apple.configuration.}"
  for forbidden in $FORBIDDEN; do
    if [ "$SUBTYPE" = "$forbidden" ]; then
      echo "FAIL: Type '$TYPE' is blocked in Fleet (requires asset references)"
      ERRORS=$((ERRORS + 1))
    fi
  done

  # 6. Check always-blocked type
  if [ "$SUBTYPE" = "management.status-subscriptions" ]; then
    echo "FAIL: management.status-subscriptions is always blocked in Fleet — use queries/policies instead"
    ERRORS=$((ERRORS + 1))
  fi

  # 7. Warn on restricted type
  if [ "$SUBTYPE" = "softwareupdate.enforcement.specific" ]; then
    echo "WARN: softwareupdate.enforcement.specific requires allowCustomOSUpdatesAndFileVault flag"
  fi
fi

# 8. Check Identifier length (max 64 UTF-8 bytes)
IDENTIFIER=$(python3 -c "import json, sys; print(json.load(open(sys.argv[1])).get('Identifier', ''))" "$FILE" 2>/dev/null || echo "")
if [ -n "$IDENTIFIER" ]; then
  BYTE_LEN=$(echo -n "$IDENTIFIER" | wc -c | tr -d ' ')
  if [ "$BYTE_LEN" -gt 64 ]; then
    echo "FAIL: Identifier exceeds 64 bytes ($BYTE_LEN bytes)"
    ERRORS=$((ERRORS + 1))
  fi
fi

# 9. Check Payload is a dict
if ! python3 -c "import json, sys; d=json.load(open(sys.argv[1])); assert isinstance(d.get('Payload'), dict)" "$FILE" 2>/dev/null; then
  echo "FAIL: Payload must be a JSON object (dict)"
  ERRORS=$((ERRORS + 1))
fi

echo "---"
if [ "$ERRORS" -eq 0 ]; then
  echo "PASS: No issues found"
else
  echo "FOUND: $ERRORS issue(s)"
fi

exit "$ERRORS"
