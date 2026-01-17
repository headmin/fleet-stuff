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
    _fleetctl_path_env = _env_vars.get("FLEETCTL_PATH", os.environ.get("FLEETCTL_PATH", ""))

    # Resolve 1Password references
    env_fleet_url = resolve_op_reference(_fleet_url_env)
    env_fleet_token = resolve_op_reference(_fleet_token_env)
    env_fleetctl_path = resolve_op_reference(_fleetctl_path_env)

    return resolve_op_reference, load_env_file, env_fleet_url, env_fleet_token, env_fleetctl_path


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
| `/api/v1/fleet/certificate_authorities` | GET | List all CAs |
| `/api/v1/fleet/certificate_authorities` | POST | Connect new CA |
| `/api/v1/fleet/certificate_authorities/:id` | GET | Get CA details |
| `/api/v1/fleet/certificate_authorities/:id` | PATCH | Update CA |
| `/api/v1/fleet/certificate_authorities/:id` | DELETE | Delete CA |
| `/api/v1/fleet/certificate_authorities/:id/request_certificate` | POST | Request certificate |

### Supported CA Types

| Type | Required Fields |
|------|-----------------|
| **digicert** | name, url, api_token, profile_id |
| **hydrant** | name, url, client_id, client_secret |
| **custom_scep_proxy** | name, url, challenge (optional) |
| **ndes_scep_proxy** | name, url, username, password |
| **custom_est_proxy** | name, url, username, password |
| **smallstep** | name, url, challenge_url (optional) |
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
### Connect Certificate Authority

Connect a new CA to Fleet. Select the CA type to see the required fields.
""")


@app.cell
def _(mo):
    ca_type_dropdown = mo.ui.dropdown(
        options={
            "DigiCert": "digicert",
            "Hydrant": "hydrant",
            "Custom SCEP Proxy": "custom_scep_proxy",
            "NDES SCEP Proxy": "ndes_scep_proxy",
            "Custom EST Proxy": "custom_est_proxy",
            "Smallstep": "smallstep",
        },
        value="DigiCert",
        label="CA Type",
    )

    # Common fields
    ca_name_input = mo.ui.text(placeholder="My Certificate Authority", label="Name", full_width=True)
    ca_url_input = mo.ui.text(placeholder="https://ca.example.com", label="URL", full_width=True)

    # DigiCert fields
    ca_api_token_input = mo.ui.text(placeholder="API Token", label="API Token", kind="password", full_width=True)
    ca_profile_id_input = mo.ui.text(placeholder="Profile ID", label="Profile ID", full_width=True)
    ca_common_name_input = mo.ui.text(placeholder="Certificate Common Name (optional)", label="Certificate Common Name", full_width=True)

    # Hydrant fields
    ca_client_id_input = mo.ui.text(placeholder="Client ID", label="Client ID", full_width=True)
    ca_client_secret_input = mo.ui.text(placeholder="Client Secret", label="Client Secret", kind="password", full_width=True)

    # SCEP/EST fields
    ca_challenge_input = mo.ui.text(placeholder="Challenge (optional for custom_scep_proxy)", label="Challenge", full_width=True)
    ca_username_input = mo.ui.text(placeholder="Username", label="Username", full_width=True)
    ca_password_input = mo.ui.text(placeholder="Password", label="Password", kind="password", full_width=True)

    # Smallstep fields
    ca_challenge_url_input = mo.ui.text(placeholder="Challenge URL (optional)", label="Challenge URL", full_width=True)

    connect_ca_btn = mo.ui.run_button(label="Connect CA")

    return (
        ca_type_dropdown, ca_name_input, ca_url_input, ca_api_token_input, ca_profile_id_input,
        ca_common_name_input, ca_client_id_input, ca_client_secret_input, ca_challenge_input,
        ca_username_input, ca_password_input, ca_challenge_url_input, connect_ca_btn
    )


@app.cell
def _(mo, ca_type_dropdown, ca_name_input, ca_url_input, ca_api_token_input, ca_profile_id_input, ca_common_name_input, ca_client_id_input, ca_client_secret_input, ca_challenge_input, ca_username_input, ca_password_input, ca_challenge_url_input, connect_ca_btn):
    _ca_type = ca_type_dropdown.value

    # Build dynamic form based on CA type
    _common_fields = [ca_type_dropdown, ca_name_input, ca_url_input]

    if _ca_type == "digicert":
        _specific_fields = [ca_api_token_input, ca_profile_id_input, ca_common_name_input]
    elif _ca_type == "hydrant":
        _specific_fields = [ca_client_id_input, ca_client_secret_input]
    elif _ca_type == "custom_scep_proxy":
        _specific_fields = [ca_challenge_input]
    elif _ca_type == "ndes_scep_proxy":
        _specific_fields = [ca_username_input, ca_password_input]
    elif _ca_type == "custom_est_proxy":
        _specific_fields = [ca_username_input, ca_password_input]
    elif _ca_type == "smallstep":
        _specific_fields = [ca_challenge_url_input]
    else:
        _specific_fields = []

    mo.vstack(_common_fields + _specific_fields + [connect_ca_btn])


@app.cell
def _(mo, json, fleet, ca_type_dropdown, ca_name_input, ca_url_input, ca_api_token_input, ca_profile_id_input, ca_common_name_input, ca_client_id_input, ca_client_secret_input, ca_challenge_input, ca_username_input, ca_password_input, ca_challenge_url_input, connect_ca_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not connect_ca_btn.value)
    mo.stop(not ca_name_input.value, fleet_tip("Enter a name for the CA."))
    mo.stop(not ca_url_input.value, fleet_tip("Enter the CA URL."))

    _ca_type = ca_type_dropdown.value
    _ca_config = {
        "name": ca_name_input.value.strip(),
        "url": ca_url_input.value.strip(),
    }

    # Add type-specific fields
    if _ca_type == "digicert":
        if not ca_api_token_input.value or not ca_profile_id_input.value:
            mo.stop(True, fleet_tip("DigiCert requires API Token and Profile ID."))
        _ca_config["api_token"] = ca_api_token_input.value.strip()
        _ca_config["profile_id"] = ca_profile_id_input.value.strip()
        if ca_common_name_input.value:
            _ca_config["certificate_common_name"] = ca_common_name_input.value.strip()
    elif _ca_type == "hydrant":
        if not ca_client_id_input.value or not ca_client_secret_input.value:
            mo.stop(True, fleet_tip("Hydrant requires Client ID and Client Secret."))
        _ca_config["client_id"] = ca_client_id_input.value.strip()
        _ca_config["client_secret"] = ca_client_secret_input.value.strip()
    elif _ca_type == "custom_scep_proxy":
        if ca_challenge_input.value:
            _ca_config["challenge"] = ca_challenge_input.value.strip()
    elif _ca_type == "ndes_scep_proxy":
        if not ca_username_input.value or not ca_password_input.value:
            mo.stop(True, fleet_tip("NDES SCEP requires Username and Password."))
        _ca_config["username"] = ca_username_input.value.strip()
        _ca_config["password"] = ca_password_input.value.strip()
    elif _ca_type == "custom_est_proxy":
        if not ca_username_input.value or not ca_password_input.value:
            mo.stop(True, fleet_tip("Custom EST requires Username and Password."))
        _ca_config["username"] = ca_username_input.value.strip()
        _ca_config["password"] = ca_password_input.value.strip()
    elif _ca_type == "smallstep":
        if ca_challenge_url_input.value:
            _ca_config["challenge_url"] = ca_challenge_url_input.value.strip()

    _payload = {_ca_type: _ca_config}
    _status, _data = fleet("POST", "/api/v1/fleet/certificate_authorities", json_data=_payload)

    if _status in (200, 201):
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Connected {_ca_type} CA: {ca_name_input.value}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to connect CA (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Update Certificate Authority

Update an existing CA. Enter the CA ID and select the CA type to see available fields.
All fields are optional for updates.
""")


