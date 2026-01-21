#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "httpx",
#     "pandas",
# ]
# description = """
# Fleet Demo Notebook - API testing and GitOps training essentials.
# Combines Fleet API exploration with GitHub repository secrets setup.
# Copyright (c) 2026 Henry Stamerjohann, for Fleet Device Management
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
    import subprocess
    import uuid
    import httpx
    import pandas as pd
    import marimo as mo
    from pathlib import Path

    return mo, base64, json, os, subprocess, uuid, httpx, pd, Path


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

    /* Lists */
    ul, ol {
        margin-bottom: 24px !important;
        padding-left: 24px !important;
    }

    li {
        margin-bottom: 8px !important;
        line-height: 150% !important;
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
        """Create collapsible output with JSON data."""
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
# Fleet Demo Notebook

<p class="meta">API Testing + GitOps Training Essentials</p>

<div style="text-align: center; margin: 2rem 0; padding: 2rem 0; border-bottom: 1px solid var(--fleet-black-10);">
    <svg width="200" height="82" viewBox="0 0 800 327" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-bottom: 1rem;">
        <path d="M244.218 208.833C234.942 208.833 226.284 208.833 217.352 208.833C217.352 199.348 217.352 190.07 217.352 180.447C226.147 180.447 234.873 180.447 244.15 180.447C244.15 177.47 244.15 174.908 244.15 172.277C244.15 161.477 244.699 150.676 247.997 140.291C254.937 118.344 269.917 106.158 292.386 103.112C295.34 102.697 298.295 102.42 301.25 102.42C324.681 102.351 348.181 102.351 371.612 102.351C372.574 102.351 373.467 102.42 374.635 102.489C374.635 176.223 374.635 251.715 374.635 325.588C363.229 325.588 351.822 325.588 340.072 325.588C340.072 263.069 340.072 198.655 340.072 136.414C339.523 135.929 339.317 135.652 339.11 135.652C327.017 135.791 314.786 135.237 302.761 136.275C289.019 137.452 281.323 145.76 279.949 159.607C279.33 166.254 279.811 172.969 279.811 180.101C290.05 180.101 300.357 180.101 310.938 180.101C310.938 189.793 310.938 199.071 310.938 208.694C300.563 208.694 290.256 208.694 279.605 208.694C279.605 247.188 279.605 287.232 279.605 325.588C267.649 325.588 256.106 325.588 244.218 325.588C244.218 287.44 244.218 247.396 244.218 208.833Z" fill="#192147"/>
        <path d="M503.166 275.501C511.461 281.649 519.269 287.454 527.355 293.397C521.639 302.344 514.11 309.038 505.187 314.229C476.258 331.236 437.43 328.982 412.474 308.56C396.929 295.855 388.913 279.258 386.961 259.655C385.149 241.555 388.216 224.48 398.602 209.112C411.847 189.441 431.017 179.264 454.788 177.146C475.491 175.302 494.383 180.015 510.555 193.266C524.985 205.014 533.001 220.382 534.884 238.55C535.72 246.61 535.023 254.806 535.023 263.275C497.868 263.275 460.853 263.275 423.349 263.275C425.998 275.433 432.202 284.312 443.356 289.435C463.083 298.451 487.76 293.26 502.12 277.072C502.469 276.663 502.748 276.116 503.166 275.501ZM499.89 238.755C499.402 220.928 482.044 207.404 461.201 207.951C437.918 208.565 425.231 223.728 423.837 238.755C449.072 238.755 474.376 238.755 499.89 238.755Z" fill="#192147"/>
        <path d="M690.882 263.452C652.915 263.452 615.991 263.452 579.067 263.452C580.736 277.262 592.279 289.294 606.743 292.234C627.117 296.405 644.64 291.687 658.826 275.689C666.614 281.501 674.471 287.312 682.538 293.328C677.74 301.122 671.342 307.07 663.971 312.061C633.723 332.297 589.776 329.563 564.603 305.634C547.358 289.226 540.961 268.716 542.212 245.608C543.256 226.944 550.001 210.467 563.769 197.409C580.04 181.958 599.858 175.737 622.18 176.899C643.736 178.061 661.816 186.265 675.375 203.015C686.64 216.962 691.021 233.165 690.882 250.735C690.882 254.837 690.882 258.94 690.882 263.452ZM578.997 238.566C604.517 238.566 629.829 238.566 655.14 238.566C654.445 225.235 643.736 209.168 619.885 207.869C598.815 206.775 581.779 219.218 578.997 238.566Z" fill="#192147"/>
        <path d="M798.97 292.08C791.411 292.08 783.784 292.08 776.295 291.388C762.552 290.211 754.856 281.903 753.482 268.056C752.863 261.409 753.345 214.192 753.345 207.13C763.583 207.13 773.89 207.13 784.471 207.13C784.471 197.437 784.471 188.16 784.471 178.536C774.096 178.536 763.789 178.536 753.138 178.536C753.138 140.042 753.138 140.706 753.138 102.351C741.182 102.351 729.639 102.351 717.751 102.351C717.751 140.568 717.751 139.973 717.751 178.536C708.475 178.536 699.817 178.536 690.885 178.536C690.885 188.021 690.885 197.299 690.885 206.922C699.68 206.922 708.406 206.922 717.683 206.922C717.683 209.899 717.683 252.963 717.683 255.525C717.683 266.325 718.232 277.126 721.531 287.511C728.471 309.458 743.45 321.643 765.919 324.689C768.874 325.105 771.828 325.382 774.783 325.382C782.822 325.382 790.862 325.382 798.97 325.382V292.08Z" fill="#192147"/>
        <path d="M27.9379 54.9974C42.8822 54.9974 54.997 42.8827 54.997 27.9384C54.997 12.9941 42.8822 0.879395 27.9379 0.879395C12.9936 0.879395 0.878906 12.9941 0.878906 27.9384C0.878906 42.8827 12.9936 54.9974 27.9379 54.9974Z" fill="#63C740"/>
        <path d="M109.116 54.9974C124.06 54.9974 136.175 42.8827 136.175 27.9384C136.175 12.9941 124.06 0.879395 109.116 0.879395C94.1714 0.879395 82.0566 12.9941 82.0566 27.9384C82.0566 42.8827 94.1714 54.9974 109.116 54.9974Z" fill="#5CABDF"/>
        <path d="M190.291 54.9974C205.236 54.9974 217.35 42.8827 217.35 27.9384C217.35 12.9941 205.236 0.879395 190.291 0.879395C175.347 0.879395 163.232 12.9941 163.232 27.9384C163.232 42.8827 175.347 54.9974 190.291 54.9974Z" fill="#D66C7B"/>
        <path d="M27.9379 136.175C42.8822 136.175 54.997 124.06 54.997 109.116C54.997 94.1714 42.8822 82.0566 27.9379 82.0566C12.9936 82.0566 0.878906 94.1714 0.878906 109.116C0.878906 124.06 12.9936 136.175 27.9379 136.175Z" fill="#C98DEF"/>
        <path d="M109.116 136.175C124.06 136.175 136.175 124.06 136.175 109.116C136.175 94.1714 124.06 82.0566 109.116 82.0566C94.1714 82.0566 82.0566 94.1714 82.0566 109.116C82.0566 124.06 94.1714 136.175 109.116 136.175Z" fill="#FAA669"/>
        <path d="M27.9379 217.351C42.8822 217.351 54.997 205.237 54.997 190.292C54.997 175.348 42.8822 163.233 27.9379 163.233C12.9936 163.233 0.878906 175.348 0.878906 190.292C0.878906 205.237 12.9936 217.351 27.9379 217.351Z" fill="#3AEFC4"/>
    </svg>
</div>

This notebook combines:
- **Fleet API Testing** - Connect and explore your Fleet instance
- **GitOps Training** - Set up GitHub repository secrets for automation

---
""")


# =============================================================================
# SECTION 1: FLEET API CONNECTION
# =============================================================================


@app.cell
def _(mo):
    mo.md("""
## 1. Fleet API Connection

Connect to your Fleet instance and test the API.
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
                return ""
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return ""

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

    # Try to load from .env file
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
### Configuration

Enter your Fleet instance details:

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
def _(mo, httpx, fleet_url_input, api_token_input, test_connection_btn, fleet_success, fleet_error):
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


# =============================================================================
# SECTION 2: QUICK API ENDPOINTS
# =============================================================================


@app.cell
def _(mo):
    mo.md("""
---

### Quick API Endpoints

Test common Fleet API endpoints:
""")


@app.cell
def _(mo):
    endpoint_select = mo.ui.dropdown(
        options={
            "Get Current User": "/api/v1/fleet/me",
            "Get Version": "/api/v1/fleet/version",
            "Get Config": "/api/v1/fleet/config",
            "List Hosts": "/api/v1/fleet/hosts",
            "List Teams": "/api/v1/fleet/teams",
            "List Policies": "/api/v1/fleet/policies",
            "List Queries": "/api/v1/fleet/queries",
            "List Labels": "/api/v1/fleet/labels",
        },
        value="/api/v1/fleet/me",
        label="Select Endpoint",
    )

    run_endpoint_btn = mo.ui.run_button(label="Query Endpoint")

    mo.hstack([endpoint_select, run_endpoint_btn], justify="start", gap=1)

    return endpoint_select, run_endpoint_btn


@app.cell
def _(mo, httpx, json, fleet_url_input, api_token_input, endpoint_select, run_endpoint_btn, fleet_success, fleet_error):
    mo.stop(not run_endpoint_btn.value)

    _url = fleet_url_input.value.rstrip("/")
    _token = api_token_input.value
    _endpoint = endpoint_select.value

    if not _url or not _token:
        mo.stop(True, fleet_error("Please configure Fleet URL and API Token above."))

    try:
        _response = httpx.get(
            f"{_url}{_endpoint}",
            headers={"Authorization": f"Bearer {_token}"},
            timeout=30.0,
        )

        if _response.status_code == 200:
            _data = _response.json()
            _formatted = json.dumps(_data, indent=2)
            _result = mo.vstack([
                fleet_success(f"GET {_endpoint}"),
                mo.md(f"```json\n{_formatted[:5000]}{'...' if len(_formatted) > 5000 else ''}\n```"),
            ])
        else:
            _result = fleet_error(f"Status {_response.status_code}: {_response.text[:500]}")

    except Exception as e:
        _result = fleet_error(f"Error: {str(e)}")

    _result


# =============================================================================
# SECTION 3: GITOPS TRAINING - GITHUB SECRETS SETUP
# =============================================================================


@app.cell
def _(mo):
    mo.md("""
---

## 2. GitOps Training: GitHub Repository Secrets

Set up your GitHub repository with the required secrets for Fleet GitOps automation.

### Required Repository Secrets

To connect your GitHub repository to Fleet, you need to add these secrets in:
`Settings > Secrets and variables > Actions > Repository secrets`
""")


@app.cell
def _(mo, fleet_url_input, api_token_input):
    _url = fleet_url_input.value.rstrip("/") if fleet_url_input.value else "https://fleet-xxxx.onrender.com"
    _token = api_token_input.value if api_token_input.value else ""
    _token_preview = f"{_token[:12]}..." if len(_token) > 12 else "(not set)"

    mo.md(f"""
### Step 1: Add Fleet URL Secret

1. Click **"New repository secret"** in GitHub
2. Name: `FLEET_URL`
3. Value: `{_url}`

### Step 2: Add Fleet API Token Secret

1. Click **"New repository secret"**
2. Name: `FLEET_API_TOKEN`
3. Value: `{_token_preview}` (copy from the field above)
""")


@app.cell
def _(mo):
    mo.md("""
### Step 3: Generate Enroll Secrets

Use the UUID generator below to create unique enroll secrets for each team:
""")


@app.cell
def _(mo):
    generate_uuid_button = mo.ui.button(
        label="Generate New UUIDs",
        kind="success",
    )
    generate_uuid_button
    return (generate_uuid_button,)


@app.cell
def _(mo, uuid, generate_uuid_button):
    _ = generate_uuid_button.value

    # Generate 5 UUIDs
    _uuids = [str(uuid.uuid4()) for _ in range(5)]

    mo.md(f"""
### Generated Enroll Secrets

Copy these UUIDs to use as your GitHub repository secrets:

| Secret Name | Value |
|-------------|-------|
| `FLEET_GLOBAL_ENROLL_SECRET` | `{_uuids[0]}` |
| `FLEET_ENGINEERING_ENROLL_SECRET` | `{_uuids[1]}` |
| `FLEET_NEW_HIRES_ENROLL_SECRET` | `{_uuids[2]}` |
| `FLEET_WORKSTATIONS_ENROLL_SECRET` | `{_uuids[3]}` |
| `FLEET_WORKSTATIONS_CANARY_ENROLL_SECRET` | `{_uuids[4]}` |

### Add Each Secret to GitHub

For each secret above:
1. Go to your GitHub repo > **Settings** > **Secrets and variables** > **Actions**
2. Click **"New repository secret"**
3. Enter the **Secret Name** (e.g., `FLEET_GLOBAL_ENROLL_SECRET`)
4. Paste the **UUID value**
5. Click **"Add secret"**
""")


@app.cell
def _(mo):
    mo.md("""
### Step 4: Update workflow.yml

Add the enroll secrets as environment variables in `.github/workflows/workflow.yml`:

```yaml
env:
  FLEET_URL: ${{ secrets.FLEET_URL }}
  FLEET_API_TOKEN: ${{ secrets.FLEET_API_TOKEN }}
  FLEET_GLOBAL_ENROLL_SECRET: ${{ secrets.FLEET_GLOBAL_ENROLL_SECRET }}
  FLEET_ENGINEERING_ENROLL_SECRET: ${{ secrets.FLEET_ENGINEERING_ENROLL_SECRET }}
  FLEET_NEW_HIRES_ENROLL_SECRET: ${{ secrets.FLEET_NEW_HIRES_ENROLL_SECRET }}
  FLEET_WORKSTATIONS_ENROLL_SECRET: ${{ secrets.FLEET_WORKSTATIONS_ENROLL_SECRET }}
  FLEET_WORKSTATIONS_CANARY_ENROLL_SECRET: ${{ secrets.FLEET_WORKSTATIONS_CANARY_ENROLL_SECRET }}
```
""")


# =============================================================================
# SECTION 4: COPY SECRETS TO GITHUB (AUTOMATED)
# =============================================================================


@app.cell
def _(mo):
    mo.md("""
---

## 3. Automated Secret Setup (Optional)

Use the GitHub CLI (`gh`) to automatically add secrets to your repository.
""")


@app.cell
def _(mo):
    github_repo_input = mo.ui.text(
        placeholder="owner/repo-name",
        label="GitHub Repository (owner/repo)",
        full_width=True,
    )

    mo.md(f"""
### Target Repository

Enter your GitHub repository in the format `owner/repo-name`:

{github_repo_input}
""")

    return (github_repo_input,)


@app.cell
def _(mo, fleet_url_input, api_token_input, github_repo_input, uuid, fleet_tip):
    _repo = github_repo_input.value.strip() if github_repo_input.value else "owner/repo-name"
    _url = fleet_url_input.value.rstrip("/") if fleet_url_input.value else "https://fleet-xxxx.onrender.com"
    _token = api_token_input.value if api_token_input.value else "YOUR_API_TOKEN"

    # Generate consistent UUIDs for the commands
    _uuid1 = str(uuid.uuid4())
    _uuid2 = str(uuid.uuid4())
    _uuid3 = str(uuid.uuid4())
    _uuid4 = str(uuid.uuid4())
    _uuid5 = str(uuid.uuid4())

    # Mask the token for display
    _token_masked = f"{_token[:8]}..." if len(_token) > 8 else "<YOUR_API_TOKEN>"

    _commands = f"""# First, authenticate with GitHub CLI (if not already done)
gh auth login

# Set Fleet URL
gh secret set FLEET_URL --repo {_repo} --body "{_url}"

# Set Fleet API Token (replace with your actual token)
gh secret set FLEET_API_TOKEN --repo {_repo} --body "{_token_masked}"

# Set Enroll Secrets (using generated UUIDs)
gh secret set FLEET_GLOBAL_ENROLL_SECRET --repo {_repo} --body "{_uuid1}"
gh secret set FLEET_ENGINEERING_ENROLL_SECRET --repo {_repo} --body "{_uuid2}"
gh secret set FLEET_NEW_HIRES_ENROLL_SECRET --repo {_repo} --body "{_uuid3}"
gh secret set FLEET_WORKSTATIONS_ENROLL_SECRET --repo {_repo} --body "{_uuid4}"
gh secret set FLEET_WORKSTATIONS_CANARY_ENROLL_SECRET --repo {_repo} --body "{_uuid5}"

echo "All secrets have been set for {_repo}"
"""

    mo.vstack([
        fleet_tip("Copy and run these commands in your terminal to set all secrets at once."),
        mo.md(f"""
### GitHub CLI Commands

```bash
{_commands}
```
"""),
    ])


@app.cell
def _(mo):
    run_gh_setup_btn = mo.ui.run_button(label="Run GitHub CLI Setup (requires gh auth)")

    mo.hstack([run_gh_setup_btn], justify="start")

    return (run_gh_setup_btn,)


@app.cell
def _(mo, subprocess, uuid, fleet_url_input, api_token_input, github_repo_input, run_gh_setup_btn, fleet_success, fleet_error, fleet_warning):
    mo.stop(not run_gh_setup_btn.value)

    _repo = github_repo_input.value.strip() if github_repo_input.value else ""
    _url = fleet_url_input.value.rstrip("/") if fleet_url_input.value else ""
    _token = api_token_input.value if api_token_input.value else ""

    if not _repo:
        mo.stop(True, fleet_warning("Please enter your GitHub repository (owner/repo) above."))

    if not _url or not _token:
        mo.stop(True, fleet_warning("Please configure Fleet URL and API Token in section 1."))

    # Generate UUIDs for enroll secrets
    _secrets = {
        "FLEET_URL": _url,
        "FLEET_API_TOKEN": _token,
        "FLEET_GLOBAL_ENROLL_SECRET": str(uuid.uuid4()),
        "FLEET_ENGINEERING_ENROLL_SECRET": str(uuid.uuid4()),
        "FLEET_NEW_HIRES_ENROLL_SECRET": str(uuid.uuid4()),
        "FLEET_WORKSTATIONS_ENROLL_SECRET": str(uuid.uuid4()),
        "FLEET_WORKSTATIONS_CANARY_ENROLL_SECRET": str(uuid.uuid4()),
    }

    _results = []
    _all_success = True

    for _name, _value in _secrets.items():
        try:
            _proc = subprocess.run(
                ["gh", "secret", "set", _name, "--repo", _repo, "--body", _value],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if _proc.returncode == 0:
                _results.append(f"- `{_name}`: Set successfully")
            else:
                _results.append(f"- `{_name}`: Failed - {_proc.stderr[:100]}")
                _all_success = False
        except FileNotFoundError:
            mo.stop(True, fleet_error("GitHub CLI (`gh`) not found. Please install it first: https://cli.github.com/"))
        except Exception as e:
            _results.append(f"- `{_name}`: Error - {str(e)[:100]}")
            _all_success = False

    if _all_success:
        _header = fleet_success(f"All secrets set for {_repo}")
    else:
        _header = fleet_error("Some secrets failed to set")

    mo.vstack([
        _header,
        mo.md("\n".join(_results)),
    ])


# =============================================================================
# SECTION 5: VERIFICATION
# =============================================================================


@app.cell
def _(mo):
    mo.md("""
---

## 4. Verification Checklist

Verify your GitOps setup is complete:
""")


@app.cell
def _(mo, github_repo_input):
    _repo = github_repo_input.value.strip() if github_repo_input.value else "owner/repo-name"

    mo.md(f"""
### Repository Secrets Checklist

- [ ] `FLEET_URL` - Your Fleet instance URL
- [ ] `FLEET_API_TOKEN` - Your Fleet API token
- [ ] `FLEET_GLOBAL_ENROLL_SECRET` - For "No Team" devices
- [ ] `FLEET_ENGINEERING_ENROLL_SECRET` - For Engineering team
- [ ] `FLEET_NEW_HIRES_ENROLL_SECRET` - For New Hires team
- [ ] `FLEET_WORKSTATIONS_ENROLL_SECRET` - For Workstations team
- [ ] `FLEET_WORKSTATIONS_CANARY_ENROLL_SECRET` - For Canary team

### Verify in GitHub

1. Go to: https://github.com/{_repo}/settings/secrets/actions
2. Confirm all 7 secrets are listed
3. Push a commit to trigger the workflow
4. Check: https://github.com/{_repo}/actions for workflow status
""")


@app.cell
def _(mo, fleet_tip):
    mo.vstack([
        fleet_tip("Your Fleet GitOps setup is ready! Push changes to your repository to trigger automated deployments."),
        mo.md("""
### Resources

- [Fleet Documentation](https://fleetdm.com/docs)
- [Fleet GitOps Guide](https://fleetdm.com/docs/using-fleet/gitops)
- [fleetctl CLI Guide](https://fleetdm.com/guides/fleetctl)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
"""),
    ])


# Self-contained: run with `uv run fleet-demo-notebook.py`
if __name__ == "__main__":
    import os
    import sys

    os.execvp(
        "marimo",
        ["marimo", "run", sys.argv[0], "--host", "127.0.0.1", "--port", "2718"],
    )
