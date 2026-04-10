#!/bin/zsh
# Set and validate GH secrets between local .env and GitHub Secrets
# Usful for GitOps setup
# Copyright (c) 2026 Henry Stamerjohann, for Fleet Device Management
#
#
set -euo pipefail

# REPO="headmin/fleet-test-gitops"
REPO="<github_username>/<name_of_repo>"
ENV_FILE="${0:A:h}/.env"

usage() {
    echo "Usage: ${0:t} <apply|validate>"
    echo ""
    echo "  apply     Push all secrets from .env to GitHub Actions"
    echo "  validate  Compare .env keys against GitHub Actions secrets"
    exit 1
}

[[ $# -eq 1 ]] || usage

parse_env() {
    local keys=() values=()
    while IFS= read -r line || [[ -n "$line" ]]; do
        [[ -z "$line" || "$line" == \#* ]] && continue
        keys+=("${line%%=*}")
        values+=("${line#*=}")
    done < "$ENV_FILE"
    # return via global arrays
    _keys=("${keys[@]}")
    _values=("${values[@]}")
}

cmd_apply() {
    echo "Pushing secrets from ${ENV_FILE} to ${REPO}..."
    echo ""

    parse_env
    local failed=0

    for i in {1..${#_keys}}; do
        local key="${_keys[$i]}"
        local value="${_values[$i]}"
        printf "  %-45s" "$key"
        if echo "$value" | gh secret set "$key" --repo "$REPO" 2>/dev/null; then
            echo "ok"
        else
            echo "FAILED"
            ((failed++))
        fi
    done

    echo ""
    if (( failed == 0 )); then
        echo "All ${#_keys} secrets applied."
    else
        echo "${failed} of ${#_keys} secrets failed."
        exit 1
    fi
}

cmd_validate() {
    echo "Validating secrets on ${REPO} against ${ENV_FILE}..."
    echo ""

    parse_env
    local remote_keys=("${(@f)$(gh secret list --repo "$REPO" --json name -q '.[].name')}")
    local missing=0 extra=0

    # Check each .env key exists in GitHub
    for key in "${_keys[@]}"; do
        printf "  %-45s" "$key"
        if (( ${remote_keys[(Ie)$key]} )); then
            echo "ok"
        else
            echo "MISSING"
            ((missing++))
        fi
    done

    # Check for extra secrets in GitHub not in .env
    for rkey in "${remote_keys[@]}"; do
        if ! (( ${_keys[(Ie)$rkey]} )); then
            printf "  %-45s%s\n" "$rkey" "EXTRA (not in .env)"
            ((extra++))
        fi
    done

    echo ""
    echo "${#_keys} expected, ${#remote_keys} on GitHub."
    (( missing )) && echo "${missing} secret(s) missing from GitHub."
    (( extra ))   && echo "${extra} extra secret(s) on GitHub not in .env."
    if (( missing == 0 && extra == 0 )); then
        echo "All secrets match."
    else
        exit 1
    fi
}

case "$1" in
    apply)    cmd_apply    ;;
    validate) cmd_validate ;;
    *)        usage        ;;
esac
