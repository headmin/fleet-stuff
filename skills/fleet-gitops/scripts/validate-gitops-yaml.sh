#!/bin/bash
# validate-gitops-yaml.sh
#
# Validates Fleet GitOps YAML files for common structural errors.
# Catches missing required keys, scope violations, and label consistency issues.
#
# Usage: ./validate-gitops-yaml.sh <file.yml> [--type default|fleet|unassigned]
#
# If --type is not specified, attempts to auto-detect from file name/content.

set -euo pipefail

FILE="${1:?Usage: validate-gitops-yaml.sh <file.yml> [--type default|fleet|unassigned]}"
TYPE="${2:-auto}"

if [ ! -f "$FILE" ]; then
  echo "ERROR: File not found: $FILE"
  exit 1
fi

ERRORS=0
WARNINGS=0

echo "Validating: $FILE"
echo "---"

# Auto-detect file type
if [ "$TYPE" = "auto" ] || [ "$TYPE" = "--type" ]; then
  if [ "$TYPE" = "--type" ]; then
    TYPE="${3:-auto}"
  fi
fi

if [ "$TYPE" = "auto" ]; then
  BASENAME=$(basename "$FILE")
  if [ "$BASENAME" = "default.yml" ]; then
    TYPE="default"
  elif [ "$BASENAME" = "unassigned.yml" ] || [ "$BASENAME" = "no-team.yml" ]; then
    TYPE="unassigned"
  elif grep -q '^name:' "$FILE" 2>/dev/null; then
    TYPE="fleet"
  else
    echo "WARN: Could not auto-detect file type. Use --type to specify."
    TYPE="fleet"
  fi
fi

echo "File type: $TYPE"

# Check for deprecated file name
if [ "$(basename "$FILE")" = "no-team.yml" ]; then
  echo "WARN: no-team.yml is deprecated since v4.82. Rename to unassigned.yml"
  WARNINGS=$((WARNINGS + 1))
fi

# Check for deprecated team_settings key
if grep -q '^team_settings:' "$FILE" 2>/dev/null; then
  echo "WARN: 'team_settings:' is deprecated since v4.82. Use 'settings:' instead"
  WARNINGS=$((WARNINGS + 1))
fi

# Check for deprecated queries key
if grep -q '^queries:' "$FILE" 2>/dev/null; then
  echo "WARN: 'queries:' is deprecated since v4.82. Use 'reports:' instead"
  WARNINGS=$((WARNINGS + 1))
fi

# Define required keys per type
case "$TYPE" in
  default)
    REQUIRED_KEYS="policies reports agent_options controls org_settings"
    FORBIDDEN_KEYS=""
    ;;
  fleet)
    REQUIRED_KEYS="name policies reports agent_options controls software settings"
    FORBIDDEN_KEYS="org_settings"
    ;;
  unassigned)
    REQUIRED_KEYS="name policies controls software settings"
    FORBIDDEN_KEYS="org_settings reports agent_options labels"
    ;;
esac

# Check required top-level keys
for key in $REQUIRED_KEYS; do
  if ! grep -q "^${key}:" "$FILE" 2>/dev/null; then
    # Also check deprecated aliases
    if [ "$key" = "settings" ] && grep -q "^team_settings:" "$FILE" 2>/dev/null; then
      continue  # deprecated but present
    fi
    if [ "$key" = "reports" ] && grep -q "^queries:" "$FILE" 2>/dev/null; then
      continue  # deprecated but present
    fi
    echo "FAIL: Missing required key '$key' — this will silently reset/delete resources"
    ERRORS=$((ERRORS + 1))
  fi
done

# Check forbidden keys for this file type
for key in $FORBIDDEN_KEYS; do
  if grep -q "^${key}:" "$FILE" 2>/dev/null; then
    echo "FAIL: Key '$key' is not supported in $TYPE files"
    ERRORS=$((ERRORS + 1))
  fi
done

# Check label consistency: labels referenced in policies/software should be defined
if grep -q 'labels_include_any\|labels_exclude_any' "$FILE" 2>/dev/null; then
  if ! grep -q '^labels:' "$FILE" 2>/dev/null; then
    echo "WARN: File references labels (labels_include_any/labels_exclude_any) but has no 'labels:' section"
    WARNINGS=$((WARNINGS + 1))
  fi
fi

# Check for unquoted numeric values that should be strings
if grep -E '^\s+app_store_id:\s+[0-9]+\s*$' "$FILE" 2>/dev/null; then
  echo "WARN: app_store_id should be quoted (e.g., \"1091189122\")"
  WARNINGS=$((WARNINGS + 1))
fi

if grep -E '^\s+(minimum_)?version:\s+[0-9]+\.[0-9]+' "$FILE" 2>/dev/null | grep -vq '"' 2>/dev/null; then
  echo "WARN: Version numbers should be quoted (e.g., \"15.4\")"
  WARNINGS=$((WARNINGS + 1))
fi

echo "---"
if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
  echo "PASS: No issues found"
elif [ "$ERRORS" -eq 0 ]; then
  echo "PASS with $WARNINGS warning(s)"
else
  echo "FOUND: $ERRORS error(s), $WARNINGS warning(s)"
fi

exit "$ERRORS"
