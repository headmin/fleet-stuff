#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
# ]
# description = """
# Smallstep Profile Generator - Generate Fleet mobileconfig profiles for Smallstep CA.
# Transforms Smallstep SCEP URLs to Fleet proxy URLs and generates Trust, SCEP, WiFi, and VPN profiles.
# """
# ///

import marimo

__generated_with = "0.19.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import hashlib
    import base64
    import re
    import os
    from pathlib import Path
    from datetime import datetime
    import marimo as mo

    return hashlib, base64, re, os, Path, datetime, mo


@app.cell
def _(mo):
    # Fleet's official article styling with maximum CSS specificity for marimo
    fleet_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Source+Code+Pro:wght@400&display=swap');

    /* Fleet DM CSS Custom Properties */
    :root {
        /* Core Fleet Black Scale */
        --fleet-black: #192147;
        --fleet-black-75: #515774;
        --fleet-black-50: #8b8fa2;
        --fleet-black-33: #B3B6C1;
        --fleet-black-25: #C5C7D1;
        --fleet-black-10: #E2E4EA;

        /* Vibrant Blue Scale */
        --fleet-blue: #6A67FE;
        --fleet-blue-50: #B4B2FE;
        --fleet-blue-25: #D9D9FE;
        --fleet-blue-10: #F1F0FF;

        /* Utility Colors */
        --fleet-brand: #14acc2;
        --fleet-red: #FF5C83;
        --fleet-green: #009A7D;
        --fleet-off-white: #F9FAFC;
        --fleet-white: #fff;
        --fleet-callout-bg: #F7F7FC;

        /* Typography */
        --font-main: 'Inter', sans-serif;
        --font-code: 'Source Code Pro', monospace;
        --font-weight-normal: 400;
        --font-weight-bold: 700;
    }

    /* MAXIMUM SPECIFICITY OVERRIDES FOR MARIMO */
    html body #root .App .App-content * {
        font-family: 'Inter', sans-serif !important;
        background: transparent !important;
    }

    html body #root .App .App-content {
        font-family: 'Inter', sans-serif !important;
        color: #515774 !important;
        background: #fff !important;
        max-width: 800px !important;
        margin: 0 auto !important;
        padding: 40px 20px !important;
        font-size: 16px !important;
        line-height: 150% !important;
    }

    /* Typography - Headings */
    html body #root .App .App-content h1,
    html body #root .App .App-content h2,
    html body #root .App .App-content h3,
    html body #root .App .App-content h4,
    html body #root h1,
    html body #root h2,
    html body #root h3,
    html body #root h4 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        color: #192147 !important;
        line-height: 120% !important;
    }

    html body #root h1 { font-size: 36px !important; margin-top: 0 !important; margin-bottom: 24px !important; }
    html body #root h2 { font-size: 24px !important; margin-top: 64px !important; margin-bottom: 32px !important; }
    html body #root h3 { font-size: 20px !important; margin-top: 48px !important; margin-bottom: 32px !important; }

    /* Paragraphs */
    html body #root p {
        font-size: 16px !important;
        line-height: 150% !important;
        color: #515774 !important;
        margin-bottom: 24px !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Links */
    a { color: var(--fleet-blue) !important; text-decoration: none !important; }
    a:hover { text-decoration: underline !important; }

    /* Code Styling */
    code {
        font-family: var(--font-code) !important;
        font-size: 13px !important;
        background-color: var(--fleet-blue-10) !important;
        color: var(--fleet-black) !important;
        padding: 4px 8px !important;
        border-radius: 4px !important;
    }

    pre {
        background-color: var(--fleet-off-white) !important;
        border: 1px solid var(--fleet-black-10) !important;
        border-radius: 6px !important;
        padding: 24px !important;
        margin: 0 0 40px !important;
        overflow-x: auto !important;
    }

    pre code {
        background: none !important;
        padding: 0 !important;
        font-size: 13px !important;
        line-height: 20px !important;
    }

    /* Tables */
    table {
        width: 100% !important;
        border: 1px solid var(--fleet-black-10) !important;
        border-collapse: collapse !important;
        margin-bottom: 32px !important;
    }

    th, td {
        border: 1px solid var(--fleet-black-10) !important;
        padding: 8px !important;
        text-align: left !important;
    }

    th {
        font-weight: 700 !important;
        color: var(--fleet-black) !important;
        background-color: var(--fleet-off-white) !important;
    }

    /* Callout Boxes */
    .fleet-note, .fleet-tip, .fleet-warning {
        margin: 16px 0 32px !important;
        padding: 16px !important;
        border-radius: 8px !important;
        font-size: 16px !important;
        line-height: 150% !important;
    }

    .fleet-note {
        background-color: var(--fleet-callout-bg) !important;
        border: 1px solid var(--fleet-blue-50) !important;
    }
    .fleet-note::before { content: "Note: " !important; font-weight: 700 !important; color: var(--fleet-black) !important; }

    .fleet-tip {
        background-color: #F0FDF9 !important;
        border: 1px solid var(--fleet-green) !important;
    }
    .fleet-tip::before { content: "Tip: " !important; font-weight: 700 !important; color: var(--fleet-green) !important; }

    .fleet-warning {
        background-color: #FFF5F7 !important;
        border: 1px solid var(--fleet-red) !important;
    }
    .fleet-warning::before { content: "Warning: " !important; font-weight: 700 !important; color: var(--fleet-red) !important; }

    .fleet-success {
        background-color: #F0FDF9 !important;
        border: 1px solid var(--fleet-green) !important;
        margin: 16px 0 32px !important;
        padding: 16px !important;
        border-radius: 8px !important;
    }
    .fleet-success::before { content: "Success: " !important; font-weight: 700 !important; color: var(--fleet-green) !important; }

    .fleet-error {
        background-color: #FFF5F7 !important;
        border: 1px solid var(--fleet-red) !important;
        margin: 16px 0 32px !important;
        padding: 16px !important;
        border-radius: 8px !important;
    }
    .fleet-error::before { content: "Error: " !important; font-weight: 700 !important; color: var(--fleet-red) !important; }

    /* Input styling */
    input[type="text"], input[type="password"], textarea {
        font-family: var(--font-main) !important;
        font-size: 16px !important;
        color: var(--fleet-black) !important;
        background: var(--fleet-white) !important;
        border: 1px solid var(--fleet-black-25) !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
    }

    input:focus, textarea:focus {
        outline: none !important;
        border-color: var(--fleet-blue) !important;
        box-shadow: 0 0 0 2px var(--fleet-blue-25) !important;
    }

    /* Meta text */
    .meta {
        font-size: 14px !important;
        color: #8b8fa2 !important;
        margin-top: 8px !important;
        margin-bottom: 32px !important;
    }

    hr {
        border: none !important;
        border-top: 1px solid var(--fleet-black-10) !important;
        margin: 48px 0 !important;
    }
    </style>
    """
    mo.Html(fleet_css)


@app.cell
def _(mo):
    def fleet_note(content):
        return mo.Html(f'<div class="fleet-note">{content}</div>')

    def fleet_tip(content):
        return mo.Html(f'<div class="fleet-tip">{content}</div>')

    def fleet_warning(content):
        return mo.Html(f'<div class="fleet-warning">{content}</div>')

    def fleet_success(content):
        return mo.Html(f'<div class="fleet-success">{content}</div>')

    def fleet_error(content):
        return mo.Html(f'<div class="fleet-error">{content}</div>')

    return fleet_note, fleet_tip, fleet_warning, fleet_success, fleet_error


@app.cell
def _(mo):
    mo.md("""
