---
name: windows-csp-profile
description: Help with Windows CSP profile XML files (SyncML fragments) — creating, validating, and reviewing for Fleet GitOps Windows MDM deployment.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash, WebFetch
effort: high
---

You are helping with Windows MDM configuration profiles (SyncML XML): $ARGUMENTS

Focus on validation against Microsoft CSP documentation and Fleet's SyncML fragment constraints. Apply the following rules for all work.

## Core Rules

### SyncML fragments only — no envelope, no XML declaration
Fleet profiles are SyncML **body fragments**. They must NOT contain:
- `<?xml version="1.0"?>` — Fleet classifies files with XML declarations as macOS profiles
- `<SyncML>`, `<SyncHdr>`, `<SyncBody>` — Fleet wraps the fragment itself

Start directly with `<Replace>`, `<Add>`, `<Atomic>`, or `<!-- comment -->`.

### Valid top-level elements
Only four elements allowed at top level:
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
Paths are case-sensitive with no trailing slash.

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

## Local References

Before starting, read `learnings.md` for accumulated knowledge from prior sessions.

| When you need... | Read this file |
|---|---|
| Common CSP URIs and data types | `references/common-csp-settings.md` |
| Fleet variable substitution | `references/fleet-variables.md` |
| Template (single setting) | `references/template-single.xml` |
| Template (multi-setting) | `references/template-multi.xml` |
| Template (atomic) | `references/template-atomic.xml` |
| Full validation checklist | `references/validation-checklist.md` |

## Creating a Profile

1. Ask: settings to manage, scope (Device/User), atomic or non-atomic
2. Verify LocURIs are not reserved by Fleet
3. Build from appropriate template
4. Look up exact OMA-URI paths and data types in Microsoft CSP docs
5. Validate: xmllint → manual checklist

## Reviewing a Profile

1. Parse the XML
2. Check: no XML declaration, no SyncML envelope, valid top-level elements, atomic rules, no reserved LocURIs, no `<Delete>`
3. Verify data types match CSP expectations
4. Flag issues with fix recommendations

## Fleet GitOps Integration

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

---

## Failure Patterns

| Pattern | Why It's Wrong | Fix |
|---------|----------------|-----|
| `<?xml version="1.0"?>` present | Fleet classifies as macOS profile | Remove XML declaration entirely |
| `<SyncML>` or `<SyncBody>` wrapper | Fleet wraps fragments itself | Remove envelope, start with `<Replace>` or `<Add>` |
| `<Atomic>` with sibling elements | Atomic must be sole top-level element | Move everything inside `<Atomic>` or remove it |
| `<Delete>` anywhere | Not supported by Fleet | Remove `<Delete>` commands |
| Processing instruction `<?target?>` | Forbidden by Fleet validator | Remove all processing instructions |
| Missing `xmlns="syncml:metinf"` in Format | Validation fails | Add namespace to all `<Format>` tags |
| Wrong data type (`chr` vs `int`) | CSP rejects value | Check Microsoft CSP docs for exact type |
| Trailing slash in LocURI | Path matching may fail | Remove trailing slash |
| Reserved LocURI used | Conflicts with Fleet built-ins | Use Fleet's UI settings instead |
| Incorrect case in OMA-URI | Paths are case-sensitive | Match exact case from Microsoft docs |

---

## Standard Verification

**Validation order** (run in this sequence):

### 1. XML well-formedness (REQUIRED)
```bash
xmllint --noout <file>.xml 2>&1
```

### 2. Manual checklist
- [ ] No XML declaration (`<?xml ...?>`)
- [ ] No SyncML envelope (`<SyncML>`, `<SyncBody>`)
- [ ] Valid top-level elements only (`<Replace>`, `<Add>`, `<Atomic>`, `<Exec>`)
- [ ] Atomic isolation (if present, sole top-level element)
- [ ] No `<Delete>` commands
- [ ] Format namespace on all `<Format>` tags
- [ ] Correct data types per CSP docs
- [ ] Valid LocURIs (correct prefix, case, no trailing slash)
- [ ] No reserved paths (BitLocker, Update)

---

## Capture Learnings

After every session, update `learnings.md`:
- **Failures** → new Rule entry (what broke, fix, when to check)
- **Successes** → new Observation entry (what worked, when to reuse)

## References

- Microsoft CSP reference: https://learn.microsoft.com/en-us/windows/client-management/mdm/
- Policy CSP: https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-configuration-service-provider
- CSP support matrix: https://learn.microsoft.com/en-us/windows/client-management/mdm/configuration-service-provider-support
- Fleet GitOps documentation: https://fleetdm.com/docs/configuration/yaml-files
