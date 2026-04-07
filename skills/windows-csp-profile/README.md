# windows-csp-profile

**Expert at creating and validating Windows CSP (Configuration Service Provider) profile XML files for Fleet GitOps.**

## Purpose

This skill helps you create, validate, and review Windows MDM profiles for Fleet device management. It enforces Fleet's SyncML fragment requirements and Microsoft CSP specifications.

## When to Use

- Creating new Windows CSP profile XML files for Fleet GitOps
- Reviewing existing Windows profiles for errors
- Converting Microsoft CSP documentation into Fleet-compatible profiles
- Troubleshooting Windows MDM profile deployment issues
- Understanding Fleet's SyncML fragment requirements

## How It Works

The skill follows a structured workflow:

1. **Read Context** - Loads `learnings.md` for hard rules from real-world usage
2. **Gather Requirements** - Asks about settings, scope (Device/User), atomic requirements
3. **Verify LocURIs** - Checks against Fleet's reserved LocURI list
4. **Create/Review** - Builds from templates or analyzes existing profiles
5. **Validate** - Runs through 3-tier validation (xmllint → Fleet validator → manual checklist)
6. **Capture Learnings** - Updates `learnings.md` with new rules and observations

## Key Features

### Fleet-Specific Rules
- **No XML declaration** - File must NOT start with `<?xml version="1.0"?>`
- **No SyncML envelope** - No `<SyncML>`, `<SyncHdr>`, or `<SyncBody>` wrappers
- **No Delete commands** - `<Delete>` not supported anywhere
- **Reserved LocURIs** - BitLocker and Windows Update paths managed by Fleet UI

### SyncML Fragment Requirements
- Top-level elements: `<Replace>`, `<Add>`, `<Atomic>`, or `<Exec>` only
- If `<Atomic>` is present, it must be the ONLY top-level element
- Format tags require namespace: `<Format xmlns="syncml:metinf">int</Format>`
- LocURIs must start with `./Device/Vendor/MSFT/` or `./User/Vendor/MSFT/`

### Validation Tiers
1. **xmllint** (required) - XML well-formedness check
2. **Fleet validator** (optional) - Fleet's Windows profile validator script
3. **Manual checklist** - SyncML fragment rules, LocURI format, data types

## File Structure

```
windows-csp-profile/
├── SKILL.md                    # Main skill instructions
├── README.md                   # This file
├── learnings.md                # Hard rules from real-world usage
└── references/                 # Static documentation
    ├── reserved-locuri.md      # Fleet's reserved LocURI paths
    ├── template-single.xml     # Single setting template
    ├── template-multi.xml      # Multiple settings template
    ├── template-atomic.xml     # Atomic transaction template
    └── fleet-examples.md       # 43 production examples from Fleet docs
```

## Quick Start

### Interactive (Claude Code)
```bash
cd /path/to/fleet-stuff
claude

# Then type:
/windows-csp-profile

Create a profile to enable Windows Defender real-time protection
```

### Example Output
The skill will:
1. Ask for scope (Device or User) and atomic preference
2. Look up the correct LocURI from Microsoft CSP docs
3. Determine the correct data type (int/bool/chr)
4. Create the SyncML fragment (no envelope, no XML declaration)
5. Validate with xmllint
6. Provide the complete, Fleet-compatible `.xml` file

## Tools Used

- **xmllint** (required) - XML well-formedness validation
- **Fleet validator** (optional) - `scripts/validate-windows-profile.sh` if available

**Note:** Unlike macOS skills, this skill does NOT use `contour` (Windows-specific tooling).

## Common Use Cases

1. **Enable Windows Firewall** - Configure firewall settings
2. **Configure Windows Defender** - Real-time protection, cloud protection, exclusions
3. **Disable Windows features** - Turn off Cortana, OneDrive, etc.
4. **Set security policies** - Password policies, account lockout, audit settings
5. **Configure BitLocker** - Use Fleet UI (LocURI is reserved, not for custom profiles)

## Common Mistakes (Automatically Caught)

| Mistake | Why It Fails | Fix |
|---------|--------------|-----|
| `<?xml version="1.0"?>` | Fleet classifies as macOS profile | Remove declaration |
| `<SyncML>` wrapper | Fleet expects fragments only | Remove envelope |
| `<Delete>` command | Not supported by Fleet | Use `<Replace>` with default |
| `<Atomic>` with siblings | Invalid structure | Move everything inside `<Atomic>` |
| Missing `xmlns="syncml:metinf"` | Namespace required | Add to all `<Format>` tags |
| BitLocker LocURI | Reserved by Fleet | Use Fleet UI settings |

## Fleet Examples

Fleet provides 43 production-ready Windows profiles in `docs/solutions/windows/configuration-profiles/`:
- Firewall configurations
- Windows Defender settings
- Security policies
- Feature management
- And more

The skill references these examples before creating new profiles from scratch.

## Related Skills

- **fleet-gitops** - For adding Windows profiles to Fleet GitOps YAML
- **mobileconfig-profile** - For macOS profiles (different format)
- **fleet-api** - For uploading profiles via REST API

## Contributing to Learnings

The skill tracks **Rules** (hard constraints) and **Observations** (soft learnings):

```markdown
### Rule #N: Short Title
**What failed**: Description of the failure
**Fix**: How to prevent it
**How to apply**: When this rule should be checked
```

After 70 lines of accumulated rules, the skill knows exactly what Fleet accepts and rejects.

## Important Notes

- Windows profiles go under `windows_settings.custom_settings` in Fleet GitOps YAML
- Device vs User scope determined by LocURI path (`./Device/` vs `./User/`)
- Atomic profiles are all-or-nothing (entire profile succeeds or fails together)
- Non-atomic profiles apply each setting independently (default, recommended)
- Always check Microsoft CSP documentation for exact LocURI paths and data types
