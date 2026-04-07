---
name: ddm-declaration
description: "Expert at creating and validating Apple DDM declaration JSON files for Fleet GitOps. Use when working with Declarative Device Management, DDM declarations, or Fleet declarative profiles."
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

---

## Failure Patterns

Observable warning signs that indicate problems:

| Pattern | Why It's Wrong | Fix |
|---------|----------------|-----|
| `ServerToken` included in JSON | Fleet generates this automatically | Remove the `ServerToken` key entirely |
| Type doesn't start with `com.apple.configuration.` | Fleet only accepts configuration types | Use a valid configuration type or switch to .mobileconfig |
| Forbidden type (e.g., `account.mail`) | Requires asset references Fleet doesn't support | Use .mobileconfig instead or remove asset dependency |
| `softwareupdate.enforcement.specific` without flag | Restricted type, requires feature flag | Enable `allowCustomOSUpdatesAndFileVault` or use settings type |
| Identifier over 64 bytes | DDM spec limit | Shorten to ≤64 UTF-8 bytes |
| snake_case or camelCase payload keys | DDM uses PascalCase | Use `RequireAlphanumericPasscode` not `require_alphanumeric_passcode` |
| Invalid JSON syntax | JSON parser fails | Fix syntax errors (missing commas, quotes, brackets) |
| Duplicate Identifier across declarations | Fleet rejects duplicate identifiers | Make each Identifier unique per team/fleet |
| Type typo (e.g., `com.apple.config.passcode`) | Wrong namespace | Use `com.apple.configuration.passcode.settings` |
| Empty Payload object `{}` | No settings configured | Add actual payload keys or remove declaration |

**Common slip-ups:**
- Copying ServerToken from Fleet UI export (it changes on every edit)
- Using .mobileconfig PayloadTypes instead of DDM Types
- Forgetting DDM uses combine semantics (multiple declarations merge)
- Using restricted types without understanding Fleet's limitations

---

## Standard Verification

**Validation order** (run in this sequence):

### 1. contour validation (optional, if available)
```bash
# Check if contour is installed
command -v contour >/dev/null 2>&1 && contour ddm validate <file>.json
```

**What contour DDM validation catches:**
- Invalid Type (not in Apple's 42 DDM types)
- Forbidden types (the 12 blocked configuration types)
- Missing required top-level keys (Type, Identifier, Payload)
- ServerToken present (should be auto-generated)
- Payload key validation against Apple schemas
- PascalCase violations in payload keys
- Identifier length violations (>64 bytes)

**If contour catches issues, fix them before proceeding to jq.**

### 2. JSON well-formedness check (REQUIRED)
```bash
# Validate JSON syntax
jq empty <file>.json 2>&1
```

**What jq catches:**
- Malformed JSON (missing commas, quotes, brackets)
- Invalid escape sequences
- Trailing commas (not allowed in strict JSON)
- UTF-8 encoding issues

**jq must pass before proceeding to manual checks.**

### 3. Manual skill checklist

After validation passes, verify:

- [ ] **Valid Type**: Starts with `com.apple.configuration.` (e.g., `com.apple.configuration.passcode.settings`)
- [ ] **Not forbidden**: Type is NOT one of the 12 forbidden configuration types requiring assets
- [ ] **Not restricted**: If using `softwareupdate.enforcement.specific`, confirm `allowCustomOSUpdatesAndFileVault` is enabled
- [ ] **Identifier format**: Reverse-DNS format (e.g., `com.fleetdm.config.passcode-settings`)
- [ ] **Identifier length**: ≤64 UTF-8 bytes
- [ ] **Identifier uniqueness**: Not used by another declaration in the same team/fleet
- [ ] **No ServerToken**: File does NOT contain `ServerToken` key
- [ ] **Payload present**: `Payload` object exists and is not empty `{}`
- [ ] **PascalCase keys**: All payload keys use PascalCase (e.g., `RequireAlphanumericPasscode`)
- [ ] **Valid payload keys**: Keys match Apple's schema for that Type (check `references/<type>.yaml`)
- [ ] **Correct data types**: String/number/boolean/array types match schema requirements

### 4. Production readiness

- [ ] Tested on macOS 14+/iOS 17+/iPadOS 17+ device via Fleet MDM
- [ ] Understand combine semantics (if multiple declarations of same Type exist)
- [ ] File placed in `platforms/{macos|ios|ipados}/declaration-profiles/` directory
- [ ] Descriptive filename with `.json` extension (e.g., "Passcode settings.json")
- [ ] Added to `custom_settings` list in Fleet GitOps YAML
- [ ] Label targeting configured if needed (`labels_include_any`, etc.)
- [ ] Documented purpose in comments or team README