@app.cell
def _(mo):
    update_ca_id_input = mo.ui.text(placeholder="CA ID", label="CA ID to Update", full_width=True)

    update_ca_type_dropdown = mo.ui.dropdown(
        options={
            "DigiCert": "digicert",
            "Hydrant": "hydrant",
            "Custom SCEP Proxy": "custom_scep_proxy",
            "NDES SCEP Proxy": "ndes_scep_proxy",
            "Custom EST Proxy": "custom_est_proxy",
            "Smallstep": "smallstep",
        },
        value="DigiCert",
        label="CA Type",
    )

    # Update fields (all optional)
    update_ca_name_input = mo.ui.text(placeholder="New Name (optional)", label="Name", full_width=True)
    update_ca_url_input = mo.ui.text(placeholder="New URL (optional)", label="URL", full_width=True)
    update_ca_api_token_input = mo.ui.text(placeholder="New API Token (optional)", label="API Token", kind="password", full_width=True)
    update_ca_profile_id_input = mo.ui.text(placeholder="New Profile ID (optional)", label="Profile ID", full_width=True)
    update_ca_common_name_input = mo.ui.text(placeholder="New Common Name (optional)", label="Certificate Common Name", full_width=True)
    update_ca_client_id_input = mo.ui.text(placeholder="New Client ID (optional)", label="Client ID", full_width=True)
    update_ca_client_secret_input = mo.ui.text(placeholder="New Client Secret (optional)", label="Client Secret", kind="password", full_width=True)
    update_ca_challenge_input = mo.ui.text(placeholder="New Challenge (optional)", label="Challenge", full_width=True)
    update_ca_username_input = mo.ui.text(placeholder="New Username (optional)", label="Username", full_width=True)
    update_ca_password_input = mo.ui.text(placeholder="New Password (optional)", label="Password", kind="password", full_width=True)
    update_ca_challenge_url_input = mo.ui.text(placeholder="New Challenge URL (optional)", label="Challenge URL", full_width=True)

    update_ca_btn = mo.ui.run_button(label="Update CA")

    return (
        update_ca_id_input, update_ca_type_dropdown, update_ca_name_input, update_ca_url_input,
        update_ca_api_token_input, update_ca_profile_id_input, update_ca_common_name_input,
        update_ca_client_id_input, update_ca_client_secret_input, update_ca_challenge_input,
        update_ca_username_input, update_ca_password_input, update_ca_challenge_url_input, update_ca_btn
    )


