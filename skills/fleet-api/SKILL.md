---
name: fleet-api
description: Help with the Fleet REST API and fleetctl CLI — scripting, automation, and integration for device management including hosts, policies, software, profiles, and MDM commands.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash, WebFetch
effort: high
---

You are helping with Fleet REST API usage and automation: $ARGUMENTS

Apply the following constraints for all work.

## Core Rules

### Authentication
- All requests require `Authorization: Bearer <token>` header
- Get token from Fleet UI (My account > Get API token) or `POST /api/v1/fleet/login`
- SSO/MFA users cannot use email/password login — must get token from UI
- For GitOps automation, create API-only users: `fleetctl user create --api-only`

### Base URL pattern
All endpoints follow: `<fleet-url>/api/v1/fleet/<resource>`

### Pagination
Most list endpoints support: `page`, `per_page`, `order_key`, `order_direction` (asc/desc)

### Error format
```json
{
  "message": "Description of the error",
  "errors": [{"name": "field_name", "reason": "specific reason"}],
  "uuid": "unique-error-id"
}
```

### Dangerous endpoints (confirm before using)
These are destructive and irreversible — always confirm with the user:
- `POST /api/v1/fleet/hosts/delete` — Batch-deletes hosts
- `DELETE /api/v1/fleet/hosts/:id` — Deletes a single host
- `POST /api/v1/fleet/hosts/:id/wipe` — Factory-wipes a device
- `POST /api/v1/fleet/hosts/:id/lock` — Locks a device
- `DELETE /api/v1/fleet/fleets/:id` — Deletes a fleet

## fleetctl CLI (if available)

```bash
command -v fleetctl >/dev/null 2>&1 && echo "fleetctl available"

fleetctl get hosts                    # List hosts
fleetctl get queries                  # List queries
fleetctl apply -f <file>.yaml         # Apply GitOps YAML
fleetctl api get /api/v1/fleet/hosts  # Raw API via fleetctl
```

**When to use fleetctl vs raw API:**
- `fleetctl` for: GitOps apply, bulk operations, authentication, common queries
- Raw API for: webhooks, integrations, custom automation, endpoints not in fleetctl

Don't assume fleetctl is installed — always check first.

## Local References

Before starting, read `learnings.md` for accumulated knowledge from prior sessions.

Read `references/endpoint-index.md` for all endpoints grouped by domain (Hosts, Software, Policies, OS Settings, Fleets, Labels, Users, Config, Scripts, Commands).

## Common Patterns

### Using curl
```bash
curl -s -H "Authorization: Bearer $FLEET_API_TOKEN" \
  "https://fleet.example.com/api/v1/fleet/hosts?per_page=10"
```

### Key patterns
1. **List + filter**: Most list endpoints accept `query`, `fleet_id`, `label_id`, `platform`
2. **By ID vs identifier**: Hosts via `GET /hosts/:id` or `GET /hosts/identifier/:identifier` (hostname, UUID, or serial)
3. **Batch operations**: Use `POST /hosts/delete` with IDs, not one-by-one
4. **Async operations**: Lock, wipe, MDM commands are queued — check status via activities endpoint
5. **Profile uploads**: Use `multipart/form-data`, not JSON
6. **Populate flags**: `?populate_software=true&populate_policies=true` reduces API calls

## Keeping the Index Current

The endpoint index can go stale as Fleet releases new versions:
- `scripts/update-endpoint-index.sh` — Regenerate from latest API docs
- `scripts/validate-endpoints.sh` — Probe a live Fleet instance for changes

Run `update-endpoint-index.sh` when an endpoint returns 404.

---

## Failure Patterns

| Pattern | Why It's Wrong | Fix |
|---------|----------------|-----|
| Profile upload as JSON body | 400 error | Use `multipart/form-data` (`curl -F`) |
| SSO user calling `/fleet/login` | 401 error | Get token from Fleet UI instead |
| `DELETE /hosts` for bulk delete | Endpoint doesn't exist | Use `POST /hosts/delete` with `{"ids": [...]}` |
| Expecting sync lock/wipe response | Commands are async | Poll activities endpoint for status |
| Global endpoint for fleet policy | Wrong scope | Use `/fleets/:id/policies` for fleet-scoped |
| Only using numeric ID for hosts | Missing flexible lookup | Use `/hosts/identifier/:identifier` for serial/UUID |
| Using `teams`/`queries` in API | Deprecated in v4.82+ | Use `fleets`/`reports` field names |

---

## Standard Verification

- Use `--dry-run` with `fleetctl gitops` for config changes
- Check response codes: 200 (success), 201 (created), 204 (deleted), 4xx (client), 5xx (server)
- For profile uploads, verify `Content-Type: multipart/form-data`

---

## Capture Learnings

After every session, update `learnings.md`:
- **Failures** → new Rule entry (what broke, fix, when to check)
- **Successes** → new Observation entry (what worked, when to reuse)

## References

- Fleet API documentation (canonical): https://fleetdm.com/docs/rest-api/rest-api
- Fleet tables (osquery): https://fleetdm.com/tables
- Fleet GitOps documentation: https://fleetdm.com/docs/configuration/yaml-files
