# ddm-declaration

**Expert at creating and validating Apple DDM (Declarative Device Management) declaration JSON files for Fleet GitOps.**

## Purpose

This skill helps you create, validate, and review DDM declaration JSON files for modern Apple device management. DDM is the successor to configuration profiles, available on macOS 14+, iOS 17+, and iPadOS 17+.

## When to Use

- Creating new DDM `.json` declaration files for Fleet GitOps
- Reviewing existing DDM declarations for errors
- Understanding DDM vs .mobileconfig differences
- Validating declarations against Apple schemas
- Working with Fleet's DDM implementation (allowed/forbidden types)

## How It Works

The skill follows a structured workflow:

1. **Read Context** - Loads `learnings.md` for hard rules and observations
2. **Check Tools** - Optionally uses `contour ddm` CLI if available for validation
3. **Gather Requirements** - Asks about settings, platform (macOS/iOS/iPadOS), organization
4. **Create/Review** - Builds from templates or analyzes existing declarations
5. **Validate** - Runs through 3-tier validation (contour → jq → manual checklist)
6. **Capture Learnings** - Updates `learnings.md` with new rules and observations

## Key Features

### DDM-Specific Rules
- **No ServerToken** - Fleet generates this automatically (never include it)
- **Only configuration types** - `com.apple.configuration.*` types only
- **PascalCase payload keys** - DDM uses PascalCase (e.g., `RequireAlphanumericPasscode`)
- **Combine semantics** - Multiple declarations of same Type merge (not override)

### Forbidden Types (12 blocked by Fleet)
The skill knows which DDM types require asset references that Fleet doesn't support:
- `account.*` (mail, caldav, ldap, etc.)
- `scep`, `certificate.root`, `certificate.pkcs12`
- `softwareupdate.enforcement.specific` (restricted, requires feature flag)

### Validation Tiers
1. **contour ddm** (optional) - Validates against Apple's 42 DDM declaration schemas
2. **jq** (required) - JSON syntax validation
3. **Manual checklist** - Type validation, identifier rules, PascalCase enforcement

## File Structure

```
ddm-declaration/
├── SKILL.md                    # Main skill instructions
├── README.md                   # This file
├── learnings.md                # Hard rules and observations
└── references/                 # Static documentation
    ├── allowed-types.md        # 30 allowed configuration types
    ├── forbidden-types.md      # 12 forbidden types requiring assets
    ├── template.json           # Starting template
    └── <type>.yaml            # Apple schema references
```

## Quick Start

### Interactive (Claude Code)
```bash
cd /path/to/fleet-stuff
claude

# Then type:
/ddm-declaration

Create a passcode settings declaration requiring alphanumeric passwords
```

### Example Output
The skill will:
1. Confirm platform and organization
2. Select the correct Type (`com.apple.configuration.passcode.settings`)
3. Create reverse-DNS identifier
4. Build Payload with PascalCase keys
5. Validate with contour ddm (if available) and jq
6. Provide the complete, production-ready `.json` file

## Tools Used

- **contour** (optional) - DDM declaration validation against Apple schemas
- **jq** (required) - JSON syntax and well-formedness validation

## Common Use Cases

1. **Create passcode policy** - Enforce password requirements
2. **Configure system preferences** - Lock/hide System Settings panes
3. **Software update enforcement** - Configure automatic updates
4. **Restrict features** - Disable AirDrop, iCloud, etc.
5. **Replace .mobileconfig with DDM** - Migrate to declarative management

## DDM vs .mobileconfig

| Feature | .mobileconfig | DDM Declaration |
|---------|---------------|-----------------|
| Format | XML plist | JSON |
| Availability | All macOS/iOS versions | macOS 14+, iOS 17+ |
| Conflict resolution | Last profile wins | Declarations merge by key |
| Scope | PayloadScope (System/User) | Implicit based on Type |
| Server state | ServerToken optional | ServerToken auto-generated |
| Fleet GitOps key | `custom_settings` | Same `custom_settings` list |

## Related Skills

- **mobileconfig-profile** - For legacy .mobileconfig profiles
- **fleet-gitops** - For adding declarations to Fleet GitOps YAML
- **fleet-api** - For uploading declarations via REST API

## Contributing to Learnings

The skill tracks both **Rules** (hard constraints) and **Observations** (soft learnings):

```markdown
### Rule #N: Short Title
**What failed**: Description of the failure
**Fix**: How to prevent it
**How to apply**: When this rule should be checked
```

This knowledge accumulates and helps catch issues before they reach production.

## Important Notes

- DDM declarations and .mobileconfig files share the same `custom_settings` list in Fleet GitOps
- Fleet differentiates them by file content (JSON vs XML), not by config key
- Use separate directories: `platforms/macos/declaration-profiles/` vs `configuration-profiles/`
- Identifier must be ≤64 UTF-8 bytes
- All identifiers must be unique across your fleet/team