@app.cell
def _(mo, update_ca_id_input, update_ca_type_dropdown, update_ca_name_input, update_ca_url_input, update_ca_api_token_input, update_ca_profile_id_input, update_ca_common_name_input, update_ca_client_id_input, update_ca_client_secret_input, update_ca_challenge_input, update_ca_username_input, update_ca_password_input, update_ca_challenge_url_input, update_ca_btn):
    _ca_type = update_ca_type_dropdown.value

    _common_fields = [update_ca_id_input, update_ca_type_dropdown, update_ca_name_input, update_ca_url_input]

    if _ca_type == "digicert":
        _specific_fields = [update_ca_api_token_input, update_ca_profile_id_input, update_ca_common_name_input]
    elif _ca_type == "hydrant":
        _specific_fields = [update_ca_client_id_input, update_ca_client_secret_input]
    elif _ca_type == "custom_scep_proxy":
        _specific_fields = [update_ca_challenge_input]
    elif _ca_type == "ndes_scep_proxy":
        _specific_fields = [update_ca_username_input, update_ca_password_input]
    elif _ca_type == "custom_est_proxy":
        _specific_fields = [update_ca_username_input, update_ca_password_input]
    elif _ca_type == "smallstep":
        _specific_fields = [update_ca_challenge_url_input]
    else:
        _specific_fields = []

    mo.vstack(_common_fields + _specific_fields + [update_ca_btn])


