# fleet-gitops

**Expert at authoring and reviewing Fleet GitOps YAML files for managing device fleets as code.**

## Purpose

This skill helps you create, validate, and review Fleet GitOps YAML configuration files. It enforces Fleet's schema requirements, catches silent deletion scenarios, and ensures your fleet configuration is production-ready.

## When to Use

- Creating or editing Fleet GitOps YAML files (`default.yml`, `fleets/*.yml`, `unassigned.yml`)
- Adding policies, reports, software, controls, labels, or profiles to fleets
- Migrating from teams/queries to fleets/reports (v4.82+ terminology)
- Validating YAML before applying with `fleetctl gitops`
- Understanding Fleet's "missing key = silent deletion" behavior
- Troubleshooting GitOps apply failures

## How It Works

The skill follows a structured workflow:

1. **Read Context** - Loads `learnings.md` (177 lines of hard rules!) and scope rules
2. **Check Tools** - Uses `fleetctl apply --dry-run` and optionally `contour` for profile validation
3. **Enforce v4.82+ Terminology** - teams→fleets, queries→reports, no-team.yml→unassigned.yml
4. **Validate Keys** - Checks for missing/misspelled keys that cause silent deletion
5. **Review Profiles** - Validates referenced .mobileconfig/.json files with contour
6. **Capture Learnings** - Updates `learnings.md` with new rules and observations

## Key Features

### Critical Safety Rules
- **Missing keys = silent deletion** - Omitting `software:` deletes all software
- **Misspelled keys = silent reset** - `policy:` instead of `policies:` deletes all policies
- **Fleet rename = fleet deletion** - Rename in UI first, then update YAML
- **Label rename = label deletion** - Warns about deletion implications

### v4.82+ Renaming (March 2026)
- `teams` → `fleets` (everywhere: YAML, API, CLI, UI)
- `queries` → `reports` (everywhere: YAML, API, CLI, UI)
- `no-team.yml` → `unassigned.yml` (deprecated filename)

### Required Top-Level Keys
Every YAML file needs ALL of these (even if empty):
- `name`, `policies`, `reports`, `agent_options`, `controls`, `software`, `settings`

### Validation Tiers
1. **fleetctl apply --dry-run** - Validates YAML structure and schema
2. **contour** (optional) - Validates .mobileconfig and DDM .json files in `custom_settings`
3. **Manual checklist** - Key presence, scope rules, label references

## File Structure

```
fleet-gitops/
├── SKILL.md                    # Main skill instructions
├── README.md                   # This file
├── learnings.md                # 177 lines of hard rules (21 rules, 5 observations!)
├── references/
│   ├── scope-rules.md          # What can be configured where (global/fleet/unassigned)
│   ├── yaml-schema.md          # Complete YAML schema reference
│   ├── fleet-variables.md      # $FLEET_VAR_* and $FLEET_SECRET_* usage
│   ├── certificate-authorities.md  # CA variable setup
│   ├── file-structure-template.md  # Recommended directory layout
│   └── templates/              # YAML templates for common scenarios
└── scripts/
    └── validate-gitops-yaml.sh
```

## Quick Start

### Interactive (Claude Code)
```bash
cd /path/to/fleet-stuff
claude

# Then type:
/fleet-gitops

Review default.yml and check for any missing required keys
```

### Example Output
The skill will:
1. Read your YAML file
2. Check for all required top-level keys
3. Validate label references (labels used must be declared)
4. Check scope rules (e.g., policy automations only in fleet/unassigned)
5. Verify .mobileconfig files in `custom_settings` with contour
6. Suggest `fleetctl apply --dry-run` for final validation

## Tools Used

- **fleetctl** (required) - Fleet's official CLI for GitOps validation and apply
- **contour** (optional) - Validates profiles referenced in `custom_settings`
- **yq** (optional) - YAML parsing for advanced validation

## Common Use Cases

1. **Add a new policy** - Add to `policies:` list with path reference
2. **Configure software installation** - Add Fleet-maintained apps or custom packages
3. **Deploy MDM profiles** - Add .mobileconfig files to `custom_settings`
4. **Set OS update enforcement** - Configure `macos_updates` or `windows_updates`
5. **Create fleet-specific settings** - Configure agent options, controls per fleet
6. **Migrate from v4.81 to v4.82** - Update terminology (teams→fleets, queries→reports)

## 21 Hard Rules (from learnings.md)

The skill enforces critical constraints learned from production usage:

| Rule | What Fails | Fix |
|------|-----------|-----|
| Missing keys | All resources deleted | Include all required keys (even if empty) |
| Misspelled keys | Resources silently reset | Copy keys from schema, don't type |
| Fleet rename | Hosts moved to Unassigned | Rename in UI first |
| Label references | GitOps error | Declare labels in `labels:` section |
| Array vs object syntax | Parse error | Arrays use `- path:`, objects use `path:` |
| Policy automations scope | Error | Only in fleet/unassigned, not global |
| app_store_id | Type error | Always quote: `"1091189122"` |
| version | Truncation | Always quote: `"4.47.65"` |
| hostname identifier | Deprecation warning | Use `hardware_serial` or `uuid` |
| Software field scope | Silent ignore | Set at fleet level, not package level |

...and 11 more! See `learnings.md` for full details.

## Scope Rules

| Setting | Global (default.yml) | Fleet (fleets/*.yml) | Unassigned (unassigned.yml) |
|---------|---------------------|----------------------|----------------------------|
| Agent options | ✅ | ✅ Override | ✅ Override |
| Policies | ✅ | ✅ Additional | ✅ Additional |
| Policy automations | ❌ | ✅ | ✅ |
| Reports (queries) | ✅ | ❌ Use global | ❌ Use global |
| Software | ❌ | ✅ | ✅ |
| MDM profiles | ✅ | ✅ Additional | ✅ Additional |
| OS updates | ✅ | ✅ Override | ✅ Override |

## Related Skills

- **mobileconfig-profile** - For creating .mobileconfig files to reference in YAML
- **ddm-declaration** - For creating DDM .json files to reference in YAML
- **windows-csp-profile** - For creating Windows profiles to reference in YAML
- **fleet-api** - For applying configurations via API instead of GitOps

## Contributing to Learnings

The skill has accumulated 21 hard rules and 5 observations from real-world usage:

```markdown
### Rule #N: Short Title
**What failed**: Description of what happened
**Fix**: How to prevent/resolve it
**How to apply**: When this rule should be checked
```

This makes the skill extremely resilient to common GitOps pitfalls.

## Important Notes

- Always run `fleetctl apply --dry-run` before applying changes
- v4.82+ uses fleets/reports terminology (old names deprecated)
- Missing keys cause silent deletion (not errors!)
- Labels must be declared before they can be referenced
- Software fields moved to fleet level in v4.81+
- Profile removal from `default.yml` works correctly in v4.82+ (was buggy before)
