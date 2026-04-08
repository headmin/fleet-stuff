---
name: ddm-declaration
description: Help with Apple DDM declaration JSON files — creating, validating, and reviewing for Fleet GitOps declarative device management on macOS 14+, iOS 17+, iPadOS 17+.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash, WebFetch
effort: high
---

You are helping with Apple DDM declaration profiles (.json): $ARGUMENTS

Focus on validation against Apple's DDM schemas and Fleet's declaration constraints. Apply the following rules for all work.

## Core Rules

### Only `com.apple.configuration.*` types in Fleet
Fleet only accepts declarations with `Type` starting with `com.apple.configuration.`. Activations, assets, and management types are rejected.

### Required top-level keys
Every declaration JSON needs exactly three user-provided keys:

```json
{
    "Type": "com.apple.configuration.<subtype>",
    "Identifier": "com.<org>.config.<descriptive-name>",
    "Payload": { }
}
```

### Do NOT include ServerToken
Fleet generates `ServerToken` automatically from a hash of the JSON contents. Including it causes issues.

### Forbidden declaration types (default behavior)
These 12 configuration types are blocked by default (require asset references):
`account.caldav`, `account.carddav`, `account.exchange`, `account.google`, `account.ldap`, `account.mail`, `screensharing.connection`, `security.certificate`, `security.identity`, `security.passkey.attestation`, `services.configuration-files`, `watch.enrollment`

**Fleet 4.83+ override**: Setting `FLEET_MDM_ALLOW_ALL_DECLARATIONS` bypasses all type restrictions — including forbidden types, activations, assets, and management declarations. Cloud customers must request Fleet enable this flag. See #38366. A follow-up (#38986) plans to enable all types by default without the flag.

### Restricted types
- `softwareupdate.enforcement.specific` — blocked unless `allowCustomOSUpdatesAndFileVault` is enabled
- `management.status-subscriptions` — always blocked (use queries/policies instead)
- Both restrictions are also bypassed by `FLEET_MDM_ALLOW_ALL_DECLARATIONS`

### Identifier format
- Max 64 bytes (UTF-8 octets)
- Fleet convention: `com.fleetdm.config.<descriptive-name>`
- Must be unique per fleet/team

### Payload keys are PascalCase
DDM uses `RequireAlphanumericPasscode`, not `require_alphanumeric_passcode` or `requireAlphanumericPasscode`.

### DDM combine semantics
Multiple declarations of the same type merge payloads using per-key rules (`boolean-or`, `number-max`, `number-min`, `enum-last`, `set-union`). This is fundamentally different from .mobileconfig where last profile wins.

## Contour CLI (if available)

```bash
command -v contour >/dev/null 2>&1 && contour profile ddm validate <file>.json
contour profile ddm list       # List all 42+ DDM declaration types
contour profile ddm info <type>  # Show schema for a type
```

Don't assume contour is installed — always check first with `command -v contour`.

## Local References

Before starting, read `learnings.md` for accumulated knowledge from prior sessions.

| When you need... | Read this file |
|---|---|
| Passcode settings schema and keys | `references/passcode.settings.yaml` |
| Software update settings schema | `references/softwareupdate.settings.yaml` |
| Software update enforcement schema | `references/softwareupdate.enforcement.specific.yaml` |
| All available configuration types | `references/declaration-types.md` |
| Starting template | `references/template.json` |
| Full validation checklist | `references/validation-checklist.md` |

To add new schemas: download from the Apple device-management declarative repo and save to `references/`.

## Creating a Declaration

1. Ask: settings to manage, target platform (macOS/iOS/iPadOS), org name
2. Verify the type is allowed in Fleet (not forbidden, not restricted)
3. Build from `references/template.json`
4. Look up payload keys in the appropriate schema reference
5. Validate: contour → jq → manual checklist

## Reviewing a Declaration

1. Parse the JSON
2. Check: Type starts with `com.apple.configuration.`, Identifier is reverse-DNS, no ServerToken, Type not forbidden/restricted, valid JSON
3. Validate payload keys against the schema
4. Flag any issues with fix recommendations

## Fleet GitOps Integration

DDM declarations go in the **same** `custom_settings` list as .mobileconfig:

```yaml
controls:
  macos_settings:
    custom_settings:
      - path: ../platforms/macos/configuration-profiles/firewall.mobileconfig
      - path: ../platforms/macos/declaration-profiles/passcode-settings.json
```

Fleet differentiates by file content (JSON = DDM, XML = .mobileconfig), not by config key.

**Directory convention:** `platforms/{platform}/declaration-profiles/`
**File naming:** Descriptive with `.json` extension (e.g., `Passcode settings.json`)

---

## Failure Patterns

| Pattern | Why It's Wrong | Fix |
|---------|----------------|-----|
| `ServerToken` in JSON | Fleet generates this automatically | Remove the key entirely |
| Type without `com.apple.configuration.` prefix | Fleet rejects non-configuration types | Use correct prefix |
| Forbidden type (e.g., `account.mail`) | Requires asset references (default) | Use .mobileconfig, or enable `FLEET_MDM_ALLOW_ALL_DECLARATIONS` (4.83+) |
| `softwareupdate.enforcement.specific` without flag | Restricted type | Enable `allowCustomOSUpdatesAndFileVault` |
| Identifier over 64 bytes | DDM spec limit | Shorten identifier |
| snake_case or camelCase payload keys | DDM uses PascalCase | Use `RequireAlphanumericPasscode` |
| Invalid JSON syntax | Parser fails | Fix missing commas, quotes, brackets |
| Duplicate Identifier across declarations | Fleet rejects duplicates | Make each unique per team |
| Type typo (e.g., `com.apple.config.passcode`) | Wrong namespace | Use `com.apple.configuration.passcode.settings` |
| Empty Payload `{}` | No settings configured | Add payload keys or remove declaration |

---

## Standard Verification

**Validation order** (run in this sequence):

### 1. contour validation (if available)
```bash
command -v contour >/dev/null 2>&1 && contour profile ddm validate <file>.json
```

### 2. JSON well-formedness (REQUIRED)
```bash
jq empty <file>.json 2>&1
```

### 3. Manual checklist
- [ ] Valid Type: starts with `com.apple.configuration.`
- [ ] Not forbidden or restricted
- [ ] Identifier: reverse-DNS, ≤64 bytes, unique
- [ ] No ServerToken key
- [ ] Payload present and not empty
- [ ] All payload keys PascalCase
- [ ] Keys and data types match Apple schema

---

## Capture Learnings

After every session, update `learnings.md`:
- **Failures** → new Rule entry (what broke, fix, when to check)
- **Successes** → new Observation entry (what worked, when to reuse)

## References

- Apple DDM schemas: https://github.com/apple/device-management/tree/release/declarative/declarations
- DDM Explorer (GUI): https://github.com/Jamf-Concepts/ddm-explorer
- Fleet GitOps documentation: https://fleetdm.com/docs/configuration/yaml-files