# Smallstep Profile Generator

<p class="meta">Generate Fleet mobileconfig profiles for Smallstep CA integration</p>

This tool transforms Smallstep SCEP URLs to Fleet proxy URLs and generates configuration profiles for:
- **Trust Profile** — Install CA certificates as trusted roots
- **SCEP Profile** — Issue device identity certificates
- **WiFi Profile** — Enterprise WiFi with EAP-TLS authentication
- **VPN Profile** — IKEv2 VPN with certificate authentication
""")


# ============================================================================
# SECTION: Helper Functions
# ============================================================================


@app.cell
def _(hashlib, re):
    def generate_uuid(input_string: str) -> str:
        """Generate a deterministic UUID from input string using MD5."""
        hash_bytes = hashlib.md5(input_string.encode()).hexdigest()
        return f"{hash_bytes[0:8]}-{hash_bytes[8:12]}-{hash_bytes[12:16]}-{hash_bytes[16:20]}-{hash_bytes[20:32]}".upper()

    def normalize_ca_name(name: str) -> str:
        """Normalize CA name for use in identifiers."""
        name = name.replace(" ", "_").replace("-", "_")
        return name.upper()

    def parse_smallstep_urls(scep_url: str, challenge_url: str) -> tuple[str, str]:
        """Parse Smallstep URLs to extract team name and integration ID."""
        # Clean URLs
        scep_url = scep_url.rstrip("/").removesuffix("/pkiclient.exe")
        challenge_url = challenge_url.rstrip("/")

        # Try SCEP URL patterns
        scep_patterns = [
            r"^https://agents\.([^/]+)\.ca\.smallstep\.com/scep/([^/]+)$",
            r"^https://agents\.([^/]+)\.smallstep\.com/scep/([^/]+)$",
        ]

        for pattern in scep_patterns:
            match = re.match(pattern, scep_url)
            if match:
                return match.group(1), match.group(2)

        # Try Challenge URL patterns
        challenge_patterns = [
            r"^https://([^/]+)\.scep\.smallstep\.com/[^/]+/([^/]+)/challenge$",
            r"^https://agents\.([^/]+)\.ca\.smallstep\.com/challenge/([^/]+)",
            r"^https://agents\.([^/]+)\.smallstep\.com/challenge/([^/]+)",
        ]

        for pattern in challenge_patterns:
            match = re.match(pattern, challenge_url)
            if match:
                return match.group(1), match.group(2)

        return "", ""

    def pem_to_base64(pem: str) -> str:
        """Extract base64 content from PEM certificate."""
        lines = pem.strip().split("\n")
        b64_lines = [
            line.strip()
            for line in lines
            if line.strip() and "BEGIN CERTIFICATE" not in line and "END CERTIFICATE" not in line
        ]
        return "".join(b64_lines)

    def xml_escape(s: str) -> str:
        """Escape special XML characters."""
        return (
            s.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("'", "&apos;")
            .replace('"', "&quot;")
        )

    return generate_uuid, normalize_ca_name, parse_smallstep_urls, pem_to_base64, xml_escape


# ============================================================================
# SECTION: URL Configuration
# ============================================================================


@app.cell
def _(mo):
    mo.md("""
## Step 1: Smallstep URLs

