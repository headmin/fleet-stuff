#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "httpx",
#     "pandas",
# ]
# description = """
# Fleet API Test Notebook - Test and explore your Fleet instance API endpoints.
# """
# ///

import marimo

__generated_with = "0.19.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import base64
    import json
    import os
    import plistlib
    import subprocess
    import uuid
    import httpx
    import pandas as pd
    import marimo as mo
    from pathlib import Path

    return mo, base64, json, os, plistlib, subprocess, uuid, httpx, pd, Path


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
# Fleet API Test

<p class="meta">Test and explore your Fleet instance API endpoints</p>

This notebook allows you to test your Fleet API connection and explore various endpoints.
""")


@app.cell
def _(os, subprocess, Path):
    def resolve_op_reference(value: str) -> str:
        """Resolve 1Password CLI reference (op://vault/item/field) to actual value."""
        if not value.startswith("op://"):
            return value
        try:
            result = subprocess.run(
                ["op", "read", value],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return ""  # Failed to read, return empty
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return ""  # op CLI not available or timed out

    def load_env_file(env_path: Path) -> dict:
        """Load environment variables from a .env file."""
        env_vars = {}
        if not env_path.exists():
            return env_vars
        try:
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        env_vars[key] = value
        except Exception:
            pass
        return env_vars

    # Try to load from .env file in the notebook directory
    _env_path = Path(__file__).parent / ".env" if "__file__" in dir() else Path(".env")
    _env_vars = load_env_file(_env_path)

    # Get values from env file or environment variables
    _fleet_url_env = _env_vars.get("FLEET_URL", os.environ.get("FLEET_URL", ""))
    _fleet_token_env = _env_vars.get("FLEET_API_TOKEN", os.environ.get("FLEET_API_TOKEN", ""))

    # Resolve 1Password references
    env_fleet_url = resolve_op_reference(_fleet_url_env)
    env_fleet_token = resolve_op_reference(_fleet_token_env)

    return resolve_op_reference, load_env_file, env_fleet_url, env_fleet_token


@app.cell
def _(mo, env_fleet_url, env_fleet_token):
    _env_loaded = bool(env_fleet_url or env_fleet_token)

    fleet_url_input = mo.ui.text(
        placeholder="https://fleet.example.com",
        label="Fleet Instance URL",
        value=env_fleet_url,
        full_width=True,
    )

    api_token_input = mo.ui.text(
        placeholder="Your Fleet API Token",
        label="Fleet API Token",
        value=env_fleet_token,
        kind="password",
        full_width=True,
    )

    _env_note = ""
    if _env_loaded:
        _loaded_parts = []
        if env_fleet_url:
            _loaded_parts.append("URL")
        if env_fleet_token:
            _loaded_parts.append("Token")
        _env_note = f'\n\n<div class="fleet-tip">Loaded {" and ".join(_loaded_parts)} from <code>.env</code> file or environment variables.</div>'

    mo.md(f"""
## Configuration

[📖 API Docs](https://fleetdm.com/docs/rest-api/rest-api#get-configuration)

Enter your Fleet instance details (or use `.env` file with `FLEET_URL` and `FLEET_API_TOKEN`):

{fleet_url_input}

{api_token_input}
{_env_note}
""")

    return fleet_url_input, api_token_input


@app.cell
def _(mo, fleet_url_input, api_token_input, fleet_warning):
    _has_url = bool(fleet_url_input.value)
    _has_token = bool(api_token_input.value)

    mo.stop(
        not _has_url or not _has_token,
        fleet_warning("Please enter both your Fleet URL and API Token above to test the connection.")
    )

    mo.md(f"""
**Configuration Ready**

- **URL**: `{fleet_url_input.value.rstrip('/')}`
- **Token**: `{'*' * 20}...` (hidden)
""")


@app.cell
def _(mo):
    test_connection_btn = mo.ui.button(
        label="Test API Connection",
        kind="success",
    )

    mo.hstack([test_connection_btn], justify="start")

    return (test_connection_btn,)


@app.cell
def _(mo, httpx, json, fleet_url_input, api_token_input, test_connection_btn, fleet_success, fleet_error):
    _ = test_connection_btn.value

    mo.stop(
        not fleet_url_input.value or not api_token_input.value,
        mo.md("*Enter credentials above and click the button to test.*")
    )

    _url = fleet_url_input.value.rstrip("/")
    _token = api_token_input.value
    _result = None

    try:
        _response = httpx.get(
            f"{_url}/api/v1/fleet/me",
            headers={"Authorization": f"Bearer {_token}"},
            timeout=10.0,
        )

        if _response.status_code == 200:
            _user_data = _response.json()
            _user = _user_data.get("user", {})

            _result = mo.vstack([
                fleet_success("API connection successful!"),
                mo.md(f"""
### Authenticated User

| Field | Value |
|-------|-------|
| **Name** | {_user.get('name', 'N/A')} |
| **Email** | {_user.get('email', 'N/A')} |
| **Role** | {_user.get('global_role', 'N/A')} |
| **ID** | {_user.get('id', 'N/A')} |
"""),
            ])
        else:
            _result = fleet_error(f"API returned status {_response.status_code}: {_response.text[:200]}")

    except httpx.ConnectError:
        _result = fleet_error(f"Connection failed: Could not connect to {_url}")
    except httpx.TimeoutException:
        _result = fleet_error("Connection timed out after 10 seconds")
    except Exception as e:
        _result = fleet_error(f"Error: {str(e)}")

    _result


@app.cell
def _(mo):
    mo.md("""
---

## API Endpoints Explorer

[📖 API Docs](https://fleetdm.com/docs/rest-api/rest-api)

Select an endpoint to query:
""")


@app.cell
def _(mo):
    endpoint_select = mo.ui.dropdown(
        options={
            "Get Current User": "/api/v1/fleet/me",
            "Get Version": "/api/v1/fleet/version",
            "Get Config": "/api/v1/fleet/config",
            "Get Hosts": "/api/v1/fleet/hosts",
            "Get Host Count": "/api/v1/fleet/hosts/count",
            "Get Teams": "/api/v1/fleet/teams",
            "Get Global Policies": "/api/v1/fleet/global/policies",
            "Get Global Schedule": "/api/v1/fleet/global/schedule",
            "Get Queries": "/api/v1/fleet/queries",
            "Get Software": "/api/v1/fleet/software",
            "Get Labels": "/api/v1/fleet/labels",
            "Get Activities": "/api/v1/fleet/activities",
            "Get Enroll Secrets": "/api/v1/fleet/spec/enroll_secret",
        },
        value="Get Current User",
        label="Select Endpoint",
    )

    query_btn = mo.ui.button(
        label="Query Endpoint",
        kind="neutral",
    )

    mo.hstack([endpoint_select, query_btn], justify="start", gap=1)

    return endpoint_select, query_btn


@app.cell
def _(mo, httpx, json, fleet_url_input, api_token_input, endpoint_select, query_btn, fleet_error):
    _ = query_btn.value

    mo.stop(
        not fleet_url_input.value or not api_token_input.value,
        mo.md("*Enter credentials above first.*")
    )

    mo.stop(
        not endpoint_select.value,
        mo.md("*Select an endpoint and click Query.*")
    )

    _url = fleet_url_input.value.rstrip("/")
    _token = api_token_input.value
    _endpoint = endpoint_select.value
    _result = None

    try:
        _response = httpx.get(
            f"{_url}{_endpoint}",
            headers={"Authorization": f"Bearer {_token}"},
            timeout=15.0,
        )

        if _response.status_code == 200:
            _data = _response.json()
            _formatted = json.dumps(_data, indent=2)

            # Truncate if too long
            if len(_formatted) > 5000:
                _formatted = _formatted[:5000] + "\n\n... (truncated)"

            _result = mo.md(f"""
### Response from `{_endpoint}`

**Status**: {_response.status_code} OK

```json
{_formatted}
```
""")
        else:
            _result = fleet_error(f"API returned status {_response.status_code}: {_response.text[:500]}")

    except httpx.TimeoutException:
        _result = fleet_error("Request timed out after 15 seconds")
    except Exception as e:
        _result = fleet_error(f"Error: {str(e)}")

    _result


@app.cell
def _(mo):
    mo.md("""
---

## Custom API Request

[📖 API Docs](https://fleetdm.com/docs/rest-api/rest-api)

Make a custom GET request to any Fleet API endpoint:
""")


@app.cell
def _(mo):
    custom_endpoint_input = mo.ui.text(
        placeholder="/api/v1/fleet/hosts?per_page=5",
        label="Custom Endpoint",
        value="",
        full_width=True,
    )

    custom_query_btn = mo.ui.button(
        label="Execute Custom Request",
        kind="neutral",
    )

    mo.vstack([
        custom_endpoint_input,
        mo.hstack([custom_query_btn], justify="start"),
    ])

    return custom_endpoint_input, custom_query_btn


@app.cell
def _(mo, httpx, json, fleet_url_input, api_token_input, custom_endpoint_input, custom_query_btn, fleet_error, fleet_tip):
    _ = custom_query_btn.value

    mo.stop(
        not fleet_url_input.value or not api_token_input.value,
        mo.md("*Enter credentials above first.*")
    )

    mo.stop(
        not custom_endpoint_input.value,
        fleet_tip("Enter a custom endpoint path like <code>/api/v1/fleet/hosts?per_page=5</code> and click Execute.")
    )

    _url = fleet_url_input.value.rstrip("/")
    _token = api_token_input.value
    _endpoint = custom_endpoint_input.value

    # Ensure endpoint starts with /
    if not _endpoint.startswith("/"):
        _endpoint = "/" + _endpoint

    _result = None

    try:
        _response = httpx.get(
            f"{_url}{_endpoint}",
            headers={"Authorization": f"Bearer {_token}"},
            timeout=15.0,
        )

        if _response.status_code == 200:
            _data = _response.json()
            _full_json = json.dumps(_data, indent=2)
            _formatted = _full_json
            _truncated = False

            if len(_formatted) > 5000:
                _formatted = _formatted[:5000] + "\n\n... (truncated - download full response below)"
                _truncated = True

            # Create safe filename from endpoint
            _safe_filename = _endpoint.replace("/", "_").replace("?", "_").strip("_")[:50]
            _download_btn = mo.download(
                data=_full_json.encode("utf-8"),
                filename=f"fleet-api-{_safe_filename}.json",
                mimetype="application/json",
                label="Download Full Response",
            )

            _result = mo.vstack([
                mo.md(f"""
### Response from `{_endpoint}`

**Status**: {_response.status_code} OK
"""),
                _download_btn if _truncated else mo.md(""),
                mo.md(f"""
```json
{_formatted}
```
"""),
                _download_btn,
            ])
        else:
            _result = fleet_error(f"API returned status {_response.status_code}: {_response.text[:500]}")

    except httpx.TimeoutException:
        _result = fleet_error("Request timed out after 15 seconds")
    except Exception as e:
        _result = fleet_error(f"Error: {str(e)}")

    _result


@app.cell
def _(mo):
    mo.md("""
---

## Labels CRUD Operations

[📖 API Docs](https://fleetdm.com/docs/rest-api/rest-api#labels)

Test create, read, and delete operations on Fleet labels:
""")


@app.cell
def _(httpx, fleet_url_input, api_token_input):
    # Reusable Fleet API helper function
    def fleet(method: str, endpoint: str, json_data: dict = None):
        """Make a request to the Fleet API.

        Returns: (status_code, response_data)
        """
        url = fleet_url_input.value.rstrip("/")
        token = api_token_input.value

        if not url or not token:
            return None, {"error": "Missing URL or token"}

        headers = {"Authorization": f"Bearer {token}"}
        full_url = f"{url}{endpoint}"

        try:
            if method.upper() == "GET":
                response = httpx.get(full_url, headers=headers, timeout=15.0)
            elif method.upper() == "POST":
                response = httpx.post(full_url, headers=headers, json=json_data, timeout=15.0)
            elif method.upper() == "DELETE":
                response = httpx.delete(full_url, headers=headers, timeout=15.0)
            elif method.upper() == "PATCH":
                response = httpx.patch(full_url, headers=headers, json=json_data, timeout=15.0)
            else:
                return None, {"error": f"Unsupported method: {method}"}

            try:
                data = response.json()
            except Exception:
                data = {"raw": response.text}

            return response.status_code, data
        except Exception as e:
            return None, {"error": str(e)}

    LABEL_PREFIX = "test_label_"

    return fleet, LABEL_PREFIX


@app.cell
def _(mo):
    list_labels_btn = mo.ui.run_button(label="List Labels")
    create_label_btn = mo.ui.run_button(label="Create Test Label")

    mo.hstack([list_labels_btn, create_label_btn], justify="start", gap=1)
    return list_labels_btn, create_label_btn


@app.cell
def _(mo, pd, fleet, list_labels_btn, fleet_error):
    mo.stop(not list_labels_btn.value)

    _status, _data = fleet("GET", "/api/v1/fleet/labels")
    _result = None

    if _status != 200:
        _result = fleet_error(f"Failed to list labels: {_data}")
    else:
        _labels = _data.get("labels", [])
        if _labels:
            _df = pd.DataFrame(_labels)[["id", "name", "label_type", "platform", "count"]]
            _result = mo.vstack([
                mo.md(f"**Labels** ({len(_labels)} total)"),
                mo.ui.table(_df, selection=None),
            ])
        else:
            _result = mo.md("*No labels found.*")

    _result


@app.cell
def _(mo, uuid, fleet, create_label_btn, LABEL_PREFIX, fleet_success, fleet_error):
    mo.stop(not create_label_btn.value)

    created_label_name = f"{LABEL_PREFIX}{uuid.uuid4().hex[:8]}"
    _payload = {
        "name": created_label_name,
        "query": "SELECT 1 FROM os_version WHERE platform = 'darwin';",
        "platform": "darwin",
    }

    _status, _data = fleet("POST", "/api/v1/fleet/labels", json_data=_payload)
    created_label_id = None
    _result = None

    if _status == 200 or _status == 201:
        _created_label = _data.get("label", {})
        created_label_id = _created_label.get("id")
        _result = fleet_success(f"Created label: **{created_label_name}** (ID: {created_label_id})")
    else:
        _result = fleet_error(f"Failed to create label (status {_status}): {_data}")

    _result

    return created_label_name, created_label_id


@app.cell
def _(mo):
    label_id_input = mo.ui.text(
        placeholder="e.g. 21",
        label="Label ID",
    )
    verify_btn = mo.ui.run_button(label="Verify")
    delete_btn = mo.ui.run_button(label="Delete")

    mo.hstack([label_id_input, verify_btn, delete_btn], justify="start", gap=1)
    return label_id_input, verify_btn, delete_btn


@app.cell
def _(mo, json, fleet, label_id_input, verify_btn, fleet_success, fleet_error):
    mo.stop(not verify_btn.value or not label_id_input.value)

    _status, _data = fleet("GET", f"/api/v1/fleet/labels/{label_id_input.value}")
    _result = None

    if _status == 200:
        _label = _data.get("label", _data)
        _result = mo.vstack([
            fleet_success("Label found!"),
            mo.md(f"```json\n{json.dumps(_label, indent=2)}\n```"),
        ])
    else:
        _result = fleet_error(f"Label not found (status {_status}): {_data}")

    _result


@app.cell
def _(mo, fleet, label_id_input, delete_btn, fleet_success, fleet_error):
    mo.stop(not delete_btn.value or not label_id_input.value)

    _status, _data = fleet("DELETE", f"/api/v1/fleet/labels/id/{label_id_input.value}")
    _result = None

    if _status == 200:
        _result = fleet_success(f"Label {label_id_input.value} deleted!")
    else:
        _result = fleet_error(f"Failed to delete (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
---

## MDM Commands

[📖 API Docs](https://fleetdm.com/docs/rest-api/rest-api#run-mdm-command)

Run MDM commands on enrolled macOS hosts. These commands are **read-only queries** that retrieve device information without making any changes:

| Command | Description |
|---------|-------------|
| DeviceInformation | Query 60+ device details (hardware, OS, network, security) |
| ProfileList | List installed configuration profiles |
| InstalledApplicationList | List installed applications |
| SecurityInfo | Security-related information |
| CertificateList | List installed certificates |
""")


@app.cell
def _(mo, uuid, base64):
    # MDM command plist templates (safe, read-only queries)
    # CommandUUID placeholder will be replaced with unique UUID at runtime
    MDM_COMMAND_TEMPLATES = {
        "DeviceInformation": '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Command</key>
    <dict>
        <key>RequestType</key>
        <string>DeviceInformation</string>
        <key>Queries</key>
        <array>
            <string>DeviceName</string>
            <string>SerialNumber</string>
            <string>Model</string>
            <string>ModelName</string>
            <string>OSVersion</string>
            <string>BuildVersion</string>
            <string>DeviceCapacity</string>
            <string>AvailableDeviceCapacity</string>
            <string>WiFiMAC</string>
            <string>BluetoothMAC</string>
            <string>IsSupervised</string>
            <string>IsActivationLockEnabled</string>
            <string>BatteryLevel</string>
        </array>
    </dict>
    <key>CommandUUID</key>
    <string>{{CMD_UUID}}</string>
</dict>
</plist>''',
        "ProfileList": '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Command</key>
    <dict>
        <key>ManagedOnly</key>
        <false/>
        <key>RequestType</key>
        <string>ProfileList</string>
    </dict>
    <key>CommandUUID</key>
    <string>{{CMD_UUID}}</string>
</dict>
</plist>''',
        "InstalledApplicationList": '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Command</key>
    <dict>
        <key>ManagedAppsOnly</key>
        <false/>
        <key>RequestType</key>
        <string>InstalledApplicationList</string>
    </dict>
    <key>CommandUUID</key>
    <string>{{CMD_UUID}}</string>
</dict>
</plist>''',
        "SecurityInfo": '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Command</key>
    <dict>
        <key>RequestType</key>
        <string>SecurityInfo</string>
    </dict>
    <key>CommandUUID</key>
    <string>{{CMD_UUID}}</string>
</dict>
</plist>''',
        "CertificateList": '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Command</key>
    <dict>
        <key>ManagedOnly</key>
        <false/>
        <key>RequestType</key>
        <string>CertificateList</string>
    </dict>
    <key>CommandUUID</key>
    <string>{{CMD_UUID}}</string>
</dict>
</plist>''',
    }

    def build_mdm_command(command_name: str) -> str:
        """Build a base64-encoded MDM command with a unique UUID."""
        template = MDM_COMMAND_TEMPLATES.get(command_name, "")
        if not template:
            return ""
        # Replace placeholder with unique UUID
        cmd_uuid = str(uuid.uuid4()).upper()
        plist = template.replace("{{CMD_UUID}}", cmd_uuid)
        return base64.b64encode(plist.encode('utf-8')).decode('utf-8')

    return MDM_COMMAND_TEMPLATES, build_mdm_command


@app.cell
def _(mo):
    fetch_mdm_hosts_btn = mo.ui.run_button(label="Fetch MDM-Enabled Hosts")
    fetch_mdm_hosts_btn

    return (fetch_mdm_hosts_btn,)


@app.cell
def _(mo, fleet, fetch_mdm_hosts_btn):
    # Default empty state
    mdm_host_options = {}
    _status_msg = "Click **Fetch MDM-Enabled Hosts** to load available hosts."

    if fetch_mdm_hosts_btn.value:
        _status, _data = fleet("GET", "/api/v1/fleet/hosts?per_page=100")

        if _status == 200:
            _hosts = _data.get("hosts", [])
            for _h in _hosts:
                _mdm = _h.get("mdm") or {}
                _enrollment = _mdm.get("enrollment_status") or ""
                _mdm_name = _mdm.get("name") or ""
                # Only include hosts enrolled in Fleet's MDM
                if "On" in _enrollment and _mdm_name == "Fleet":
                    _display = f"{_h.get('display_name') or _h.get('hostname') or 'Unknown'} ({(_h.get('uuid') or '')[:8]}...)"
                    mdm_host_options[_display] = _h.get("uuid")

            if mdm_host_options:
                _status_msg = f"**Found {len(mdm_host_options)} MDM-capable host(s)**"
            else:
                _status_msg = f"**No MDM-capable hosts found.** Found {len(_hosts)} total hosts, but none enrolled in Fleet's MDM with status On."
        else:
            _status_msg = f"**Error:** Failed to fetch hosts - {_data}"

    mo.md(_status_msg)

    return (mdm_host_options,)


@app.cell
def _(mo, mdm_host_options, MDM_COMMAND_TEMPLATES):
    # Custom command XML template
    CUSTOM_COMMAND_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Command</key>
    <dict>
        <key>RequestType</key>
        <string>DeviceInformation</string>
        <key>Queries</key>
        <array>
            <string>DeviceName</string>
            <string>SerialNumber</string>
        </array>
    </dict>
</dict>
</plist>'''

    # Host selection dropdown - populated from fetched hosts
    mdm_host_dropdown = mo.ui.dropdown(
        options=mdm_host_options if mdm_host_options else {},
        label="Select Host",
        value=None,
    )

    # Manual UUID input as fallback
    mdm_host_uuid_input = mo.ui.text(
        placeholder="Or enter UUID manually",
        label="Manual Host UUID",
        full_width=True,
    )

    # Preset commands dropdown
    mdm_command_dropdown = mo.ui.dropdown(
        options=list(MDM_COMMAND_TEMPLATES.keys()),
        value="DeviceInformation",
        label="Command Preset",
    )

    run_mdm_command_btn = mo.ui.run_button(label="Run Preset Command")

    # Toggle for custom command
    use_custom_command = mo.ui.checkbox(label="Use custom command instead")

    # Custom command text area
    mdm_custom_command = mo.ui.text_area(
        placeholder="Enter custom MDM command XML (CommandUUID will be auto-generated)",
        label="Custom Command XML",
        value=CUSTOM_COMMAND_TEMPLATE,
        full_width=True,
        rows=12,
    )

    run_custom_command_btn = mo.ui.run_button(label="Run Custom Command")

    mo.vstack([
        mo.md("**Target Host**"),
        mdm_host_dropdown,
        mdm_host_uuid_input,
        mo.md("---"),
        mo.md("**Preset Commands**"),
        mo.hstack([mdm_command_dropdown, run_mdm_command_btn], justify="start", gap=1),
        mo.md("---"),
        mo.md("**Custom Command**"),
        mdm_custom_command,
        mo.hstack([run_custom_command_btn], justify="start"),
    ])

    return mdm_host_dropdown, mdm_host_uuid_input, mdm_command_dropdown, mdm_custom_command, run_mdm_command_btn, run_custom_command_btn


@app.cell
def _(mo, fleet, build_mdm_command, mdm_host_dropdown, mdm_host_uuid_input, mdm_command_dropdown, run_mdm_command_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not run_mdm_command_btn.value)

    # Use dropdown selection, fall back to manual input
    _host_uuid = mdm_host_dropdown.value if mdm_host_dropdown.value else mdm_host_uuid_input.value.strip()

    mo.stop(
        not _host_uuid,
        fleet_tip("Select a host from the dropdown above, or enter a Host UUID manually.")
    )

    _command_name = mdm_command_dropdown.value
    _command_base64 = build_mdm_command(_command_name)

    _payload = {
        "command": _command_base64,
        "host_uuids": [_host_uuid],
    }

    _status, _data = fleet("POST", "/api/v1/fleet/commands/run", json_data=_payload)
    mdm_command_uuid = _data.get("command_uuid", "") if _status in (200, 202) else ""

    if _status == 200 or _status == 202:
        _output = mo.vstack([
            fleet_success(f"Command <strong>{_command_name}</strong> sent successfully!"),
            mo.callout(
                mo.md(f"**Command UUID:** `{mdm_command_uuid}`"),
                kind="success"
            ),
            mo.md(f"""
**Target Host**: `{_host_uuid}`

**Request Type**: `{_data.get('request_type', 'N/A')}`

Copy the Command UUID above and paste it in "Get Results" below.
"""),
        ])
    else:
        _output = fleet_error(f"Failed to send command (status {_status}): {_data}")

    _output

    return (mdm_command_uuid,)


@app.cell
def _(mo, fleet, uuid, base64, mdm_host_dropdown, mdm_host_uuid_input, mdm_custom_command, run_custom_command_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not run_custom_command_btn.value)

    # Use dropdown selection, fall back to manual input
    _host_uuid = mdm_host_dropdown.value if mdm_host_dropdown.value else mdm_host_uuid_input.value.strip()

    mo.stop(
        not _host_uuid,
        fleet_tip("Select a host from the dropdown above, or enter a Host UUID manually.")
    )

    # Build custom command with auto-generated UUID
    _custom_xml = mdm_custom_command.value
    _cmd_uuid = str(uuid.uuid4()).upper()

    # Insert CommandUUID before closing </dict></plist> if not already present
    if "<key>CommandUUID</key>" not in _custom_xml:
        _custom_xml = _custom_xml.replace(
            "</dict>\n</plist>",
            f"    <key>CommandUUID</key>\n    <string>{_cmd_uuid}</string>\n</dict>\n</plist>"
        )

    _command_base64 = base64.b64encode(_custom_xml.encode('utf-8')).decode('utf-8')

    _payload = {
        "command": _command_base64,
        "host_uuids": [_host_uuid],
    }

    _status, _data = fleet("POST", "/api/v1/fleet/commands/run", json_data=_payload)
    custom_command_uuid = _data.get("command_uuid", "") if _status in (200, 202) else ""

    if _status == 200 or _status == 202:
        _output = mo.vstack([
            fleet_success(f"Custom command sent successfully!"),
            mo.callout(
                mo.md(f"**Command UUID:** `{custom_command_uuid}`"),
                kind="success"
            ),
            mo.md(f"""
**Target Host**: `{_host_uuid}`

**Request Type**: `{_data.get('request_type', 'N/A')}`

Copy the Command UUID above and paste it in "Get Results" below.
"""),
        ])
    else:
        _output = fleet_error(f"Failed to send custom command (status {_status}): {_data}")

    _output

    return (custom_command_uuid,)


@app.cell
def _(mo):
    mo.md("""
### Get Command Results

Enter a command UUID to retrieve the results:
""")


@app.cell
def _(mo):
    mdm_result_uuid_input = mo.ui.text(
        placeholder="Command UUID",
        label="Command UUID",
        full_width=True,
    )

    get_mdm_results_btn = mo.ui.run_button(label="Get Results")

    mo.vstack([
        mdm_result_uuid_input,
        mo.hstack([get_mdm_results_btn], justify="start"),
    ])

    return mdm_result_uuid_input, get_mdm_results_btn


@app.cell
def _(mo, json, base64, plistlib, fleet, mdm_result_uuid_input, get_mdm_results_btn, fleet_success, fleet_error, fleet_tip):
    def decode_mdm_result(result_b64: str) -> dict:
        """Decode base64-encoded plist result to dict."""
        try:
            plist_bytes = base64.b64decode(result_b64)
            return plistlib.loads(plist_bytes)
        except Exception as e:
            return {"decode_error": str(e), "raw_base64": result_b64[:100] + "..."}

    mo.stop(not get_mdm_results_btn.value)

    mo.stop(
        not mdm_result_uuid_input.value,
        fleet_tip("Enter a Command UUID to retrieve results.")
    )

    _cmd_uuid = mdm_result_uuid_input.value.strip()
    _status, _data = fleet("GET", f"/api/v1/fleet/commands/results?command_uuid={_cmd_uuid}")
    _result = None

    if _status == 200:
        _results = _data.get("results", [])
        if _results:
            # Decode base64 plist results to JSON
            _decoded_results = []
            for _r in _results:
                _decoded = dict(_r)  # Copy the result dict
                if "result" in _decoded and _decoded["result"]:
                    _decoded["result"] = decode_mdm_result(_decoded["result"])
                _decoded_results.append(_decoded)

            _full_json = json.dumps(_decoded_results, indent=2, default=str)
            _formatted = _full_json
            _truncated = False
            if len(_formatted) > 8000:
                _formatted = _formatted[:8000] + "\n\n... (truncated - download full results below)"
                _truncated = True
            _download_btn = mo.download(
                data=_full_json.encode("utf-8"),
                filename=f"mdm-results-{_cmd_uuid}.json",
                mimetype="application/json",
                label="Download Full Results",
            )
            _result = mo.vstack([
                fleet_success(f"Results retrieved for command <code>{_cmd_uuid}</code>"),
                _download_btn if _truncated else mo.md(""),
                mo.md(f"""
```json
{_formatted}
```
"""),
                _download_btn,
            ])
        else:
            _result = mo.md(f"""
**No results yet** for command `{_cmd_uuid}`

The device may not have responded yet. MDM commands are asynchronous - the device must be online and check in to receive and respond to commands.
""")
    else:
        _result = fleet_error(f"Failed to get results (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
---

## Certificate Authorities

[📖 API Docs](https://fleetdm.com/docs/rest-api/rest-api#list-certificate-authorities-cas)

Manage certificate authorities (CAs) connected to Fleet for issuing certificates.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/fleet/certificate_authorities` | GET | List all certificate authorities |
| `/api/v1/fleet/certificate_authorities/:id` | GET | Get certificate authority details |
""")


@app.cell
def _(mo):
    list_cas_btn = mo.ui.run_button(label="List Certificate Authorities")
    ca_id_input = mo.ui.text(placeholder="CA ID", label="CA ID")
    get_ca_btn = mo.ui.run_button(label="Get CA Details")

    mo.vstack([
        mo.hstack([list_cas_btn], justify="start"),
        mo.hstack([ca_id_input, get_ca_btn], justify="start", gap=1),
    ])

    return list_cas_btn, ca_id_input, get_ca_btn


@app.cell
def _(mo, json, fleet, list_cas_btn, fleet_success, fleet_error):
    mo.stop(not list_cas_btn.value)

    _status, _data = fleet("GET", "/api/v1/fleet/certificate_authorities")

    if _status == 200:
        _cas = _data.get("certificate_authorities", [])
        if _cas:
            _formatted = json.dumps(_cas, indent=2)
            _result = mo.vstack([
                fleet_success(f"Found {len(_cas)} certificate authority(ies)"),
                mo.md(f"```json\n{_formatted}\n```"),
            ])
        else:
            _result = mo.md("**No certificate authorities configured.**")
    else:
        _result = fleet_error(f"Failed to list CAs (status {_status}): {_data}")

    _result


@app.cell
def _(mo, json, fleet, ca_id_input, get_ca_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not get_ca_btn.value)
    mo.stop(not ca_id_input.value, fleet_tip("Enter a CA ID to get details."))

    _ca_id = ca_id_input.value.strip()
    _status, _data = fleet("GET", f"/api/v1/fleet/certificate_authorities/{_ca_id}")

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Certificate Authority {_ca_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get CA (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
---

## Certificate Templates

[📖 API Docs](https://fleetdm.com/docs/rest-api/rest-api#list-certificate-templates)

List and view certificate templates configured in Fleet.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/fleet/certificates` | GET | List all certificate templates |
| `/api/v1/fleet/certificates/:id` | GET | Get certificate template details |

**Authentication options for Get Certificate Template:**
- `Authorization: Bearer <api_token>` (standard API token)
- `Authorization: Node key <host_uuid>` (device node key)
""")


@app.cell
def _(mo):
    list_certs_btn = mo.ui.run_button(label="List Certificate Templates")
    cert_id_input = mo.ui.text(placeholder="Certificate ID", label="Certificate ID")
    cert_node_key_input = mo.ui.text(placeholder="Optional: Node key (host UUID)", label="Node Key (optional)")
    get_cert_btn = mo.ui.run_button(label="Get Certificate Details")

    mo.vstack([
        mo.hstack([list_certs_btn], justify="start"),
        mo.hstack([cert_id_input, cert_node_key_input, get_cert_btn], justify="start", gap=1),
    ])

    return list_certs_btn, cert_id_input, cert_node_key_input, get_cert_btn


@app.cell
def _(mo, json, fleet, list_certs_btn, fleet_success, fleet_error):
    mo.stop(not list_certs_btn.value)

    _status, _data = fleet("GET", "/api/v1/fleet/certificates")

    if _status == 200:
        _certs = _data.get("certificates", [])
        if _certs:
            _formatted = json.dumps(_certs, indent=2)
            _result = mo.vstack([
                fleet_success(f"Found {len(_certs)} certificate template(s)"),
                mo.md(f"```json\n{_formatted}\n```"),
            ])
        else:
            _result = mo.md("**No certificate templates configured.**")
    else:
        _result = fleet_error(f"Failed to list certificates (status {_status}): {_data}")

    _result


@app.cell
def _(mo, json, httpx, fleet_url_input, api_token_input, cert_id_input, cert_node_key_input, get_cert_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not get_cert_btn.value)
    mo.stop(not cert_id_input.value, fleet_tip("Enter a Certificate ID to get details."))

    _cert_id = cert_id_input.value.strip()
    _node_key = cert_node_key_input.value.strip() if cert_node_key_input.value else None

    # Use Node key auth if provided, otherwise use Bearer token
    if _node_key:
        _headers = {"Authorization": f"Node key {_node_key}"}
        _auth_method = "Node key"
    else:
        _headers = {"Authorization": f"Bearer {api_token_input.value}"}
        _auth_method = "Bearer token"

    try:
        _response = httpx.get(
            f"{fleet_url_input.value}/api/v1/fleet/certificates/{_cert_id}",
            headers=_headers,
            verify=True,
            timeout=30.0,
        )
        _status = _response.status_code
        _data = _response.json() if _response.text else {}
    except Exception as e:
        _status = 0
        _data = {"error": str(e)}

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Certificate Template {_cert_id} (via {_auth_method})"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get certificate (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
---

## Webhook Settings

[📖 API Docs](https://fleetdm.com/docs/rest-api/rest-api#webhook-settings)

View and manage Fleet webhook configurations. Webhooks notify external services about Fleet events.

| Webhook | Description |
|---------|-------------|
| **host_status_webhook** | Triggered when hosts fail to check in |
| **failing_policies_webhook** | Triggered when policies fail on hosts |
| **vulnerabilities_webhook** | Triggered when new vulnerabilities are detected |
| **activities_webhook** | Triggered for Fleet activities |
""")


@app.cell
def _(mo, json, fleet, fleet_success, fleet_error):
    get_webhooks_btn = mo.ui.run_button(label="Get Current Webhook Settings")

    mo.hstack([get_webhooks_btn], justify="start")

    return (get_webhooks_btn,)


@app.cell
def _(mo, json, fleet, get_webhooks_btn, fleet_success, fleet_error):
    mo.stop(not get_webhooks_btn.value)

    _status, _data = fleet("GET", "/api/v1/fleet/config")

    if _status == 200:
        _webhook_settings = _data.get("webhook_settings", {})
        _formatted = json.dumps(_webhook_settings, indent=2)
        _result = mo.vstack([
            fleet_success("Current Webhook Settings"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get config (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Update Webhook Settings

Configure individual webhook settings below. Fill in the fields and click Update.
""")


@app.cell
def _(mo):
    webhook_type_dropdown = mo.ui.dropdown(
        options={
            "Host Status Webhook": "host_status_webhook",
            "Failing Policies Webhook": "failing_policies_webhook",
            "Vulnerabilities Webhook": "vulnerabilities_webhook",
            "Activities Webhook": "activities_webhook",
        },
        value="Host Status Webhook",
        label="Webhook Type",
    )

    webhook_enabled = mo.ui.checkbox(label="Enable Webhook")

    webhook_url = mo.ui.text(
        placeholder="https://your-webhook-endpoint.com/hook",
        label="Destination URL",
        full_width=True,
    )

    # Additional settings for specific webhooks
    host_percentage = mo.ui.number(
        start=1, stop=100, step=1, value=5,
        label="Host Percentage (host_status only)",
    )

    days_count = mo.ui.number(
        start=1, stop=30, step=1, value=7,
        label="Days Count (host_status only)",
    )

    host_batch_size = mo.ui.number(
        start=100, stop=10000, step=100, value=1000,
        label="Host Batch Size (policies/vulnerabilities)",
    )

    update_webhook_btn = mo.ui.run_button(label="Update Webhook")

    mo.vstack([
        webhook_type_dropdown,
        webhook_enabled,
        webhook_url,
        host_percentage,
        days_count,
        host_batch_size,
        mo.hstack([update_webhook_btn], justify="start"),
    ])

    return webhook_type_dropdown, webhook_enabled, webhook_url, host_percentage, days_count, host_batch_size, update_webhook_btn


@app.cell
def _(mo, json, fleet, webhook_type_dropdown, webhook_enabled, webhook_url, host_percentage, days_count, host_batch_size, update_webhook_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not update_webhook_btn.value)
    mo.stop(not webhook_url.value, fleet_tip("Enter a destination URL for the webhook."))

    _webhook_key = webhook_type_dropdown.value
    _enable_key = f"enable_{_webhook_key}"

    # Build webhook config based on type
    _webhook_config = {
        _enable_key: webhook_enabled.value,
        "destination_url": webhook_url.value,
    }

    if _webhook_key == "host_status_webhook":
        _webhook_config["host_percentage"] = host_percentage.value
        _webhook_config["days_count"] = days_count.value
    elif _webhook_key in ("failing_policies_webhook", "vulnerabilities_webhook"):
        _webhook_config["host_batch_size"] = host_batch_size.value

    _payload = {
        "webhook_settings": {
            _webhook_key: _webhook_config
        }
    }

    _status, _data = fleet("PATCH", "/api/v1/fleet/config", json_data=_payload)

    if _status == 200:
        _updated = _data.get("webhook_settings", {}).get(_webhook_key, {})
        _formatted = json.dumps(_updated, indent=2)
        _result = mo.vstack([
            fleet_success(f"Updated {_webhook_key}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to update webhook (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
---

## Common API Endpoints Reference

[📖 Full API Documentation](https://fleetdm.com/docs/rest-api/rest-api)

| Endpoint | Description |
|----------|-------------|
| `/api/v1/fleet/me` | Current authenticated user |
| `/api/v1/fleet/version` | Fleet server version |
| `/api/v1/fleet/config` | Get Fleet configuration |
| `/api/v1/fleet/hosts` | List all hosts |
| `/api/v1/fleet/hosts/count` | Get host count |
| `/api/v1/fleet/hosts/{id}` | Get specific host |
| `/api/v1/fleet/teams` | List all teams |
| `/api/v1/fleet/teams/{id}` | Get specific team |
| `/api/v1/fleet/global/policies` | List global policies |
| `/api/v1/fleet/global/schedule` | List global schedule |
| `/api/v1/fleet/teams/{id}/policies` | List team policies |
| `/api/v1/fleet/queries` | List all queries |
| `/api/v1/fleet/software` | List software inventory |
| `/api/v1/fleet/labels` | List all labels |
| `/api/v1/fleet/labels/{id}` | Get label by ID |
| `/api/v1/fleet/labels/id/{id}` | Delete label by ID |
| `/api/v1/fleet/labels/{name}` | Delete label by name |
| `/api/v1/fleet/activities` | Get activity feed |
| `/api/v1/fleet/spec/enroll_secret` | Get global enroll secrets |

For full API documentation, see: [Fleet REST API](https://fleetdm.com/docs/rest-api/rest-api)
""")


# Self-contained: run with `uv run fleet-api-test.py`
if __name__ == "__main__":
    import os
    import sys

    os.execvp(
        "marimo",
        ["marimo", "run", sys.argv[0], "--host", "127.0.0.1", "--port", "2719"],
    )
