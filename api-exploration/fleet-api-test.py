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
def _(mo, json):
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

    def fleet_output(title, data, success=True):
        """Create collapsible output with JSON data.

        Args:
            title: Header text for the accordion
            data: Data to display (will be JSON formatted if dict/list)
            success: If True, show success styling; if False, show error styling
        """
        if isinstance(data, (dict, list)):
            _formatted = json.dumps(data, indent=2)
        else:
            _formatted = str(data)

        _header = fleet_success(title) if success else fleet_error(title)
        _content = mo.md(f"```json\n{_formatted}\n```")

        return mo.vstack([
            _header,
            mo.accordion({f"View Response ({len(_formatted):,} chars)": _content}),
        ])

    return fleet_note, fleet_tip, fleet_warning, fleet_success, fleet_error, fleet_output


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

## Custom Variables

[📖 API Docs](https://fleetdm.com/docs/rest-api/rest-api#custom-variables)

Manage custom variables that can be used in scripts and profiles. Custom variables are prefixed with `$FLEET_SECRET_` and allow you to inject secrets into scripts without exposing them in source code.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/fleet/custom_variables` | GET | List all custom variables |
| `/api/v1/fleet/custom_variables` | POST | Create a custom variable |
| `/api/v1/fleet/custom_variables/:name` | DELETE | Delete a custom variable |

**Usage in scripts:**
```bash
echo "Connecting to $FLEET_SECRET_API_KEY"
```

**Variable names:** Must be alphanumeric with underscores (e.g., `API_KEY`, `DB_PASSWORD`). The `$FLEET_SECRET_` prefix is added automatically.
""")


@app.cell
def _(mo):
    list_custom_vars_btn = mo.ui.run_button(label="List Custom Variables")

    mo.hstack([list_custom_vars_btn], justify="start")

    return (list_custom_vars_btn,)


@app.cell
def _(mo, json, fleet, list_custom_vars_btn, fleet_success, fleet_error):
    mo.stop(not list_custom_vars_btn.value)

    _status, _data = fleet("GET", "/api/v1/fleet/custom_variables")

    if _status == 200:
        _vars = _data.get("custom_variables", [])
        if _vars:
            _formatted = json.dumps(_vars, indent=2)
            _result = mo.vstack([
                fleet_success(f"Found {len(_vars)} custom variable(s)"),
                mo.md(f"```json\n{_formatted}\n```"),
            ])
        else:
            _result = mo.md("**No custom variables configured.**")
    else:
        _result = fleet_error(f"Failed to list custom variables (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Create Custom Variable

Create a new custom variable. The variable will be available as `$FLEET_SECRET_<name>` in scripts and profiles.
""")


@app.cell
def _(mo):
    custom_var_name_input = mo.ui.text(
        placeholder="API_KEY",
        label="Variable Name (without FLEET_SECRET_ prefix)",
        full_width=True,
    )

    custom_var_value_input = mo.ui.text(
        placeholder="your-secret-value",
        label="Variable Value",
        kind="password",
        full_width=True,
    )

    custom_var_team_id_input = mo.ui.number(
        start=0, stop=999999, step=1, value=0,
        label="Team ID (0 = global)",
    )

    create_custom_var_btn = mo.ui.run_button(label="Create Variable")

    mo.vstack([
        custom_var_name_input,
        custom_var_value_input,
        custom_var_team_id_input,
        mo.hstack([create_custom_var_btn], justify="start"),
    ])

    return custom_var_name_input, custom_var_value_input, custom_var_team_id_input, create_custom_var_btn


@app.cell
def _(mo, json, fleet, custom_var_name_input, custom_var_value_input, custom_var_team_id_input, create_custom_var_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not create_custom_var_btn.value)
    mo.stop(not custom_var_name_input.value, fleet_tip("Enter a variable name."))
    mo.stop(not custom_var_value_input.value, fleet_tip("Enter a variable value."))

    _payload = {
        "name": custom_var_name_input.value.strip(),
        "value": custom_var_value_input.value,
    }

    # Add team_id if specified (non-zero)
    if custom_var_team_id_input.value > 0:
        _payload["team_id"] = custom_var_team_id_input.value

    _status, _data = fleet("POST", "/api/v1/fleet/custom_variables", json_data=_payload)

    if _status in (200, 201):
        _var_name = custom_var_name_input.value.strip()
        _result = mo.vstack([
            fleet_success(f"Created custom variable: <code>$FLEET_SECRET_{_var_name}</code>"),
            mo.md(f"```json\n{json.dumps(_data, indent=2)}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to create custom variable (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Delete Custom Variable

Delete a custom variable. This action cannot be undone.
""")


@app.cell
def _(mo):
    delete_custom_var_name_input = mo.ui.text(
        placeholder="API_KEY",
        label="Variable Name to Delete (without FLEET_SECRET_ prefix)",
    )
    delete_custom_var_btn = mo.ui.run_button(label="Delete Variable", kind="danger")

    mo.hstack([delete_custom_var_name_input, delete_custom_var_btn], justify="start", gap=1)

    return delete_custom_var_name_input, delete_custom_var_btn


@app.cell
def _(mo, fleet, delete_custom_var_name_input, delete_custom_var_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not delete_custom_var_btn.value)
    mo.stop(not delete_custom_var_name_input.value, fleet_tip("Enter a variable name to delete."))

    _var_name = delete_custom_var_name_input.value.strip()
    _status, _data = fleet("DELETE", f"/api/v1/fleet/custom_variables/{_var_name}")

    if _status == 200:
        _result = fleet_success(f"Deleted custom variable: <code>$FLEET_SECRET_{_var_name}</code>")
    else:
        _result = fleet_error(f"Failed to delete custom variable (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
---

## Teams

[📖 API Docs](https://fleetdm.com/docs/rest-api/rest-api#teams)

Manage Fleet teams. Teams allow you to segment hosts and apply different configurations.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/fleet/teams` | GET | List all teams |
| `/api/v1/fleet/teams/:id` | GET | Get team details |
| `/api/v1/fleet/teams` | POST | Create team |
| `/api/v1/fleet/teams/:id` | PATCH | Update team |
| `/api/v1/fleet/teams/:id/users` | PATCH | Add users to team |
| `/api/v1/fleet/teams/:id/agent_options` | POST | Update team's agent options |
| `/api/v1/fleet/teams/:id` | DELETE | Delete team |
""")


@app.cell
def _(mo):
    list_teams_btn = mo.ui.run_button(label="List Teams")
    team_id_input = mo.ui.text(placeholder="Team ID", label="Team ID")
    get_team_btn = mo.ui.run_button(label="Get Team")

    mo.vstack([
        mo.hstack([list_teams_btn], justify="start"),
        mo.hstack([team_id_input, get_team_btn], justify="start", gap=1),
    ])

    return list_teams_btn, team_id_input, get_team_btn


@app.cell
def _(mo, json, fleet, list_teams_btn, fleet_success, fleet_error):
    mo.stop(not list_teams_btn.value)

    _status, _data = fleet("GET", "/api/v1/fleet/teams")

    if _status == 200:
        _teams = _data.get("teams", [])
        if _teams:
            _formatted = json.dumps(_teams, indent=2)
            _result = mo.vstack([
                fleet_success(f"Found {len(_teams)} teams"),
                mo.md(f"```json\n{_formatted}\n```"),
            ])
        else:
            _result = mo.md("**No teams found.** Teams are a Fleet Premium feature.")
    else:
        _result = fleet_error(f"Failed to list teams (status {_status}): {_data}")

    _result


@app.cell
def _(mo, json, fleet, team_id_input, get_team_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not get_team_btn.value)
    mo.stop(not team_id_input.value, fleet_tip("Enter a Team ID."))

    _team_id = team_id_input.value.strip()
    _status, _data = fleet("GET", f"/api/v1/fleet/teams/{_team_id}")

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Team {_team_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get team (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Create Team

Create a new team. Teams are a Fleet Premium feature.
""")


@app.cell
def _(mo):
    create_team_name = mo.ui.text(placeholder="Engineering", label="Team Name", full_width=True)
    create_team_description = mo.ui.text(placeholder="Engineering department hosts", label="Description (optional)", full_width=True)

    create_team_btn = mo.ui.run_button(label="Create Team")

    mo.vstack([
        create_team_name,
        create_team_description,
        mo.hstack([create_team_btn], justify="start"),
    ])

    return create_team_name, create_team_description, create_team_btn


@app.cell
def _(mo, json, fleet, create_team_name, create_team_description, create_team_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not create_team_btn.value)
    mo.stop(not create_team_name.value, fleet_tip("Enter a team name."))

    _payload = {
        "name": create_team_name.value.strip(),
    }

    if create_team_description.value:
        _payload["description"] = create_team_description.value.strip()

    _status, _data = fleet("POST", "/api/v1/fleet/teams", json_data=_payload)

    if _status in (200, 201):
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Created team: {create_team_name.value}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to create team (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Update Team

Update an existing team's name or description.
""")


@app.cell
def _(mo):
    update_team_id = mo.ui.text(placeholder="Team ID", label="Team ID to Update", full_width=True)
    update_team_name = mo.ui.text(placeholder="New name (optional)", label="Name", full_width=True)
    update_team_description = mo.ui.text(placeholder="New description (optional)", label="Description", full_width=True)

    update_team_btn = mo.ui.run_button(label="Update Team")

    mo.vstack([
        update_team_id,
        update_team_name,
        update_team_description,
        mo.hstack([update_team_btn], justify="start"),
    ])

    return update_team_id, update_team_name, update_team_description, update_team_btn


@app.cell
def _(mo, json, fleet, update_team_id, update_team_name, update_team_description, update_team_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not update_team_btn.value)
    mo.stop(not update_team_id.value, fleet_tip("Enter a Team ID."))

    _team_id = update_team_id.value.strip()
    _payload = {}

    if update_team_name.value:
        _payload["name"] = update_team_name.value.strip()
    if update_team_description.value:
        _payload["description"] = update_team_description.value.strip()

    if not _payload:
        mo.stop(True, fleet_tip("Enter at least one field to update."))

    _status, _data = fleet("PATCH", f"/api/v1/fleet/teams/{_team_id}", json_data=_payload)

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Updated team {_team_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to update team (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Add Users to Team

Add users to a team by specifying their user IDs and roles.
""")


@app.cell
def _(mo):
    team_users_team_id = mo.ui.text(placeholder="Team ID", label="Team ID", full_width=True)
    team_users_ids = mo.ui.text(
        placeholder="1, 5, 12 (comma-separated user IDs)",
        label="User IDs to Add",
        full_width=True,
    )
    team_users_role = mo.ui.dropdown(
        options={
            "Observer": "observer",
            "Observer+": "observer_plus",
            "Maintainer": "maintainer",
            "Admin": "admin",
        },
        value="Observer",
        label="Role for Users",
    )

    add_team_users_btn = mo.ui.run_button(label="Add Users to Team")

    mo.vstack([
        team_users_team_id,
        team_users_ids,
        team_users_role,
        mo.hstack([add_team_users_btn], justify="start"),
    ])

    return team_users_team_id, team_users_ids, team_users_role, add_team_users_btn


@app.cell
def _(mo, json, fleet, team_users_team_id, team_users_ids, team_users_role, add_team_users_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not add_team_users_btn.value)
    mo.stop(not team_users_team_id.value, fleet_tip("Enter a Team ID."))
    mo.stop(not team_users_ids.value, fleet_tip("Enter User IDs."))

    _team_id = team_users_team_id.value.strip()
    _user_ids = [int(uid.strip()) for uid in team_users_ids.value.split(",") if uid.strip().isdigit()]

    if not _user_ids:
        mo.stop(True, fleet_tip("Enter valid User IDs."))

    _users = [{"id": uid, "role": team_users_role.value} for uid in _user_ids]
    _payload = {"users": _users}

    _status, _data = fleet("PATCH", f"/api/v1/fleet/teams/{_team_id}/users", json_data=_payload)

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Added {len(_user_ids)} user(s) to team {_team_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to add users to team (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Update Team Agent Options

Configure osquery agent options for a specific team.
""")


@app.cell
def _(mo):
    agent_options_team_id = mo.ui.text(placeholder="Team ID", label="Team ID", full_width=True)
    agent_options_json = mo.ui.text_area(
        placeholder="""{
  "config": {
    "options": {
      "logger_plugin": "tls",
      "pack_delimiter": "/",
      "distributed_interval": 10,
      "disable_distributed": false
    }
  }
}""",
        label="Agent Options (JSON)",
        full_width=True,
        rows=10,
    )

    update_agent_options_btn = mo.ui.run_button(label="Update Agent Options")

    mo.vstack([
        agent_options_team_id,
        agent_options_json,
        mo.hstack([update_agent_options_btn], justify="start"),
    ])

    return agent_options_team_id, agent_options_json, update_agent_options_btn


@app.cell
def _(mo, json, fleet, agent_options_team_id, agent_options_json, update_agent_options_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not update_agent_options_btn.value)
    mo.stop(not agent_options_team_id.value, fleet_tip("Enter a Team ID."))
    mo.stop(not agent_options_json.value, fleet_tip("Enter agent options JSON."))

    _team_id = agent_options_team_id.value.strip()

    try:
        _payload = json.loads(agent_options_json.value)
    except json.JSONDecodeError as e:
        mo.stop(True, fleet_error(f"Invalid JSON: {e}"))

    _status, _data = fleet("POST", f"/api/v1/fleet/teams/{_team_id}/agent_options", json_data=_payload)

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Updated agent options for team {_team_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to update agent options (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Delete Team

Delete a team. This action cannot be undone.
""")


@app.cell
def _(mo):
    delete_team_id_input = mo.ui.text(placeholder="Team ID", label="Team ID to Delete")
    delete_team_btn = mo.ui.run_button(label="Delete Team", kind="danger")

    mo.hstack([delete_team_id_input, delete_team_btn], justify="start", gap=1)

    return delete_team_id_input, delete_team_btn


@app.cell
def _(mo, fleet, delete_team_id_input, delete_team_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not delete_team_btn.value)
    mo.stop(not delete_team_id_input.value, fleet_tip("Enter a Team ID."))

    _team_id = delete_team_id_input.value.strip()
    _status, _data = fleet("DELETE", f"/api/v1/fleet/teams/{_team_id}")

    if _status == 200:
        _result = fleet_success(f"Deleted team {_team_id}")
    else:
        _result = fleet_error(f"Failed to delete team (status {_status}): {_data}")

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
            elif method.upper() == "PUT":
                response = httpx.put(full_url, headers=headers, json=json_data, timeout=15.0)
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

## Setup Experience

[📖 API Docs](https://fleetdm.com/docs/rest-api/rest-api#setup-experience)

Configure the macOS/iOS automated device enrollment (ADE) setup experience, including enrollment profiles, bootstrap packages, EULAs, and setup scripts.

### Endpoints Overview

| Category | Endpoint | Method | Description |
|----------|----------|--------|-------------|
| **Enrollment Profile** | `/mdm/apple/enrollment_profile` | POST | Update custom MDM setup enrollment profile |
| | `/mdm/apple/enrollment_profile` | GET | Get custom MDM setup enrollment profile |
| | `/mdm/apple/enrollment_profile` | DELETE | Delete custom MDM setup enrollment profile |
| **OTA/Manual** | `/api/v1/fleet/enrollment_profiles/ota` | GET | Get Over-the-Air (OTA) enrollment profile |
| | `/api/v1/fleet/enrollment_profiles/manual` | GET | Get manual enrollment profile |
| **Bootstrap Package** | `/api/v1/fleet/bootstrap` | POST | Create/upload bootstrap package |
| | `/api/v1/fleet/bootstrap/:team_id/metadata` | GET | Get bootstrap package metadata |
| | `/api/v1/fleet/bootstrap/:team_id` | DELETE | Delete bootstrap package |
| | `/api/v1/fleet/bootstrap` | GET | Download bootstrap package |
| | `/api/v1/fleet/bootstrap/:team_id/summary` | GET | Get bootstrap package status summary |
| **Setup Experience** | `/api/v1/fleet/setup_experience` | PATCH | Update setup experience settings |
| **EULA** | `/api/v1/fleet/setup_experience/eula` | POST | Upload EULA |
| | `/api/v1/fleet/setup_experience/eula/:token/metadata` | GET | Get EULA metadata |
| | `/api/v1/fleet/setup_experience/eula/:token` | DELETE | Delete EULA |
| | `/api/v1/fleet/setup_experience/eula/:token` | GET | Download EULA |
| **Software** | `/api/v1/fleet/setup_experience/software` | GET | List setup experience software |
| | `/api/v1/fleet/setup_experience/software` | PUT | Update setup experience software |
| **Script** | `/api/v1/fleet/setup_experience/script` | POST | Create setup experience script |
| | `/api/v1/fleet/setup_experience/script` | GET | Get/download setup experience script |
| | `/api/v1/fleet/setup_experience/script` | DELETE | Delete setup experience script |
""")


@app.cell
def _(mo):
    mo.md("""
### Custom MDM Setup Enrollment Profile

Manage the custom enrollment profile used during Automated Device Enrollment (ADE).
""")


@app.cell
def _(mo):
    enrollment_profile_team_id = mo.ui.number(
        start=0, stop=999999, step=1, value=0,
        label="Team ID (0 = no team filter)",
    )

    get_enrollment_profile_btn = mo.ui.run_button(label="Get Enrollment Profile")
    delete_enrollment_profile_btn = mo.ui.run_button(label="Delete Enrollment Profile", kind="danger")

    mo.vstack([
        enrollment_profile_team_id,
        mo.hstack([get_enrollment_profile_btn, delete_enrollment_profile_btn], justify="start", gap=1),
    ])

    return enrollment_profile_team_id, get_enrollment_profile_btn, delete_enrollment_profile_btn


@app.cell
def _(mo, json, fleet, enrollment_profile_team_id, get_enrollment_profile_btn, fleet_success, fleet_error):
    mo.stop(not get_enrollment_profile_btn.value)

    _team_param = f"?team_id={enrollment_profile_team_id.value}" if enrollment_profile_team_id.value > 0 else ""
    _status, _data = fleet("GET", f"/mdm/apple/enrollment_profile{_team_param}")

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = fleet_success("Enrollment Profile retrieved")
        _result = mo.vstack([_result, mo.md(f"```json\n{_formatted}\n```")])
    else:
        _result = fleet_error(f"Failed to get enrollment profile (status {_status}): {_data}")

    _result


@app.cell
def _(mo, fleet, enrollment_profile_team_id, delete_enrollment_profile_btn, fleet_success, fleet_error):
    mo.stop(not delete_enrollment_profile_btn.value)

    _team_param = f"?team_id={enrollment_profile_team_id.value}" if enrollment_profile_team_id.value > 0 else ""
    _status, _data = fleet("DELETE", f"/mdm/apple/enrollment_profile{_team_param}")

    if _status == 200:
        _result = fleet_success("Enrollment profile deleted")
    else:
        _result = fleet_error(f"Failed to delete enrollment profile (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
#### Update Enrollment Profile

Upload a custom enrollment profile (mobileconfig file content).
""")


@app.cell
def _(mo):
    enrollment_profile_content = mo.ui.text_area(
        placeholder="""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- Your enrollment profile content -->
</dict>
</plist>""",
        label="Enrollment Profile Content (mobileconfig XML)",
        full_width=True,
        rows=10,
    )

    update_enrollment_profile_team_id = mo.ui.number(
        start=0, stop=999999, step=1, value=0,
        label="Team ID (0 = no team)",
    )

    update_enrollment_profile_btn = mo.ui.run_button(label="Update Enrollment Profile")

    mo.vstack([
        enrollment_profile_content,
        update_enrollment_profile_team_id,
        mo.hstack([update_enrollment_profile_btn], justify="start"),
    ])

    return enrollment_profile_content, update_enrollment_profile_team_id, update_enrollment_profile_btn


@app.cell
def _(mo, httpx, fleet_url_input, api_token_input, enrollment_profile_content, update_enrollment_profile_team_id, update_enrollment_profile_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not update_enrollment_profile_btn.value)
    mo.stop(not enrollment_profile_content.value, fleet_tip("Enter enrollment profile content."))

    _url = fleet_url_input.value.rstrip("/")
    _token = api_token_input.value
    _team_param = f"?team_id={update_enrollment_profile_team_id.value}" if update_enrollment_profile_team_id.value > 0 else ""

    try:
        _response = httpx.post(
            f"{_url}/mdm/apple/enrollment_profile{_team_param}",
            headers={"Authorization": f"Bearer {_token}"},
            content=enrollment_profile_content.value.encode('utf-8'),
            timeout=30.0,
        )
        _status = _response.status_code
        _data = _response.json() if _response.text else {}
    except Exception as e:
        _status = 0
        _data = {"error": str(e)}

    if _status == 200:
        _result = fleet_success("Enrollment profile updated successfully")
    else:
        _result = fleet_error(f"Failed to update enrollment profile (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Enrollment Profiles (OTA / Manual)

Download Over-the-Air (OTA) or manual enrollment profiles for device enrollment.
""")


@app.cell
def _(mo):
    get_ota_profile_btn = mo.ui.run_button(label="Get OTA Enrollment Profile")
    get_manual_profile_btn = mo.ui.run_button(label="Get Manual Enrollment Profile")

    mo.hstack([get_ota_profile_btn, get_manual_profile_btn], justify="start", gap=1)

    return get_ota_profile_btn, get_manual_profile_btn


@app.cell
def _(mo, httpx, fleet_url_input, api_token_input, get_ota_profile_btn, fleet_success, fleet_error):
    mo.stop(not get_ota_profile_btn.value)

    _url = fleet_url_input.value.rstrip("/")
    _token = api_token_input.value

    try:
        _response = httpx.get(
            f"{_url}/api/v1/fleet/enrollment_profiles/ota",
            headers={"Authorization": f"Bearer {_token}"},
            timeout=30.0,
        )
        _status = _response.status_code
        _content = _response.text
    except Exception as e:
        _status = 0
        _content = str(e)

    if _status == 200:
        _download_btn = mo.download(
            data=_content.encode("utf-8"),
            filename="ota-enrollment.mobileconfig",
            mimetype="application/x-apple-aspen-config",
            label="Download OTA Profile",
        )
        _result = mo.vstack([
            fleet_success("OTA enrollment profile retrieved"),
            _download_btn,
            mo.md(f"```xml\n{_content[:3000]}{'...' if len(_content) > 3000 else ''}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get OTA profile (status {_status}): {_content[:500]}")

    _result


@app.cell
def _(mo, httpx, fleet_url_input, api_token_input, get_manual_profile_btn, fleet_success, fleet_error):
    mo.stop(not get_manual_profile_btn.value)

    _url = fleet_url_input.value.rstrip("/")
    _token = api_token_input.value

    try:
        _response = httpx.get(
            f"{_url}/api/v1/fleet/enrollment_profiles/manual",
            headers={"Authorization": f"Bearer {_token}"},
            timeout=30.0,
        )
        _status = _response.status_code
        _content = _response.text
    except Exception as e:
        _status = 0
        _content = str(e)

    if _status == 200:
        _download_btn = mo.download(
            data=_content.encode("utf-8"),
            filename="manual-enrollment.mobileconfig",
            mimetype="application/x-apple-aspen-config",
            label="Download Manual Profile",
        )
        _result = mo.vstack([
            fleet_success("Manual enrollment profile retrieved"),
            _download_btn,
            mo.md(f"```xml\n{_content[:3000]}{'...' if len(_content) > 3000 else ''}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get manual profile (status {_status}): {_content[:500]}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Bootstrap Package

Manage bootstrap packages that are installed during macOS Setup Assistant.
""")


@app.cell
def _(mo):
    bootstrap_team_id = mo.ui.number(
        start=0, stop=999999, step=1, value=0,
        label="Team ID (0 = no team)",
    )

    get_bootstrap_metadata_btn = mo.ui.run_button(label="Get Metadata")
    download_bootstrap_btn = mo.ui.run_button(label="Download Package")
    get_bootstrap_status_btn = mo.ui.run_button(label="Get Status Summary")
    delete_bootstrap_btn = mo.ui.run_button(label="Delete Package", kind="danger")

    mo.vstack([
        bootstrap_team_id,
        mo.hstack([get_bootstrap_metadata_btn, download_bootstrap_btn, get_bootstrap_status_btn, delete_bootstrap_btn], justify="start", gap=1),
    ])

    return bootstrap_team_id, get_bootstrap_metadata_btn, download_bootstrap_btn, get_bootstrap_status_btn, delete_bootstrap_btn


@app.cell
def _(mo, json, fleet, bootstrap_team_id, get_bootstrap_metadata_btn, fleet_success, fleet_error):
    mo.stop(not get_bootstrap_metadata_btn.value)

    _team_id = bootstrap_team_id.value if bootstrap_team_id.value > 0 else 0
    _status, _data = fleet("GET", f"/api/v1/fleet/bootstrap/{_team_id}/metadata")

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success("Bootstrap package metadata"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get bootstrap metadata (status {_status}): {_data}")

    _result


@app.cell
def _(mo, httpx, fleet_url_input, api_token_input, bootstrap_team_id, download_bootstrap_btn, fleet_success, fleet_error):
    mo.stop(not download_bootstrap_btn.value)

    _url = fleet_url_input.value.rstrip("/")
    _token = api_token_input.value
    _team_param = f"?team_id={bootstrap_team_id.value}" if bootstrap_team_id.value > 0 else ""

    try:
        _response = httpx.get(
            f"{_url}/api/v1/fleet/bootstrap{_team_param}",
            headers={"Authorization": f"Bearer {_token}"},
            timeout=60.0,
        )
        _status = _response.status_code
        _content = _response.content
    except Exception as e:
        _status = 0
        _content = str(e).encode()

    if _status == 200:
        _download_btn = mo.download(
            data=_content,
            filename="bootstrap.pkg",
            mimetype="application/octet-stream",
            label="Download Bootstrap Package",
        )
        _result = mo.vstack([
            fleet_success(f"Bootstrap package ready ({len(_content)} bytes)"),
            _download_btn,
        ])
    else:
        _result = fleet_error(f"Failed to download bootstrap (status {_status})")

    _result


@app.cell
def _(mo, json, fleet, bootstrap_team_id, get_bootstrap_status_btn, fleet_success, fleet_error):
    mo.stop(not get_bootstrap_status_btn.value)

    _team_id = bootstrap_team_id.value if bootstrap_team_id.value > 0 else 0
    _status, _data = fleet("GET", f"/api/v1/fleet/bootstrap/{_team_id}/summary")

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success("Bootstrap package status summary"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get bootstrap status (status {_status}): {_data}")

    _result


@app.cell
def _(mo, fleet, bootstrap_team_id, delete_bootstrap_btn, fleet_success, fleet_error):
    mo.stop(not delete_bootstrap_btn.value)

    _team_id = bootstrap_team_id.value if bootstrap_team_id.value > 0 else 0
    _status, _data = fleet("DELETE", f"/api/v1/fleet/bootstrap/{_team_id}")

    if _status == 200:
        _result = fleet_success("Bootstrap package deleted")
    else:
        _result = fleet_error(f"Failed to delete bootstrap (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
#### Upload Bootstrap Package

Upload a new bootstrap package (.pkg file). The package must be signed.
""")


@app.cell
def _(mo):
    bootstrap_upload_team_id = mo.ui.number(
        start=0, stop=999999, step=1, value=0,
        label="Team ID (0 = no team)",
    )

    bootstrap_file_path = mo.ui.text(
        placeholder="/path/to/bootstrap.pkg",
        label="Bootstrap Package File Path",
        full_width=True,
    )

    upload_bootstrap_btn = mo.ui.run_button(label="Upload Bootstrap Package")

    mo.vstack([
        bootstrap_upload_team_id,
        bootstrap_file_path,
        mo.hstack([upload_bootstrap_btn], justify="start"),
    ])

    return bootstrap_upload_team_id, bootstrap_file_path, upload_bootstrap_btn


@app.cell
def _(mo, httpx, Path, fleet_url_input, api_token_input, bootstrap_upload_team_id, bootstrap_file_path, upload_bootstrap_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not upload_bootstrap_btn.value)
    mo.stop(not bootstrap_file_path.value, fleet_tip("Enter the path to the bootstrap package file."))

    _file_path = Path(bootstrap_file_path.value.strip())
    if not _file_path.exists():
        mo.stop(True, fleet_error(f"File not found: {_file_path}"))

    _url = fleet_url_input.value.rstrip("/")
    _token = api_token_input.value

    try:
        with open(_file_path, "rb") as _f:
            _file_content = _f.read()

        _files = {
            "package": (_file_path.name, _file_content, "application/octet-stream"),
        }
        _data_fields = {}
        if bootstrap_upload_team_id.value > 0:
            _data_fields["team_id"] = str(bootstrap_upload_team_id.value)

        _response = httpx.post(
            f"{_url}/api/v1/fleet/bootstrap",
            headers={"Authorization": f"Bearer {_token}"},
            files=_files,
            data=_data_fields,
            timeout=120.0,
        )
        _status = _response.status_code
        _resp_data = _response.json() if _response.text else {}
    except Exception as e:
        _status = 0
        _resp_data = {"error": str(e)}

    if _status in (200, 201):
        _result = fleet_success(f"Bootstrap package uploaded: {_file_path.name}")
    else:
        _result = fleet_error(f"Failed to upload bootstrap (status {_status}): {_resp_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Setup Experience Settings

Update the setup experience configuration for a team.
""")


@app.cell
def _(mo):
    setup_exp_team_id = mo.ui.number(
        start=0, stop=999999, step=1, value=0,
        label="Team ID (0 = no team)",
    )

    setup_exp_await_config = mo.ui.checkbox(label="Enable await configuration (hold at Setup Assistant)")
    setup_exp_release_manually = mo.ui.checkbox(label="Release device manually")

    update_setup_exp_btn = mo.ui.run_button(label="Update Setup Experience")

    mo.vstack([
        setup_exp_team_id,
        setup_exp_await_config,
        setup_exp_release_manually,
        mo.hstack([update_setup_exp_btn], justify="start"),
    ])

    return setup_exp_team_id, setup_exp_await_config, setup_exp_release_manually, update_setup_exp_btn


@app.cell
def _(mo, json, fleet, setup_exp_team_id, setup_exp_await_config, setup_exp_release_manually, update_setup_exp_btn, fleet_success, fleet_error):
    mo.stop(not update_setup_exp_btn.value)

    _team_param = f"?team_id={setup_exp_team_id.value}" if setup_exp_team_id.value > 0 else ""
    _payload = {
        "enable_end_user_authentication": setup_exp_await_config.value,
        "enable_release_device_manually": setup_exp_release_manually.value,
    }

    _status, _data = fleet("PATCH", f"/api/v1/fleet/setup_experience{_team_param}", json_data=_payload)

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success("Setup experience updated"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to update setup experience (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### EULA Management

Upload and manage End User License Agreements shown during device setup.
""")


@app.cell
def _(mo):
    eula_token_input = mo.ui.text(
        placeholder="EULA token (from metadata)",
        label="EULA Token",
        full_width=True,
    )

    get_eula_metadata_btn = mo.ui.run_button(label="Get EULA Metadata")
    download_eula_btn = mo.ui.run_button(label="Download EULA")
    delete_eula_btn = mo.ui.run_button(label="Delete EULA", kind="danger")

    mo.vstack([
        eula_token_input,
        mo.hstack([get_eula_metadata_btn, download_eula_btn, delete_eula_btn], justify="start", gap=1),
    ])

    return eula_token_input, get_eula_metadata_btn, download_eula_btn, delete_eula_btn


@app.cell
def _(mo, json, fleet, eula_token_input, get_eula_metadata_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not get_eula_metadata_btn.value)
    mo.stop(not eula_token_input.value, fleet_tip("Enter an EULA token."))

    _token = eula_token_input.value.strip()
    _status, _data = fleet("GET", f"/api/v1/fleet/setup_experience/eula/{_token}/metadata")

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success("EULA metadata"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get EULA metadata (status {_status}): {_data}")

    _result


@app.cell
def _(mo, httpx, fleet_url_input, api_token_input, eula_token_input, download_eula_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not download_eula_btn.value)
    mo.stop(not eula_token_input.value, fleet_tip("Enter an EULA token."))

    _url = fleet_url_input.value.rstrip("/")
    _api_token = api_token_input.value
    _eula_token = eula_token_input.value.strip()

    try:
        _response = httpx.get(
            f"{_url}/api/v1/fleet/setup_experience/eula/{_eula_token}",
            headers={"Authorization": f"Bearer {_api_token}"},
            timeout=30.0,
        )
        _status = _response.status_code
        _content = _response.content
    except Exception as e:
        _status = 0
        _content = str(e).encode()

    if _status == 200:
        _download_btn = mo.download(
            data=_content,
            filename="eula.pdf",
            mimetype="application/pdf",
            label="Download EULA File",
        )
        _result = mo.vstack([
            fleet_success(f"EULA ready ({len(_content)} bytes)"),
            _download_btn,
        ])
    else:
        _result = fleet_error(f"Failed to download EULA (status {_status})")

    _result


@app.cell
def _(mo, fleet, eula_token_input, delete_eula_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not delete_eula_btn.value)
    mo.stop(not eula_token_input.value, fleet_tip("Enter an EULA token."))

    _eula_token = eula_token_input.value.strip()
    _status, _data = fleet("DELETE", f"/api/v1/fleet/setup_experience/eula/{_eula_token}")

    if _status == 200:
        _result = fleet_success("EULA deleted")
    else:
        _result = fleet_error(f"Failed to delete EULA (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
#### Upload EULA

Upload a new EULA file (PDF format recommended).
""")


@app.cell
def _(mo):
    eula_upload_team_id = mo.ui.number(
        start=0, stop=999999, step=1, value=0,
        label="Team ID (0 = no team)",
    )

    eula_file_path = mo.ui.text(
        placeholder="/path/to/eula.pdf",
        label="EULA File Path",
        full_width=True,
    )

    upload_eula_btn = mo.ui.run_button(label="Upload EULA")

    mo.vstack([
        eula_upload_team_id,
        eula_file_path,
        mo.hstack([upload_eula_btn], justify="start"),
    ])

    return eula_upload_team_id, eula_file_path, upload_eula_btn


@app.cell
def _(mo, json, httpx, Path, fleet_url_input, api_token_input, eula_upload_team_id, eula_file_path, upload_eula_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not upload_eula_btn.value)
    mo.stop(not eula_file_path.value, fleet_tip("Enter the path to the EULA file."))

    _file_path = Path(eula_file_path.value.strip())
    if not _file_path.exists():
        mo.stop(True, fleet_error(f"File not found: {_file_path}"))

    _url = fleet_url_input.value.rstrip("/")
    _token = api_token_input.value

    try:
        with open(_file_path, "rb") as _f:
            _file_content = _f.read()

        _files = {
            "eula": (_file_path.name, _file_content, "application/pdf"),
        }
        _data_fields = {}
        if eula_upload_team_id.value > 0:
            _data_fields["team_id"] = str(eula_upload_team_id.value)

        _response = httpx.post(
            f"{_url}/api/v1/fleet/setup_experience/eula",
            headers={"Authorization": f"Bearer {_token}"},
            files=_files,
            data=_data_fields,
            timeout=60.0,
        )
        _status = _response.status_code
        _resp_data = _response.json() if _response.text else {}
    except Exception as e:
        _status = 0
        _resp_data = {"error": str(e)}

    if _status in (200, 201):
        _formatted = json.dumps(_resp_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"EULA uploaded: {_file_path.name}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to upload EULA (status {_status}): {_resp_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Setup Experience Software

List and configure software to be installed during device setup.
""")


@app.cell
def _(mo):
    setup_sw_team_id = mo.ui.number(
        start=0, stop=999999, step=1, value=0,
        label="Team ID (0 = no team)",
    )

    list_setup_sw_btn = mo.ui.run_button(label="List Setup Experience Software")

    mo.vstack([
        setup_sw_team_id,
        mo.hstack([list_setup_sw_btn], justify="start"),
    ])

    return setup_sw_team_id, list_setup_sw_btn


@app.cell
def _(mo, json, fleet, setup_sw_team_id, list_setup_sw_btn, fleet_success, fleet_error):
    mo.stop(not list_setup_sw_btn.value)

    _team_param = f"?team_id={setup_sw_team_id.value}" if setup_sw_team_id.value > 0 else ""
    _status, _data = fleet("GET", f"/api/v1/fleet/setup_experience/software{_team_param}")

    if _status == 200:
        _software = _data.get("software", [])
        if _software:
            _formatted = json.dumps(_software, indent=2)
            _result = mo.vstack([
                fleet_success(f"Found {len(_software)} setup experience software item(s)"),
                mo.md(f"```json\n{_formatted}\n```"),
            ])
        else:
            _result = mo.md("**No setup experience software configured.**")
    else:
        _result = fleet_error(f"Failed to list setup software (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
#### Update Setup Experience Software

Add or remove software from the setup experience. Provide a comma-separated list of software title IDs.
""")


@app.cell
def _(mo):
    update_setup_sw_team_id = mo.ui.number(
        start=0, stop=999999, step=1, value=0,
        label="Team ID (0 = no team)",
    )

    setup_sw_title_ids = mo.ui.text(
        placeholder="1, 5, 12 (comma-separated software title IDs)",
        label="Software Title IDs to include",
        full_width=True,
    )

    update_setup_sw_btn = mo.ui.run_button(label="Update Setup Experience Software")

    mo.vstack([
        update_setup_sw_team_id,
        setup_sw_title_ids,
        mo.hstack([update_setup_sw_btn], justify="start"),
    ])

    return update_setup_sw_team_id, setup_sw_title_ids, update_setup_sw_btn


@app.cell
def _(mo, json, fleet, update_setup_sw_team_id, setup_sw_title_ids, update_setup_sw_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not update_setup_sw_btn.value)

    # Parse software title IDs
    _sw_ids = []
    if setup_sw_title_ids.value.strip():
        _sw_ids = [int(sid.strip()) for sid in setup_sw_title_ids.value.split(",") if sid.strip().isdigit()]

    _team_param = f"?team_id={update_setup_sw_team_id.value}" if update_setup_sw_team_id.value > 0 else ""
    _payload = {"software_title_ids": _sw_ids}

    _status, _data = fleet("PUT", f"/api/v1/fleet/setup_experience/software{_team_param}", json_data=_payload)

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Setup experience software updated ({len(_sw_ids)} items)"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to update setup software (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Setup Experience Script

Manage scripts that run during device setup.
""")


@app.cell
def _(mo):
    setup_script_team_id = mo.ui.number(
        start=0, stop=999999, step=1, value=0,
        label="Team ID (0 = no team)",
    )

    get_setup_script_btn = mo.ui.run_button(label="Get Setup Script")
    delete_setup_script_btn = mo.ui.run_button(label="Delete Setup Script", kind="danger")

    mo.vstack([
        setup_script_team_id,
        mo.hstack([get_setup_script_btn, delete_setup_script_btn], justify="start", gap=1),
    ])

    return setup_script_team_id, get_setup_script_btn, delete_setup_script_btn


@app.cell
def _(mo, httpx, fleet_url_input, api_token_input, setup_script_team_id, get_setup_script_btn, fleet_success, fleet_error):
    mo.stop(not get_setup_script_btn.value)

    _url = fleet_url_input.value.rstrip("/")
    _token = api_token_input.value
    _team_param = f"?team_id={setup_script_team_id.value}" if setup_script_team_id.value > 0 else ""

    try:
        _response = httpx.get(
            f"{_url}/api/v1/fleet/setup_experience/script{_team_param}",
            headers={"Authorization": f"Bearer {_token}"},
            timeout=30.0,
        )
        _status = _response.status_code
        _content = _response.text
    except Exception as e:
        _status = 0
        _content = str(e)

    if _status == 200:
        _download_btn = mo.download(
            data=_content.encode("utf-8"),
            filename="setup_script.sh",
            mimetype="text/plain",
            label="Download Script",
        )
        _result = mo.vstack([
            fleet_success("Setup experience script retrieved"),
            _download_btn,
            mo.md(f"```bash\n{_content[:5000]}{'...' if len(_content) > 5000 else ''}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get setup script (status {_status}): {_content[:500]}")

    _result


@app.cell
def _(mo, fleet, setup_script_team_id, delete_setup_script_btn, fleet_success, fleet_error):
    mo.stop(not delete_setup_script_btn.value)

    _team_param = f"?team_id={setup_script_team_id.value}" if setup_script_team_id.value > 0 else ""
    _status, _data = fleet("DELETE", f"/api/v1/fleet/setup_experience/script{_team_param}")

    if _status == 200:
        _result = fleet_success("Setup experience script deleted")
    else:
        _result = fleet_error(f"Failed to delete setup script (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
#### Create Setup Experience Script

Upload a new setup experience script.
""")


@app.cell
def _(mo):
    create_setup_script_team_id = mo.ui.number(
        start=0, stop=999999, step=1, value=0,
        label="Team ID (0 = no team)",
    )

    setup_script_name = mo.ui.text(
        placeholder="setup_script.sh",
        label="Script Name",
        full_width=True,
    )

    setup_script_content = mo.ui.text_area(
        placeholder="""#!/bin/bash
# Setup experience script
echo "Setting up device..."
# Your setup commands here
exit 0""",
        label="Script Content",
        full_width=True,
        rows=12,
    )

    create_setup_script_btn = mo.ui.run_button(label="Create Setup Script")

    mo.vstack([
        create_setup_script_team_id,
        setup_script_name,
        setup_script_content,
        mo.hstack([create_setup_script_btn], justify="start"),
    ])

    return create_setup_script_team_id, setup_script_name, setup_script_content, create_setup_script_btn


@app.cell
def _(mo, json, httpx, fleet_url_input, api_token_input, create_setup_script_team_id, setup_script_name, setup_script_content, create_setup_script_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not create_setup_script_btn.value)
    mo.stop(not setup_script_content.value, fleet_tip("Enter script content."))

    _url = fleet_url_input.value.rstrip("/")
    _token = api_token_input.value
    _name = setup_script_name.value.strip() if setup_script_name.value else "setup_script.sh"

    try:
        _files = {
            "script": (_name, setup_script_content.value.encode('utf-8'), "text/plain"),
        }
        _data_fields = {}
        if create_setup_script_team_id.value > 0:
            _data_fields["team_id"] = str(create_setup_script_team_id.value)

        _response = httpx.post(
            f"{_url}/api/v1/fleet/setup_experience/script",
            headers={"Authorization": f"Bearer {_token}"},
            files=_files,
            data=_data_fields,
            timeout=30.0,
        )
        _status = _response.status_code
        _resp_data = _response.json() if _response.text else {}
    except Exception as e:
        _status = 0
        _resp_data = {"error": str(e)}

    if _status in (200, 201):
        _formatted = json.dumps(_resp_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Setup experience script created: {_name}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to create setup script (status {_status}): {_resp_data}")

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

<div class="fleet-note"><strong>Only these 3 variables are supported in certificate templates.</strong> Other <code>$FLEET_VAR_*</code> variables (like IDP_FULL_NAME, IDP_DEPARTMENT) are only available in MDM profiles. Custom <code>$FLEET_SECRET_*</code> variables are not supported in certificate subject names.</div>

**Subject Name Format:** Uses DN (Distinguished Name) format: `/KEY=value/KEY=value`

Common DN keys: `CN` (Common Name), `OU` (Organizational Unit), `O` (Organization), `ST` (State), `C` (Country)
""")


@app.cell
def _(mo):
    # Subject name builder - Only 3 Fleet variables are supported in certificate templates
    # See: fleet/server/service/certificate_templates.go
    CERT_TEMPLATE_VARS = {
        "Host UUID": "$FLEET_VAR_HOST_UUID",
        "Hardware Serial": "$FLEET_VAR_HOST_HARDWARE_SERIAL",
        "IDP Username (email)": "$FLEET_VAR_HOST_END_USER_IDP_USERNAME",
    }

    SUBJECT_TEMPLATES = {
        "WiFi Certificate (User + Device)": "/CN=$FLEET_VAR_HOST_END_USER_IDP_USERNAME/OU=$FLEET_VAR_HOST_UUID/ST=$FLEET_VAR_HOST_HARDWARE_SERIAL",
        "VPN Certificate (User + UUID)": "/CN=$FLEET_VAR_HOST_END_USER_IDP_USERNAME/OU=$FLEET_VAR_HOST_UUID",
        "Device Only (Serial + UUID)": "/CN=$FLEET_VAR_HOST_HARDWARE_SERIAL/OU=$FLEET_VAR_HOST_UUID",
        "User Identity Only": "/CN=$FLEET_VAR_HOST_END_USER_IDP_USERNAME",
        "Device Identity Only": "/CN=$FLEET_VAR_HOST_HARDWARE_SERIAL",
        "Custom (build below)": "",
    }

    # Template selector
    subject_template_dropdown = mo.ui.dropdown(
        options=SUBJECT_TEMPLATES,
        value="WiFi Certificate (User + Device)",
        label="Quick Template",
    )

    # DN components for custom builder - only 3 variables supported
    dn_cn_var = mo.ui.dropdown(
        options={"(none)": "", **CERT_TEMPLATE_VARS},
        value="IDP Username (email)",
        label="CN (Common Name)",
    )

    dn_ou_var = mo.ui.dropdown(
        options={"(none)": "", **CERT_TEMPLATE_VARS},
        value="Host UUID",
        label="OU (Org Unit)",
    )

    dn_o_var = mo.ui.dropdown(
        options={"(none)": "", "(custom text)": "CUSTOM", **CERT_TEMPLATE_VARS},
        value="(none)",
        label="O (Organization)",
    )

    dn_o_custom_text = mo.ui.text(placeholder="Custom org name", label="Custom O")

    dn_st_var = mo.ui.dropdown(
        options={"(none)": "", **CERT_TEMPLATE_VARS},
        value="(none)",
        label="ST (State/Extra)",
    )

    return CERT_TEMPLATE_VARS, SUBJECT_TEMPLATES, subject_template_dropdown, dn_cn_var, dn_ou_var, dn_o_var, dn_o_custom_text, dn_st_var


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

## Queries

[📖 API Docs](https://fleetdm.com/docs/rest-api/rest-api#queries)

Manage saved queries and run live queries against hosts.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/fleet/queries` | GET | List all queries |
| `/api/v1/fleet/queries/:id` | GET | Get query details |
| `/api/v1/fleet/queries/:id/report` | GET | Get query report |
| `/api/v1/fleet/hosts/:id/queries/:query_id` | GET | Get host's query report |
| `/api/v1/fleet/queries` | POST | Create query |
| `/api/v1/fleet/queries/:id` | PATCH | Update query |
| `/api/v1/fleet/queries/:name` | DELETE | Delete query by name |
| `/api/v1/fleet/queries/id/:id` | DELETE | Delete query by ID |
| `/api/v1/fleet/queries/delete` | POST | Delete multiple queries |
| `/api/v1/fleet/queries/run` | POST | Run live query |
""")


@app.cell
def _(mo):
    list_queries_btn = mo.ui.run_button(label="List Queries")
    query_id_input = mo.ui.text(placeholder="Query ID", label="Query ID")
    get_query_btn = mo.ui.run_button(label="Get Query")
    get_query_report_btn = mo.ui.run_button(label="Get Report")

    mo.vstack([
        mo.hstack([list_queries_btn], justify="start"),
        mo.hstack([query_id_input, get_query_btn, get_query_report_btn], justify="start", gap=1),
    ])

    return list_queries_btn, query_id_input, get_query_btn, get_query_report_btn


@app.cell
def _(mo, json, fleet, list_queries_btn, fleet_success, fleet_error):
    mo.stop(not list_queries_btn.value)

    _status, _data = fleet("GET", "/api/v1/fleet/queries")

    if _status == 200:
        _queries = _data.get("queries", [])
        if _queries:
            _formatted = json.dumps(_queries, indent=2)
            if len(_formatted) > 5000:
                _formatted = _formatted[:5000] + "\n... (truncated)"
            _result = mo.vstack([
                fleet_success(f"Found {len(_queries)} queries"),
                mo.md(f"```json\n{_formatted}\n```"),
            ])
        else:
            _result = mo.md("**No queries found.**")
    else:
        _result = fleet_error(f"Failed to list queries (status {_status}): {_data}")

    _result


@app.cell
def _(mo, json, fleet, query_id_input, get_query_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not get_query_btn.value)
    mo.stop(not query_id_input.value, fleet_tip("Enter a Query ID."))

    _query_id = query_id_input.value.strip()
    _status, _data = fleet("GET", f"/api/v1/fleet/queries/{_query_id}")

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Query {_query_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get query (status {_status}): {_data}")

    _result


@app.cell
def _(mo, json, fleet, query_id_input, get_query_report_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not get_query_report_btn.value)
    mo.stop(not query_id_input.value, fleet_tip("Enter a Query ID."))

    _query_id = query_id_input.value.strip()
    _status, _data = fleet("GET", f"/api/v1/fleet/queries/{_query_id}/report")

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        if len(_formatted) > 8000:
            _formatted = _formatted[:8000] + "\n... (truncated)"
        _result = mo.vstack([
            fleet_success(f"Query Report for {_query_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get query report (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Host's Query Report

Get query results for a specific host.
""")


@app.cell
def _(mo):
    host_query_host_id = mo.ui.text(placeholder="Host ID", label="Host ID")
    host_query_query_id = mo.ui.text(placeholder="Query ID", label="Query ID")
    get_host_query_report_btn = mo.ui.run_button(label="Get Host Query Report")

    mo.hstack([host_query_host_id, host_query_query_id, get_host_query_report_btn], justify="start", gap=1)

    return host_query_host_id, host_query_query_id, get_host_query_report_btn


@app.cell
def _(mo, json, fleet, host_query_host_id, host_query_query_id, get_host_query_report_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not get_host_query_report_btn.value)
    mo.stop(not host_query_host_id.value, fleet_tip("Enter a Host ID."))
    mo.stop(not host_query_query_id.value, fleet_tip("Enter a Query ID."))

    _host_id = host_query_host_id.value.strip()
    _query_id = host_query_query_id.value.strip()
    _status, _data = fleet("GET", f"/api/v1/fleet/hosts/{_host_id}/queries/{_query_id}")

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Query {_query_id} results for Host {_host_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get host query report (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Create Query

Create a new saved query.
""")


@app.cell
def _(mo):
    create_query_name = mo.ui.text(placeholder="Query Name", label="Name", full_width=True)
    create_query_sql = mo.ui.text_area(
        placeholder="SELECT * FROM system_info;",
        label="SQL Query",
        full_width=True,
        rows=6,
    )
    create_query_description = mo.ui.text(placeholder="Query description (optional)", label="Description", full_width=True)
    create_query_interval = mo.ui.number(start=0, stop=604800, step=60, value=0, label="Interval (seconds, 0 = manual)")
    create_query_observer_can_run = mo.ui.checkbox(label="Observer can run")

    create_query_btn = mo.ui.run_button(label="Create Query")

    mo.vstack([
        create_query_name,
        create_query_sql,
        create_query_description,
        mo.hstack([create_query_interval, create_query_observer_can_run], gap=2),
        mo.hstack([create_query_btn], justify="start"),
    ])

    return create_query_name, create_query_sql, create_query_description, create_query_interval, create_query_observer_can_run, create_query_btn


@app.cell
def _(mo, json, fleet, create_query_name, create_query_sql, create_query_description, create_query_interval, create_query_observer_can_run, create_query_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not create_query_btn.value)
    mo.stop(not create_query_name.value, fleet_tip("Enter a query name."))
    mo.stop(not create_query_sql.value, fleet_tip("Enter the SQL query."))

    _payload = {
        "name": create_query_name.value.strip(),
        "query": create_query_sql.value.strip(),
        "observer_can_run": create_query_observer_can_run.value,
    }

    if create_query_description.value:
        _payload["description"] = create_query_description.value.strip()
    if create_query_interval.value > 0:
        _payload["interval"] = create_query_interval.value

    _status, _data = fleet("POST", "/api/v1/fleet/queries", json_data=_payload)

    if _status in (200, 201):
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Created query: {create_query_name.value}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to create query (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Update Query

Update an existing query.
""")


@app.cell
def _(mo):
    update_query_id = mo.ui.text(placeholder="Query ID", label="Query ID to Update", full_width=True)
    update_query_name = mo.ui.text(placeholder="New name (optional)", label="Name", full_width=True)
    update_query_sql = mo.ui.text_area(placeholder="New SQL (optional)", label="SQL Query", full_width=True, rows=4)
    update_query_description = mo.ui.text(placeholder="New description (optional)", label="Description", full_width=True)

    update_query_btn = mo.ui.run_button(label="Update Query")

    mo.vstack([
        update_query_id,
        update_query_name,
        update_query_sql,
        update_query_description,
        mo.hstack([update_query_btn], justify="start"),
    ])

    return update_query_id, update_query_name, update_query_sql, update_query_description, update_query_btn


@app.cell
def _(mo, json, fleet, update_query_id, update_query_name, update_query_sql, update_query_description, update_query_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not update_query_btn.value)
    mo.stop(not update_query_id.value, fleet_tip("Enter a Query ID."))

    _query_id = update_query_id.value.strip()
    _payload = {}

    if update_query_name.value:
        _payload["name"] = update_query_name.value.strip()
    if update_query_sql.value:
        _payload["query"] = update_query_sql.value.strip()
    if update_query_description.value:
        _payload["description"] = update_query_description.value.strip()

    if not _payload:
        mo.stop(True, fleet_tip("Enter at least one field to update."))

    _status, _data = fleet("PATCH", f"/api/v1/fleet/queries/{_query_id}", json_data=_payload)

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Updated query {_query_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to update query (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Delete Query

Delete a query by ID or name.
""")


@app.cell
def _(mo):
    delete_query_id_input = mo.ui.text(placeholder="Query ID", label="Query ID")
    delete_query_by_id_btn = mo.ui.run_button(label="Delete by ID", kind="danger")

    delete_query_name_input = mo.ui.text(placeholder="Query Name", label="Query Name")
    delete_query_by_name_btn = mo.ui.run_button(label="Delete by Name", kind="danger")

    mo.vstack([
        mo.hstack([delete_query_id_input, delete_query_by_id_btn], justify="start", gap=1),
        mo.hstack([delete_query_name_input, delete_query_by_name_btn], justify="start", gap=1),
    ])

    return delete_query_id_input, delete_query_by_id_btn, delete_query_name_input, delete_query_by_name_btn


@app.cell
def _(mo, fleet, delete_query_id_input, delete_query_by_id_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not delete_query_by_id_btn.value)
    mo.stop(not delete_query_id_input.value, fleet_tip("Enter a Query ID."))

    _query_id = delete_query_id_input.value.strip()
    _status, _data = fleet("DELETE", f"/api/v1/fleet/queries/id/{_query_id}")

    if _status == 200:
        _result = fleet_success(f"Deleted query ID {_query_id}")
    else:
        _result = fleet_error(f"Failed to delete query (status {_status}): {_data}")

    _result


@app.cell
def _(mo, fleet, delete_query_name_input, delete_query_by_name_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not delete_query_by_name_btn.value)
    mo.stop(not delete_query_name_input.value, fleet_tip("Enter a Query Name."))

    _query_name = delete_query_name_input.value.strip()
    _status, _data = fleet("DELETE", f"/api/v1/fleet/queries/{_query_name}")

    if _status == 200:
        _result = fleet_success(f"Deleted query: {_query_name}")
    else:
        _result = fleet_error(f"Failed to delete query (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Run Live Query

Execute a query in real-time against selected hosts.
""")


@app.cell
def _(mo):
    live_query_sql = mo.ui.text_area(
        placeholder="SELECT * FROM system_info;",
        label="SQL Query",
        full_width=True,
        rows=4,
    )
    live_query_host_ids = mo.ui.text(
        placeholder="1, 5, 12 (comma-separated host IDs)",
        label="Host IDs",
        full_width=True,
    )
    run_live_query_btn = mo.ui.run_button(label="Run Live Query")

    mo.vstack([
        live_query_sql,
        live_query_host_ids,
        mo.hstack([run_live_query_btn], justify="start"),
    ])

    return live_query_sql, live_query_host_ids, run_live_query_btn


@app.cell
def _(mo, json, fleet, live_query_sql, live_query_host_ids, run_live_query_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not run_live_query_btn.value)
    mo.stop(not live_query_sql.value, fleet_tip("Enter a SQL query."))
    mo.stop(not live_query_host_ids.value, fleet_tip("Enter at least one Host ID."))

    _host_ids = [int(hid.strip()) for hid in live_query_host_ids.value.split(",") if hid.strip().isdigit()]
    if not _host_ids:
        mo.stop(True, fleet_tip("Enter valid Host IDs."))

    _payload = {
        "query": live_query_sql.value.strip(),
        "selected": {"hosts": _host_ids},
    }

    _status, _data = fleet("POST", "/api/v1/fleet/queries/run", json_data=_payload)

    if _status in (200, 201, 202):
        _formatted = json.dumps(_data, indent=2)
        if len(_formatted) > 8000:
            _formatted = _formatted[:8000] + "\n... (truncated)"
        _result = mo.vstack([
            fleet_success("Live query executed"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to run live query (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
---

## Scripts

[📖 API Docs](https://fleetdm.com/docs/rest-api/rest-api#scripts)

Manage and execute scripts on hosts.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/fleet/scripts/run` | POST | Run script on a host |
| `/api/v1/fleet/scripts/results/:execution_id` | GET | Get script result |
| `/api/v1/fleet/scripts/run/batch` | POST | Batch-run script on multiple hosts |
| `/api/v1/fleet/scripts/batch` | GET | List batch executions |
| `/api/v1/fleet/scripts/batch/:batch_execution_id` | GET | Get batch execution details |
| `/api/v1/fleet/scripts/batch/:batch_execution_id/host-results` | GET | Get host results in batch |
| `/api/v1/fleet/scripts/batch/:batch_execution_id/cancel` | POST | Cancel batch execution |
| `/api/v1/fleet/scripts` | POST | Create/upload script |
| `/api/v1/fleet/scripts/:id` | PATCH | Update script |
| `/api/v1/fleet/scripts/:id` | DELETE | Delete script |
| `/api/v1/fleet/scripts` | GET | List scripts |
| `/api/v1/fleet/hosts/:id/scripts` | GET | List host's scripts |
| `/api/v1/fleet/scripts/:id` | GET | Get or download script |
""")


@app.cell
def _(mo):
    mo.md("""
### Run Script on Host

Execute a script on a single host.
""")


@app.cell
def _(mo):
    run_script_host_id = mo.ui.text(placeholder="Host ID", label="Host ID", full_width=True)
    run_script_id = mo.ui.text(placeholder="Script ID (use saved script)", label="Script ID (optional)", full_width=True)
    run_script_content = mo.ui.text_area(
        placeholder="""#!/bin/bash
echo "Hello from Fleet!"
""",
        label="Script Content (if not using Script ID)",
        full_width=True,
        rows=6,
    )
    run_script_btn = mo.ui.run_button(label="Run Script")

    mo.vstack([
        run_script_host_id,
        run_script_id,
        run_script_content,
        mo.hstack([run_script_btn], justify="start"),
    ])

    return run_script_host_id, run_script_id, run_script_content, run_script_btn


@app.cell
def _(mo, json, fleet, run_script_host_id, run_script_id, run_script_content, run_script_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not run_script_btn.value)
    mo.stop(not run_script_host_id.value, fleet_tip("Enter a Host ID."))
    mo.stop(not run_script_id.value and not run_script_content.value, fleet_tip("Enter a Script ID or script content."))

    _payload = {
        "host_id": int(run_script_host_id.value.strip()),
    }

    if run_script_id.value:
        _payload["script_id"] = int(run_script_id.value.strip())
    else:
        _payload["script_contents"] = run_script_content.value

    _status, _data = fleet("POST", "/api/v1/fleet/scripts/run", json_data=_payload)

    if _status in (200, 201, 202):
        _formatted = json.dumps(_data, indent=2)
        _execution_id = _data.get("execution_id", "N/A")
        _result = mo.vstack([
            fleet_success(f"Script queued - Execution ID: {_execution_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to run script (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Get Script Result

Retrieve the result of a script execution.
""")


@app.cell
def _(mo):
    script_execution_id = mo.ui.text(placeholder="Execution ID", label="Execution ID", full_width=True)
    get_script_result_btn = mo.ui.run_button(label="Get Script Result")

    mo.hstack([script_execution_id, get_script_result_btn], justify="start", gap=1)

    return script_execution_id, get_script_result_btn


@app.cell
def _(mo, json, fleet, script_execution_id, get_script_result_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not get_script_result_btn.value)
    mo.stop(not script_execution_id.value, fleet_tip("Enter an Execution ID."))

    _exec_id = script_execution_id.value.strip()
    _status, _data = fleet("GET", f"/api/v1/fleet/scripts/results/{_exec_id}")

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Script result for execution {_exec_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get script result (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Batch Run Script

Run a script asynchronously on multiple hosts. Requires Fleet Premium.

**Two ways to target hosts:**
1. **By Host IDs**: Specify exact host IDs (comma-separated)
2. **By Filters**: Use `team_id` filter to target all hosts in a team (leave Host IDs empty)

**Note:** `team_id=0` targets hosts with **no team** assigned.
""")


@app.cell
def _(mo):
    batch_script_id = mo.ui.text(placeholder="Script ID", label="Script ID", full_width=True)
    batch_host_ids = mo.ui.text(
        placeholder="1, 5, 12 (comma-separated, OR leave empty to use team filter)",
        label="Host IDs (optional if using team filter)",
        full_width=True,
    )
    batch_use_filter = mo.ui.checkbox(label="Use Team Filter (instead of Host IDs)")
    batch_team_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Team ID for filter (0 = hosts with no team)")
    run_batch_script_btn = mo.ui.run_button(label="Run Batch Script")

    mo.vstack([
        batch_script_id,
        batch_host_ids,
        batch_use_filter,
        batch_team_id,
        mo.hstack([run_batch_script_btn], justify="start"),
    ])

    return batch_script_id, batch_host_ids, batch_use_filter, batch_team_id, run_batch_script_btn


@app.cell
def _(mo, json, fleet, batch_script_id, batch_host_ids, batch_use_filter, batch_team_id, run_batch_script_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not run_batch_script_btn.value)
    mo.stop(not batch_script_id.value, fleet_tip("Enter a Script ID."))

    _payload = {
        "script_id": int(batch_script_id.value.strip()),
    }

    if batch_use_filter.value:
        # Use team filter - targets all hosts in a team (or no team if team_id=0)
        _payload["filters"] = {"team_id": batch_team_id.value}
        _target_desc = f"hosts in team {batch_team_id.value}" if batch_team_id.value > 0 else "hosts with no team"
    else:
        # Use explicit host IDs
        mo.stop(not batch_host_ids.value, fleet_tip("Enter Host IDs or check 'Use Team Filter'."))
        _host_ids = [int(hid.strip()) for hid in batch_host_ids.value.split(",") if hid.strip().isdigit()]
        if not _host_ids:
            mo.stop(True, fleet_tip("Enter valid Host IDs."))
        _payload["host_ids"] = _host_ids
        _target_desc = f"{len(_host_ids)} hosts"

    _status, _data = fleet("POST", "/api/v1/fleet/scripts/run/batch", json_data=_payload)

    if _status in (200, 201, 202):
        _formatted = json.dumps(_data, indent=2)
        _batch_id = _data.get("batch_execution_id", "N/A")
        _result = mo.vstack([
            fleet_success(f"Batch script started on {_target_desc} - Batch ID: {_batch_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to run batch script (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Batch Script Management

List, get details, or cancel batch script executions.
""")


@app.cell
def _(mo):
    batch_mgmt_team_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Team ID (0 = no team)")
    list_batch_scripts_btn = mo.ui.run_button(label="List Batch Executions")
    batch_exec_id_input = mo.ui.text(placeholder="Batch Execution ID", label="Batch Execution ID")
    get_batch_script_btn = mo.ui.run_button(label="Get Batch Details")
    batch_host_status = mo.ui.dropdown(
        options={
            "Pending": "pending",
            "Ran (success)": "ran",
            "Errored": "errored",
            "Canceled": "canceled",
            "Incompatible": "incompatible",
        },
        value="Pending",
        label="Host Status Filter",
    )
    get_batch_hosts_btn = mo.ui.run_button(label="Get Host Results")
    cancel_batch_script_btn = mo.ui.run_button(label="Cancel Batch", kind="danger")

    mo.vstack([
        batch_mgmt_team_id,
        mo.hstack([list_batch_scripts_btn], justify="start"),
        batch_exec_id_input,
        mo.hstack([get_batch_script_btn, batch_host_status, get_batch_hosts_btn, cancel_batch_script_btn], justify="start", gap=1),
    ])

    return batch_mgmt_team_id, list_batch_scripts_btn, batch_exec_id_input, get_batch_script_btn, batch_host_status, get_batch_hosts_btn, cancel_batch_script_btn


@app.cell
def _(mo, json, fleet, batch_mgmt_team_id, list_batch_scripts_btn, fleet_success, fleet_error):
    mo.stop(not list_batch_scripts_btn.value)

    _status, _data = fleet("GET", f"/api/v1/fleet/scripts/batch?team_id={batch_mgmt_team_id.value}")

    if _status == 200:
        _batches = _data.get("batch_executions", [])
        if _batches:
            _formatted = json.dumps(_batches, indent=2)
            _result = mo.vstack([
                fleet_success(f"Found {len(_batches)} batch executions"),
                mo.md(f"```json\n{_formatted}\n```"),
            ])
        else:
            _result = mo.md("**No batch executions found.**")
    else:
        _result = fleet_error(f"Failed to list batch scripts (status {_status}): {_data}")

    _result


@app.cell
def _(mo, json, fleet, batch_exec_id_input, get_batch_script_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not get_batch_script_btn.value)
    mo.stop(not batch_exec_id_input.value, fleet_tip("Enter a Batch Execution ID."))

    _batch_id = batch_exec_id_input.value.strip()
    _status, _data = fleet("GET", f"/api/v1/fleet/scripts/batch/{_batch_id}")

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Batch execution {_batch_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get batch details (status {_status}): {_data}")

    _result


@app.cell
def _(mo, json, fleet, batch_exec_id_input, batch_host_status, get_batch_hosts_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not get_batch_hosts_btn.value)
    mo.stop(not batch_exec_id_input.value, fleet_tip("Enter a Batch Execution ID."))

    _batch_id = batch_exec_id_input.value.strip()
    _filter_status = batch_host_status.value
    _status, _data = fleet("GET", f"/api/v1/fleet/scripts/batch/{_batch_id}/host-results?status={_filter_status}")

    if _status == 200:
        _hosts = _data.get("hosts", [])
        _count = _data.get("count", len(_hosts))
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Host results in batch {_batch_id} (status: {_filter_status}, count: {_count})"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get batch host results (status {_status}): {_data}")

    _result


@app.cell
def _(mo, fleet, batch_exec_id_input, cancel_batch_script_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not cancel_batch_script_btn.value)
    mo.stop(not batch_exec_id_input.value, fleet_tip("Enter a Batch Execution ID."))

    _batch_id = batch_exec_id_input.value.strip()
    _status, _data = fleet("POST", f"/api/v1/fleet/scripts/batch/{_batch_id}/cancel")

    if _status in (200, 204):
        _result = fleet_success(f"Cancelled batch execution {_batch_id}")
    else:
        _result = fleet_error(f"Failed to cancel batch (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### List and Get Scripts

List all saved scripts or get/download a specific script.
""")


@app.cell
def _(mo):
    scripts_team_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Team ID (0 = no team)")
    list_scripts_btn = mo.ui.run_button(label="List Scripts")
    script_id_input = mo.ui.text(placeholder="Script ID", label="Script ID")
    get_script_btn = mo.ui.run_button(label="Get Script")
    delete_script_btn = mo.ui.run_button(label="Delete Script", kind="danger")

    mo.vstack([
        mo.hstack([scripts_team_id, list_scripts_btn], justify="start", gap=1),
        mo.hstack([script_id_input, get_script_btn, delete_script_btn], justify="start", gap=1),
    ])

    return scripts_team_id, list_scripts_btn, script_id_input, get_script_btn, delete_script_btn


@app.cell
def _(mo, json, fleet, scripts_team_id, list_scripts_btn, fleet_success, fleet_error):
    mo.stop(not list_scripts_btn.value)

    _team_param = f"?team_id={scripts_team_id.value}" if scripts_team_id.value > 0 else ""
    _status, _data = fleet("GET", f"/api/v1/fleet/scripts{_team_param}")

    if _status == 200:
        _scripts = _data.get("scripts", [])
        if _scripts:
            _formatted = json.dumps(_scripts, indent=2)
            _result = mo.vstack([
                fleet_success(f"Found {len(_scripts)} scripts"),
                mo.md(f"```json\n{_formatted}\n```"),
            ])
        else:
            _result = mo.md("**No scripts found.**")
    else:
        _result = fleet_error(f"Failed to list scripts (status {_status}): {_data}")

    _result


@app.cell
def _(mo, json, httpx, fleet_url_input, api_token_input, script_id_input, get_script_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not get_script_btn.value)
    mo.stop(not script_id_input.value, fleet_tip("Enter a Script ID."))

    _url = fleet_url_input.value.rstrip("/")
    _token = api_token_input.value
    _script_id = script_id_input.value.strip()

    try:
        # Get metadata first
        _meta_response = httpx.get(
            f"{_url}/api/v1/fleet/scripts/{_script_id}",
            headers={"Authorization": f"Bearer {_token}"},
            timeout=30.0,
        )
        _meta_status = _meta_response.status_code
        _metadata = _meta_response.json() if _meta_response.text else {}

        # Get actual script content with alt=media
        _content_response = httpx.get(
            f"{_url}/api/v1/fleet/scripts/{_script_id}?alt=media",
            headers={"Authorization": f"Bearer {_token}"},
            timeout=30.0,
        )
        _content_status = _content_response.status_code
        _script_content = _content_response.text
    except Exception as e:
        _meta_status = 0
        _content_status = 0
        _metadata = {"error": str(e)}
        _script_content = str(e)

    if _meta_status == 200:
        _script_name = _metadata.get("name", f"script_{_script_id}.sh")
        _formatted_meta = json.dumps(_metadata, indent=2)

        if _content_status == 200:
            _download_btn = mo.download(
                data=_script_content.encode("utf-8"),
                filename=_script_name,
                mimetype="text/plain",
                label=f"Download {_script_name}",
            )
            _result = mo.vstack([
                fleet_success(f"Script {_script_id}: {_script_name}"),
                mo.md(f"**Metadata:**\n```json\n{_formatted_meta}\n```"),
                _download_btn,
                mo.md(f"**Content:**\n```bash\n{_script_content[:5000]}{'...' if len(_script_content) > 5000 else ''}\n```"),
            ])
        else:
            _result = mo.vstack([
                fleet_success(f"Script {_script_id} metadata (content unavailable)"),
                mo.md(f"```json\n{_formatted_meta}\n```"),
            ])
    else:
        _result = fleet_error(f"Failed to get script (status {_meta_status}): {_metadata}")

    _result


@app.cell
def _(mo, fleet, script_id_input, delete_script_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not delete_script_btn.value)
    mo.stop(not script_id_input.value, fleet_tip("Enter a Script ID."))

    _script_id = script_id_input.value.strip()
    _status, _data = fleet("DELETE", f"/api/v1/fleet/scripts/{_script_id}")

    if _status == 200:
        _result = fleet_success(f"Deleted script {_script_id}")
    else:
        _result = fleet_error(f"Failed to delete script (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### List Host's Scripts

Get scripts assigned to a specific host.
""")


@app.cell
def _(mo):
    host_scripts_id = mo.ui.text(placeholder="Host ID", label="Host ID")
    list_host_scripts_btn = mo.ui.run_button(label="List Host Scripts")

    mo.hstack([host_scripts_id, list_host_scripts_btn], justify="start", gap=1)

    return host_scripts_id, list_host_scripts_btn


@app.cell
def _(mo, json, fleet, host_scripts_id, list_host_scripts_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not list_host_scripts_btn.value)
    mo.stop(not host_scripts_id.value, fleet_tip("Enter a Host ID."))

    _host_id = host_scripts_id.value.strip()
    _status, _data = fleet("GET", f"/api/v1/fleet/hosts/{_host_id}/scripts")

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Scripts for Host {_host_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to list host scripts (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Create Script

Upload a new script.
""")


@app.cell
def _(mo):
    create_script_team_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Team ID (0 = no team)")
    create_script_name = mo.ui.text(placeholder="my_script.sh", label="Script Name", full_width=True)
    create_script_content = mo.ui.text_area(
        placeholder="""#!/bin/bash
# Your script here
echo "Hello from Fleet!"
exit 0""",
        label="Script Content",
        full_width=True,
        rows=10,
    )
    create_script_btn = mo.ui.run_button(label="Create Script")

    mo.vstack([
        create_script_team_id,
        create_script_name,
        create_script_content,
        mo.hstack([create_script_btn], justify="start"),
    ])

    return create_script_team_id, create_script_name, create_script_content, create_script_btn


@app.cell
def _(mo, json, httpx, fleet_url_input, api_token_input, create_script_team_id, create_script_name, create_script_content, create_script_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not create_script_btn.value)
    mo.stop(not create_script_content.value, fleet_tip("Enter script content."))

    _url = fleet_url_input.value.rstrip("/")
    _token = api_token_input.value
    _name = create_script_name.value.strip() if create_script_name.value else "script.sh"

    try:
        _files = {
            "script": (_name, create_script_content.value.encode('utf-8'), "text/plain"),
        }
        _data_fields = {}
        if create_script_team_id.value > 0:
            _data_fields["team_id"] = str(create_script_team_id.value)

        _response = httpx.post(
            f"{_url}/api/v1/fleet/scripts",
            headers={"Authorization": f"Bearer {_token}"},
            files=_files,
            data=_data_fields,
            timeout=30.0,
        )
        _status = _response.status_code
        _resp_data = _response.json() if _response.text else {}
    except Exception as e:
        _status = 0
        _resp_data = {"error": str(e)}

    if _status in (200, 201):
        _formatted = json.dumps(_resp_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Created script: {_name}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to create script (status {_status}): {_resp_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Update Script

Update an existing script's content.
""")


@app.cell
def _(mo):
    update_script_id_input = mo.ui.text(placeholder="Script ID", label="Script ID", full_width=True)
    update_script_content = mo.ui.text_area(
        placeholder="New script content",
        label="New Script Content",
        full_width=True,
        rows=8,
    )
    update_script_btn = mo.ui.run_button(label="Update Script")

    mo.vstack([
        update_script_id_input,
        update_script_content,
        mo.hstack([update_script_btn], justify="start"),
    ])

    return update_script_id_input, update_script_content, update_script_btn


@app.cell
def _(mo, json, httpx, fleet_url_input, api_token_input, update_script_id_input, update_script_content, update_script_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not update_script_btn.value)
    mo.stop(not update_script_id_input.value, fleet_tip("Enter a Script ID."))
    mo.stop(not update_script_content.value, fleet_tip("Enter new script content."))

    _url = fleet_url_input.value.rstrip("/")
    _token = api_token_input.value
    _script_id = update_script_id_input.value.strip()

    try:
        _files = {
            "script": ("script.sh", update_script_content.value.encode('utf-8'), "text/plain"),
        }

        _response = httpx.patch(
            f"{_url}/api/v1/fleet/scripts/{_script_id}",
            headers={"Authorization": f"Bearer {_token}"},
            files=_files,
            timeout=30.0,
        )
        _status = _response.status_code
        _resp_data = _response.json() if _response.text else {}
    except Exception as e:
        _status = 0
        _resp_data = {"error": str(e)}

    if _status == 200:
        _formatted = json.dumps(_resp_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Updated script {_script_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to update script (status {_status}): {_resp_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
---

## Software

[📖 API Docs](https://fleetdm.com/docs/rest-api/rest-api#software)

Manage software packages, App Store apps, and Fleet-maintained apps.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/fleet/software/titles` | GET | List software titles |
| `/api/v1/fleet/software/titles/:id` | GET | Get software title |
| `/api/v1/fleet/software/versions` | GET | List software versions |
| `/api/v1/fleet/software/versions/:id` | GET | Get software version |
| `/api/v1/fleet/os_versions` | GET | List operating systems |
| `/api/v1/fleet/os_versions/:id` | GET | Get operating system version |
| `/api/v1/fleet/software/package` | POST | Add software package |
| `/api/v1/fleet/software/titles/:id/package` | PATCH | Update software package |
| `/api/v1/fleet/software/titles/:title_id/available_for_install` | DELETE | Delete software |
| `/api/v1/fleet/software/titles/:title_id/icon` | PUT | Update software icon |
| `/api/v1/fleet/software/titles/:title_id/icon` | GET | Download software icon |
| `/api/v1/fleet/software/titles/:title_id/icon` | DELETE | Delete software icon |
| `/api/v1/fleet/software/app_store_apps` | GET | List Apple App Store apps |
| `/api/v1/fleet/software/app_store_apps` | POST | Add App Store app |
| `/api/v1/fleet/software/titles/:title_id/app_store_app` | PATCH | Update App Store app |
| `/api/v1/fleet/software/fleet_maintained_apps` | GET | List Fleet-maintained apps |
| `/api/v1/fleet/software/fleet_maintained_apps/:app_id` | GET | Get Fleet-maintained app |
| `/api/v1/fleet/software/fleet_maintained_apps` | POST | Add Fleet-maintained app |
| `/api/v1/fleet/hosts/:host_id/software/:software_title_id/install` | POST | Install software |
| `/api/v1/fleet/hosts/:host_id/software/:software_title_id/uninstall` | POST | Uninstall software |
| `/api/v1/fleet/software/install/:install_uuid/results` | GET | Get install result |
| `/api/v1/fleet/software/titles/:title_id/package` | GET | Download software |
""")


@app.cell
def _(mo):
    mo.md("""
### List Software Titles

List all software titles across your fleet. Titles group multiple versions of the same software.
""")


@app.cell
def _(mo):
    sw_titles_team_id = mo.ui.number(start=-1, stop=999999, step=1, value=-1, label="Team ID (-1 = all, 0 = no team)")
    sw_titles_query = mo.ui.text(placeholder="Search by name...", label="Search Query")
    sw_titles_per_page = mo.ui.dropdown(
        options={"25": "25", "50": "50", "100": "100", "250": "250"},
        value="50",
        label="Per Page",
    )
    sw_titles_page = mo.ui.number(start=0, stop=9999, step=1, value=0, label="Page (0 = first)")
    sw_titles_order = mo.ui.dropdown(
        options={"Most installed": "hosts_count,desc", "Least installed": "hosts_count,asc", "Name A-Z": "name,asc", "Name Z-A": "name,desc"},
        value="Most installed",
        label="Sort by",
    )
    sw_titles_platform = mo.ui.dropdown(
        options={"All platforms": "", "macOS": "darwin", "Windows": "windows", "Linux": "linux", "iOS": "ios", "iPadOS": "ipados", "Chrome": "chrome"},
        value="All platforms",
        label="Platform",
    )
    sw_titles_vuln_only = mo.ui.checkbox(label="Vulnerable only")
    sw_titles_exploit = mo.ui.checkbox(label="Known exploit")
    sw_titles_min_cvss = mo.ui.number(start=0, stop=10, step=0.1, value=0, label="Min CVSS")
    sw_titles_max_cvss = mo.ui.number(start=0, stop=10, step=0.1, value=0, label="Max CVSS")
    sw_titles_available_install = mo.ui.checkbox(label="Available for install")
    sw_titles_self_service = mo.ui.checkbox(label="Self-service only")
    sw_titles_packages_only = mo.ui.checkbox(label="Packages only")
    sw_titles_exclude_fma = mo.ui.checkbox(label="Exclude Fleet-maintained apps")
    list_sw_titles_btn = mo.ui.run_button(label="List Software Titles")

    mo.vstack([
        mo.hstack([sw_titles_team_id, sw_titles_query, sw_titles_per_page, sw_titles_page, sw_titles_order, sw_titles_platform], gap=1),
        mo.hstack([sw_titles_available_install, sw_titles_self_service, sw_titles_packages_only, sw_titles_exclude_fma], gap=2),
        mo.hstack([sw_titles_vuln_only, sw_titles_exploit, sw_titles_min_cvss, sw_titles_max_cvss], gap=2),
        mo.hstack([list_sw_titles_btn], justify="start"),
    ])

    return sw_titles_team_id, sw_titles_query, sw_titles_per_page, sw_titles_page, sw_titles_order, sw_titles_platform, sw_titles_vuln_only, sw_titles_exploit, sw_titles_min_cvss, sw_titles_max_cvss, sw_titles_available_install, sw_titles_self_service, sw_titles_packages_only, sw_titles_exclude_fma, list_sw_titles_btn


@app.cell
def _(mo, fleet, sw_titles_team_id, sw_titles_query, sw_titles_per_page, sw_titles_page, sw_titles_order, sw_titles_platform, sw_titles_vuln_only, sw_titles_exploit, sw_titles_min_cvss, sw_titles_max_cvss, sw_titles_available_install, sw_titles_self_service, sw_titles_packages_only, sw_titles_exclude_fma, list_sw_titles_btn, fleet_error, fleet_output, fleet_tip):
    mo.stop(not list_sw_titles_btn.value)

    # Validate filter combinations
    if sw_titles_packages_only.value and sw_titles_team_id.value < 0:
        mo.stop(True, fleet_tip("'Packages only' filter requires a Team ID to be set (use 0 for 'no team')."))
    if sw_titles_platform.value and sw_titles_team_id.value < 0:
        mo.stop(True, fleet_tip("'Platform' filter requires a Team ID to be set (use 0 for 'no team')."))
    if (sw_titles_min_cvss.value > 0 or sw_titles_max_cvss.value > 0 or sw_titles_exploit.value) and not sw_titles_vuln_only.value:
        mo.stop(True, fleet_tip("CVSS and exploit filters require 'Vulnerable only' to be checked."))

    # Parse sort option
    _order_key, _order_dir = sw_titles_order.value.split(",")

    _params = [f"per_page={sw_titles_per_page.value}", f"page={sw_titles_page.value}", f"order_key={_order_key}", f"order_direction={_order_dir}"]
    if sw_titles_team_id.value >= 0:  # -1 = all teams (don't send), 0 = no team, >0 = specific team
        _params.append(f"team_id={sw_titles_team_id.value}")
    if sw_titles_query.value:
        _params.append(f"query={sw_titles_query.value}")
    if sw_titles_platform.value:
        _params.append(f"platform={sw_titles_platform.value}")
    if sw_titles_vuln_only.value:
        _params.append("vulnerable=true")
    if sw_titles_exploit.value:
        _params.append("exploit=true")
    if sw_titles_min_cvss.value > 0:
        _params.append(f"min_cvss_score={sw_titles_min_cvss.value}")
    if sw_titles_max_cvss.value > 0:
        _params.append(f"max_cvss_score={sw_titles_max_cvss.value}")
    if sw_titles_available_install.value:
        _params.append("available_for_install=true")
    if sw_titles_self_service.value:
        _params.append("self_service=true")
    if sw_titles_packages_only.value:
        _params.append("packages_only=true")
    if sw_titles_exclude_fma.value:
        _params.append("exclude_fleet_maintained_apps=true")

    _query_str = "?" + "&".join(_params)

    with mo.status.spinner(title="Fetching software titles..."):
        _status, _data = fleet("GET", f"/api/v1/fleet/software/titles{_query_str}")

    if _status == 200:
        _titles = _data.get("software_titles", [])
        _count = _data.get("count", 0)
        _meta = _data.get("meta", {})
        _has_next = _meta.get("has_next_results", False)
        _has_prev = _meta.get("has_previous_results", False)
        if _titles:
            _page_info = f"Page {sw_titles_page.value} | Showing {len(_titles)} of {_count} total"
            if _has_next:
                _page_info += " | More pages available →"
            _result = fleet_output(f"{_page_info}", _titles)
        else:
            _result = mo.md("**No software titles found.**")
    else:
        _result = fleet_error(f"Failed to list software titles (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Get Software Title

Get details for a specific software title by ID.
""")


@app.cell
def _(mo):
    get_sw_title_id = mo.ui.text(placeholder="Software Title ID", label="Software Title ID")
    get_sw_title_team_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Team ID (optional)")
    get_sw_title_btn = mo.ui.run_button(label="Get Software Title")

    mo.hstack([get_sw_title_id, get_sw_title_team_id, get_sw_title_btn], justify="start", gap=1)

    return get_sw_title_id, get_sw_title_team_id, get_sw_title_btn


@app.cell
def _(mo, json, fleet, get_sw_title_id, get_sw_title_team_id, get_sw_title_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not get_sw_title_btn.value)
    mo.stop(not get_sw_title_id.value, fleet_tip("Enter a Software Title ID."))

    _title_id = get_sw_title_id.value.strip()
    _team_param = f"?team_id={get_sw_title_team_id.value}" if get_sw_title_team_id.value > 0 else ""
    _status, _data = fleet("GET", f"/api/v1/fleet/software/titles/{_title_id}{_team_param}")

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Software title {_title_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get software title (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### List Software Versions

List all software versions across your fleet. Each version is a specific release of a software title.
""")


@app.cell
def _(mo):
    sw_versions_team_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Team ID (0 = all teams)")
    sw_versions_query = mo.ui.text(placeholder="Search by name...", label="Search Query")
    sw_versions_per_page = mo.ui.dropdown(
        options={"25": "25", "50": "50", "100": "100", "250": "250"},
        value="50",
        label="Per Page",
    )
    sw_versions_page = mo.ui.number(start=0, stop=9999, step=1, value=0, label="Page")
    sw_versions_vuln_only = mo.ui.checkbox(label="Vulnerable only")
    list_sw_versions_btn = mo.ui.run_button(label="List Software Versions")

    mo.vstack([
        mo.hstack([sw_versions_team_id, sw_versions_query, sw_versions_per_page, sw_versions_page], gap=1),
        mo.hstack([sw_versions_vuln_only, list_sw_versions_btn], gap=2, justify="start"),
    ])

    return sw_versions_team_id, sw_versions_query, sw_versions_per_page, sw_versions_page, sw_versions_vuln_only, list_sw_versions_btn


@app.cell
def _(mo, fleet, sw_versions_team_id, sw_versions_query, sw_versions_per_page, sw_versions_page, sw_versions_vuln_only, list_sw_versions_btn, fleet_error, fleet_output):
    mo.stop(not list_sw_versions_btn.value)

    _params = [f"per_page={sw_versions_per_page.value}", f"page={sw_versions_page.value}"]
    if sw_versions_team_id.value > 0:
        _params.append(f"team_id={sw_versions_team_id.value}")
    if sw_versions_query.value:
        _params.append(f"query={sw_versions_query.value}")
    if sw_versions_vuln_only.value:
        _params.append("vulnerable=true")

    _query_str = "?" + "&".join(_params)

    with mo.status.spinner(title="Fetching software versions..."):
        _status, _data = fleet("GET", f"/api/v1/fleet/software/versions{_query_str}")

    if _status == 200:
        _versions = _data.get("software", [])
        _count = _data.get("count", 0)
        _meta = _data.get("meta", {})
        _has_next = _meta.get("has_next_results", False)
        if _versions:
            _page_info = f"Page {sw_versions_page.value} | Showing {len(_versions)} of {_count} total"
            if _has_next:
                _page_info += " | More pages available →"
            _result = fleet_output(f"{_page_info}", _versions)
        else:
            _result = mo.md("**No software versions found.**")
    else:
        _result = fleet_error(f"Failed to list software versions (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Get Software Version

Get details for a specific software version by ID.
""")


@app.cell
def _(mo):
    get_sw_version_id = mo.ui.text(placeholder="Software Version ID", label="Software Version ID")
    get_sw_version_team_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Team ID (optional)")
    get_sw_version_btn = mo.ui.run_button(label="Get Software Version")

    mo.hstack([get_sw_version_id, get_sw_version_team_id, get_sw_version_btn], justify="start", gap=1)

    return get_sw_version_id, get_sw_version_team_id, get_sw_version_btn


@app.cell
def _(mo, json, fleet, get_sw_version_id, get_sw_version_team_id, get_sw_version_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not get_sw_version_btn.value)
    mo.stop(not get_sw_version_id.value, fleet_tip("Enter a Software Version ID."))

    _version_id = get_sw_version_id.value.strip()
    _team_param = f"?team_id={get_sw_version_team_id.value}" if get_sw_version_team_id.value > 0 else ""
    _status, _data = fleet("GET", f"/api/v1/fleet/software/versions/{_version_id}{_team_param}")

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Software version {_version_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get software version (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### List Operating Systems

List all operating system versions across your fleet.
""")


@app.cell
def _(mo):
    os_versions_team_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Team ID (0 = all teams)")
    os_versions_platform = mo.ui.dropdown(
        options={"All platforms": "", "macOS": "darwin", "Windows": "windows", "Ubuntu": "ubuntu", "CentOS": "centos", "Chrome": "chrome"},
        value="All platforms",
        label="Platform",
    )
    os_versions_per_page = mo.ui.dropdown(
        options={"25": "25", "50": "50", "100": "100", "250": "250"},
        value="50",
        label="Per Page",
    )
    os_versions_page = mo.ui.number(start=0, stop=9999, step=1, value=0, label="Page")
    os_versions_name = mo.ui.text(placeholder="OS name filter (e.g., macOS)", label="OS Name")
    list_os_versions_btn = mo.ui.run_button(label="List Operating Systems")

    mo.vstack([
        mo.hstack([os_versions_team_id, os_versions_platform, os_versions_per_page, os_versions_page], gap=1),
        mo.hstack([os_versions_name, list_os_versions_btn], justify="start", gap=1),
    ])

    return os_versions_team_id, os_versions_platform, os_versions_per_page, os_versions_page, os_versions_name, list_os_versions_btn


@app.cell
def _(mo, fleet, os_versions_team_id, os_versions_platform, os_versions_per_page, os_versions_page, os_versions_name, list_os_versions_btn, fleet_error, fleet_output):
    mo.stop(not list_os_versions_btn.value)

    _params = [f"per_page={os_versions_per_page.value}", f"page={os_versions_page.value}"]
    if os_versions_team_id.value > 0:
        _params.append(f"team_id={os_versions_team_id.value}")
    if os_versions_platform.value:
        _params.append(f"platform={os_versions_platform.value}")
    if os_versions_name.value:
        _params.append(f"os_name={os_versions_name.value}")

    _query_str = "?" + "&".join(_params)

    with mo.status.spinner(title="Fetching operating systems..."):
        _status, _data = fleet("GET", f"/api/v1/fleet/os_versions{_query_str}")

    if _status == 200:
        _os_versions = _data.get("os_versions", [])
        _count = _data.get("count", 0)
        _meta = _data.get("meta", {})
        _has_next = _meta.get("has_next_results", False)
        if _os_versions:
            _page_info = f"Page {os_versions_page.value} | Showing {len(_os_versions)} of {_count} total"
            if _has_next:
                _page_info += " | More pages available →"
            _result = fleet_output(f"{_page_info}", _os_versions)
        else:
            _result = mo.md("**No operating system versions found.**")
    else:
        _result = fleet_error(f"Failed to list OS versions (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Get Operating System Version

Get details for a specific operating system version by ID.
""")


@app.cell
def _(mo):
    get_os_version_id = mo.ui.text(placeholder="OS Version ID", label="OS Version ID")
    get_os_version_team_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Team ID (optional)")
    get_os_version_btn = mo.ui.run_button(label="Get OS Version")

    mo.hstack([get_os_version_id, get_os_version_team_id, get_os_version_btn], justify="start", gap=1)

    return get_os_version_id, get_os_version_team_id, get_os_version_btn


@app.cell
def _(mo, json, fleet, get_os_version_id, get_os_version_team_id, get_os_version_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not get_os_version_btn.value)
    mo.stop(not get_os_version_id.value, fleet_tip("Enter an OS Version ID."))

    _version_id = get_os_version_id.value.strip()
    _team_param = f"?team_id={get_os_version_team_id.value}" if get_os_version_team_id.value > 0 else ""
    _status, _data = fleet("GET", f"/api/v1/fleet/os_versions/{_version_id}{_team_param}")

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"OS version {_version_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get OS version (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Add Software Package

Upload a software package (.pkg, .msi, .exe, .deb) to Fleet. Requires Fleet Premium.
""")


@app.cell
def _(mo):
    add_pkg_team_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Team ID (0 = no team)")
    add_pkg_file = mo.ui.file(filetypes=[".pkg", ".msi", ".exe", ".deb", ".rpm"], label="Software Package", multiple=False)
    add_pkg_install_script = mo.ui.text_area(placeholder="#!/bin/bash\ninstaller -pkg $INSTALLER_PATH -target /", label="Install Script (optional)", rows=3, full_width=True)
    add_pkg_uninstall_script = mo.ui.text_area(placeholder="#!/bin/bash\nrm -rf /Applications/MyApp.app", label="Uninstall Script (optional)", rows=3, full_width=True)
    add_pkg_pre_install_query = mo.ui.text_area(placeholder="SELECT 1 FROM osquery_info WHERE version >= '5.0.0';", label="Pre-install Query (optional)", rows=2, full_width=True)
    add_pkg_post_install_script = mo.ui.text_area(placeholder="#!/bin/bash\necho 'Post-install complete'", label="Post-install Script (optional)", rows=2, full_width=True)
    add_pkg_self_service = mo.ui.checkbox(label="Self-service (allow users to install)")
    add_pkg_auto_install = mo.ui.checkbox(label="Automatic install")
    add_pkg_labels_include = mo.ui.text(placeholder="label1, label2, ...", label="Labels Include Any (comma-separated)", full_width=True)
    add_pkg_labels_exclude = mo.ui.text(placeholder="label1, label2, ...", label="Labels Exclude Any (comma-separated)", full_width=True)
    add_pkg_btn = mo.ui.run_button(label="Upload Package")

    mo.vstack([
        mo.hstack([add_pkg_team_id, add_pkg_self_service, add_pkg_auto_install], gap=2),
        add_pkg_file,
        add_pkg_install_script,
        add_pkg_uninstall_script,
        add_pkg_pre_install_query,
        add_pkg_post_install_script,
        mo.md("**Label Targeting** (install only on hosts matching labels)"),
        add_pkg_labels_include,
        add_pkg_labels_exclude,
        mo.hstack([add_pkg_btn], justify="start"),
    ])

    return add_pkg_team_id, add_pkg_file, add_pkg_install_script, add_pkg_uninstall_script, add_pkg_pre_install_query, add_pkg_post_install_script, add_pkg_self_service, add_pkg_auto_install, add_pkg_labels_include, add_pkg_labels_exclude, add_pkg_btn


@app.cell
def _(mo, json, httpx, fleet_url_input, api_token_input, add_pkg_team_id, add_pkg_file, add_pkg_install_script, add_pkg_uninstall_script, add_pkg_pre_install_query, add_pkg_post_install_script, add_pkg_self_service, add_pkg_auto_install, add_pkg_labels_include, add_pkg_labels_exclude, add_pkg_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not add_pkg_btn.value)
    mo.stop(not add_pkg_file.value, fleet_tip("Select a software package file."))

    _file = add_pkg_file.value[0]
    _files = {"software": (_file.name, _file.contents, "application/octet-stream")}
    _data = {}

    if add_pkg_team_id.value > 0:
        _data["team_id"] = str(add_pkg_team_id.value)
    if add_pkg_install_script.value:
        _data["install_script"] = add_pkg_install_script.value
    if add_pkg_uninstall_script.value:
        _data["uninstall_script"] = add_pkg_uninstall_script.value
    if add_pkg_pre_install_query.value:
        _data["pre_install_query"] = add_pkg_pre_install_query.value
    if add_pkg_post_install_script.value:
        _data["post_install_script"] = add_pkg_post_install_script.value
    if add_pkg_self_service.value:
        _data["self_service"] = "true"
    if add_pkg_auto_install.value:
        _data["automatic_install"] = "true"

    # Labels - need to send as multiple form fields with same name
    _labels_include = [l.strip() for l in add_pkg_labels_include.value.split(",") if l.strip()] if add_pkg_labels_include.value else []
    _labels_exclude = [l.strip() for l in add_pkg_labels_exclude.value.split(",") if l.strip()] if add_pkg_labels_exclude.value else []

    # Convert _data dict to list of tuples for repeated field names (labels)
    _form_data = list(_data.items())
    for _label in _labels_include:
        _form_data.append(("labels_include_any", _label))
    for _label in _labels_exclude:
        _form_data.append(("labels_exclude_any", _label))

    try:
        _response = httpx.post(
            f"{fleet_url_input.value}/api/v1/fleet/software/package",
            headers={"Authorization": f"Bearer {api_token_input.value}"},
            files=_files,
            data=_form_data,
            timeout=300.0,  # Long timeout for large files
        )
        _status = _response.status_code
        _resp_data = _response.json() if _response.text else {}
    except Exception as e:
        _status = 0
        _resp_data = {"error": str(e)}

    if _status in (200, 201):
        _pkg = _resp_data.get("software_package", {})
        _title_id = _pkg.get("title_id", "N/A")
        _name = _pkg.get("name", _file.name)
        _formatted = json.dumps(_resp_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Uploaded package: {_name}"),
            mo.callout(f"**Software Title ID: `{_title_id}`** — Use this ID to update, delete, or install this software.", kind="success"),
            mo.accordion({"View Full Response": mo.md(f"```json\n{_formatted}\n```")}),
        ])
    else:
        _result = fleet_error(f"Failed to upload package (status {_status}): {_resp_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Update Software Package

Update an existing software package by title ID.
""")


@app.cell
def _(mo):
    update_pkg_title_id = mo.ui.text(placeholder="Software Title ID", label="Software Title ID", full_width=True)
    update_pkg_team_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Team ID (0 = no team)")
    update_pkg_display_name = mo.ui.text(placeholder="Custom display name (max 255 chars)", label="Display Name", full_width=True)
    update_pkg_file = mo.ui.file(filetypes=[".pkg", ".msi", ".exe", ".deb", ".rpm"], label="New Package (optional)", multiple=False)
    update_pkg_install_script = mo.ui.text_area(placeholder="Install script (leave empty to keep existing)", label="Install Script", rows=3, full_width=True)
    update_pkg_uninstall_script = mo.ui.text_area(placeholder="Uninstall script (leave empty to keep existing)", label="Uninstall Script", rows=3, full_width=True)
    update_pkg_pre_install_query = mo.ui.text_area(placeholder="SELECT 1 FROM osquery_info WHERE version >= '5.0.0';", label="Pre-install Query", rows=2, full_width=True)
    update_pkg_post_install_script = mo.ui.text_area(placeholder="Post-install script (leave empty to keep existing)", label="Post-install Script", rows=2, full_width=True)
    update_pkg_self_service = mo.ui.dropdown(options={"Keep existing": "", "Enable": "true", "Disable": "false"}, value="Keep existing", label="Self-service")
    update_pkg_labels_include = mo.ui.text(placeholder="label1, label2, ...", label="Labels Include Any (comma-separated)", full_width=True)
    update_pkg_labels_exclude = mo.ui.text(placeholder="label1, label2, ...", label="Labels Exclude Any (comma-separated)", full_width=True)
    update_pkg_categories = mo.ui.multiselect(
        options=["Productivity", "Browsers", "Communication", "Developer tools", "Security", "Utilities"],
        label="Categories",
    )
    update_pkg_btn = mo.ui.run_button(label="Update Package")

    mo.vstack([
        mo.hstack([update_pkg_title_id, update_pkg_team_id], gap=1),
        update_pkg_display_name,
        update_pkg_file,
        update_pkg_install_script,
        update_pkg_uninstall_script,
        update_pkg_pre_install_query,
        update_pkg_post_install_script,
        update_pkg_self_service,
        mo.md("**Label Targeting** (install only on hosts matching labels)"),
        update_pkg_labels_include,
        update_pkg_labels_exclude,
        update_pkg_categories,
        mo.hstack([update_pkg_btn], justify="start"),
    ])

    return update_pkg_title_id, update_pkg_team_id, update_pkg_display_name, update_pkg_file, update_pkg_install_script, update_pkg_uninstall_script, update_pkg_pre_install_query, update_pkg_post_install_script, update_pkg_self_service, update_pkg_labels_include, update_pkg_labels_exclude, update_pkg_categories, update_pkg_btn


@app.cell
def _(mo, json, httpx, fleet_url_input, api_token_input, update_pkg_title_id, update_pkg_team_id, update_pkg_display_name, update_pkg_file, update_pkg_install_script, update_pkg_uninstall_script, update_pkg_pre_install_query, update_pkg_post_install_script, update_pkg_self_service, update_pkg_labels_include, update_pkg_labels_exclude, update_pkg_categories, update_pkg_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not update_pkg_btn.value)
    mo.stop(not update_pkg_title_id.value, fleet_tip("Enter a Software Title ID."))

    _title_id = update_pkg_title_id.value.strip()
    _data = {}

    # team_id is required (0 = no team)
    _data["team_id"] = str(int(update_pkg_team_id.value))
    if update_pkg_display_name.value:
        _data["display_name"] = update_pkg_display_name.value
    if update_pkg_install_script.value:
        _data["install_script"] = update_pkg_install_script.value
    if update_pkg_uninstall_script.value:
        _data["uninstall_script"] = update_pkg_uninstall_script.value
    if update_pkg_pre_install_query.value:
        _data["pre_install_query"] = update_pkg_pre_install_query.value
    if update_pkg_post_install_script.value:
        _data["post_install_script"] = update_pkg_post_install_script.value
    if update_pkg_self_service.value:
        _data["self_service"] = update_pkg_self_service.value

    # Labels - need to send as multiple form fields with same name
    _labels_include = [l.strip() for l in update_pkg_labels_include.value.split(",") if l.strip()] if update_pkg_labels_include.value else []
    _labels_exclude = [l.strip() for l in update_pkg_labels_exclude.value.split(",") if l.strip()] if update_pkg_labels_exclude.value else []
    _categories = update_pkg_categories.value if update_pkg_categories.value else []

    # Build multipart form - all fields go in files dict for proper multipart encoding
    _multipart = []
    for _key, _val in _data.items():
        _multipart.append((_key, (None, _val)))
    for _label in _labels_include:
        _multipart.append(("labels_include_any", (None, _label)))
    for _label in _labels_exclude:
        _multipart.append(("labels_exclude_any", (None, _label)))
    for _cat in _categories:
        _multipart.append(("categories", (None, _cat)))

    # Add file if provided
    if update_pkg_file.value:
        _file = update_pkg_file.value[0]
        _multipart.append(("software", (_file.name, _file.contents, "application/octet-stream")))

    try:
        _response = httpx.patch(
            f"{fleet_url_input.value}/api/v1/fleet/software/titles/{_title_id}/package",
            headers={"Authorization": f"Bearer {api_token_input.value}"},
            files=_multipart if _multipart else None,
            timeout=300.0,
        )
        _status = _response.status_code
        _resp_data = _response.json() if _response.text else {}
    except Exception as e:
        _status = 0
        _resp_data = {"error": str(e)}

    if _status == 200:
        _formatted = json.dumps(_resp_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Updated software title {_title_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to update package (status {_status}): {_resp_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Software Icon Management

Upload, download, or delete custom icons for software titles.
""")


@app.cell
def _(mo):
    icon_title_id = mo.ui.text(placeholder="Software Title ID", label="Software Title ID")
    icon_file = mo.ui.file(filetypes=[".png", ".jpg", ".jpeg", ".gif", ".svg"], label="Icon File (for upload)", multiple=False)
    upload_icon_btn = mo.ui.run_button(label="Upload Icon")
    download_icon_btn = mo.ui.run_button(label="Download Icon")
    delete_icon_btn = mo.ui.run_button(label="Delete Icon", kind="danger")

    mo.vstack([
        mo.hstack([icon_title_id], gap=1),
        icon_file,
        mo.hstack([upload_icon_btn, download_icon_btn, delete_icon_btn], justify="start", gap=1),
    ])

    return icon_title_id, icon_file, upload_icon_btn, download_icon_btn, delete_icon_btn


@app.cell
def _(mo, json, httpx, fleet_url_input, api_token_input, icon_title_id, icon_file, upload_icon_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not upload_icon_btn.value)
    mo.stop(not icon_title_id.value, fleet_tip("Enter a Software Title ID."))
    mo.stop(not icon_file.value, fleet_tip("Select an icon file."))

    _title_id = icon_title_id.value.strip()
    _file = icon_file.value[0]
    _files = {"icon": (_file.name, _file.contents, "image/png")}

    try:
        _response = httpx.put(
            f"{fleet_url_input.value}/api/v1/fleet/software/titles/{_title_id}/icon",
            headers={"Authorization": f"Bearer {api_token_input.value}"},
            files=_files,
            timeout=60.0,
        )
        _status = _response.status_code
        _resp_data = _response.json() if _response.text else {}
    except Exception as e:
        _status = 0
        _resp_data = {"error": str(e)}

    if _status == 200:
        _formatted = json.dumps(_resp_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Uploaded icon for title {_title_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to upload icon (status {_status}): {_resp_data}")

    _result


@app.cell
def _(mo, httpx, fleet_url_input, api_token_input, icon_title_id, download_icon_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not download_icon_btn.value)
    mo.stop(not icon_title_id.value, fleet_tip("Enter a Software Title ID."))

    _title_id = icon_title_id.value.strip()

    try:
        _response = httpx.get(
            f"{fleet_url_input.value}/api/v1/fleet/software/titles/{_title_id}/icon",
            headers={"Authorization": f"Bearer {api_token_input.value}"},
            timeout=60.0,
        )
        _status = _response.status_code
    except Exception as e:
        _status = 0
        _response = None

    if _status == 200 and _response:
        _content_type = _response.headers.get("content-type", "image/png")
        _result = mo.vstack([
            fleet_success(f"Icon for title {_title_id} ({_content_type})"),
            mo.image(_response.content),
        ])
    else:
        _result = fleet_error(f"Failed to download icon (status {_status})")

    _result


@app.cell
def _(mo, fleet, icon_title_id, delete_icon_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not delete_icon_btn.value)
    mo.stop(not icon_title_id.value, fleet_tip("Enter a Software Title ID."))

    _title_id = icon_title_id.value.strip()
    _status, _data = fleet("DELETE", f"/api/v1/fleet/software/titles/{_title_id}/icon")

    if _status in (200, 204):
        _result = fleet_success(f"Deleted icon for title {_title_id}")
    else:
        _result = fleet_error(f"Failed to delete icon (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Delete Software

Remove software from Fleet. This deletes the package but not any installed instances on hosts.
""")


@app.cell
def _(mo):
    delete_sw_title_id = mo.ui.text(placeholder="Software Title ID", label="Software Title ID")
    delete_sw_team_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Team ID (0 = no team)")
    delete_sw_btn = mo.ui.run_button(label="Delete Software", kind="danger")

    mo.hstack([delete_sw_title_id, delete_sw_team_id, delete_sw_btn], justify="start", gap=1)

    return delete_sw_title_id, delete_sw_team_id, delete_sw_btn


@app.cell
def _(mo, fleet, delete_sw_title_id, delete_sw_team_id, delete_sw_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not delete_sw_btn.value)
    mo.stop(not delete_sw_title_id.value, fleet_tip("Enter a Software Title ID."))

    _title_id = delete_sw_title_id.value.strip()
    _team_param = f"?team_id={delete_sw_team_id.value}" if delete_sw_team_id.value > 0 else ""
    _status, _data = fleet("DELETE", f"/api/v1/fleet/software/titles/{_title_id}/available_for_install{_team_param}")

    if _status in (200, 204):
        _result = fleet_success(f"Deleted software title {_title_id}")
    else:
        _result = fleet_error(f"Failed to delete software (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Apple App Store Apps

Manage VPP (Volume Purchase Program) apps from Apple App Store. Requires Apple Business Manager integration.
""")


@app.cell
def _(mo):
    vpp_team_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Team ID (0 = no team)")
    list_vpp_btn = mo.ui.run_button(label="List App Store Apps")

    mo.hstack([vpp_team_id, list_vpp_btn], justify="start", gap=1)

    return vpp_team_id, list_vpp_btn


@app.cell
def _(mo, json, fleet, vpp_team_id, list_vpp_btn, fleet_success, fleet_error):
    mo.stop(not list_vpp_btn.value)

    _status, _data = fleet("GET", f"/api/v1/fleet/software/app_store_apps?team_id={vpp_team_id.value}")

    if _status == 200:
        _apps = _data.get("app_store_apps", [])
        if _apps:
            _formatted = json.dumps(_apps, indent=2)
            _result = mo.vstack([
                fleet_success(f"Found {len(_apps)} App Store app(s)"),
                mo.md(f"```json\n{_formatted}\n```"),
            ])
        else:
            _result = mo.md("**No App Store apps configured.**")
    else:
        _result = fleet_error(f"Failed to list App Store apps (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Add App Store App

Add an app from the Apple App Store via VPP.
""")


@app.cell
def _(mo):
    add_vpp_team_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Team ID (0 = no team)")
    add_vpp_app_store_id = mo.ui.text(placeholder="App Store ID (e.g., 497799835 for Xcode)", label="App Store ID", full_width=True)
    add_vpp_platform = mo.ui.dropdown(options={"iOS/iPadOS": "ios", "macOS": "macos"}, value="iOS/iPadOS", label="Platform")
    add_vpp_self_service = mo.ui.checkbox(label="Self-service")
    add_vpp_auto_install = mo.ui.checkbox(label="Automatic install")
    add_vpp_btn = mo.ui.run_button(label="Add App Store App")

    mo.vstack([
        mo.hstack([add_vpp_team_id, add_vpp_platform], gap=1),
        add_vpp_app_store_id,
        mo.hstack([add_vpp_self_service, add_vpp_auto_install], gap=2),
        mo.hstack([add_vpp_btn], justify="start"),
    ])

    return add_vpp_team_id, add_vpp_app_store_id, add_vpp_platform, add_vpp_self_service, add_vpp_auto_install, add_vpp_btn


@app.cell
def _(mo, json, fleet, add_vpp_team_id, add_vpp_app_store_id, add_vpp_platform, add_vpp_self_service, add_vpp_auto_install, add_vpp_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not add_vpp_btn.value)
    mo.stop(not add_vpp_app_store_id.value, fleet_tip("Enter an App Store ID."))

    _payload = {
        "app_store_id": add_vpp_app_store_id.value.strip(),
        "platform": add_vpp_platform.value,
        "self_service": add_vpp_self_service.value,
        "automatic_install": add_vpp_auto_install.value,
    }
    if add_vpp_team_id.value > 0:
        _payload["team_id"] = add_vpp_team_id.value

    _status, _data = fleet("POST", "/api/v1/fleet/software/app_store_apps", json_data=_payload)

    if _status in (200, 201):
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Added App Store app: {add_vpp_app_store_id.value}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to add App Store app (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Update App Store App

Update settings for an existing App Store app.
""")


@app.cell
def _(mo):
    update_vpp_title_id = mo.ui.text(placeholder="Software Title ID", label="Software Title ID", full_width=True)
    update_vpp_team_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Team ID")
    update_vpp_self_service = mo.ui.dropdown(options={"Keep existing": "", "Enable": "true", "Disable": "false"}, value="Keep existing", label="Self-service")
    update_vpp_btn = mo.ui.run_button(label="Update App Store App")

    mo.vstack([
        mo.hstack([update_vpp_title_id, update_vpp_team_id], gap=1),
        update_vpp_self_service,
        mo.hstack([update_vpp_btn], justify="start"),
    ])

    return update_vpp_title_id, update_vpp_team_id, update_vpp_self_service, update_vpp_btn


@app.cell
def _(mo, json, fleet, update_vpp_title_id, update_vpp_team_id, update_vpp_self_service, update_vpp_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not update_vpp_btn.value)
    mo.stop(not update_vpp_title_id.value, fleet_tip("Enter a Software Title ID."))

    _title_id = update_vpp_title_id.value.strip()
    _payload = {}
    if update_vpp_team_id.value > 0:
        _payload["team_id"] = update_vpp_team_id.value
    if update_vpp_self_service.value:
        _payload["self_service"] = update_vpp_self_service.value == "true"

    _status, _data = fleet("PATCH", f"/api/v1/fleet/software/titles/{_title_id}/app_store_app", json_data=_payload)

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Updated App Store app (title {_title_id})"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to update App Store app (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Fleet-Maintained Apps

Browse and add pre-packaged apps maintained by Fleet.
""")


@app.cell
def _(mo):
    fma_team_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Team ID (optional)")
    list_fma_btn = mo.ui.run_button(label="List Fleet-Maintained Apps")
    fma_app_id = mo.ui.text(placeholder="Fleet App ID", label="Fleet App ID")
    get_fma_btn = mo.ui.run_button(label="Get App Details")

    mo.vstack([
        mo.hstack([fma_team_id, list_fma_btn], justify="start", gap=1),
        mo.hstack([fma_app_id, get_fma_btn], justify="start", gap=1),
    ])

    return fma_team_id, list_fma_btn, fma_app_id, get_fma_btn


@app.cell
def _(mo, json, fleet, fma_team_id, list_fma_btn, fleet_success, fleet_error):
    mo.stop(not list_fma_btn.value)

    _team_param = f"?team_id={fma_team_id.value}" if fma_team_id.value > 0 else ""
    _status, _data = fleet("GET", f"/api/v1/fleet/software/fleet_maintained_apps{_team_param}")

    if _status == 200:
        _apps = _data.get("fleet_maintained_apps", [])
        if _apps:
            _formatted = json.dumps(_apps, indent=2)
            _result = mo.vstack([
                fleet_success(f"Found {len(_apps)} Fleet-maintained app(s)"),
                mo.md(f"```json\n{_formatted}\n```"),
            ])
        else:
            _result = mo.md("**No Fleet-maintained apps available.**")
    else:
        _result = fleet_error(f"Failed to list Fleet-maintained apps (status {_status}): {_data}")

    _result


@app.cell
def _(mo, json, fleet, fma_app_id, get_fma_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not get_fma_btn.value)
    mo.stop(not fma_app_id.value, fleet_tip("Enter a Fleet App ID."))

    _app_id = fma_app_id.value.strip()
    _status, _data = fleet("GET", f"/api/v1/fleet/software/fleet_maintained_apps/{_app_id}")

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Fleet-maintained app {_app_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get Fleet-maintained app (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Add Fleet-Maintained App

Add a Fleet-maintained app to your Fleet instance.
""")


@app.cell
def _(mo):
    add_fma_team_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Team ID (0 = no team)")
    add_fma_app_id = mo.ui.text(placeholder="Fleet Maintained App ID", label="Fleet App ID", full_width=True)
    add_fma_install_script = mo.ui.text_area(placeholder="Custom install script (optional, uses default if empty)", label="Install Script", rows=3, full_width=True)
    add_fma_uninstall_script = mo.ui.text_area(placeholder="Custom uninstall script (optional)", label="Uninstall Script", rows=3, full_width=True)
    add_fma_self_service = mo.ui.checkbox(label="Self-service")
    add_fma_auto_install = mo.ui.checkbox(label="Automatic install")
    add_fma_btn = mo.ui.run_button(label="Add Fleet-Maintained App")

    mo.vstack([
        mo.hstack([add_fma_team_id, add_fma_app_id], gap=1),
        add_fma_install_script,
        add_fma_uninstall_script,
        mo.hstack([add_fma_self_service, add_fma_auto_install], gap=2),
        mo.hstack([add_fma_btn], justify="start"),
    ])

    return add_fma_team_id, add_fma_app_id, add_fma_install_script, add_fma_uninstall_script, add_fma_self_service, add_fma_auto_install, add_fma_btn


@app.cell
def _(mo, json, fleet, add_fma_team_id, add_fma_app_id, add_fma_install_script, add_fma_uninstall_script, add_fma_self_service, add_fma_auto_install, add_fma_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not add_fma_btn.value)
    mo.stop(not add_fma_app_id.value, fleet_tip("Enter a Fleet App ID."))

    _payload = {
        "fleet_maintained_app_id": int(add_fma_app_id.value.strip()),
        "self_service": add_fma_self_service.value,
        "automatic_install": add_fma_auto_install.value,
    }
    if add_fma_team_id.value > 0:
        _payload["team_id"] = add_fma_team_id.value
    if add_fma_install_script.value:
        _payload["install_script"] = add_fma_install_script.value
    if add_fma_uninstall_script.value:
        _payload["uninstall_script"] = add_fma_uninstall_script.value

    _status, _data = fleet("POST", "/api/v1/fleet/software/fleet_maintained_apps", json_data=_payload)

    if _status in (200, 201):
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Added Fleet-maintained app {add_fma_app_id.value}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to add Fleet-maintained app (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Batch Add Fleet-Maintained Apps

Add multiple Fleet-maintained apps to a team at once. Enter app names (one per line or comma-separated).

**Available apps:** 1Password, Adobe Acrobat Reader, Box Drive, Brave Browser, Cloudflare WARP, Docker, Figma, Firefox, Google Chrome, Microsoft Edge, Microsoft Excel, Microsoft Teams, Microsoft Word, Notion, Postman, Slack, TeamViewer, Visual Studio Code, WhatsApp, Zoom
""")


@app.cell
def _(mo):
    # Static mapping of app names to identifiers (used by Fleet API)
    FLEET_MAINTAINED_APPS = {
        "1password": {"name": "1Password", "identifier": "1password"},
        "adobe acrobat reader": {"name": "Adobe Acrobat Reader", "identifier": "adobe-acrobat-reader"},
        "box drive": {"name": "Box Drive", "identifier": "box-drive"},
        "brave browser": {"name": "Brave Browser", "identifier": "brave-browser"},
        "brave": {"name": "Brave Browser", "identifier": "brave-browser"},
        "cloudflare warp": {"name": "Cloudflare WARP", "identifier": "cloudflare-warp"},
        "warp": {"name": "Cloudflare WARP", "identifier": "cloudflare-warp"},
        "docker": {"name": "Docker Desktop", "identifier": "docker-desktop"},
        "docker desktop": {"name": "Docker Desktop", "identifier": "docker-desktop"},
        "figma": {"name": "Figma", "identifier": "figma"},
        "firefox": {"name": "Firefox", "identifier": "firefox"},
        "google chrome": {"name": "Google Chrome", "identifier": "google-chrome"},
        "chrome": {"name": "Google Chrome", "identifier": "google-chrome"},
        "microsoft edge": {"name": "Microsoft Edge", "identifier": "microsoft-edge"},
        "edge": {"name": "Microsoft Edge", "identifier": "microsoft-edge"},
        "microsoft excel": {"name": "Microsoft Excel", "identifier": "microsoft-excel"},
        "excel": {"name": "Microsoft Excel", "identifier": "microsoft-excel"},
        "microsoft teams": {"name": "Microsoft Teams", "identifier": "microsoft-teams"},
        "teams": {"name": "Microsoft Teams", "identifier": "microsoft-teams"},
        "microsoft word": {"name": "Microsoft Word", "identifier": "microsoft-word"},
        "word": {"name": "Microsoft Word", "identifier": "microsoft-word"},
        "notion": {"name": "Notion", "identifier": "notion"},
        "postman": {"name": "Postman", "identifier": "postman"},
        "slack": {"name": "Slack", "identifier": "slack"},
        "teamviewer": {"name": "TeamViewer", "identifier": "teamviewer"},
        "visual studio code": {"name": "Visual Studio Code", "identifier": "visual-studio-code"},
        "vscode": {"name": "Visual Studio Code", "identifier": "visual-studio-code"},
        "vs code": {"name": "Visual Studio Code", "identifier": "visual-studio-code"},
        "whatsapp": {"name": "WhatsApp", "identifier": "whatsapp"},
        "zoom": {"name": "Zoom", "identifier": "zoom-for-it-admins"},
    }

    batch_fma_team_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Team ID (0 = no team)")
    batch_fma_platform = mo.ui.dropdown(
        options={"macOS": "darwin", "Windows": "windows", "All platforms": ""},
        value="macOS",
        label="Platform",
    )
    batch_fma_apps = mo.ui.text_area(
        placeholder="Enter app names, one per line or comma-separated:\nSlack\nZoom\nChrome",
        label="App Names",
        rows=6,
        full_width=True,
    )
    batch_fma_self_service = mo.ui.checkbox(label="Self-service")
    batch_fma_auto_install = mo.ui.checkbox(label="Automatic install")
    batch_fma_btn = mo.ui.run_button(label="Add Apps to Team")

    mo.vstack([
        mo.hstack([batch_fma_team_id, batch_fma_platform, batch_fma_self_service, batch_fma_auto_install], gap=2),
        batch_fma_apps,
        mo.hstack([batch_fma_btn], justify="start"),
    ])

    return FLEET_MAINTAINED_APPS, batch_fma_team_id, batch_fma_platform, batch_fma_apps, batch_fma_self_service, batch_fma_auto_install, batch_fma_btn


@app.cell
def _(mo, fleet, FLEET_MAINTAINED_APPS, batch_fma_team_id, batch_fma_platform, batch_fma_apps, batch_fma_self_service, batch_fma_auto_install, batch_fma_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not batch_fma_btn.value)
    mo.stop(not batch_fma_apps.value.strip(), fleet_tip("Enter app names to add."))

    # Parse app names from input (handle both comma and newline separated)
    _input_text = batch_fma_apps.value.replace(",", "\n")
    _app_names = [name.strip().lower() for name in _input_text.split("\n") if name.strip()]

    # Selected platform filter
    _platform_filter = batch_fma_platform.value  # "darwin", "windows", or "" for all

    # First, get the list of Fleet-maintained apps to get their IDs
    _team_param = f"?team_id={int(batch_fma_team_id.value)}" if batch_fma_team_id.value >= 0 else ""
    with mo.status.spinner(title="Fetching Fleet-maintained apps catalog..."):
        _status, _catalog = fleet("GET", f"/api/v1/fleet/software/fleet_maintained_apps{_team_param}")

    if _status != 200:
        mo.stop(True, fleet_error(f"Failed to fetch app catalog (status {_status}): {_catalog}. Fleet Premium required."))

    # Build lookup from name/identifier to app ID (filtered by platform)
    _catalog_apps = _catalog.get("fleet_maintained_apps", [])
    _app_lookup = {}
    for _app in _catalog_apps:
        # Filter by platform if specified
        if _platform_filter and _app.get("platform") != _platform_filter:
            continue
        _app_lookup[_app.get("name", "").lower()] = _app
        # Also index by identifier slug
        _slug = _app.get("name", "").lower().replace(" ", "-")
        _app_lookup[_slug] = _app

    # Match input names to catalog apps
    _results = []
    _errors = []
    _success_count = 0

    with mo.status.spinner(title="Adding apps..."):
        for _name in _app_names:
            # Try to find in our static mapping first
            _mapped = FLEET_MAINTAINED_APPS.get(_name)
            if _mapped:
                _lookup_name = _mapped["name"].lower()
            else:
                _lookup_name = _name

            # Find in catalog
            _found_app = _app_lookup.get(_lookup_name)
            if not _found_app:
                # Try partial match
                for _cat_name, _cat_app in _app_lookup.items():
                    if _name in _cat_name or _cat_name in _name:
                        _found_app = _cat_app
                        break

            if not _found_app:
                _platform_note = f" for {batch_fma_platform.selected_key}" if _platform_filter else ""
                _errors.append(f"❌ **{_name}**: Not found in Fleet-maintained apps catalog{_platform_note}")
                continue

            # Check if already added to team
            if _found_app.get("software_title_id"):
                _results.append(f"⏭️ **{_found_app['name']}**: Already added (title ID: {_found_app['software_title_id']})")
                continue

            # Add the app
            _payload = {
                "fleet_maintained_app_id": _found_app["id"],
                "self_service": batch_fma_self_service.value,
                "automatic_install": batch_fma_auto_install.value,
            }
            if batch_fma_team_id.value > 0:
                _payload["team_id"] = int(batch_fma_team_id.value)

            _add_status, _add_data = fleet("POST", "/api/v1/fleet/software/fleet_maintained_apps", json_data=_payload)
            if _add_status == 200:
                _title_id = _add_data.get("software_title_id", "N/A")
                _results.append(f"✅ **{_found_app['name']}**: Added successfully (title ID: {_title_id})")
                _success_count += 1
            else:
                _err_msg = _add_data.get("message", str(_add_data)) if isinstance(_add_data, dict) else str(_add_data)
                _errors.append(f"❌ **{_found_app['name']}**: {_err_msg}")

    # Build result output
    _output_parts = []
    if _success_count > 0:
        _output_parts.append(fleet_success(f"Added {_success_count} app(s) to team {int(batch_fma_team_id.value)}"))
    if _results:
        _output_parts.append(mo.md("\n".join(_results)))
    if _errors:
        _output_parts.append(mo.md("### Errors\n" + "\n".join(_errors)))

    _result = mo.vstack(_output_parts) if _output_parts else mo.md("No apps processed.")
    _result


@app.cell
def _(mo, FLEET_MAINTAINED_APPS):
    mo.md("#### Batch Remove Fleet-Maintained Apps")

    batch_rm_team_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Team ID (0 = no team)")
    batch_rm_platform = mo.ui.dropdown(
        options={"macOS": "darwin", "Windows": "windows", "All platforms": ""},
        value="macOS",
        label="Platform",
    )
    batch_rm_apps = mo.ui.text_area(
        placeholder="Enter app names to remove, one per line or comma-separated:\nSlack\nZoom\nChrome",
        label="App Names to Remove",
        rows=6,
        full_width=True,
    )
    batch_rm_btn = mo.ui.run_button(label="Remove Apps from Team", kind="danger")

    mo.vstack([
        mo.hstack([batch_rm_team_id, batch_rm_platform], gap=2),
        batch_rm_apps,
        mo.hstack([batch_rm_btn], justify="start"),
    ])

    return batch_rm_team_id, batch_rm_platform, batch_rm_apps, batch_rm_btn


@app.cell
def _(mo, fleet, FLEET_MAINTAINED_APPS, batch_rm_team_id, batch_rm_platform, batch_rm_apps, batch_rm_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not batch_rm_btn.value)
    mo.stop(not batch_rm_apps.value.strip(), fleet_tip("Enter app names to remove."))

    # Parse app names from input (handle both comma and newline separated)
    _input_text = batch_rm_apps.value.replace(",", "\n")
    _app_names = [name.strip().lower() for name in _input_text.split("\n") if name.strip()]

    # Selected platform filter
    _platform_filter = batch_rm_platform.value  # "darwin", "windows", or "" for all

    # First, get the list of Fleet-maintained apps to get their software_title_id
    _team_param = f"?team_id={int(batch_rm_team_id.value)}" if batch_rm_team_id.value >= 0 else ""
    with mo.status.spinner(title="Fetching Fleet-maintained apps catalog..."):
        _status, _catalog = fleet("GET", f"/api/v1/fleet/software/fleet_maintained_apps{_team_param}")

    if _status != 200:
        mo.stop(True, fleet_error(f"Failed to fetch app catalog (status {_status}): {_catalog}. Fleet Premium required."))

    # Build lookup from name to app (filtered by platform)
    _catalog_apps = _catalog.get("fleet_maintained_apps", [])
    _app_lookup = {}
    for _app in _catalog_apps:
        # Filter by platform if specified
        if _platform_filter and _app.get("platform") != _platform_filter:
            continue
        _app_lookup[_app.get("name", "").lower()] = _app
        # Also index by identifier slug
        _slug = _app.get("name", "").lower().replace(" ", "-")
        _app_lookup[_slug] = _app

    # Match input names and remove
    _results = []
    _errors = []
    _success_count = 0

    with mo.status.spinner(title="Removing apps..."):
        for _name in _app_names:
            # Try to find in our static mapping first
            _mapped = FLEET_MAINTAINED_APPS.get(_name)
            if _mapped:
                _lookup_name = _mapped["name"].lower()
            else:
                _lookup_name = _name

            # Find in catalog
            _found_app = _app_lookup.get(_lookup_name)
            if not _found_app:
                # Try partial match
                for _cat_name, _cat_app in _app_lookup.items():
                    if _name in _cat_name or _cat_name in _name:
                        _found_app = _cat_app
                        break

            if not _found_app:
                _platform_note = f" for {batch_rm_platform.selected_key}" if _platform_filter else ""
                _errors.append(f"❌ **{_name}**: Not found in Fleet-maintained apps catalog{_platform_note}")
                continue

            # Check if it has a software_title_id (meaning it's added to the team)
            _title_id = _found_app.get("software_title_id")
            if not _title_id:
                _results.append(f"⏭️ **{_found_app['name']}**: Not currently added to this team")
                continue

            # Remove the app (team_id is required per API docs)
            _del_url = f"/api/v1/fleet/software/titles/{_title_id}/available_for_install?team_id={int(batch_rm_team_id.value)}"

            _del_status, _del_data = fleet("DELETE", _del_url)
            if _del_status in (200, 204):
                _results.append(f"✅ **{_found_app['name']}**: Removed successfully (was title ID: {_title_id})")
                _success_count += 1
            else:
                _err_msg = _del_data.get("message", str(_del_data)) if isinstance(_del_data, dict) else str(_del_data)
                _errors.append(f"❌ **{_found_app['name']}**: {_err_msg}")

    # Build result output
    _output_parts = []
    if _success_count > 0:
        _output_parts.append(fleet_success(f"Removed {_success_count} app(s) from team {int(batch_rm_team_id.value)}"))
    if _results:
        _output_parts.append(mo.md("\n".join(_results)))
    if _errors:
        _output_parts.append(mo.md("### Errors\n" + "\n".join(_errors)))

    _result = mo.vstack(_output_parts) if _output_parts else mo.md("No apps processed.")
    _result


@app.cell
def _(mo):
    mo.md("""
### Install / Uninstall Software

Install or uninstall software on a specific host.
""")


@app.cell
def _(mo):
    install_host_id = mo.ui.text(placeholder="Host ID", label="Host ID")
    install_title_id = mo.ui.text(placeholder="Software Title ID", label="Software Title ID")
    install_sw_btn = mo.ui.run_button(label="Install Software")
    uninstall_sw_btn = mo.ui.run_button(label="Uninstall Software", kind="danger")

    mo.hstack([install_host_id, install_title_id, install_sw_btn, uninstall_sw_btn], justify="start", gap=1)

    return install_host_id, install_title_id, install_sw_btn, uninstall_sw_btn


@app.cell
def _(mo, json, fleet, install_host_id, install_title_id, install_sw_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not install_sw_btn.value)
    mo.stop(not install_host_id.value, fleet_tip("Enter a Host ID."))
    mo.stop(not install_title_id.value, fleet_tip("Enter a Software Title ID."))

    _host_id = install_host_id.value.strip()
    _title_id = install_title_id.value.strip()
    _status, _data = fleet("POST", f"/api/v1/fleet/hosts/{_host_id}/software/{_title_id}/install")

    if _status in (200, 202):
        _formatted = json.dumps(_data, indent=2) if _data else "{}"
        _result = mo.vstack([
            fleet_success(f"Install queued for host {_host_id}, software {_title_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to install software (status {_status}): {_data}")

    _result


@app.cell
def _(mo, json, fleet, install_host_id, install_title_id, uninstall_sw_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not uninstall_sw_btn.value)
    mo.stop(not install_host_id.value, fleet_tip("Enter a Host ID."))
    mo.stop(not install_title_id.value, fleet_tip("Enter a Software Title ID."))

    _host_id = install_host_id.value.strip()
    _title_id = install_title_id.value.strip()
    _status, _data = fleet("POST", f"/api/v1/fleet/hosts/{_host_id}/software/{_title_id}/uninstall")

    if _status in (200, 202):
        _formatted = json.dumps(_data, indent=2) if _data else "{}"
        _result = mo.vstack([
            fleet_success(f"Uninstall queued for host {_host_id}, software {_title_id}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to uninstall software (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Get Software Install Result

Check the result of a software installation.
""")


@app.cell
def _(mo):
    install_uuid_input = mo.ui.text(placeholder="Install UUID", label="Install UUID", full_width=True)
    get_install_result_btn = mo.ui.run_button(label="Get Install Result")

    mo.hstack([install_uuid_input, get_install_result_btn], justify="start", gap=1)

    return install_uuid_input, get_install_result_btn


@app.cell
def _(mo, json, fleet, install_uuid_input, get_install_result_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not get_install_result_btn.value)
    mo.stop(not install_uuid_input.value, fleet_tip("Enter an Install UUID."))

    _uuid = install_uuid_input.value.strip()
    _status, _data = fleet("GET", f"/api/v1/fleet/software/install/{_uuid}/results")

    if _status == 200:
        _formatted = json.dumps(_data, indent=2)
        _result = mo.vstack([
            fleet_success(f"Install result for {_uuid}"),
            mo.md(f"```json\n{_formatted}\n```"),
        ])
    else:
        _result = fleet_error(f"Failed to get install result (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Download Software Package

Download the software package file for a given title.
""")


@app.cell
def _(mo):
    download_sw_title_id = mo.ui.text(placeholder="Software Title ID", label="Software Title ID")
    download_sw_team_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Team ID (0 = no team)")
    download_sw_btn = mo.ui.run_button(label="Download Software")

    mo.hstack([download_sw_title_id, download_sw_team_id, download_sw_btn], justify="start", gap=1)

    return download_sw_title_id, download_sw_team_id, download_sw_btn


@app.cell
def _(mo, httpx, fleet_url_input, api_token_input, download_sw_title_id, download_sw_team_id, download_sw_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not download_sw_btn.value)
    mo.stop(not download_sw_title_id.value, fleet_tip("Enter a Software Title ID."))

    _title_id = download_sw_title_id.value.strip()
    _team_param = f"&team_id={download_sw_team_id.value}" if download_sw_team_id.value > 0 else ""

    try:
        _response = httpx.get(
            f"{fleet_url_input.value}/api/v1/fleet/software/titles/{_title_id}/package?alt=media{_team_param}",
            headers={"Authorization": f"Bearer {api_token_input.value}"},
            timeout=300.0,
            follow_redirects=True,
        )
        _status = _response.status_code
    except Exception as e:
        _status = 0
        _response = None

    if _status == 200 and _response:
        _content_disp = _response.headers.get("content-disposition", "")
        _filename = "software_package"
        if "filename=" in _content_disp:
            _filename = _content_disp.split("filename=")[-1].strip('"')
        _size = len(_response.content)
        _result = mo.vstack([
            fleet_success(f"Downloaded: {_filename} ({_size:,} bytes)"),
            mo.download(_response.content, filename=_filename, label=f"Save {_filename}"),
        ])
    else:
        _result = fleet_error(f"Failed to download software (status {_status})")

    _result


@app.cell
def _(mo):
    mo.md("""
---

## Policies

Policies are yes/no questions you can ask about your hosts using osquery queries.
A passing host returns results for the policy's query; a failing host does not.
""")


@app.cell
def _(mo):
    mo.md("""
### List Policies

List global policies or team-specific policies.
""")


@app.cell
def _(mo):
    list_policies_scope = mo.ui.dropdown(
        options={"Global policies": "global", "Team policies": "team"},
        value="Global policies",
        label="Scope",
    )
    list_policies_team_id = mo.ui.number(start=1, stop=999999, step=1, value=1, label="Team ID (for team scope)")
    list_policies_query = mo.ui.text(placeholder="Search by name...", label="Search Query")
    list_policies_merge_inherited = mo.ui.checkbox(label="Merge inherited (team only)")
    list_policies_per_page = mo.ui.dropdown(
        options={"25": "25", "50": "50", "100": "100"},
        value="50",
        label="Per Page",
    )
    list_policies_page = mo.ui.number(start=0, stop=9999, step=1, value=0, label="Page")
    list_policies_btn = mo.ui.run_button(label="List Policies")

    mo.vstack([
        mo.hstack([list_policies_scope, list_policies_team_id, list_policies_query], gap=1),
        mo.hstack([list_policies_merge_inherited, list_policies_per_page, list_policies_page], gap=1),
        mo.hstack([list_policies_btn], justify="start"),
    ])

    return list_policies_scope, list_policies_team_id, list_policies_query, list_policies_merge_inherited, list_policies_per_page, list_policies_page, list_policies_btn


@app.cell
def _(mo, fleet, list_policies_scope, list_policies_team_id, list_policies_query, list_policies_merge_inherited, list_policies_per_page, list_policies_page, list_policies_btn, fleet_error, fleet_output):
    mo.stop(not list_policies_btn.value)

    _params = [f"per_page={list_policies_per_page.value}", f"page={list_policies_page.value}"]
    if list_policies_query.value:
        _params.append(f"query={list_policies_query.value}")

    if list_policies_scope.value == "global":
        _endpoint = "/api/v1/fleet/global/policies"
    else:
        _endpoint = f"/api/v1/fleet/teams/{int(list_policies_team_id.value)}/policies"
        if list_policies_merge_inherited.value:
            _params.append("merge_inherited=true")

    _query_str = "?" + "&".join(_params) if _params else ""

    with mo.status.spinner(title="Fetching policies..."):
        _status, _data = fleet("GET", f"{_endpoint}{_query_str}")

    if _status == 200:
        _policies = _data.get("policies", [])
        _inherited = _data.get("inherited_policies", [])
        if _policies:
            _result = fleet_output(f"Found {len(_policies)} policies", _policies)
            if _inherited:
                _result = mo.vstack([_result, fleet_output(f"Inherited policies: {len(_inherited)}", _inherited)])
        else:
            _result = mo.md("**No policies found.**")
    else:
        _result = fleet_error(f"Failed to list policies (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Get Policies Count

Get the count of policies (global or team).
""")


@app.cell
def _(mo):
    count_policies_scope = mo.ui.dropdown(
        options={"Global": "global", "Team": "team"},
        value="Global",
        label="Scope",
    )
    count_policies_team_id = mo.ui.number(start=1, stop=999999, step=1, value=1, label="Team ID")
    count_policies_query = mo.ui.text(placeholder="Search by name...", label="Search Query")
    count_policies_merge = mo.ui.checkbox(label="Include inherited (team only)")
    count_policies_btn = mo.ui.run_button(label="Get Count")

    mo.vstack([
        mo.hstack([count_policies_scope, count_policies_team_id, count_policies_query, count_policies_merge], gap=1),
        mo.hstack([count_policies_btn], justify="start"),
    ])

    return count_policies_scope, count_policies_team_id, count_policies_query, count_policies_merge, count_policies_btn


@app.cell
def _(mo, fleet, count_policies_scope, count_policies_team_id, count_policies_query, count_policies_merge, count_policies_btn, fleet_success, fleet_error):
    mo.stop(not count_policies_btn.value)

    _params = []
    if count_policies_query.value:
        _params.append(f"query={count_policies_query.value}")

    if count_policies_scope.value == "global":
        _endpoint = "/api/v1/fleet/policies/count"
    else:
        _endpoint = f"/api/v1/fleet/team/{int(count_policies_team_id.value)}/policies/count"
        if count_policies_merge.value:
            _params.append("merge_inherited=true")

    _query_str = "?" + "&".join(_params) if _params else ""
    _status, _data = fleet("GET", f"{_endpoint}{_query_str}")

    if _status == 200:
        _count = _data.get("count", 0)
        _result = fleet_success(f"Policy count: {_count}")
    else:
        _result = fleet_error(f"Failed to get count (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Get Policy

Get a specific policy by ID (global or team).
""")


@app.cell
def _(mo):
    get_policy_scope = mo.ui.dropdown(
        options={"Global": "global", "Team": "team"},
        value="Global",
        label="Scope",
    )
    get_policy_id = mo.ui.number(start=1, stop=999999, step=1, value=1, label="Policy ID")
    get_policy_team_id = mo.ui.number(start=1, stop=999999, step=1, value=1, label="Team ID (for team scope)")
    get_policy_btn = mo.ui.run_button(label="Get Policy")

    mo.vstack([
        mo.hstack([get_policy_scope, get_policy_id, get_policy_team_id], gap=1),
        mo.hstack([get_policy_btn], justify="start"),
    ])

    return get_policy_scope, get_policy_id, get_policy_team_id, get_policy_btn


@app.cell
def _(mo, fleet, get_policy_scope, get_policy_id, get_policy_team_id, get_policy_btn, fleet_error, fleet_output):
    mo.stop(not get_policy_btn.value)

    if get_policy_scope.value == "global":
        _endpoint = f"/api/v1/fleet/global/policies/{int(get_policy_id.value)}"
    else:
        _endpoint = f"/api/v1/fleet/teams/{int(get_policy_team_id.value)}/policies/{int(get_policy_id.value)}"

    _status, _data = fleet("GET", _endpoint)

    if _status == 200:
        _policy = _data.get("policy", {})
        _result = fleet_output(f"Policy: {_policy.get('name', 'Unknown')}", _policy)
    else:
        _result = fleet_error(f"Failed to get policy (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Create Policy

Create a new global or team policy.
""")


@app.cell
def _(mo):
    create_policy_scope = mo.ui.dropdown(
        options={"Global": "global", "Team": "team"},
        value="Global",
        label="Scope",
    )
    create_policy_team_id = mo.ui.number(start=1, stop=999999, step=1, value=1, label="Team ID (for team scope)")
    create_policy_name = mo.ui.text(placeholder="Policy name", label="Name", full_width=True)
    create_policy_query = mo.ui.text_area(placeholder="SELECT 1 FROM ... WHERE ...;", label="Query (SQL)", rows=3, full_width=True)
    create_policy_description = mo.ui.text_area(placeholder="What this policy checks", label="Description", rows=2, full_width=True)
    create_policy_resolution = mo.ui.text_area(placeholder="Steps to resolve if failing", label="Resolution", rows=2, full_width=True)
    create_policy_platform = mo.ui.dropdown(
        options={"All platforms": "", "macOS": "darwin", "Windows": "windows", "Linux": "linux", "macOS & Windows": "darwin,windows", "macOS & Linux": "darwin,linux"},
        value="All platforms",
        label="Platform",
    )
    create_policy_critical = mo.ui.checkbox(label="Critical (high impact)")
    create_policy_software_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Software Title ID (0 = none, team only)")
    create_policy_script_id = mo.ui.number(start=0, stop=999999, step=1, value=0, label="Script ID (0 = none, team only)")
    create_policy_btn = mo.ui.run_button(label="Create Policy")

    mo.vstack([
        mo.hstack([create_policy_scope, create_policy_team_id, create_policy_platform, create_policy_critical], gap=1),
        create_policy_name,
        create_policy_query,
        create_policy_description,
        create_policy_resolution,
        mo.hstack([create_policy_software_id, create_policy_script_id], gap=1),
        mo.hstack([create_policy_btn], justify="start"),
    ])

    return create_policy_scope, create_policy_team_id, create_policy_name, create_policy_query, create_policy_description, create_policy_resolution, create_policy_platform, create_policy_critical, create_policy_software_id, create_policy_script_id, create_policy_btn


@app.cell
def _(mo, fleet, create_policy_scope, create_policy_team_id, create_policy_name, create_policy_query, create_policy_description, create_policy_resolution, create_policy_platform, create_policy_critical, create_policy_software_id, create_policy_script_id, create_policy_btn, fleet_error, fleet_output, fleet_tip):
    mo.stop(not create_policy_btn.value)
    mo.stop(not create_policy_name.value, fleet_tip("Enter a policy name."))
    mo.stop(not create_policy_query.value, fleet_tip("Enter a policy query."))

    _payload = {
        "name": create_policy_name.value,
        "query": create_policy_query.value,
    }
    if create_policy_description.value:
        _payload["description"] = create_policy_description.value
    if create_policy_resolution.value:
        _payload["resolution"] = create_policy_resolution.value
    if create_policy_platform.value:
        _payload["platform"] = create_policy_platform.value
    if create_policy_critical.value:
        _payload["critical"] = True

    if create_policy_scope.value == "global":
        _endpoint = "/api/v1/fleet/global/policies"
    else:
        _endpoint = f"/api/v1/fleet/teams/{int(create_policy_team_id.value)}/policies"
        if create_policy_software_id.value > 0:
            _payload["software_title_id"] = int(create_policy_software_id.value)
        if create_policy_script_id.value > 0:
            _payload["script_id"] = int(create_policy_script_id.value)

    _status, _data = fleet("POST", _endpoint, json_data=_payload)

    if _status == 200:
        _policy = _data.get("policy", {})
        _result = fleet_output(f"Created policy: {_policy.get('name', 'Unknown')} (ID: {_policy.get('id', 'N/A')})", _policy)
    else:
        _result = fleet_error(f"Failed to create policy (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Update Policy

Update an existing global or team policy.
""")


@app.cell
def _(mo):
    update_policy_scope = mo.ui.dropdown(
        options={"Global": "global", "Team": "team"},
        value="Global",
        label="Scope",
    )
    update_policy_id = mo.ui.number(start=1, stop=999999, step=1, value=1, label="Policy ID")
    update_policy_team_id = mo.ui.number(start=1, stop=999999, step=1, value=1, label="Team ID (for team scope)")
    update_policy_name = mo.ui.text(placeholder="Policy name (leave empty to keep)", label="Name", full_width=True)
    update_policy_query = mo.ui.text_area(placeholder="SQL query (leave empty to keep)", label="Query", rows=3, full_width=True)
    update_policy_description = mo.ui.text_area(placeholder="Description (leave empty to keep)", label="Description", rows=2, full_width=True)
    update_policy_resolution = mo.ui.text_area(placeholder="Resolution (leave empty to keep)", label="Resolution", rows=2, full_width=True)
    update_policy_platform = mo.ui.dropdown(
        options={"Keep existing": "", "All platforms": "all", "macOS": "darwin", "Windows": "windows", "Linux": "linux"},
        value="Keep existing",
        label="Platform",
    )
    update_policy_critical = mo.ui.dropdown(
        options={"Keep existing": "", "Yes": "true", "No": "false"},
        value="Keep existing",
        label="Critical",
    )
    update_policy_calendar = mo.ui.dropdown(
        options={"Keep existing": "", "Enable": "true", "Disable": "false"},
        value="Keep existing",
        label="Calendar Events (team)",
    )
    update_policy_conditional = mo.ui.dropdown(
        options={"Keep existing": "", "Enable": "true", "Disable": "false"},
        value="Keep existing",
        label="Conditional Access (team)",
    )
    update_policy_btn = mo.ui.run_button(label="Update Policy")

    mo.vstack([
        mo.hstack([update_policy_scope, update_policy_id, update_policy_team_id], gap=1),
        update_policy_name,
        update_policy_query,
        update_policy_description,
        update_policy_resolution,
        mo.hstack([update_policy_platform, update_policy_critical, update_policy_calendar, update_policy_conditional], gap=1),
        mo.hstack([update_policy_btn], justify="start"),
    ])

    return update_policy_scope, update_policy_id, update_policy_team_id, update_policy_name, update_policy_query, update_policy_description, update_policy_resolution, update_policy_platform, update_policy_critical, update_policy_calendar, update_policy_conditional, update_policy_btn


@app.cell
def _(mo, fleet, update_policy_scope, update_policy_id, update_policy_team_id, update_policy_name, update_policy_query, update_policy_description, update_policy_resolution, update_policy_platform, update_policy_critical, update_policy_calendar, update_policy_conditional, update_policy_btn, fleet_error, fleet_output):
    mo.stop(not update_policy_btn.value)

    _payload = {}
    if update_policy_name.value:
        _payload["name"] = update_policy_name.value
    if update_policy_query.value:
        _payload["query"] = update_policy_query.value
    if update_policy_description.value:
        _payload["description"] = update_policy_description.value
    if update_policy_resolution.value:
        _payload["resolution"] = update_policy_resolution.value
    if update_policy_platform.value:
        _payload["platform"] = "" if update_policy_platform.value == "all" else update_policy_platform.value
    if update_policy_critical.value:
        _payload["critical"] = update_policy_critical.value == "true"

    if update_policy_scope.value == "global":
        _endpoint = f"/api/v1/fleet/global/policies/{int(update_policy_id.value)}"
    else:
        _endpoint = f"/api/v1/fleet/teams/{int(update_policy_team_id.value)}/policies/{int(update_policy_id.value)}"
        if update_policy_calendar.value:
            _payload["calendar_events_enabled"] = update_policy_calendar.value == "true"
        if update_policy_conditional.value:
            _payload["conditional_access_enabled"] = update_policy_conditional.value == "true"

    _status, _data = fleet("PATCH", _endpoint, json_data=_payload)

    if _status == 200:
        _policy = _data.get("policy", {})
        _result = fleet_output(f"Updated policy: {_policy.get('name', 'Unknown')}", _policy)
    else:
        _result = fleet_error(f"Failed to update policy (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Delete Policies

Delete one or more policies (global or team).
""")


@app.cell
def _(mo):
    delete_policies_scope = mo.ui.dropdown(
        options={"Global": "global", "Team": "team"},
        value="Global",
        label="Scope",
    )
    delete_policies_team_id = mo.ui.number(start=1, stop=999999, step=1, value=1, label="Team ID (for team scope)")
    delete_policies_ids = mo.ui.text(placeholder="1, 2, 3", label="Policy IDs (comma-separated)", full_width=True)
    delete_policies_btn = mo.ui.run_button(label="Delete Policies")

    mo.vstack([
        mo.hstack([delete_policies_scope, delete_policies_team_id], gap=1),
        delete_policies_ids,
        mo.hstack([delete_policies_btn], justify="start"),
    ])

    return delete_policies_scope, delete_policies_team_id, delete_policies_ids, delete_policies_btn


@app.cell
def _(mo, fleet, delete_policies_scope, delete_policies_team_id, delete_policies_ids, delete_policies_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not delete_policies_btn.value)
    mo.stop(not delete_policies_ids.value, fleet_tip("Enter policy IDs to delete."))

    _ids = [int(x.strip()) for x in delete_policies_ids.value.split(",") if x.strip().isdigit()]
    if not _ids:
        mo.stop(True, fleet_tip("Enter valid policy IDs (numbers)."))

    _payload = {"ids": _ids}

    if delete_policies_scope.value == "global":
        _endpoint = "/api/v1/fleet/global/policies/delete"
    else:
        _endpoint = f"/api/v1/fleet/teams/{int(delete_policies_team_id.value)}/policies/delete"

    _status, _data = fleet("POST", _endpoint, json_data=_payload)

    if _status == 200:
        _deleted = _data.get("deleted", 0)
        _result = fleet_success(f"Deleted {_deleted} policy(ies)")
    else:
        _result = fleet_error(f"Failed to delete policies (status {_status}): {_data}")

    _result


@app.cell
def _(mo):
    mo.md("""
### Reset Policy Automations

Reset automation status for all hosts failing the specified policies. On the next automation run, any failing host will be considered newly failing.

**Note:** Currently only resets ticket and webhook automations. Team IDs filter requires Fleet Premium.
""")


@app.cell
def _(mo):
    reset_auto_policy_ids = mo.ui.text(placeholder="1, 2, 3", label="Policy IDs (comma-separated)", full_width=True)
    reset_auto_team_ids = mo.ui.text(placeholder="1, 2 (Premium, must be > 0)", label="Team IDs (comma-separated, optional)", full_width=True)
    reset_auto_btn = mo.ui.run_button(label="Reset Automations")

    mo.vstack([
        reset_auto_policy_ids,
        reset_auto_team_ids,
        mo.hstack([reset_auto_btn], justify="start"),
    ])

    return reset_auto_policy_ids, reset_auto_team_ids, reset_auto_btn


@app.cell
def _(mo, fleet, reset_auto_policy_ids, reset_auto_team_ids, reset_auto_btn, fleet_success, fleet_error, fleet_tip):
    mo.stop(not reset_auto_btn.value)

    _payload = {}

    if reset_auto_policy_ids.value:
        # Policy IDs must be > 0
        _policy_ids = [int(x.strip()) for x in reset_auto_policy_ids.value.split(",") if x.strip().isdigit() and int(x.strip()) > 0]
        if _policy_ids:
            _payload["policy_ids"] = _policy_ids

    if reset_auto_team_ids.value:
        # Team IDs must be > 0 (0 is not valid for this endpoint)
        _team_ids = [int(x.strip()) for x in reset_auto_team_ids.value.split(",") if x.strip().isdigit() and int(x.strip()) > 0]
        if _team_ids:
            _payload["team_ids"] = _team_ids

    if not _payload:
        mo.stop(True, fleet_tip("Enter valid policy IDs (> 0). Team IDs filter requires Premium."))

    _status, _data = fleet("POST", "/api/v1/fleet/automations/reset", json_data=_payload)

    if _status == 200:
        _result = fleet_success("Policy automations reset successfully")
    else:
        _result = fleet_error(f"Failed to reset automations (status {_status}): {_data}")

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
