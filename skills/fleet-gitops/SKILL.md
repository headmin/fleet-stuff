---
name: fleet-gitops
description: Help with Fleet GitOps YAML configuration files — authoring, reviewing, and validating for managing device fleets as code including policies, profiles, software, and controls.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash, WebFetch
effort: high
---

You are helping with Fleet GitOps configuration files: $ARGUMENTS

Focus on the `it-and-security` folder. Apply the following constraints for all work.

## Core Rules

### v4.82+ Renaming (CRITICAL)
As of Fleet 4.82 (Mar 2026):
- **teams → fleets** (everywhere: YAML, API, CLI, UI)
- **queries → reports** (everywhere: YAML, API, CLI, UI)
- **no-team.yml → unassigned.yml** (`no-team.yml` is deprecated)
- `fleetctl generate-gitops` outputs `fleet_maintained_apps` in a dedicated YAML section
- Software fields `self_service`, `labels_include_any`, `labels_exclude_any`, `categories`, `setup_experience` are now at **fleet level** (not package level)

As of Fleet 4.83:
- **`FLEET_MDM_ALLOW_ALL_DECLARATIONS`** — server flag that bypasses all DDM type restrictions. When enabled, forbidden types (account.mail, security.certificate, etc.), activations, assets, and management declarations are all accepted in `custom_settings`. Default: disabled (12 types still blocked). Cloud customers must request Fleet enable it. Follow-up #38986 plans to allow all types by default.

### Required top-level keys
Every YAML file needs ALL required keys. Missing or misspelled keys **silently reset to defaults or delete resources**.

```yaml
# default.yml                    # fleets/fleet-name.yml
policies:                        name:
reports:                         policies:
agent_options:                   reports:
controls:                        agent_options:
software:                        controls:
org_settings:                    software:
                                 settings:
```

### Path conventions
- All paths are **relative to the file being edited**
- Arrays (policies, reports, labels) use `- path:` with dash
- Objects (agent_options) use `path:` without dash

### Label consistency
Labels referenced in policies, reports, or software MUST be defined in the `labels:` section. If the `labels` key is present, unlisted labels are **deleted**.

### Fleet renaming safety
Always rename in Fleet UI first, then update YAML. YAML-only rename = fleet deletion.

### Software priority
Always check Fleet-maintained apps catalog before custom packages:
- https://github.com/fleetdm/fleet/tree/main/ee/maintained-apps

## Contour and fleetctl (if available)

```bash
# Check if tools are available
command -v fleetctl >/dev/null 2>&1 && echo "fleetctl available"
command -v contour >/dev/null 2>&1 && echo "contour available"

# fleetctl - GitOps validation and apply
fleetctl apply -f default.yml --dry-run        # Validate without applying

# contour - Profile validation (for MDM profiles referenced in YAML)
contour profile validate platforms/macos/configuration-profiles/*.mobileconfig
contour profile ddm validate platforms/macos/declaration-profiles/*.json
```

Don't assume tools are installed — always check first.

## Local References

Before starting, read `learnings.md` for accumulated knowledge from prior sessions.

| When you need... | Read this file |
|---|---|
| Full YAML key reference with types/defaults | `references/yaml-schema.md` |
| What can be configured at global/fleet/unassigned level | `references/scope-rules.md` |
| Repo layout and directory structure | `references/file-structure-template.md` |
| Copy-paste YAML templates | `references/templates/` (default.yml, fleet.yml, unassigned.yml, etc.) |
| Fleet reserved variables (`$FLEET_VAR_*`) | `references/fleet-variables.md` |
| Configuration profile rules (.mobileconfig) | Use the `mobileconfig-profile` skill |

## Creating Fleet YAML

1. Ask: fleet name, platform(s), policies/profiles/software needed, label targeting
2. Read `references/file-structure-template.md` for the starter template
3. Read `references/yaml-schema.md` for exact key names and types
4. Check `references/scope-rules.md` to ensure settings are at the right level
5. For .mobileconfig profiles, delegate to the `mobileconfig-profile` skill
6. Validate with `fleetctl apply --dry-run`

## Reviewing Fleet YAML

1. Check all required top-level keys present
2. Verify paths exist and are relative-correct
3. Check label consistency (referenced = defined)
4. Verify scope rules (org_settings vs settings)
5. Validate profiles against platform-specific rules
6. Check software uses Fleet-maintained apps where available

---

## Failure Patterns

| Pattern | Why It's Wrong | Fix |
|---------|----------------|-----|
| Missing top-level key (e.g., no `software:`) | Silently deletes all existing resources of that type | Always include all required keys, even if empty |
| Misspelled key (`policy:` vs `policies:`) | Silently resets/deletes | Copy from schema, don't type from memory |
| Fleet renamed in YAML only | Old fleet deleted, hosts moved to Unassigned | Rename in UI first, then update YAML |
| Label referenced but not defined | GitOps error | Add label to `labels:` section |
| `- path:` for agent_options | Parse error | Use `path:` without dash for object types |
| `path:` for policies/reports | Parse error | Use `- path:` with dash for array types |
| Unquoted `app_store_id` | Interpreted as integer | Always quote: `"1091189122"` |
| Unquoted `version` | Float truncates patch version | Always quote: `"4.47.65"` |
| Policy automations in `default.yml` | Error — only fleet/unassigned | Move to fleet-level YAML |
| Using `teams`/`queries` terminology | Deprecated in v4.82+ | Use `fleets`/`reports` |
| `no-team.yml` | Deprecated | Rename to `unassigned.yml` |

---

## Standard Verification

### 1. fleetctl dry-run (if available)
```bash
command -v fleetctl >/dev/null 2>&1 && fleetctl apply -f <file>.yml --dry-run
```

### 2. Profile validation (if profiles referenced)
```bash
command -v contour >/dev/null 2>&1 && contour profile validate <profiles-dir>/*.mobileconfig
```

### 3. Manual checklist
- [ ] All required top-level keys present
- [ ] Key names match schema exactly
- [ ] Paths are relative and files exist
- [ ] Labels referenced = labels defined
- [ ] Scope rules respected (global vs fleet vs unassigned)
- [ ] Versions and app_store_ids quoted
- [ ] Software checks Fleet-maintained catalog first
- [ ] v4.82+ terminology used (fleets/reports/unassigned)

---

## Capture Learnings

After every session, update `learnings.md`:
- **Failures** → new Rule entry (what broke, fix, when to check)
- **Successes** → new Observation entry (what worked, when to reuse)

## References

- Fleet GitOps documentation: https://fleetdm.com/docs/configuration/yaml-files
- Fleet tables (osquery): https://fleetdm.com/tables
- Fleet API: https://fleetdm.com/docs/rest-api/rest-api
- Fleet-maintained apps: https://github.com/fleetdm/fleet/tree/main/ee/maintained-apps
- Apple device-management profiles: https://github.com/apple/device-management/tree/release/mdm/profiles
- Windows CSPs: https://learn.microsoft.com/en-us/windows/client-management/mdm/
- Android policies: https://developers.google.com/android/management/reference/rest/v1/enterprises.policies
