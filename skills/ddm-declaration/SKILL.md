---
description: "Expert at creating and validating Apple DDM declaration JSON files for Fleet GitOps."
---

# Apple DDM Declaration Profile Skill

Expert at creating and validating Apple Declarative Device Management (DDM) JSON declaration files for macOS 14+, iOS 17+, and iPadOS 17+.

## When to Activate

- User creates, edits, or reviews a DDM `.json` declaration file
- Mentions DDM, declarative device management, or declaration profiles
- Asks about declaration types, passcode settings, or software update enforcement via JSON
- References `com.apple.configuration.*` types
- Needs a DDM profile for Fleet GitOps (as opposed to a legacy `.mobileconfig`)

## Step 1: Read Context

Before starting, read these for accumulated knowledge:
- Read `learnings.md` — known gotchas and patterns from prior sessions

## Step 2: Core Rules (Always Enforce)

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
Fleet generates `ServerToken` automatically from a hash of the JSON contents. Including it in the file will cause issues.

### Forbidden declaration types
These 12 configuration types are blocked because they require asset references Fleet doesn't support:
`account.caldav`, `account.carddav`, `account.exchange`, `account.google`, `account.ldap`, `account.mail`, `screensharing.connection`, `security.certificate`, `security.identity`, `security.passkey.attestation`, `services.configuration-files`, `watch.enrollment`

### Restricted types
- `softwareupdate.enforcement.specific` — blocked unless `allowCustomOSUpdatesAndFileVault` is enabled
- `management.status-subscriptions` — always blocked (use queries/policies instead)

### Identifier format
- Max 64 bytes (UTF-8 octets)
- Fleet convention: `com.fleetdm.config.<descriptive-name>` (e.g., `com.fleetdm.config.passcode.settings`)
- Must be unique per fleet/team

### Payload keys are PascalCase
DDM uses `RequireAlphanumericPasscode`, not `require_alphanumeric_passcode` or `requireAlphanumericPasscode`.

### DDM combine semantics
Multiple declarations of the same type merge payloads using per-key rules (`boolean-or`, `number-max`, `number-min`, `enum-last`, `set-union`). This is fundamentally different from .mobileconfig where last profile wins.

## Step 3: Look Up Details As Needed

| When you need... | Read this file |
|---|---|
| Passcode settings schema and keys | `references/passcode-settings.yaml` |
| Software update settings schema | `references/softwareupdate-settings.yaml` |
| Software update enforcement schema | `references/softwareupdate-enforcement-specific.yaml` |
| All available configuration types | `references/declaration-types.md` |
| Starting template for a new declaration | `references/template.json` |
| Full validation checklist before delivery | `references/validation-checklist.md` |

To add new schemas: download from `https://raw.githubusercontent.com/apple/device-management/release/declarative/declarations/configurations/<type>.yaml` and save to `references/`.

### External references
- Apple DDM schemas: https://github.com/apple/device-management/tree/release/declarative/declarations
- DDM explorer (GUI for schemas): https://github.com/Jamf-Concepts/ddm-explorer
- KMFDDM (open-source DDM server): https://github.com/jessepeterson/kmfddm

## Step 4: Create or Review

### Creating a New Declaration
1. Ask: what settings to manage, target platform (macOS/iOS/iPadOS), org name
2. Verify the type is allowed in Fleet (not forbidden, not restricted)
3. Build from `references/template.json`
4. Look up payload keys in the appropriate schema reference
5. Validate using `scripts/validate-ddm-declaration.sh`

### Reviewing an Existing Declaration
1. Parse the JSON
2. Check: Type starts with `com.apple.configuration.`, Identifier is reverse-DNS, no ServerToken, Type not forbidden/restricted, valid JSON
3. Validate payload keys against the schema
4. Run `scripts/validate-ddm-declaration.sh <file>`

## Step 5: Fleet GitOps Integration

DDM declarations go in the **same** `configuration_profiles` list as .mobileconfig:

```yaml
controls:
  macos_settings:
    custom_settings:
      - path: ../platforms/macos/configuration-profiles/firewall.mobileconfig
      - path: ../platforms/macos/declaration-profiles/passcode-settings.json
```

Fleet differentiates by file content (JSON = DDM, XML = .mobileconfig), not by config key.

**Directory convention:** `platforms/{platform}/declaration-profiles/` (separate from `configuration-profiles/`)
**File naming:** Descriptive with `.json` extension (e.g., `Passcode settings.json`)

## Step 6: Capture Learnings

After every session, update `learnings.md`:
- **Failures** → new Rule entry (what broke, fix, when to check)
- **Successes** → new Observation entry (what worked, when to reuse)