@app.cell
def _(mo, json, fleet, update_ca_id_input, update_ca_type_dropdown, update_ca_name_input, update_ca_url_input, update_ca_api_token_input, update_ca_profile_id_input, update_ca_common_name_input, update_ca_client_id_input, update_ca_client_secret_input, update_ca_challenge_input, update_ca_username_input, update_ca_password_input, update_ca_challenge_url_input, update_ca_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not update_ca_btn.value)
    mo.stop(not update_ca_id_input.value, fleet_tip("Enter a CA ID to update."))

    _ca_id = update_ca_id_input.value.strip()
    _ca_type = update_ca_type_dropdown.value
    _ca_config = {}

    # Add non-empty fields
    if update_ca_name_input.value:
        _ca_config["name"] = update_ca_name_input.value.strip()
    if update_ca_url_input.value:
        _ca_config["url"] = update_ca_url_input.value.strip()

    if _ca_type == "digicert":
        if update_ca_api_token_input.value:
            _ca_config["api_token"] = update_ca_api_token_input.value.strip()
        if update_ca_profile_id_input.value:
            _ca_config["profile_id"] = update_ca_profile_id_input.value.strip()
        if update_ca_common_name_input.value:
            _ca_config["certificate_common_name"] = update_ca_common_name_input.value.strip()
    elif _ca_type == "hydrant":
        if update_ca_client_id_input.value:
            _ca_config["client_id"] = update_ca_client_id_input.value.strip()
        if update_ca_client_secret_input.value:
            _ca_config["client_secret"] = update_ca_client_secret_input.value.strip()
    elif _ca_type == "custom_scep_proxy":
        if update_ca_challenge_input.value:
            _ca_config["challenge"] = update_ca_challenge_input.value.strip()
    elif _ca_type == "ndes_scep_proxy":
        if update_ca_username_input.value:
            _ca_config["username"] = update_ca_username_input.value.strip()
        if update_ca_password_input.value:
            _ca_config["password"] = update_ca_password_input.value.strip()
    elif _ca_type == "custom_est_proxy":
        if update_ca_username_input.value:
            _ca_config["username"] = update_ca_username_input.value.strip()
        if update_ca_password_input.value:
            _ca_config["password"] = update_ca_password_input.value.strip()
    elif _ca_type == "smallstep":
        if update_ca_challenge_url_input.value:
            _ca_config["challenge_url"] = update_ca_challenge_url_input.value.strip()

    if not _ca_config:
        mo.stop(True, fleet_tip("Enter at least one field to update."))

    _payload = {_ca_type: _ca_config}
    _status, _data = fleet("PATCH", f"/api/v1/fleet/certificate_authorities/{_ca_id}", json_data=_payload)

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Updated CA {_ca_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to update CA (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Delete Certificate Authority

Delete a CA from Fleet. This action cannot be undone.
""")


@app.cell
def _(mo):
    delete_ca_id_input = mo.ui.text(placeholder="CA ID", label="CA ID to Delete")
    delete_ca_btn = mo.ui.run_button(label="Delete CA", kind="danger")

    mo.hstack([delete_ca_id_input, delete_ca_btn], justify="start", gap=1)

    return delete_ca_id_input, delete_ca_btn


@app.cell
def _(mo, fleet, delete_ca_id_input, delete_ca_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not delete_ca_btn.value)
    mo.stop(not delete_ca_id_input.value, fleet_tip("Enter a CA ID to delete."))

    _ca_id = delete_ca_id_input.value.strip()
    _status, _data = fleet("DELETE", f"/api/v1/fleet/certificate_authorities/{_ca_id}")

    if _status == 200:
        _result = fleet_success(f"Deleted Certificate Authority {_ca_id}")
    else:
        _result = fleet_error(f"Failed to delete CA (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
---

## Certificate Templates

[📖 API Docs](https://fleetdm.com/docs/rest-api/rest-api#list-certificate-templates)

Manage certificate templates configured in Fleet.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/fleet/certificates` | GET | List all templates |
| `/api/v1/fleet/certificates` | POST | Add new template |
| `/api/v1/fleet/certificates/:id` | GET | Get template details |
| `/api/v1/fleet/certificates/:id` | DELETE | Delete template |

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
### Add Certificate Template

Add a new certificate template. The template links a CA to hosts via team assignment.

#### Subject Name Variables Reference

The subject name field supports Fleet variables that are replaced with device/user-specific values at runtime.

| Variable | Description |
|----------|-------------|
| `$FLEET_VAR_HOST_UUID` | Unique host identifier |
| `$FLEET_VAR_HOST_HARDWARE_SERIAL` | Device hardware serial number |
| `$FLEET_VAR_HOST_END_USER_IDP_USERNAME` | End user's IDP username (typically email) |
| `$FLEET_VAR_HOST_END_USER_IDP_USERNAME_LOCAL_PART` | Local part of IDP username (before @) |
| `$FLEET_VAR_HOST_END_USER_IDP_FULL_NAME` | End user's full name from IDP |
| `$FLEET_VAR_HOST_END_USER_IDP_DEPARTMENT` | End user's department from IDP |
| `$FLEET_VAR_HOST_END_USER_IDP_GROUPS` | Comma-separated IDP group memberships |
| `$FLEET_VAR_HOST_PLATFORM` | Device platform (darwin, windows, linux) |

**Subject Name Format:** Uses DN (Distinguished Name) format: `/KEY=value/KEY=value`

Common DN keys: `CN` (Common Name), `OU` (Organizational Unit), `O` (Organization), `ST` (State), `C` (Country)
""")


@app.cell
def _(mo):
    # Subject name builder - Fleet variables and common templates
    FLEET_VARS = {
        "Host UUID": "$FLEET_VAR_HOST_UUID",
        "Hardware Serial": "$FLEET_VAR_HOST_HARDWARE_SERIAL",
        "IDP Username": "$FLEET_VAR_HOST_END_USER_IDP_USERNAME",
        "IDP Username (local part)": "$FLEET_VAR_HOST_END_USER_IDP_USERNAME_LOCAL_PART",
        "IDP Full Name": "$FLEET_VAR_HOST_END_USER_IDP_FULL_NAME",
        "IDP Department": "$FLEET_VAR_HOST_END_USER_IDP_DEPARTMENT",
        "IDP Groups": "$FLEET_VAR_HOST_END_USER_IDP_GROUPS",
        "Host Platform": "$FLEET_VAR_HOST_PLATFORM",
    }

    SUBJECT_TEMPLATES = {
        "WiFi Certificate (User + Device)": "/CN=$FLEET_VAR_HOST_END_USER_IDP_USERNAME/OU=$FLEET_VAR_HOST_UUID/ST=$FLEET_VAR_HOST_HARDWARE_SERIAL",
        "VPN Certificate (User + UUID)": "/CN=$FLEET_VAR_HOST_END_USER_IDP_USERNAME/OU=$FLEET_VAR_HOST_UUID",
        "Device Only (Serial + UUID)": "/CN=$FLEET_VAR_HOST_HARDWARE_SERIAL/OU=$FLEET_VAR_HOST_UUID",
        "User Email Only": "/CN=$FLEET_VAR_HOST_END_USER_IDP_USERNAME",
        "Full User Info": "/CN=$FLEET_VAR_HOST_END_USER_IDP_FULL_NAME/OU=$FLEET_VAR_HOST_END_USER_IDP_DEPARTMENT/O=$FLEET_VAR_HOST_END_USER_IDP_USERNAME",
        "Custom (build below)": "",
    }

    # Template selector
    subject_template_dropdown = mo.ui.dropdown(
        options=SUBJECT_TEMPLATES,
        value="WiFi Certificate (User + Device)",
        label="Quick Template",
    )

    # DN components for custom builder
    dn_cn_var = mo.ui.dropdown(
        options={"(none)": "", **FLEET_VARS},
        value="IDP Username",
        label="CN (Common Name)",
    )

    dn_ou_var = mo.ui.dropdown(
        options={"(none)": "", **FLEET_VARS},
        value="Host UUID",
        label="OU (Org Unit)",
    )

    dn_o_var = mo.ui.dropdown(
        options={"(none)": "", "(custom text)": "CUSTOM", **FLEET_VARS},
        value="(none)",
        label="O (Organization)",
    )

    dn_o_custom_text = mo.ui.text(placeholder="Custom org name", label="Custom O")

    dn_st_var = mo.ui.dropdown(
        options={"(none)": "", **FLEET_VARS},
        value="(none)",
        label="ST (State/Extra)",
    )

    return FLEET_VARS, SUBJECT_TEMPLATES, subject_template_dropdown, dn_cn_var, dn_ou_var, dn_o_var, dn_o_custom_text, dn_st_var


@app.cell
def _(mo, SUBJECT_TEMPLATES, subject_template_dropdown, dn_cn_var, dn_ou_var, dn_o_var, dn_o_custom_text, dn_st_var):
    # Build subject name from template or custom components
    _template_value = subject_template_dropdown.value

    if _template_value:
        # Using a preset template
        built_subject_name = _template_value
        _builder_mode = "template"
    else:
        # Build custom subject name from components
        _parts = []
        if dn_cn_var.value:
            _parts.append(f"/CN={dn_cn_var.value}")
        if dn_ou_var.value:
            _parts.append(f"/OU={dn_ou_var.value}")
        if dn_o_var.value:
            if dn_o_var.value == "CUSTOM" and dn_o_custom_text.value:
                _parts.append(f"/O={dn_o_custom_text.value}")
            elif dn_o_var.value != "CUSTOM":
                _parts.append(f"/O={dn_o_var.value}")
        if dn_st_var.value:
            _parts.append(f"/ST={dn_st_var.value}")

        built_subject_name = "".join(_parts) if _parts else ""
        _builder_mode = "custom"

    mo.vstack([
        mo.md("#### Subject Name Builder"),
        subject_template_dropdown,
        mo.md("**Custom Builder** *(select 'Custom' template above to use)*:"),
        mo.hstack([dn_cn_var, dn_ou_var], gap=1),
        mo.hstack([dn_o_var, dn_o_custom_text, dn_st_var], gap=1),
        mo.callout(
            mo.md(f"**Built Subject Name:**\n```\n{built_subject_name}\n```") if built_subject_name else mo.md("*Select a template or build custom*"),
            kind="info",
        ),
    ])

    return (built_subject_name,)


@app.cell
def _(mo, built_subject_name):
    add_cert_name_input = mo.ui.text(
        placeholder="My Certificate Template",
        label="Name (max 255 characters)",
        full_width=True,
    )

    add_cert_ca_id_input = mo.ui.text(
        placeholder="Certificate Authority ID",
        label="Certificate Authority ID",
        full_width=True,
    )

    # Pre-fill with built subject name, but allow override
    add_cert_subject_input = mo.ui.text(
        placeholder="CN=$FLEET_VAR_HOST_END_USER_IDP_USERNAME",
        label="Subject Name (edit or use builder above)",
        value=built_subject_name if built_subject_name else "",
        full_width=True,
    )

    add_cert_team_id_input = mo.ui.number(
        start=0, stop=999999, step=1, value=0,
        label="Team ID (0 = no team)",
    )

    add_cert_btn = mo.ui.run_button(label="Add Certificate Template")

    mo.vstack([
        mo.md("#### Template Details"),
        add_cert_name_input,
        add_cert_ca_id_input,
        add_cert_subject_input,
        add_cert_team_id_input,
        mo.hstack([add_cert_btn], justify="start"),
    ])

    return add_cert_name_input, add_cert_ca_id_input, add_cert_subject_input, add_cert_team_id_input, add_cert_btn


@app.cell
def _(mo, json, fleet, add_cert_name_input, add_cert_ca_id_input, add_cert_subject_input, add_cert_team_id_input, add_cert_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not add_cert_btn.value)
    mo.stop(not add_cert_name_input.value, fleet_tip("Enter a name for the certificate template."))
    mo.stop(not add_cert_ca_id_input.value, fleet_tip("Enter a Certificate Authority ID."))
    mo.stop(not add_cert_subject_input.value, fleet_tip("Enter a subject name for the certificate."))

    _payload = {
        "name": add_cert_name_input.value.strip()[:255],
        "certificate_authority_id": int(add_cert_ca_id_input.value.strip()),
        "subject_name": add_cert_subject_input.value.strip(),
    }

    # Add team_id if specified (non-zero)
    if add_cert_team_id_input.value > 0:
        _payload["team_id"] = add_cert_team_id_input.value

    _status, _data = fleet("POST", "/api/v1/fleet/certificates", json_data=_payload)

    if _status in (200, 201):
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Created certificate template: {add_cert_name_input.value}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to add certificate template (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Delete Certificate Template

Delete a certificate template from Fleet. This action cannot be undone.
""")


@app.cell
def _(mo):
    delete_cert_id_input = mo.ui.text(placeholder="Certificate Template ID", label="Certificate ID to Delete")
    delete_cert_btn = mo.ui.run_button(label="Delete Template", kind="danger")

    mo.hstack([delete_cert_id_input, delete_cert_btn], justify="start", gap=1)

    return delete_cert_id_input, delete_cert_btn


@app.cell
def _(mo, fleet, delete_cert_id_input, delete_cert_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not delete_cert_btn.value)
    mo.stop(not delete_cert_id_input.value, fleet_tip("Enter a Certificate Template ID to delete."))

    _cert_id = delete_cert_id_input.value.strip()
    _status, _data = fleet("DELETE", f"/api/v1/fleet/certificates/{_cert_id}")

    if _status == 200:
        _result = fleet_success(f"Deleted Certificate Template {_cert_id}")
    else:
        _result = fleet_error(f"Failed to delete certificate template (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
---

## Request Certificate

[📖 API Docs](https://fleetdm.com/docs/rest-api/rest-api#request-certificate)

Request a certificate from a Certificate Authority. This endpoint is used by devices
to request certificates using a CSR (Certificate Signing Request).

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/fleet/certificate_authorities/:id/request_certificate` | POST | Request a certificate |

**Supported CA Types:**
- Hydrant
- Custom EST Proxy

**Required Fields:**
- `csr` - PEM-encoded Certificate Signing Request

**Optional IDP Authentication Fields:**
- `idp_oauth_url` - Identity Provider OAuth URL
- `idp_access_token` - IDP access token
- `idp_client_id` - IDP client ID
""")


@app.cell
def _(mo):
    request_cert_ca_id_input = mo.ui.text(
        placeholder="Certificate Authority ID",
        label="CA ID",
        full_width=True,
    )

    request_cert_csr_input = mo.ui.text_area(
        placeholder="""-----BEGIN CERTIFICATE REQUEST-----
MIICYTCCAUkCAQAwHDELMAkGA1UEBhMCVVMxDTALBgNVBAoMBFRlc3QwggEiMA0G
...
-----END CERTIFICATE REQUEST-----""",
        label="CSR (PEM format)",
        full_width=True,
        rows=10,
    )

    request_cert_idp_url_input = mo.ui.text(
        placeholder="https://idp.example.com/oauth (optional)",
        label="IDP OAuth URL (optional)",
        full_width=True,
    )

    request_cert_idp_token_input = mo.ui.text(
        placeholder="IDP access token (optional)",
        label="IDP Access Token (optional)",
        kind="password",
        full_width=True,
    )

    request_cert_idp_client_id_input = mo.ui.text(
        placeholder="IDP client ID (optional)",
        label="IDP Client ID (optional)",
        full_width=True,
    )

    request_cert_btn = mo.ui.run_button(label="Request Certificate")

    mo.vstack([
        request_cert_ca_id_input,
        request_cert_csr_input,
        mo.md("**Optional IDP Authentication:**"),
        request_cert_idp_url_input,
        request_cert_idp_token_input,
        request_cert_idp_client_id_input,
        mo.hstack([request_cert_btn], justify="start"),
    ])

    return (
        request_cert_ca_id_input, request_cert_csr_input, request_cert_idp_url_input,
        request_cert_idp_token_input, request_cert_idp_client_id_input, request_cert_btn
    )


@app.cell
def _(mo, json, fleet, request_cert_ca_id_input, request_cert_csr_input, request_cert_idp_url_input, request_cert_idp_token_input, request_cert_idp_client_id_input, request_cert_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not request_cert_btn.value)
    mo.stop(not request_cert_ca_id_input.value, fleet_tip("Enter a Certificate Authority ID."))
    mo.stop(not request_cert_csr_input.value, fleet_tip("Enter a PEM-encoded CSR."))

    _ca_id = request_cert_ca_id_input.value.strip()
    _payload = {
        "csr": request_cert_csr_input.value.strip(),
    }

    # Add optional IDP fields if provided
    if request_cert_idp_url_input.value:
        _payload["idp_oauth_url"] = request_cert_idp_url_input.value.strip()
    if request_cert_idp_token_input.value:
        _payload["idp_access_token"] = request_cert_idp_token_input.value.strip()
    if request_cert_idp_client_id_input.value:
        _payload["idp_client_id"] = request_cert_idp_client_id_input.value.strip()

    _status, _data = fleet("POST", f"/api/v1/fleet/certificate_authorities/{_ca_id}/request_certificate", json_data=_payload)

    if _status in (200, 201):
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Certificate requested from CA {_ca_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to request certificate (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
---

## Webhook Settings

[📖 API Docs](https://fleetdm.com/docs/rest-api/rest-api#webhook-settings)

View and manage Fleet webhook configurations. Webhooks notify external services about Fleet events.

### Webhook Types and Trigger Behavior

| Webhook | Trigger | Controlled by `interval`? |
|---------|---------|---------------------------|
| **host_status_webhook** | Scheduled (cron-like) | Yes |
| **failing_policies_webhook** | Scheduled (cron-like) | Yes |
| **vulnerabilities_webhook** | Event-driven (when CVEs detected) | No |
| **activities_webhook** | Real-time (immediate, async) | No |

### Configuration Notes

**`interval` setting:**
- Only applies to `host_status_webhook` and `failing_policies_webhook`
- Default: `"24h"`
- Valid formats: Go duration strings (`"1h"`, `"30m"`, `"90m"`, `"24h"`, `"1h30m"`)

**`policy_ids` (failing_policies_webhook only):**
- Array of specific policy IDs to monitor
- If empty, monitors all policies

**Validation rules:**
- Cannot enable vulnerabilities webhook AND Jira/Zendesk vulnerability automation simultaneously
- Cannot enable failing policies webhook AND Jira/Zendesk failing policies automation simultaneously
- Destination URL required when webhook is enabled
""")


@app.cell
def _(mo, json, fleet, fleet_success, fleet_error):
    get_webhooks_btn = mo.ui.run_button(label="Get Current Webhook Settings")

    mo.hstack([get_webhooks_btn], justify="start")

    return (get_webhooks_btn,)


@app.cell
def _(mo, json, fleet, get_webhooks_btn, fleet_success, fleet_error, fleet_note):
    mo.stop(not get_webhooks_btn.value)

    _status, _data = fleet("GET", "/api/v1/fleet/config")

    if _status == 200:
        _webhook_settings = _data.get("webhook_settings", {})
        _integrations = _data.get("integrations", {})

        # Extract interval (at top level of webhook_settings)
        _interval = _webhook_settings.get("interval", "not returned by API")

        # Build summary table
        _summary_rows = []
        for _wh_key in ["host_status_webhook", "failing_policies_webhook", "vulnerabilities_webhook", "activities_webhook"]:
            _wh = _webhook_settings.get(_wh_key, {})
            _enabled = _wh.get(f"enable_{_wh_key}", False)
            _url = _wh.get("destination_url", "")
            _summary_rows.append(f"| `{_wh_key}` | {'Yes' if _enabled else 'No'} | `{_url[:40]}{'...' if len(_url) > 40 else ''}` |")

        _summary_table = "\n".join(_summary_rows)

        _formatted = json.dumps(_webhook_settings, indent=2)
        _integrations_formatted = json.dumps(_integrations, indent=2) if _integrations else "{}"

        _result = mo.vstack([
            fleet_success("Current Webhook Settings"),
            mo.md(f"""
### Summary

**Interval:** `{_interval}` (applies to host_status & failing_policies only)

| Webhook | Enabled | Destination URL |
|---------|---------|-----------------|
{_summary_table}
"""),
            fleet_note("The <code>interval</code> field may not be returned by the API in some Fleet versions. If it shows 'not returned', the server is using the default (24h) or the value was set but isn't exposed via GET."),
            mo.md(f"""
### Full webhook_settings Response

```json
{_formatted}
```

### Related: integrations (can conflict with webhooks)

```json
{_integrations_formatted}
```
"""),
        ])
    else:
        _result = fleet_error(f"Failed to get config (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Get Config via fleetctl

The `fleetctl` CLI may return more configuration details than the REST API, including the `interval` setting.

**Configuration options:**
- Set `FLEETCTL_PATH` in `.env` file or environment to specify the path to `fleetctl` binary
- If not set, defaults to `fleetctl` (must be in PATH)
- Can also use pre-configured fleetctl (with `fleetctl config set --address <url> --token <token>`)
""")


@app.cell
def _(mo, env_fleetctl_path):
    fleetctl_path_input = mo.ui.text(
        placeholder="/usr/local/bin/fleetctl",
        label="Path to fleetctl binary",
        value=env_fleetctl_path if env_fleetctl_path else "fleetctl",
        full_width=True,
    )

    fleetctl_use_env = mo.ui.checkbox(
        label="Use pre-configured fleetctl (ignore URL/token fields)",
        value=False,
    )

    run_fleetctl_btn = mo.ui.run_button(label="Run: fleetctl get config")

    mo.vstack([
        fleetctl_path_input,
        fleetctl_use_env,
        mo.hstack([run_fleetctl_btn], justify="start"),
    ])

    return fleetctl_path_input, fleetctl_use_env, run_fleetctl_btn


@app.cell
def _(mo, subprocess, fleet_url_input, api_token_input, fleetctl_path_input, fleetctl_use_env, run_fleetctl_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not run_fleetctl_btn.value)

    _url = fleet_url_input.value.rstrip("/") if fleet_url_input.value else ""
    _token = api_token_input.value.strip() if api_token_input.value else ""
    _fleetctl = fleetctl_path_input.value.strip() if fleetctl_path_input.value else "fleetctl"

    # fleetctl requires config set first, then get config (doesn't accept --address/--token on get)
    if fleetctl_use_env.value:
        # Use existing fleetctl config
        _cmd = [_fleetctl, "get", "config", "--yaml"]
        _auth_info = "Using fleetctl's pre-configured credentials (from `fleetctl config set`)"
        _cmd_display = "$FLEETCTL_PATH get config --yaml"
        _config_needed = False
    else:
        if not _url or not _token:
            mo.stop(True, fleet_tip("Enter Fleet URL and API Token above, or check 'Use pre-configured fleetctl'."))
        _auth_info = f"Using notebook credentials: `{_url}` with token `{_token[:8]}...` ({len(_token)} chars)"
        _cmd_display = "$FLEETCTL_PATH config set ... && $FLEETCTL_PATH get config --yaml"
        _config_needed = True

    try:
        if _config_needed:
            # First, configure fleetctl with credentials
            _config_cmd = [_fleetctl, "config", "set", "--address", _url, "--token", _token]
            _config_proc = subprocess.run(
                _config_cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if _config_proc.returncode != 0:
                _error = _config_proc.stderr or _config_proc.stdout or "Unknown error"
                _result = fleet_error(f"fleetctl config set failed: {_error[:500]}")
                mo.stop(True, _result)

        # Now get the config
        _cmd = [_fleetctl, "get", "config", "--yaml"]
        _proc = subprocess.run(
            _cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if _proc.returncode == 0:
            _output = _proc.stdout
            # Highlight the interval line if present
            _has_interval = "interval:" in _output

            _result = mo.vstack([
                fleet_success("fleetctl get config succeeded"),
                mo.md(f"**Auth mode:** {_auth_info}"),
                mo.md(f"**Contains interval setting:** {'Yes' if _has_interval else 'No'}"),
                mo.md(f"""
```yaml
{_output[:8000]}{'... (truncated)' if len(_output) > 8000 else ''}
```
"""),
            ])
        else:
            # fleetctl may output errors to stdout or stderr
            _stderr = _proc.stderr.strip() if _proc.stderr else ""
            _stdout = _proc.stdout.strip() if _proc.stdout else ""
            _error_output = _stderr or _stdout or "No error message"
            _help_msg = ""
            if "unauthenticated" in _error_output.lower() or "token" in _error_output.lower():
                if fleetctl_use_env.value:
                    _help_msg = "\n\n**Tip:** Uncheck 'Use pre-configured fleetctl' to use the notebook's URL/token instead."
                else:
                    _help_msg = "\n\n**Tip:** Verify your API token is valid. The REST API test above can confirm if the token works."

            _debug_info = f"""
**Auth mode:** {_auth_info}
**Command:** `{_cmd_display}`
**Exit code:** {_proc.returncode}
**stderr:** `{_stderr[:200] or '(empty)'}`
**stdout:** `{_stdout[:200] or '(empty)'}`
"""
            _result = mo.vstack([
                fleet_error(f"fleetctl failed: {_error_output[:500]}{_help_msg}"),
                mo.md(_debug_info),
            ])

    except FileNotFoundError:
        _result = fleet_error(f"fleetctl not found at '{_fleetctl}'. Set FLEETCTL_PATH in .env or enter the correct path above.")
    except subprocess.TimeoutExpired:
        _result = fleet_error("fleetctl command timed out after 30 seconds")
    except Exception as e:
        _result = fleet_error(f"Error running fleetctl: {str(e)}")

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

    webhook_interval = mo.ui.text(
        placeholder="24h",
        value="24h",
        label="Interval - host_status & failing_policies only (e.g. 90m, 24h)",
    )

    policy_ids_input = mo.ui.text(
        placeholder="1, 5, 12 (comma-separated policy IDs)",
        label="Policy IDs (failing_policies only, leave empty for all)",
        full_width=True,
    )

    update_webhook_btn = mo.ui.run_button(label="Update Webhook")

    mo.vstack([
        webhook_type_dropdown,
        webhook_enabled,
        webhook_url,
        host_percentage,
        days_count,
        host_batch_size,
        policy_ids_input,
        webhook_interval,
        mo.hstack([update_webhook_btn], justify="start"),
    ])

    return webhook_type_dropdown, webhook_enabled, webhook_url, host_percentage, days_count, host_batch_size, policy_ids_input, webhook_interval, update_webhook_btn


@app.cell
def _(mo, json, fleet, webhook_type_dropdown, webhook_enabled, webhook_url, host_percentage, days_count, host_batch_size, policy_ids_input, webhook_interval, update_webhook_btn, fleet_success, fleet_error, fleet_tip):
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
    elif _webhook_key == "failing_policies_webhook":
        _webhook_config["host_batch_size"] = host_batch_size.value
        # Parse policy_ids from comma-separated string
        if policy_ids_input.value.strip():
            _policy_ids = [int(pid.strip()) for pid in policy_ids_input.value.split(",") if pid.strip().isdigit()]
            if _policy_ids:
                _webhook_config["policy_ids"] = _policy_ids
    elif _webhook_key == "vulnerabilities_webhook":
        _webhook_config["host_batch_size"] = host_batch_size.value

    _payload = {
        "webhook_settings": {
            "interval": webhook_interval.value,
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