Enter your Smallstep SCEP and Challenge URLs from the Smallstep dashboard.
""")


@app.cell
def _(mo):
    scep_url_input = mo.ui.text(
        placeholder="https://agents.TEAM.ca.smallstep.com/scep/INTEGRATION_ID",
        label="Smallstep SCEP URL",
        full_width=True,
    )

    challenge_url_input = mo.ui.text(
        placeholder="https://TEAM.scep.smallstep.com/p/agents/INTEGRATION_ID/challenge",
        label="Smallstep Challenge URL",
        full_width=True,
    )

    mo.vstack([scep_url_input, challenge_url_input])

    return scep_url_input, challenge_url_input


@app.cell
def _(mo, scep_url_input, challenge_url_input, parse_smallstep_urls, fleet_success, fleet_warning):
    _scep = scep_url_input.value or ""
    _challenge = challenge_url_input.value or ""

    team_name, integration_id = parse_smallstep_urls(_scep, _challenge)

    if team_name and integration_id:
        fleet_proxy_url = f"https://{team_name}.scep.smallstep.com/p/agents/{integration_id}"
        _result = mo.vstack([
            fleet_success("URLs parsed successfully!"),
            mo.md(f"""
| Field | Value |
|-------|-------|
| **Team Name** | `{team_name}` |
| **Integration ID** | `{integration_id}` |
| **Fleet Proxy URL** | `{fleet_proxy_url}` |
"""),
        ])
    elif _scep or _challenge:
        fleet_proxy_url = ""
        _result = fleet_warning("Could not parse team and integration ID from URLs. Please check the format.")
    else:
        fleet_proxy_url = ""
        _result = mo.md("")

    _result

    return team_name, integration_id, fleet_proxy_url


# ============================================================================
# SECTION: CA Configuration
# ============================================================================


@app.cell
def _(mo):
    mo.md("""
## Step 2: CA Configuration

Configure your Certificate Authority name and optionally upload CA certificates.
""")


@app.cell
def _(mo):
    ca_name_input = mo.ui.text(
        placeholder="SMALLSTEP_CA",
        label="Fleet CA Name",
        value="SMALLSTEP_CA",
        full_width=True,
    )

    payload_id_input = mo.ui.text(
        placeholder="com.fleetdm.scep.smallstep_ca",
        label="Payload Identifier (optional)",
        full_width=True,
    )

    mo.vstack([ca_name_input, payload_id_input])

    return ca_name_input, payload_id_input


@app.cell
def _(mo):
    mo.md("""
### CA Certificates (Optional)

Upload your Smallstep CA certificates to generate Trust profiles.
Download from Smallstep dashboard or use: `step ca root root_ca.crt --ca-url <URL> --fingerprint <FP>`
""")


@app.cell
def _(mo):
    root_cert_input = mo.ui.file(
        label="Root CA Certificate (PEM)",
        filetypes=[".pem", ".crt", ".cer"],
        kind="area",
    )

    intermediate_cert_input = mo.ui.file(
        label="Intermediate CA Certificate (PEM, optional)",
        filetypes=[".pem", ".crt", ".cer"],
        kind="area",
    )

    radius_cert_input = mo.ui.file(
        label="RADIUS CA Certificate (PEM, optional - for enterprise WiFi)",
        filetypes=[".pem", ".crt", ".cer"],
        kind="area",
    )

    mo.vstack([root_cert_input, intermediate_cert_input, radius_cert_input])

    return root_cert_input, intermediate_cert_input, radius_cert_input


@app.cell
def _(mo, root_cert_input, intermediate_cert_input, radius_cert_input, fleet_tip):
    def _extract_pem(file_obj) -> str:
        if file_obj is None or len(file_obj) == 0:
            return ""
        try:
            content = file_obj[0].contents.decode("utf-8")
            if "BEGIN CERTIFICATE" in content:
                return content
        except Exception:
            pass
        return ""

    root_cert_pem = _extract_pem(root_cert_input.value)
    intermediate_cert_pem = _extract_pem(intermediate_cert_input.value)
    radius_cert_pem = _extract_pem(radius_cert_input.value)

    _certs_loaded = []
    if root_cert_pem:
        _certs_loaded.append("Root CA")
    if intermediate_cert_pem:
        _certs_loaded.append("Intermediate CA")
    if radius_cert_pem:
        _certs_loaded.append("RADIUS CA")

    if _certs_loaded:
        fleet_tip(f"Loaded certificates: {', '.join(_certs_loaded)}")
    else:
        mo.md("")

    return root_cert_pem, intermediate_cert_pem, radius_cert_pem


# ============================================================================
# SECTION: Computed Values
# ============================================================================


@app.cell
def _(
    ca_name_input,
    payload_id_input,
    normalize_ca_name,
    generate_uuid,
    challenge_url_input,
    fleet_proxy_url,
):
    # Compute normalized CA name
    ca_name = normalize_ca_name(ca_name_input.value or "SMALLSTEP_CA")

    # Compute payload ID
    payload_id = payload_id_input.value or f"com.fleetdm.scep.{ca_name.lower()}"

    # Generate UUIDs
    profile_uuid = generate_uuid(payload_id)
    scep_uuid = generate_uuid(f"com.apple.security.scep.{payload_id}")
    trust_profile_uuid = generate_uuid(f"trust.{payload_id}")
    root_cert_uuid = generate_uuid(f"com.apple.security.root.{payload_id}")
    intermediate_cert_uuid = generate_uuid(f"com.apple.security.pkcs1.intermediate.{payload_id}")
    radius_cert_uuid = generate_uuid(f"com.apple.security.root.radius.{payload_id}")

    # Fleet variable names
    var_prefix = "FLEET_VAR_SMALLSTEP_SCEP"
    challenge_var = f"${var_prefix}_CHALLENGE_{ca_name}"
    proxy_var = f"${var_prefix}_PROXY_URL_{ca_name}"
    renewal_var = "$FLEET_VAR_SCEP_RENEWAL_ID"

    # Store challenge URL for reference
    challenge_url = challenge_url_input.value or ""

    return (
        ca_name,
        payload_id,
        profile_uuid,
        scep_uuid,
        trust_profile_uuid,
        root_cert_uuid,
        intermediate_cert_uuid,
        radius_cert_uuid,
        challenge_var,
        proxy_var,
        renewal_var,
        challenge_url,
    )


# ============================================================================
# SECTION: Fleet Configuration Output
# ============================================================================


@app.cell
def _(mo):
    mo.md("""
