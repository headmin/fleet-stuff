# mobileconfig-profile

**Expert at creating and validating Apple .mobileconfig files for macOS, iOS, and iPadOS.**

## Purpose

This skill helps you create, validate, and review Apple configuration profiles (`.mobileconfig` files) for Fleet MDM and GitOps workflows. It enforces Apple's schema requirements, catches common mistakes, and ensures profiles are production-ready.

## When to Use

- Creating new `.mobileconfig` files for Fleet GitOps
- Reviewing existing configuration profiles for errors
- Validating profiles against Apple schemas
- Troubleshooting profile deployment issues
- Converting requirements into proper PayloadType configurations

## How It Works

The skill follows a structured workflow:

1. **Read Context** - Loads `learnings.md` for accumulated knowledge from past sessions
2. **Check Tools** - Optionally uses `contour` CLI if available for enhanced validation
3. **Gather Requirements** - Asks about settings, scope (System/User), organization
4. **Create/Review** - Builds from templates or analyzes existing profiles
5. **Validate** - Runs through 3-tier validation (contour → plutil → manual checklist)
6. **Capture Learnings** - Updates `learnings.md` with new discoveries

## Key Features

### Defaults & Safety
- **Always defaults to System scope** unless explicitly asked for User
- **Requires PayloadOrganization** (not optional)
- **Forbids placeholder UUIDs** (12345678-1234... patterns)
- **Enforces reverse-DNS identifiers** (com.org.profiles.name format)

### Validation Tiers
1. **contour** (optional) - Catches Apple schema violations, deprecated types, convention issues
2. **plutil** (required) - Built-in macOS validator for XML/plist correctness
3. **Manual checklist** - Structural verification (UUIDs, identifiers, versions, scope)

### Failure Patterns
The skill knows common mistakes to avoid:
- Bare UUIDs as PayloadIdentifiers
- `<real>1.0</real>` instead of `<integer>1</integer>` for PayloadVersion
- Missing PayloadVersion on inner payloads
- Missing PayloadScope for system-wide settings
- Deprecated PayloadTypes

## File Structure

```
mobileconfig-profile/
├── SKILL.md                    # Main skill instructions
├── README.md                   # This file
├── learnings.md                # Session-persistent discoveries
└── references/                 # Static documentation
    ├── apple-schema-*.yaml     # Apple payload schemas
    ├── common-payload-types.md # Valid PayloadType values
    ├── template.mobileconfig   # Starting template
    └── validation-checklist.md # Pre-delivery checklist
```

## Quick Start

### Interactive (Claude Code)
```bash
cd /path/to/fleet-stuff
claude

# Then type:
/mobileconfig-profile

Create a firewall profile that blocks all incoming connections
```

### Example Output
The skill will:
1. Ask for organization name and confirm System scope
2. Generate real UUIDs with `uuidgen`
3. Create the profile with all required fields
4. Validate with contour (if available) and plutil
5. Provide the complete, production-ready `.mobileconfig` file

## Tools Used

- **contour** (optional) - Enhanced validation against Apple device-management schemas
- **plutil** (required) - macOS built-in plist validator
- **uuidgen** (required) - Generate RFC 4122 compliant UUIDs

## Common Use Cases

1. **Create TCC/PPPC profile** - Privacy preferences for app permissions
2. **Create firewall profile** - Enable/configure macOS firewall
3. **Create system extensions profile** - Approve security extensions
4. **Review existing profile** - Find and fix validation errors
5. **Convert requirements to payload** - Translate settings into proper XML

## Related Skills

- **ddm-declaration** - For DDM JSON declarations (macOS 14+, iOS 17+)
- **fleet-gitops** - For adding profiles to Fleet GitOps YAML
- **windows-csp-profile** - For Windows MDM profiles

## Contributing to Learnings

As you use the skill, it accumulates knowledge in `learnings.md`. Common patterns:

```markdown
## Issue #N: Short Title
**Frequency**: How often this occurs
**Pattern**: Observable symptom
**Root cause**: Why it happens
**Fix**: How to resolve
**Affected areas**: Where this appears
```

This helps the skill get smarter over time and catch issues proactively.
