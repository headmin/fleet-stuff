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
    import json
    import os
    import uuid
    import httpx
    import pandas as pd
    import marimo as mo

    return mo, json, os, uuid, httpx, pd


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
def _(mo):
    fleet_url_input = mo.ui.text(
        placeholder="https://fleet-xxxx.onrender.com",
        label="Fleet Instance URL",
        value="",
        full_width=True,
    )

    api_token_input = mo.ui.text(
        placeholder="Your Fleet API Token",
        label="Fleet API Token",
        value="",
        kind="password",
        full_width=True,
    )

    mo.md(f"""
## Configuration

Enter your Fleet instance details:

{fleet_url_input}

{api_token_input}
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
            _formatted = json.dumps(_data, indent=2)

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

## Labels CRUD Operations

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

## Common API Endpoints Reference

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