## Step 3: Fleet Configuration

Copy these values to configure the CA in Fleet.
""")


@app.cell
def _(
    mo,
    ca_name,
    fleet_proxy_url,
    challenge_url,
    challenge_var,
    proxy_var,
    renewal_var,
    fleet_note,
):
    if fleet_proxy_url:
        mo.vstack([
            mo.md(f"""
### Fleet CA Settings

| Setting | Value |
|---------|-------|
| **Name** | `{ca_name}` |
| **SCEP URL** | `{fleet_proxy_url}` |
| **Challenge URL** | `{challenge_url}` |

### Fleet Variable Names (for profiles)

| Variable | Name |
|----------|------|
| **Challenge** | `{challenge_var}` |
| **Proxy URL** | `{proxy_var}` |
| **Renewal ID** | `{renewal_var}` |
"""),
            fleet_note(f"Add <code>{renewal_var}</code> to the OU field for automatic certificate renewal."),
        ])
    else:
        mo.md("*Enter Smallstep URLs above to see Fleet configuration.*")


# ============================================================================
# SECTION: Profile Generation
# ============================================================================


@app.cell
def _(mo):
    mo.md("""
## Step 4: Generate Profiles

Select which profiles to generate.
""")


@app.cell
def _(mo, root_cert_pem):
    gen_scep = mo.ui.checkbox(label="SCEP Profile (device identity certificate)", value=True)
    gen_trust = mo.ui.checkbox(
        label="Trust Profile (CA certificates)",
        value=bool(root_cert_pem),
    )
    gen_wifi = mo.ui.checkbox(label="WiFi + SCEP Profile (enterprise WiFi with EAP-TLS)")
    gen_vpn = mo.ui.checkbox(label="VPN Profile (IKEv2 with certificate auth)")

    mo.vstack([gen_scep, gen_trust, gen_wifi, gen_vpn])

    return gen_scep, gen_trust, gen_wifi, gen_vpn


# ============================================================================
# SECTION: WiFi Configuration (conditional)
# ============================================================================


@app.cell
def _(mo, gen_wifi):
    if gen_wifi.value:
        mo.md("""
### WiFi Configuration
""")
    else:
        mo.md("")


@app.cell
def _(mo, gen_wifi):
    if gen_wifi.value:
        wifi_ssid_input = mo.ui.text(
            placeholder="Corp-WiFi",
            label="WiFi SSID (network name)",
            full_width=True,
        )
        wifi_hidden = mo.ui.checkbox(label="Hidden network")
        wifi_auto_join = mo.ui.checkbox(label="Auto-join enabled", value=True)
        wifi_encryption = mo.ui.dropdown(
            options=["WPA2Enterprise", "WPA3", "Any"],
            value="Any",
            label="Encryption type",
        )
        wifi_trusted_servers = mo.ui.text(
            placeholder="radius.example.com, radius2.example.com",
            label="Trusted RADIUS server names (comma-separated, optional)",
            full_width=True,
        )
        _wifi_form = mo.vstack([
            wifi_ssid_input,
            mo.hstack([wifi_hidden, wifi_auto_join]),
            wifi_encryption,
            wifi_trusted_servers,
        ])
    else:
        wifi_ssid_input = None
        wifi_hidden = None
        wifi_auto_join = None
        wifi_encryption = None
        wifi_trusted_servers = None
        _wifi_form = mo.md("")

    _wifi_form

    return wifi_ssid_input, wifi_hidden, wifi_auto_join, wifi_encryption, wifi_trusted_servers


# ============================================================================
# SECTION: VPN Configuration (conditional)
# ============================================================================


@app.cell
def _(mo, gen_vpn):
    if gen_vpn.value:
        mo.md("""
