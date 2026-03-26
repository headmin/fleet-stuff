---
description: "Expert at creating and validating Windows CSP profile XML files for Fleet GitOps."
---

# Windows CSP Profile (SyncML) Skill

Expert at creating and validating Windows MDM configuration profiles using OMA-DM SyncML fragments for Fleet GitOps.

## When to Activate

- User creates, edits, or reviews a Windows MDM `.xml` profile
- Mentions Windows CSP, OMA-URI, SyncML, or Windows configuration profiles
- Asks about Group Policy via MDM, ADMX-backed policies, or Windows security settings
- Needs a Windows profile for Fleet GitOps
- Mentions specific CSPs: BitLocker, Firewall, Defender, DeviceLock, WiFi, Update

## Step 1: Read Context

Before starting, read these for accumulated knowledge:
- Read `learnings.md` — known gotchas and patterns from prior sessions

## Step 2: Core Rules (Always Enforce)

### SyncML fragments only — no envelope, no XML declaration
Fleet profiles are SyncML **body fragments**. They must NOT contain:
- `<?xml version="1.0"?>` — this makes Fleet classify the file as macOS
- `<SyncML>`, `<SyncHdr>`, `<SyncBody>` — Fleet wraps the fragment itself

Start directly with `<Replace>`, `<Add>`, `<Atomic>`, or `<!-- comment -->`.

### Valid top-level elements
Only four elements are allowed at the top level:
- `<Replace>` — modify an existing setting (most common)
- `<Add>` — create a new setting
- `<Atomic>` — all-or-nothing bundle (must be sole top-level element if present)
- `<Exec>` — only for SCEP certificate enrollment profiles

### Atomic rules
If `<Atomic>` is the first top-level element, it MUST be the ONLY top-level element. No `<Delete>` inside `<Atomic>`.

### OMA-URI path format
```
./Device/Vendor/MSFT/{CSPName}/{SettingPath}
./User/Vendor/MSFT/{CSPName}/{SettingPath}
```
Some CSPs accept `./Vendor/MSFT/` without Device/User prefix. Paths are case-sensitive with no trailing slash.

### Data types in `<Format>`
Always include the namespace: `<Format xmlns="syncml:metinf">{type}</Format>`

Valid types: `int`, `bool`, `chr` (string), `xml`, `node`, `bin`, `null`

### Reserved LocURIs (Fleet manages these)
- `/Vendor/MSFT/BitLocker` — use Fleet's built-in BitLocker settings
- `/Vendor/MSFT/Policy/Config/Update` — use Fleet's `windows_updates` (unless `enableCustomOSUpdates`)

### No `<Delete>` command
`<Delete>` is not valid as a top-level element or inside `<Atomic>`.

### No processing instructions
XML processing instructions (`<?target inst?>`) are forbidden by Fleet's validator.

## Step 3: Look Up Details As Needed

| When you need... | Read this file |
|---|---|
| Common CSP URIs and data types | `references/common-csp-settings.md` |
| Fleet variable substitution | `references/fleet-variables.md` |
| SCEP profile structure | `references/scep-profile.md` |
| Starting template (single setting) | `references/template-single.xml` |
| Starting template (multi-setting) | `references/template-multi.xml` |
| Starting template (atomic) | `references/template-atomic.xml` |
| Full validation checklist | `references/validation-checklist.md` |

### External references
- Microsoft CSP reference: https://learn.microsoft.com/en-us/windows/client-management/mdm/
- Policy CSP (largest): https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-configuration-service-provider
- CSP support matrix: https://learn.microsoft.com/en-us/windows/client-management/mdm/configuration-service-provider-support
- Fleet Windows profile examples: `docs/solutions/windows/configuration-profiles/` in the Fleet repo

## Step 4: Create or Review

### Creating a New Profile
1. Ask: what settings to manage, scope (Device/User), atomic or non-atomic
2. Verify LocURIs are not reserved by Fleet
3. Build from the appropriate template (`template-single.xml`, `template-multi.xml`, or `template-atomic.xml`)
4. Look up exact OMA-URI paths and data types in Microsoft CSP docs
5. Validate using `scripts/validate-windows-profile.sh`

### Reviewing an Existing Profile
1. Parse the XML
2. Check: no XML declaration, no SyncML envelope, valid top-level elements, atomic rules followed, no reserved LocURIs, no `<Delete>`
3. Verify data types match CSP expectations
4. Run `scripts/validate-windows-profile.sh <file>`

## Step 5: Fleet GitOps Integration

Windows profiles go under `windows_settings.custom_settings`:

```yaml
controls:
  windows_settings:
    custom_settings:
      - path: ../platforms/windows/configuration-profiles/Enable firewall.xml
        labels_include_any:
          - Windows 11
```

Label targeting supports: `labels_include_all`, `labels_include_any`, `labels_exclude_any` (one mode per profile).

**Directory convention:** `platforms/windows/configuration-profiles/`
**File naming:** Descriptive with `.xml` extension (e.g., `Enable firewall.xml`)

## Step 6: Capture Learnings

After every session, update `learnings.md`:
- **Failures** → new Rule entry (what broke, fix, when to check)
- **Successes** → new Observation entry (what worked, when to reuse)
