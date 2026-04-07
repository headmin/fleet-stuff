# fleet-api

**Expert at using and scripting against the Fleet REST API for device management automation.**

## Purpose

This skill helps you interact with Fleet's REST API for building automations, integrations, and custom tooling around Fleet device management.

## When to Use

- Calling Fleet API endpoints programmatically
- Building integrations or webhooks with Fleet
- Automating host, policy, software, or profile management
- Scripting Fleet operations (bulk updates, reporting, etc.)
- Using `fleetctl` CLI for common operations
- Understanding API authentication, pagination, and error handling

## How It Works

The skill follows a structured workflow:

1. **Read Context** - Loads `learnings.md` for API gotchas and patterns
2. **Check fleetctl** - Prefers `fleetctl` CLI over raw API when available
3. **Determine Endpoint** - Finds the correct API endpoint from reference index
4. **Handle Authentication** - Manages Bearer tokens, API-only users, SSO limitations
5. **Execute Request** - Provides complete curl examples or fleetctl commands
6. **Capture Learnings** - Updates `learnings.md` with API quirks and discoveries

## Key Features

### Tool Preference
- **Uses fleetctl first** - For GitOps apply, common queries, authentication
- **Falls back to raw API** - For webhooks, integrations, specific endpoints

### Authentication Handling
- Bearer token authentication (`Authorization: Bearer <token>`)
- API-only user creation (`fleetctl user create --api-only`)
- SSO/MFA limitations (must get token from UI, not login endpoint)

### Common Patterns
- Pagination for large datasets
- Populate flags to reduce API calls
- Batch operations for multi-host actions
- CSV exports for bulk reporting
- Async MDM command handling

## File Structure

```
fleet-api/
├── SKILL.md                    # Main skill instructions
├── README.md                   # This file
├── learnings.md                # API gotchas and patterns
├── references/
│   └── endpoint-index.md       # Searchable endpoint reference
└── scripts/
    ├── update-endpoint-index.sh
    └── validate-endpoints.sh
```

## Quick Start

### Interactive (Claude Code)
```bash
cd /path/to/fleet-stuff
claude

# Then type:
/fleet-api

Show me how to list all hosts with failed policies using the API
```

### Example Output
The skill will:
1. Check if `fleetctl` is available
2. Find the correct endpoint (`GET /api/v1/fleet/hosts`)
3. Show proper query parameters (`populate_policies=true`)
4. Provide a complete curl example with authentication
5. Explain the response structure and pagination

## Tools Used

- **fleetctl** (optional) - Fleet's official CLI tool
- **curl** - For raw API requests
- **jq** - For JSON parsing (recommended for scripting)

## Common Use Cases

1. **List hosts with filters** - Get hosts by platform, status, label
2. **Upload configuration profiles** - Add MDM profiles via API
3. **Manage policies** - Create, update, delete policies programmatically
4. **Trigger MDM commands** - Lock, wipe, restart devices
5. **Export host data** - Generate CSV reports
6. **Manage software** - Install/remove software packages

## fleetctl vs Raw API

| Task | Use fleetctl | Use Raw API |
|------|-------------|-------------|
| GitOps apply | ✅ `fleetctl apply` | ❌ Complex |
| List hosts | ✅ `fleetctl get hosts` | ✅ For filtering |
| Authentication | ✅ `fleetctl login` | ❌ Manual token |
| Webhooks | ❌ | ✅ Required |
| Custom integrations | ❌ | ✅ Required |
| Bulk operations | ✅ Better UX | ✅ More control |

## API Quirks (Automatically Handled)

| Quirk | What Fails | Fix |
|-------|------------|-----|
| Profile uploads | Sending JSON body | Use `multipart/form-data` |
| SSO/MFA users | `POST /login` returns 401 | Get token from UI |
| Batch delete | `DELETE /hosts` doesn't exist | Use `POST /hosts/delete` |
| MDM commands | Expecting immediate status | Commands are async, poll activities |
| Global vs fleet policies | Wrong endpoint | Check scope first |

All 6 hard rules documented in `learnings.md`.

## Authentication Examples

### Get API Token (UI)
```
Fleet UI → My account → Get API token
```

### Create API-Only User
```bash
fleetctl user create --email api@example.com --name "API User" --api-only
```

### Use Token in Requests
```bash
curl -H "Authorization: Bearer <token>" \
  https://fleet.example.com/api/v1/fleet/hosts
```

## Pagination Example

```bash
# Get first 100 hosts
curl -H "Authorization: Bearer <token>" \
  "https://fleet.example.com/api/v1/fleet/hosts?per_page=100&page=0"

# Get next 100
curl -H "Authorization: Bearer <token>" \
  "https://fleet.example.com/api/v1/fleet/hosts?per_page=100&page=1"
```

## Related Skills

- **fleet-gitops** - For managing Fleet configuration as code
- **mobileconfig-profile** - For creating profiles to upload via API
- **ddm-declaration** - For creating DDM declarations to upload via API
- **windows-csp-profile** - For creating Windows profiles to upload via API

## Contributing to Learnings

The skill tracks **Rules** (hard constraints) and **Observations** (soft learnings):

```markdown
### Rule #N: Short Title
**What failed**: Description of the failure
**Fix**: How to prevent it
**How to apply**: When this rule should be checked
```

Currently tracking 6 hard rules and 4 observations from real-world API usage.

## Important Notes

- All requests require `Authorization: Bearer <token>` header
- Base URL pattern: `https://<your-fleet-instance>/api/v1/fleet/<endpoint>`
- MDM commands (lock, wipe, restart) are asynchronous - poll for status
- Use populate flags (`populate_software`, `populate_policies`) to reduce round trips
- CSV export endpoint is faster than paginating for bulk data exports