### VPN Configuration
""")
    else:
        mo.md("")


@app.cell
def _(mo, gen_vpn, ca_name):
    if gen_vpn.value:
        vpn_name_input = mo.ui.text(
            placeholder=f"{ca_name} VPN",
            label="VPN connection name",
            value=f"{ca_name} VPN",
            full_width=True,
        )
        vpn_server_input = mo.ui.text(
            placeholder="vpn.example.com",
            label="VPN server address (hostname or IP)",
            full_width=True,
        )
        vpn_remote_id_input = mo.ui.text(
            placeholder="vpn.example.com",
            label="Remote identifier (server certificate CN)",
            full_width=True,
        )
        vpn_local_id_input = mo.ui.text(
            placeholder="%HardwareUUID%",
            label="Local identifier (client identity)",
            value="%HardwareUUID%",
            full_width=True,
        )
        vpn_on_demand = mo.ui.checkbox(label="Enable VPN On-Demand")
        vpn_include_all = mo.ui.checkbox(label="Route all traffic through VPN")
        _vpn_form = mo.vstack([
            vpn_name_input,
            vpn_server_input,
            vpn_remote_id_input,
            vpn_local_id_input,
            mo.hstack([vpn_on_demand, vpn_include_all]),
        ])
    else:
        vpn_name_input = None
        vpn_server_input = None
        vpn_remote_id_input = None
        vpn_local_id_input = None
        vpn_on_demand = None
        vpn_include_all = None
        _vpn_form = mo.md("")

    _vpn_form

    return (
        vpn_name_input,
        vpn_server_input,
        vpn_remote_id_input,
        vpn_local_id_input,
        vpn_on_demand,
        vpn_include_all,
    )


# ============================================================================
# SECTION: Profile Templates
# ============================================================================


@app.cell
def _(xml_escape):
    def generate_scep_profile(
        payload_id: str,
        ca_name: str,
        challenge_var: str,
        proxy_var: str,
        renewal_var: str,
        profile_uuid: str,
        scep_uuid: str,
    ) -> str:
        """Generate SCEP mobileconfig profile."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <array>
        <dict>
            <key>PayloadContent</key>
            <dict>
                <key>Challenge</key>
                <string>{challenge_var}</string>
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
                            <string>{renewal_var}</string>
                        </array>
                    </array>
                </array>
                <key>URL</key>
                <string>{proxy_var}</string>
                <key>AllowAllAppsAccess</key>
                <true/>
            </dict>
            <key>PayloadDisplayName</key>
            <string>SCEP ({ca_name})</string>
            <key>PayloadIdentifier</key>
            <string>com.apple.security.scep.{scep_uuid}</string>
            <key>PayloadType</key>
            <string>com.apple.security.scep</string>
            <key>PayloadUUID</key>
            <string>{scep_uuid}</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
        </dict>
    </array>
    <key>PayloadDisplayName</key>
    <string>Smallstep SCEP - {ca_name}</string>
    <key>PayloadIdentifier</key>
    <string>{payload_id}</string>
    <key>PayloadScope</key>
    <string>System</string>
    <key>PayloadType</key>
    <string>Configuration</string>
    <key>PayloadUUID</key>
    <string>{profile_uuid}</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
