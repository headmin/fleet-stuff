#!/usr/bin/env zsh

# smallstep-url-transform.zsh
# Transform Smallstep SCEP and Challenge URLs to Fleet configuration values.
# Provides a helper to setsp outlined in: https://fleetdm.com/guides/connect-end-user-to-wifi-with-certificate#smallstep
# Collects all inputs first, then outputs results.
# copyright 2026 Henry Stamerjohann, for Fleet Device Management https://fleetdm.com/

function trim() {
    local s="${(j::)@}"
    s="${s#"${s%%[![:space:]]*}"}"
    s="${s%"${s##*[![:space:]]}"}"
    echo "$s"
}

function validate_url() {
    local url="$1"
    local name="$2"
    if [[ -z "$url" ]]; then
        echo "$name cannot be empty. Try again."
        return 1
    fi
    if [[ ! "$url" =~ ^https?:// ]]; then
        echo "Please include scheme (https://). Try again."
        return 1
    fi
    return 0
}

function parse_scep_url() {
    local url="$1"

    # Remove trailing /pkiclient.exe and slash
    url="${url%/pkiclient.exe}"
    url="${url%/}"

    # Pattern: https://agents.<TEAM>.ca.smallstep.com/scep/<INTEGRATION_ID>
    # Team name can contain hyphens (e.g., my-company)
    if [[ "$url" =~ ^https://agents\.([^/]+)\.ca\.smallstep\.com/scep/([^/]+)$ ]]; then
        echo "${match[1]}"
        echo "${match[2]}"
        return 0
    fi

    # Pattern: https://agents.<TEAM>.smallstep.com/scep/<INTEGRATION_ID>
    if [[ "$url" =~ ^https://agents\.([^/]+)\.smallstep\.com/scep/([^/]+)$ ]]; then
        echo "${match[1]}"
        echo "${match[2]}"
        return 0
    fi

    return 1
}

function parse_challenge_url() {
    local url="$1"

    # Remove trailing slash
    url="${url%/}"

    # Pattern: https://<TEAM>.scep.smallstep.com/<MDM_TYPE>/<UUID>/challenge (Fleet/Jamf/etc format)
    if [[ "$url" =~ ^https://([^/]+)\.scep\.smallstep\.com/[^/]+/([^/]+)/challenge$ ]]; then
        echo "${match[1]}"
        echo "${match[2]}"
        return 0
    fi

    # Pattern: https://agents.<TEAM>.ca.smallstep.com/challenge/<INTEGRATION_ID>/<TOKEN>
    if [[ "$url" =~ ^https://agents\.([^/]+)\.ca\.smallstep\.com/challenge/([^/]+)/([^/]+)$ ]]; then
        echo "${match[1]}"
        echo "${match[2]}"
        return 0
    fi

    # Pattern: https://agents.<TEAM>.ca.smallstep.com/challenge/<INTEGRATION_ID>
    if [[ "$url" =~ ^https://agents\.([^/]+)\.ca\.smallstep\.com/challenge/([^/]+)$ ]]; then
        echo "${match[1]}"
        echo "${match[2]}"
        return 0
    fi

    # Pattern: https://agents.<TEAM>.smallstep.com/challenge/<INTEGRATION_ID>
    if [[ "$url" =~ ^https://agents\.([^/]+)\.smallstep\.com/challenge/([^/]+) ]]; then
        echo "${match[1]}"
        echo "${match[2]}"
        return 0
    fi

    return 1
}

echo "Smallstep -> Fleet SCEP URL transformer"
echo

# ============================================
# COLLECT ALL INPUTS FIRST
# ============================================

# 1. Read Smallstep SCEP URL
while true; do
    read -r "?Enter Smallstep SCEP URL (e.g., https://agents.TEAM.ca.smallstep.com/scep/INTEGRATION_ID): " scep_url
    scep_url="$(trim "$scep_url")"
    if validate_url "$scep_url" "SCEP URL"; then
        break
    fi
done

# 2. Read Smallstep Challenge URL
while true; do
    read -r "?Enter Smallstep Challenge URL (e.g., https://agents.TEAM.ca.smallstep.com/challenge/INTEGRATION_ID/TOKEN): " challenge_url
    challenge_url="$(trim "$challenge_url")"
    if validate_url "$challenge_url" "Challenge URL"; then
        break
    fi
done

# ============================================
# PROCESS URL INPUTS
# ============================================

# Parse SCEP URL
if parsed_scep=($(parse_scep_url "$scep_url")); then
    team_name="${parsed_scep[1]}"
    integration_id="${parsed_scep[2]}"
    scep_parse_ok=true
else
    scep_parse_ok=false
fi

# Parse Challenge URL
if parsed_challenge=($(parse_challenge_url "$challenge_url")); then
    challenge_team="${parsed_challenge[1]}"
    challenge_integration="${parsed_challenge[2]}"
    challenge_parse_ok=true
else
    challenge_parse_ok=false
fi

# If SCEP parse failed, try to use challenge URL info or ask manually
if [[ "$scep_parse_ok" != "true" ]]; then
    if [[ "$challenge_parse_ok" == "true" ]]; then
        team_name="$challenge_team"
        integration_id="$challenge_integration"
    else
        echo
        echo "Could not automatically parse team and integration ID from the provided URLs."
        echo "Please enter them manually."
        while true; do
            read -r "?Enter SMALLSTEP_TEAM_NAME (e.g., myteam or my-team): " team_name
            team_name="$(trim "$team_name")"
            [[ -n "$team_name" ]] && break
            echo "Team name cannot be empty."
        done
        while true; do
            read -r "?Enter INTEGRATION_ID: " integration_id
            integration_id="$(trim "$integration_id")"
            [[ -n "$integration_id" ]] && break
            echo "Integration ID cannot be empty."
        done
    fi
fi

# Build Fleet proxy URL (same for all CA names)
fleet_proxy_url="https://${team_name}.scep.smallstep.com/p/agents/${integration_id}"

# ============================================
# CA NAME LOOP - repeat output for different CA names
# ============================================

while true; do
    # 3. Read CA name (default: SMALLSTEP_CA)
    echo
    read -r "?Enter Fleet CA name [SMALLSTEP_CA]: " ca_name
    ca_name="$(trim "$ca_name")"
    if [[ -z "$ca_name" ]]; then
        ca_name="SMALLSTEP_CA"
    fi

    # Sanitize CA name to uppercase snake_case
    ca_name_upper="${ca_name// /_}"
    ca_name_upper="${ca_name_upper//-/_}"
    ca_name_upper="${(U)ca_name_upper}"

    # Build Fleet variable names
    var_prefix="FLEET_VAR_SMALLSTEP_SCEP"
    challenge_var="\$${var_prefix}_CHALLENGE_${ca_name_upper}"
    proxy_var="\$${var_prefix}_PROXY_URL_${ca_name_upper}"
    scep_renewal_var="\$FLEET_VAR_SCEP_RENEWAL_ID"

    # ============================================
    # ASK ABOUT MOBILECONFIG GENERATION
    # ============================================

    read -r "?Generate mobileconfig file? (y/N): " gen_config
    gen_config="$(trim "$gen_config")"
    generate_config=false

    if [[ "${(L)gen_config}" == "y" || "${(L)gen_config}" == "yes" ]]; then
        generate_config=true

        # Ask for PayloadIdentifier
        default_identifier="com.fleetdm.scep.${(L)ca_name_upper}"
        read -r "?Enter PayloadIdentifier [${default_identifier}]: " payload_id
        payload_id="$(trim "$payload_id")"
        if [[ -z "$payload_id" ]]; then
            payload_id="$default_identifier"
        fi

        # Generate output filename
        safe_ca_name="${(L)ca_name_upper}"
        output_file="smallstep-scep-${safe_ca_name}.mobileconfig"

        read -r "?Output filename [${output_file}]: " custom_filename
        custom_filename="$(trim "$custom_filename")"
        if [[ -n "$custom_filename" ]]; then
            output_file="$custom_filename"
        fi

        # Generate UUIDs
        root_uuid_hash=$(echo -n "${payload_id}" | md5)
        root_uuid="${root_uuid_hash:0:8}-${root_uuid_hash:8:4}-${root_uuid_hash:12:4}-${root_uuid_hash:16:4}-${root_uuid_hash:20:12}"
        root_uuid="${(U)root_uuid}"

        scep_uuid_hash=$(echo -n "com.apple.security.scep.${payload_id}" | md5)
        scep_uuid="${scep_uuid_hash:0:8}-${scep_uuid_hash:8:4}-${scep_uuid_hash:12:4}-${scep_uuid_hash:16:4}-${scep_uuid_hash:20:12}"
        scep_uuid="${(U)scep_uuid}"
    fi

    # ============================================
    # OUTPUT RESULTS
    # ============================================

    echo
    echo "============================================"
    echo "Fleet CA Settings (copy-paste these values)"
    echo "============================================"
    echo
    echo "Name"
    echo "$ca_name_upper"
    echo
    echo "SCEP URL"
    echo "$fleet_proxy_url"
    echo
    echo "Challenge URL"
    echo "$challenge_url"
    echo
    echo "--------------------------------------------"
    echo "Fleet Variable Names (for profiles)"
    echo "--------------------------------------------"
    echo
    echo "Challenge:   $challenge_var"
    echo "Proxy URL:   $proxy_var"
    echo "Renewal ID:  $scep_renewal_var"
    echo
    echo "--------------------------------------------"
    echo "Notes"
    echo "--------------------------------------------"
    echo "* Add $scep_renewal_var to the OU field for automatic certificate renewal."
    echo "* Original Smallstep SCEP URL: $scep_url"
    echo "* Detected team: $team_name, integration: $integration_id"

    # ============================================
    # GENERATE MOBILECONFIG IF REQUESTED
    # ============================================

    if [[ "$generate_config" == "true" ]]; then
        # Write mobileconfig file
        cat > "$output_file" << MOBILECONFIG_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <array>
        <dict>
            <key>PayloadContent</key>
            <dict>
                <key>Challenge</key>
                <string>${challenge_var}</string>
                <key>Key Type</key>
                <string>RSA</string>
                <key>Key Usage</key>
                <integer>5</integer>
                <key>Keysize</key>
                <integer>2048</integer>
                <key>Subject</key>
                <array>
                    <array>
                        <array>
                            <string>O</string>
                            <string>Fleet</string>
                        </array>
                    </array>
                    <array>
                        <array>
                            <string>CN</string>
                            <string>%HardwareUUID%</string>
                        </array>
                    </array>
                    <array>
                        <array>
                            <string>OU</string>
                            <string>${scep_renewal_var}</string>
                        </array>
                    </array>
                </array>
                <key>URL</key>
                <string>${proxy_var}</string>
            </dict>
            <key>PayloadDisplayName</key>
            <string>SCEP (${ca_name_upper})</string>
            <key>PayloadIdentifier</key>
            <string>com.apple.security.scep.${scep_uuid}</string>
            <key>PayloadType</key>
            <string>com.apple.security.scep</string>
            <key>PayloadUUID</key>
            <string>${scep_uuid}</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
        </dict>
    </array>
    <key>PayloadDisplayName</key>
    <string>Smallstep SCEP - ${ca_name_upper}</string>
    <key>PayloadIdentifier</key>
    <string>${payload_id}</string>
    <key>PayloadType</key>
    <string>Configuration</string>
    <key>PayloadUUID</key>
    <string>${root_uuid}</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
</dict>
</plist>
MOBILECONFIG_EOF

        echo
        echo "--------------------------------------------"
        echo "Generated mobileconfig"
        echo "--------------------------------------------"
        echo
        echo "  File: $output_file"
        echo
        echo "  Root PayloadIdentifier: $payload_id"
        echo "  Root PayloadUUID:       $root_uuid"
        echo "  SCEP PayloadIdentifier: com.apple.security.scep.${scep_uuid}"
        echo "  SCEP PayloadUUID:       $scep_uuid"
    fi

    echo
    # Ask if user wants to try another CA name
    read -r "?Try another CA name? (y/N): " again
    again="$(trim "$again")"
    if [[ "${(L)again}" != "y" && "${(L)again}" != "yes" ]]; then
        break
    fi
done

echo "Done."
