---
name: windows-csp-profile
description: "Expert at creating and validating Windows CSP profile XML files for Fleet GitOps. Use when working with Windows MDM, SyncML, or Fleet Windows profiles."
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

---

## Failure Patterns

Observable warning signs that indicate problems:

| Pattern | Why It's Wrong | Fix |
|---------|----------------|-----|
| `<?xml version="1.0"?>` present | Fleet classifies as macOS profile | Remove XML declaration entirely |
| `<SyncML>` or `<SyncBody>` wrapper | Fleet wraps fragments itself | Remove envelope, start with `<Replace>` or `<Add>` |
| `<Atomic>` with other top-level elements | Atomic must be sole top-level element | Move everything inside `<Atomic>` or remove it |
| `<Delete>` anywhere | Not supported by Fleet | Remove `<Delete>` commands |
| Processing instruction `<?target?>` | Forbidden by Fleet validator | Remove all processing instructions |
| Missing `xmlns="syncml:metinf"` in `<Format>` | Validation fails | Add namespace: `<Format xmlns="syncml:metinf">int</Format>` |
| Wrong data type (`chr` vs `int`) | CSP rejects value | Check Microsoft CSP docs for exact type |
| Trailing slash in LocURI | Path matching may fail | Remove: `./Device/.../Setting` not `.../Setting/` |
| Reserved LocURI used | Conflicts with Fleet built-ins | Use Fleet's UI settings or avoid reserved paths |
| Incorrect case in OMA-URI | Paths are case-sensitive | Match exact case from Microsoft docs |

**Common slip-ups:**
- Copying full SyncML examples from Microsoft docs (they include envelope)
- Using `<Delete>` inside `<Atomic>` (forbidden)
- Forgetting the `syncml:metinf` namespace on `<Format>`
- Using BitLocker or Update LocURIs instead of Fleet's built-in settings

---

## Standard Verification

**Validation order** (run in this sequence):

### 1. XML well-formedness check
```bash
# Use xmllint to check basic XML structure
xmllint --noout <file>.xml 2>&1
```

**What xmllint catches:**
- Malformed XML tags
- Unclosed elements
- Invalid character encoding
- Namespace errors

**xmllint must pass before proceeding.**

### 2. Fleet validator (if available)
```bash
# Fleet's built-in Windows profile validator (if you have Fleet locally)
# This runs the same checks Fleet server does
./scripts/validate-windows-profile.sh <file>.xml
```

**What Fleet validator catches:**
- XML declaration present
- SyncML envelope present
- Invalid top-level elements
- `<Delete>` commands
- Processing instructions
- Atomic rule violations

### 3. Manual skill checklist

After validation passes, verify:

- [ ] **No XML declaration**: File does NOT start with `<?xml version="1.0"?>`
- [ ] **No SyncML envelope**: No `<SyncML>`, `<SyncHdr>`, or `<SyncBody>` wrappers
- [ ] **Valid top-level elements**: Only `<Replace>`, `<Add>`, `<Atomic>`, or `<Exec>`
- [ ] **Atomic isolation**: If `<Atomic>` present, it's the ONLY top-level element
- [ ] **No Delete commands**: No `<Delete>` anywhere in the file
- [ ] **Format namespace**: All `<Format>` tags include `xmlns="syncml:metinf"`
- [ ] **Correct data types**: `<Format>` type matches CSP requirements (int/bool/chr/xml)
- [ ] **Valid LocURIs**: All paths start with `./Device/Vendor/MSFT/` or `./User/Vendor/MSFT/`
- [ ] **No reserved paths**: Not using BitLocker or Update LocURIs (unless intentional override)
- [ ] **Case-sensitive paths**: OMA-URI paths match exact case from Microsoft CSP docs
- [ ] **No trailing slashes**: LocURI paths don't end with `/`

### 4. Production readiness

- [ ] Tested on Windows test device via Fleet MDM
- [ ] Fleet variable substitution tested if used (`$FLEET_VAR_*`)
- [ ] Label targeting configured correctly in Fleet GitOps YAML
- [ ] File placed in `platforms/windows/configuration-profiles/` directory
- [ ] Descriptive filename (e.g., "Enable Windows Firewall.xml")
- [ ] Documented purpose in Fleet GitOps comments or team README
