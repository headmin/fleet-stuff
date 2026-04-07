---
name: fleet-gitops
description: "Expert at authoring and reviewing Fleet GitOps YAML files for managing device fleets as code. Use when working with Fleet YAML configuration, fleetctl apply, or MDM profiles in GitOps."
---

# Fleet GitOps Configuration Skill

Expert at authoring and reviewing Fleet GitOps YAML files for managing device fleets as code.

## When to Activate

- User creates, edits, or reviews Fleet GitOps YAML (`default.yml`, `fleets/*.yml`, `unassigned.yml`)
- Mentions Fleet MDM, Fleet GitOps, `fleetctl gitops`, or `it-and-security` folder
- Wants to add policies, reports, software, controls, labels, or profiles via YAML
- Asks about Fleet configuration profiles or OS update enforcement
- References teams/queries (old names) — redirect to fleets/reports (v4.82 rename)
- References `lib/` directory — redirect to `platforms/` (new recommended layout)

## Step 1: Read Context

Before starting, read these for accumulated knowledge:
- Read `learnings.md` — hard rules and observations from prior sessions
- Read `references/scope-rules.md` — what can be configured where

### Optional: Check for fleetctl and contour

If available, use these tools for validation:

```bash
# Check if tools are available
command -v fleetctl >/dev/null 2>&1 && echo "fleetctl available"
command -v contour >/dev/null 2>&1 && echo "contour available"

# fleetctl - GitOps validation and apply
fleetctl apply -f default.yml --dry-run        # Validate without applying
fleetctl apply -f fleets/engineering.yml       # Apply fleet configuration
fleetctl apply -f unassigned.yml               # Apply unassigned fleet config

# contour - Profile validation (for MDM profiles referenced in YAML)
contour profile validate platforms/macos/configuration-profiles/*.mobileconfig
contour ddm validate platforms/macos/declaration-profiles/*.json
```

**When to use which:**
- Use `fleetctl apply --dry-run` to validate YAML structure and schema
- Use `contour` to validate .mobileconfig and DDM .json files referenced in `custom_settings`
- Always validate profiles before adding them to GitOps YAML

Don't assume tools are installed — always check first.

## Step 2: Core Rules (Always Enforce)

### v4.82+ Renaming (CRITICAL)
As of Fleet 4.82 (Mar 2026):
- **teams → fleets** (everywhere: YAML, API, CLI, UI)
- **queries → reports** (everywhere: YAML, API, CLI, UI)
- **no-team.yml → unassigned.yml** (`no-team.yml` is deprecated)
- `fleetctl generate-gitops` outputs `fleet_maintained_apps` in a dedicated YAML section
- Software fields `self_service`, `labels_include_any`, `labels_exclude_any`, `categories`, `setup_experience` are now at **fleet level** (not package level)

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
Always check Fleet-maintained apps catalog before custom packages: https://github.com/fleetdm/fleet/tree/main/ee/maintained-apps

## Step 3: Look Up Details As Needed

Load these references only when the specific step requires them:

| When you need... | Read this file |
|---|---|
| Full YAML key reference with types/defaults | `references/yaml-schema.md` |
| What can be configured at global/fleet/unassigned level | `references/scope-rules.md` |
| Repo layout and directory structure | `references/file-structure-template.md` |
| Copy-paste YAML templates | `references/templates/` (default.yml, fleet.yml, unassigned.yml, policy.yml, etc.) |
| Fleet reserved variables (`$FLEET_VAR_*`) | `references/fleet-variables.md` |
| Configuration profile rules (.mobileconfig) | Use the `mobileconfig-profile` skill |

### External references
- Fleet GitOps docs: https://fleetdm.com/docs/configuration/yaml-files
- Fleet tables (osquery): https://fleetdm.com/tables
- Fleet API: https://fleetdm.com/docs/rest-api/rest-api
- Apple profiles: https://github.com/apple/device-management/tree/release/mdm/profiles
- Windows CSPs: https://learn.microsoft.com/en-us/windows/client-management/mdm/
- Android policies: https://developers.google.com/android/management/reference/rest/v1/enterprises.policies

## Step 4: Create or Review

### Creating a New Fleet YAML
1. Ask: fleet name, platform(s), policies/profiles/software needed, label targeting
2. Read `references/file-structure-template.md` for the starter template
3. Read `references/yaml-schema.md` for exact key names and types
4. Check `references/scope-rules.md` to ensure settings are at the right level
5. For .mobileconfig profiles, delegate to the `mobileconfig-profile` skill
6. Validate: run `scripts/validate-gitops-yaml.sh <file>` to check required keys, scope rules, and deprecated patterns

### Reviewing Existing GitOps YAML
1. Check all required top-level keys present
2. Verify paths exist and are relative-correct
3. Check label consistency (referenced = defined)
4. Verify scope rules (org_settings vs settings)
5. Read `references/yaml-schema.md` for key validation
6. Validate profiles against platform-specific rules
7. Check software uses Fleet-maintained apps where available

## Step 5: Capture Learnings

After every session, update `learnings.md`:
- **Failures** → new Rule entry (what broke, fix, when to check)
- **Successes** → new Observation entry (what worked, when to reuse)
- Always read `learnings.md` at start of next session