</dict>
</plist>
'''

    def generate_trust_profile(
        payload_id: str,
        ca_name: str,
        profile_uuid: str,
        root_cert_b64: str,
        root_uuid: str,
        intermediate_cert_b64: str = "",
        intermediate_uuid: str = "",
        radius_cert_b64: str = "",
        radius_uuid: str = "",
    ) -> str:
        """Generate Trust mobileconfig profile with CA certificates."""
        payloads = []

        # Root CA
        if root_cert_b64:
            payloads.append(f'''        <dict>
            <key>PayloadCertificateFileName</key>
            <string>smallstep-root-ca.cer</string>
            <key>PayloadContent</key>
            <data>{root_cert_b64}</data>
            <key>PayloadDisplayName</key>
            <string>Smallstep Root CA</string>
            <key>PayloadIdentifier</key>
            <string>com.apple.security.root.{root_uuid}</string>
            <key>PayloadType</key>
            <string>com.apple.security.root</string>
            <key>PayloadUUID</key>
            <string>{root_uuid}</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
        </dict>''')

        # Intermediate CA
        if intermediate_cert_b64:
            payloads.append(f'''        <dict>
            <key>PayloadCertificateFileName</key>
            <string>smallstep-intermediate-ca.cer</string>
            <key>PayloadContent</key>
            <data>{intermediate_cert_b64}</data>
            <key>PayloadDisplayName</key>
            <string>Smallstep Intermediate CA</string>
            <key>PayloadIdentifier</key>
            <string>com.apple.security.pkcs1.{intermediate_uuid}</string>
            <key>PayloadType</key>
            <string>com.apple.security.pkcs1</string>
            <key>PayloadUUID</key>
            <string>{intermediate_uuid}</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
        </dict>''')

        # RADIUS CA
        if radius_cert_b64:
            payloads.append(f'''        <dict>
            <key>PayloadCertificateFileName</key>
            <string>radius-ca.cer</string>
            <key>PayloadContent</key>
            <data>{radius_cert_b64}</data>
            <key>PayloadDisplayName</key>
            <string>RADIUS CA Certificate</string>
            <key>PayloadIdentifier</key>
            <string>com.apple.security.root.{radius_uuid}</string>
            <key>PayloadType</key>
            <string>com.apple.security.root</string>
            <key>PayloadUUID</key>
            <string>{radius_uuid}</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
        </dict>''')

        payload_content = "\n".join(payloads)

        return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <array>
{payload_content}
    </array>
    <key>PayloadDisplayName</key>
    <string>Smallstep CA Trust - {ca_name}</string>
    <key>PayloadIdentifier</key>
    <string>trust.{payload_id}</string>
    <key>PayloadScope</key>
    <string>System</string>
    <key>PayloadType</key>
    <string>Configuration</string>
    <key>PayloadUUID</key>
    <string>{profile_uuid}</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
</dict>
</plist>
'''

    def generate_wifi_scep_profile(
        payload_id: str,
        ca_name: str,
        profile_uuid: str,
        ssid: str,
        hidden: bool,
        auto_join: bool,
        encryption: str,
        trusted_servers: list[str],
        challenge_var: str,
        proxy_var: str,
        renewal_var: str,
        scep_uuid: str,
        wifi_uuid: str,
        cert_anchor_uuids: list[str],
    ) -> str:
        """Generate WiFi + SCEP combined profile."""
        # SCEP payload
        scep_payload = f'''        <dict>
            <key>PayloadContent</key>
            <dict>
                <key>Challenge</key>
                <string>{challenge_var}</string>
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
                            <string>{renewal_var}</string>
                        </array>
                    </array>
                </array>
                <key>URL</key>
                <string>{proxy_var}</string>
                <key>AllowAllAppsAccess</key>
                <true/>
            </dict>
            <key>PayloadDisplayName</key>
            <string>SCEP ({ca_name})</string>
            <key>PayloadIdentifier</key>
            <string>com.apple.security.scep.{scep_uuid}</string>
            <key>PayloadType</key>
            <string>com.apple.security.scep</string>
            <key>PayloadUUID</key>
            <string>{scep_uuid}</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
        </dict>'''

        # Build EAP config
        eap_parts = [
            '''                <key>AcceptEAPTypes</key>
                <array>
                    <integer>13</integer>
                </array>''',
        ]

        if cert_anchor_uuids:
            anchors = "\n".join(f"                    <string>{uuid}</string>" for uuid in cert_anchor_uuids)
            eap_parts.append(f'''                <key>PayloadCertificateAnchorUUID</key>
                <array>
{anchors}
                </array>''')

        if trusted_servers:
            servers = "\n".join(f"                    <string>{xml_escape(s)}</string>" for s in trusted_servers)
            eap_parts.append(f'''                <key>TLSTrustedServerNames</key>
                <array>
{servers}
                </array>''')

        eap_parts.append('''                <key>TLSMinimumVersion</key>
                <string>1.2</string>
                <key>TLSMaximumVersion</key>
                <string>1.3</string>''')

        eap_config = "\n".join(eap_parts)

        # WiFi payload
        wifi_payload = f'''        <dict>
            <key>AutoJoin</key>
            <{"true" if auto_join else "false"}/>
            <key>SSID_STR</key>
            <string>{xml_escape(ssid)}</string>
            <key>HIDDEN_NETWORK</key>
            <{"true" if hidden else "false"}/>
            <key>EncryptionType</key>
            <string>{encryption}</string>
            <key>PayloadCertificateUUID</key>
            <string>{scep_uuid}</string>
            <key>EAPClientConfiguration</key>
            <dict>
{eap_config}
            </dict>
            <key>PayloadDisplayName</key>
            <string>WiFi ({xml_escape(ssid)})</string>
            <key>PayloadIdentifier</key>
            <string>com.apple.wifi.managed.{wifi_uuid}</string>
            <key>PayloadType</key>
            <string>com.apple.wifi.managed</string>
            <key>PayloadUUID</key>
            <string>{wifi_uuid}</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
        </dict>'''

        return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <array>
{scep_payload}
{wifi_payload}
    </array>
    <key>PayloadDisplayName</key>
    <string>WiFi + SCEP - {xml_escape(ssid)} ({ca_name})</string>
    <key>PayloadIdentifier</key>
    <string>{payload_id}</string>
    <key>PayloadScope</key>
    <string>System</string>
    <key>PayloadType</key>
    <string>Configuration</string>
    <key>PayloadUUID</key>
    <string>{profile_uuid}</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
</dict>
</plist>
'''

    def generate_vpn_profile(
        payload_id: str,
        ca_name: str,
        profile_uuid: str,
        vpn_name: str,
        server_address: str,
        remote_id: str,
        local_id: str,
        scep_uuid: str,
        vpn_uuid: str,
        on_demand: bool = False,
        include_all_networks: bool = False,
    ) -> str:
        """Generate IKEv2 VPN profile."""
        # Build IKEv2 config
        ikev2_parts = [
            f'''                <key>RemoteAddress</key>
                <string>{xml_escape(server_address)}</string>
                <key>LocalIdentifier</key>
                <string>{xml_escape(local_id)}</string>
                <key>RemoteIdentifier</key>
                <string>{xml_escape(remote_id)}</string>
                <key>AuthenticationMethod</key>
                <string>Certificate</string>
                <key>PayloadCertificateUUID</key>
                <string>{scep_uuid}</string>''',
            f'''                <key>ServerCertificateCommonName</key>
                <string>{xml_escape(server_address)}</string>''',
            '''                <key>DeadPeerDetectionRate</key>
                <string>Medium</string>''',
        ]

        if on_demand:
            ikev2_parts.append('''                <key>OnDemandEnabled</key>
                <integer>1</integer>
                <key>OnDemandRules</key>
                <array>
                    <dict>
                        <key>Action</key>
                        <string>Connect</string>
                    </dict>
                </array>''')

        if include_all_networks:
            ikev2_parts.append('''                <key>IncludeAllNetworks</key>
                <integer>1</integer>
                <key>ExcludeLocalNetworks</key>
                <integer>1</integer>''')

        ikev2_parts.append('''                <key>IKESecurityAssociationParameters</key>
                <dict>
                    <key>EncryptionAlgorithm</key>
                    <string>AES-256-GCM</string>
                    <key>IntegrityAlgorithm</key>
                    <string>SHA2-256</string>
                    <key>DiffieHellmanGroup</key>
                    <integer>14</integer>
                    <key>LifeTimeInMinutes</key>
                    <integer>1440</integer>
                </dict>
                <key>ChildSecurityAssociationParameters</key>
                <dict>
                    <key>EncryptionAlgorithm</key>
                    <string>AES-256-GCM</string>
                    <key>IntegrityAlgorithm</key>
                    <string>SHA2-256</string>
                    <key>DiffieHellmanGroup</key>
                    <integer>14</integer>
                    <key>LifeTimeInMinutes</key>
                    <integer>1440</integer>
                </dict>''')

        ikev2_config = "\n".join(ikev2_parts)

        return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <array>
        <dict>
            <key>UserDefinedName</key>
            <string>{xml_escape(vpn_name)}</string>
            <key>VPNType</key>
            <string>IKEv2</string>
            <key>VPNSubType</key>
            <string></string>
            <key>IKEv2</key>
            <dict>
{ikev2_config}
            </dict>
            <key>PayloadDisplayName</key>
            <string>VPN ({xml_escape(vpn_name)})</string>
            <key>PayloadIdentifier</key>
            <string>com.apple.vpn.managed.{vpn_uuid}</string>
            <key>PayloadType</key>
            <string>com.apple.vpn.managed</string>
            <key>PayloadUUID</key>
            <string>{vpn_uuid}</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
        </dict>
    </array>
    <key>PayloadDisplayName</key>
    <string>VPN - {xml_escape(vpn_name)} ({ca_name})</string>
    <key>PayloadIdentifier</key>
    <string>{payload_id}</string>
    <key>PayloadScope</key>
    <string>System</string>
    <key>PayloadType</key>
    <string>Configuration</string>
    <key>PayloadUUID</key>
    <string>{profile_uuid}</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
</dict>
</plist>
'''

    return generate_scep_profile, generate_trust_profile, generate_wifi_scep_profile, generate_vpn_profile


