---
name: mobileconfig-profile
description: Help with Apple .mobileconfig configuration profiles — creating, validating, and reviewing for macOS, iOS, and iPadOS MDM deployment including Fleet GitOps.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash, WebFetch
effort: high
---

You are helping with Apple configuration profiles (.mobileconfig): $ARGUMENTS

Focus on validation against Apple's device-management schemas and Fleet GitOps conventions. Apply the following constraints for all work.

## Core Rules

### PayloadIdentifier — Reverse-DNS only
- **NEVER** use bare UUIDs. Always `com.<org>.profiles.<name>`
- Inner payloads: `com.<org>.profiles.<name>.<uuid-suffix>`
- Default org for Fleet: `com.fleetdm`

### PayloadUUID — Valid RFC 4122
- Uppercase hex only `[0-9A-F]`, format `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`
- Every UUID in profile must be unique — no duplicates
- Generate with `uuidgen` — **never use placeholders** like `12345678-1234-...`

### PayloadVersion — Required everywhere
- Must be `<integer>1</integer>` on EVERY dict (outer + each inner payload)
- Never use `<real>1.0</real>` — this is the #1 most common error

### PayloadScope — Required
- **Always `System`** unless user explicitly requests `User` scope
- Firewall, TCC, system extensions, and most payloads require system scope

### PayloadOrganization — Required
- Always include at top level (e.g., `Fleet Device Management`)
- Shows in MDM consoles for profile ownership traceability

### Plist validity
- Well-formed XML with declaration and DOCTYPE
- Validate: `plutil -lint <file>.mobileconfig`

### No deprecated APIs — macOS 13+ baseline
- **BANNED**: `com.apple.systempreferences` PayloadType, `EnabledPreferencePanes`, `DisabledPreferencePanes`, old pane IDs (`com.apple.preference.*`)
- For details on banned patterns and modern replacements, read `references/common-payload-types.md`

## Contour CLI (if available)

If `contour` is installed, use it for schema validation and generation:

```bash
command -v contour >/dev/null 2>&1 && contour profile validate <file>.mobileconfig
contour profile normalize <file>.mobileconfig   # Standardize identifiers
contour profile scan <file>.mobileconfig         # Show metadata
contour help-ai --sop profile                    # Full workflow reference
```

Don't assume contour is installed — always check first with `command -v contour`.

## Local References

Before starting, read `learnings.md` for accumulated knowledge from prior sessions.

Load these references only when the specific step requires them:

| When you need... | Read this file |
|---|---|
| Required/optional fields per Apple spec | `references/apple-schema-toplevel.yaml` and `references/apple-schema-common-payload-keys.yaml` |
| Valid PayloadType values, typos, deprecated types | `references/common-payload-types.md` |
| macOS 13+ System Settings extension IDs | `references/common-payload-types.md` (System Settings section) |
| TCC/PPPC schema | `references/apple-schema-com.apple.TCC.configuration-profile-policy.yaml` |
| BTM (login items) schema | `references/apple-schema-com.apple.servicemanagement.yaml` |
| System Extensions schema | `references/apple-schema-com.apple.system-extension-policy.yaml` |
| Firewall schema | `references/apple-schema-com.apple.security.firewall.yaml` |
| Starting template | `references/template.mobileconfig` |
| Full validation checklist | `references/validation-checklist.md` |

To add new payload schemas: download from the Apple device-management repo and save to `references/`.

## Creating a Profile

1. Gather requirements: settings to manage, scope (System default), org name
2. Generate UUIDs with `uuidgen` for each dict (top-level + each inner payload)
3. Build from `references/template.mobileconfig`
4. **Required top-level keys**: PayloadIdentifier, PayloadUUID, PayloadType (`Configuration`), PayloadVersion (`1`), PayloadDisplayName, PayloadScope (`System`), PayloadOrganization
5. **Required inner payload keys**: PayloadType, PayloadIdentifier, PayloadUUID, PayloadVersion, plus payload-specific keys
6. Validate in order: contour → plutil → manual checklist

## Reviewing a Profile

1. Parse the file
2. Check: PayloadIdentifier (reverse-DNS), PayloadUUID (valid hex), PayloadVersion (every dict), PayloadType (known + non-deprecated), plist format
3. Flag deprecated patterns with exact modern replacements
4. Offer to generate a fixed version

## Fleet GitOps Conventions

- Org prefix: `com.fleetdm`
- Profile ID pattern: `com.fleetdm.profiles.<descriptive-kebab-name>`
- CIS profiles: `com.fleetdm.<cis-benchmark-id>.check`
- Test profiles still need valid structure
- Validate against: Apple device-management repo + ProfileManifests

---

## Failure Patterns

| Pattern | Why It's Wrong | Fix |
|---------|----------------|-----|
| Bare UUID in PayloadIdentifier | Not reverse-DNS format | Use `com.org.profiles.name.uuid` |
| `<real>1.0</real>` for PayloadVersion | Apple expects integer | Change to `<integer>1</integer>` |
| Placeholder UUIDs (12345678-1234...) | Test values in production | Run `uuidgen` for each dict |
| Missing PayloadVersion in inner payload | Validation fails | Add `<key>PayloadVersion</key><integer>1</integer>` |
| Deprecated `com.apple.systempreferences` | Removed in macOS 13+ | Use specific restrictions per feature |
| Missing PayloadScope | Profile applies to wrong context | Add `System` (default) |
| Missing PayloadOrganization | Ownership unclear in MDM | Add org name |
| Duplicate PayloadUUIDs | Must be globally unique | Generate new UUID for each |
| Malformed UUID (lowercase, wrong format) | Must be uppercase `[0-9A-F]` | Use `uuidgen` output directly |

---

## Standard Verification

**Validation order** (run in this sequence):

### 1. contour validation (if available)
```bash
command -v contour >/dev/null 2>&1 && contour profile validate <file>.mobileconfig
```

### 2. plutil validation (REQUIRED)
```bash
plutil -lint <file>.mobileconfig
```

### 3. Manual checklist
- [ ] PayloadIdentifiers: all reverse-DNS format
- [ ] PayloadUUIDs: unique, uppercase hex, RFC 4122
- [ ] PayloadVersion: `<integer>1</integer>` on every dict
- [ ] PayloadScope: `System` (default) or `User` if explicitly requested
- [ ] PayloadOrganization: present at top level
- [ ] PayloadDisplayName: present and human-readable
- [ ] No placeholder UUIDs
- [ ] No deprecated PayloadTypes

---

## Capture Learnings

After every session, update `learnings.md`:
- **Failures** → new Issue entry (what broke, root cause, fix)
- **Successes** → new Observation entry (what worked, when to reuse)

## References

- Apple device-management profiles: https://github.com/apple/device-management/tree/release/mdm/profiles
- ProfileManifests (third-party payloads): https://github.com/ProfileManifests/ProfileManifests
- Fleet GitOps documentation: https://fleetdm.com/docs/configuration/yaml-files