# ============================================================================
# SECTION: Generate and Display Profiles
# ============================================================================


@app.cell
def _(mo):
    mo.md("""
## Generated Profiles

Click to expand each profile and copy or download the content.
""")


@app.cell
def _(
    mo,
    gen_scep,
    gen_trust,
    gen_wifi,
    gen_vpn,
    fleet_proxy_url,
    ca_name,
    payload_id,
    profile_uuid,
    scep_uuid,
    trust_profile_uuid,
    root_cert_uuid,
    intermediate_cert_uuid,
    radius_cert_uuid,
    challenge_var,
    proxy_var,
    renewal_var,
    root_cert_pem,
    intermediate_cert_pem,
    radius_cert_pem,
    pem_to_base64,
    generate_uuid,
    generate_scep_profile,
    generate_trust_profile,
    generate_wifi_scep_profile,
    generate_vpn_profile,
    wifi_ssid_input,
    wifi_hidden,
    wifi_auto_join,
    wifi_encryption,
    wifi_trusted_servers,
    vpn_name_input,
    vpn_server_input,
    vpn_remote_id_input,
    vpn_local_id_input,
    vpn_on_demand,
    vpn_include_all,
    fleet_warning,
):
    generated_profiles = {}
    profile_displays = []

    if not fleet_proxy_url:
        profile_displays.append(fleet_warning("Enter Smallstep URLs to generate profiles."))
    else:
        # SCEP Profile
        if gen_scep.value:
            scep_content = generate_scep_profile(
                payload_id=payload_id,
                ca_name=ca_name,
                challenge_var=challenge_var,
                proxy_var=proxy_var,
                renewal_var=renewal_var,
                profile_uuid=profile_uuid,
                scep_uuid=scep_uuid,
            )
            scep_filename = f"smallstep-scep-{ca_name.lower()}.mobileconfig"
            generated_profiles[scep_filename] = scep_content

            profile_displays.append(
                mo.accordion({
                    f"📜 SCEP Profile: {scep_filename}": mo.vstack([
                        mo.md(f"**PayloadUUID:** `{profile_uuid}`  \n**SCEP PayloadUUID:** `{scep_uuid}`"),
                        mo.ui.code_editor(value=scep_content, language="xml", disabled=True),
                        mo.download(data=scep_content.encode(), filename=scep_filename, label=f"Download {scep_filename}"),
                    ])
                })
            )

        # Trust Profile
        if gen_trust.value and root_cert_pem:
            trust_content = generate_trust_profile(
                payload_id=payload_id,
                ca_name=ca_name,
                profile_uuid=trust_profile_uuid,
                root_cert_b64=pem_to_base64(root_cert_pem),
                root_uuid=root_cert_uuid,
                intermediate_cert_b64=pem_to_base64(intermediate_cert_pem) if intermediate_cert_pem else "",
                intermediate_uuid=intermediate_cert_uuid if intermediate_cert_pem else "",
                radius_cert_b64=pem_to_base64(radius_cert_pem) if radius_cert_pem else "",
                radius_uuid=radius_cert_uuid if radius_cert_pem else "",
            )
            trust_filename = f"smallstep-trust-{ca_name.lower()}.mobileconfig"
            generated_profiles[trust_filename] = trust_content

            _certs_included = ["Root CA"]
            if intermediate_cert_pem:
                _certs_included.append("Intermediate CA")
            if radius_cert_pem:
                _certs_included.append("RADIUS CA")

            profile_displays.append(
                mo.accordion({
                    f"🔐 Trust Profile: {trust_filename}": mo.vstack([
                        mo.md(f"**Certificates:** {', '.join(_certs_included)}  \n**PayloadUUID:** `{trust_profile_uuid}`"),
                        mo.ui.code_editor(value=trust_content, language="xml", disabled=True),
                        mo.download(data=trust_content.encode(), filename=trust_filename, label=f"Download {trust_filename}"),
                    ])
                })
            )

        # WiFi Profile
        if gen_wifi.value and wifi_ssid_input and wifi_ssid_input.value:
            wifi_profile_uuid = generate_uuid(f"{payload_id}.wifi")
            wifi_scep_uuid = generate_uuid(f"{payload_id}.wifi.scep")
            wifi_payload_uuid = generate_uuid(f"{payload_id}.wifi.network")

            # Build cert anchors
            cert_anchors = []
            if root_cert_pem:
                cert_anchors.append(root_cert_uuid)
            if radius_cert_pem:
                cert_anchors.append(radius_cert_uuid)

            # Parse trusted servers
            trusted_servers_list = []
            if wifi_trusted_servers and wifi_trusted_servers.value:
                trusted_servers_list = [s.strip() for s in wifi_trusted_servers.value.split(",") if s.strip()]

            wifi_content = generate_wifi_scep_profile(
                payload_id=f"{payload_id}.wifi",
                ca_name=ca_name,
                profile_uuid=wifi_profile_uuid,
                ssid=wifi_ssid_input.value,
                hidden=wifi_hidden.value if wifi_hidden else False,
                auto_join=wifi_auto_join.value if wifi_auto_join else True,
                encryption=wifi_encryption.value if wifi_encryption else "Any",
                trusted_servers=trusted_servers_list,
                challenge_var=challenge_var,
                proxy_var=proxy_var,
                renewal_var=renewal_var,
                scep_uuid=wifi_scep_uuid,
                wifi_uuid=wifi_payload_uuid,
                cert_anchor_uuids=cert_anchors,
            )
            wifi_filename = f"smallstep-wifi-scep-{ca_name.lower()}.mobileconfig"
            generated_profiles[wifi_filename] = wifi_content

            profile_displays.append(
                mo.accordion({
                    f"📶 WiFi Profile: {wifi_filename}": mo.vstack([
                        mo.md(f"**SSID:** `{wifi_ssid_input.value}`  \n**PayloadUUID:** `{wifi_profile_uuid}`"),
                        mo.ui.code_editor(value=wifi_content, language="xml", disabled=True),
                        mo.download(data=wifi_content.encode(), filename=wifi_filename, label=f"Download {wifi_filename}"),
                    ])
                })
            )

        # VPN Profile
        if gen_vpn.value and vpn_server_input and vpn_server_input.value:
            vpn_profile_uuid = generate_uuid(f"{payload_id}.vpn")
            vpn_payload_uuid = generate_uuid(f"{payload_id}.vpn.ikev2")

            vpn_content = generate_vpn_profile(
                payload_id=f"{payload_id}.vpn",
                ca_name=ca_name,
                profile_uuid=vpn_profile_uuid,
                vpn_name=vpn_name_input.value if vpn_name_input else f"{ca_name} VPN",
                server_address=vpn_server_input.value,
                remote_id=vpn_remote_id_input.value if vpn_remote_id_input and vpn_remote_id_input.value else vpn_server_input.value,
                local_id=vpn_local_id_input.value if vpn_local_id_input else "%HardwareUUID%",
                scep_uuid=scep_uuid,
                vpn_uuid=vpn_payload_uuid,
                on_demand=vpn_on_demand.value if vpn_on_demand else False,
                include_all_networks=vpn_include_all.value if vpn_include_all else False,
            )
            vpn_filename = f"smallstep-vpn-{ca_name.lower()}.mobileconfig"
            generated_profiles[vpn_filename] = vpn_content

            profile_displays.append(
                mo.accordion({
                    f"🔒 VPN Profile: {vpn_filename}": mo.vstack([
                        mo.md(f"**Server:** `{vpn_server_input.value}`  \n**PayloadUUID:** `{vpn_profile_uuid}`"),
                        mo.ui.code_editor(value=vpn_content, language="xml", disabled=True),
                        mo.download(data=vpn_content.encode(), filename=vpn_filename, label=f"Download {vpn_filename}"),
                    ])
                })
            )

    mo.vstack(profile_displays) if profile_displays else mo.md("")

    return generated_profiles,


# ============================================================================
# SECTION: Deployment Guide
# ============================================================================


@app.cell
def _(mo, generated_profiles, fleet_note):
    if generated_profiles:
        _profile_list = "\n".join(f"   - `{name}`" for name in generated_profiles.keys())
        mo.vstack([
            mo.md(f"""
## Deployment Guide

### Generated Files

{_profile_list}

### Deployment Order

1. **Trust Profile** — Install first to establish CA trust
2. **SCEP Profile** — Issues device identity certificate
3. **WiFi/VPN Profiles** — Reference the SCEP certificate for authentication

### Fleet Upload Steps

1. Go to **Controls → Configuration profiles → Add profile**
2. Upload each `.mobileconfig` file
3. Select target teams/hosts
4. Deploy
"""),
            fleet_note("Deploy Trust profile via <strong>Device Channel</strong> (not User Channel) for system-wide trust."),
        ])
    else:
        mo.md("")


# Self-contained: run with `uv run smallstep-profile-generator.py`
if __name__ == "__main__":
    import os
    import sys

    os.execvp(
        "marimo",
        ["marimo", "run", sys.argv[0], "--host", "127.0.0.1", "--port", "2720"],
    )
