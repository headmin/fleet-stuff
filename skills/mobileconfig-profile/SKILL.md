---
name: mobileconfig-profile
description: "Expert at creating and validating Apple .mobileconfig files for macOS, iOS, and iPadOS. Use when working with MDM configuration profiles, managed preferences, or Fleet GitOps profiles."
---

# Apple Configuration Profile (.mobileconfig) Skill

Expert at creating and validating Apple `.mobileconfig` files for macOS, iOS, and iPadOS.

## When to Activate

- User creates, edits, or reviews a `.mobileconfig` file
- Mentions MDM profiles, configuration profiles, or managed preferences
- Asks about PayloadType, PayloadIdentifier, PayloadUUID, or profile structure
- References Fleet GitOps profile authoring

## Step 1: Read Context

Before starting, read these files for accumulated knowledge:
- Read `learnings.md` — known issues and patterns from prior sessions
- Read `references/validation-checklist.md` — quick pre-delivery checklist

### Optional: Check for contour CLI

If `contour` is installed, you can use it for validation and generation:

```bash
# Check if contour is available
command -v contour >/dev/null 2>&1 && echo "contour available"

# Quick reference
contour help-ai --sop profile          # Profile generation workflow
contour profile validate <file>.mobileconfig   # Validate against Apple schema
contour profile normalize <file>.mobileconfig  # Standardize identifiers
contour profile scan <file>.mobileconfig       # Show metadata
```

For detailed command help: `contour help-ai --command profile.<subcommand>`

Don't assume contour is installed — always check first with `command -v contour`.

## Step 2: Core Rules (Always Enforce)

### PayloadIdentifier — Reverse-DNS only
- **NEVER** use bare UUIDs. Always `com.<org>.profiles.<name>`
- Inner payloads: `com.<org>.profiles.<name>.<uuid-suffix>`
- Default org for Fleet: `com.fleetdm`

### PayloadUUID — Valid RFC 4122
- Uppercase hex only `[0-9A-F]`, format `XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`
- Every UUID in profile must be unique — no duplicates
- Generate with `uuidgen`

### PayloadVersion — Required everywhere
- Must be `<integer>1</integer>` on EVERY dict (outer + each inner payload)
- Never use `<real>1.0</real>` — this is the #1 most common error

### Plist validity
- Well-formed XML with declaration and DOCTYPE
- Validate: `plutil -lint <file>.mobileconfig`

### No deprecated APIs — macOS 13+ baseline
- **BANNED**: `com.apple.systempreferences` PayloadType, `EnabledPreferencePanes`, `DisabledPreferencePanes`, old pane IDs (`com.apple.preference.*`)
- For details on banned patterns and modern replacements, read `references/common-payload-types.md`

## Step 3: Look Up Details As Needed

Load these references only when the specific step requires them:

| When you need... | Read this file |
|---|---|
| Required/optional fields per Apple spec | `references/apple-schema-toplevel.yaml` and `references/apple-schema-common-payload-keys.yaml` |
| Valid PayloadType values, typos, deprecated types | `references/common-payload-types.md` |
| macOS 13+ System Settings extension IDs | `references/common-payload-types.md` (System Settings section) |
| SSO ExtensionIdentifier values | `references/common-payload-types.md` (SSO section) |
| TCC/PPPC (privacy preferences) schema | `references/apple-schema-com.apple.TCC.configuration-profile-policy.yaml` |
| BTM (background task management/login items) schema | `references/apple-schema-com.apple.servicemanagement.yaml` |
| System Extensions schema | `references/apple-schema-com.apple.system-extension-policy.yaml` |
| Firewall schema | `references/apple-schema-com.apple.security.firewall.yaml` |
| System Preferences restrictions schema | `references/apple-schema-com.apple.systempreferences.yaml` |
| Per-payload schema (other types) | `references/apple-schema-<payloadtype>.yaml` |
| Starting template for a new profile | `references/template.mobileconfig` |
| Full validation checklist before delivery | `references/validation-checklist.md` |

To add new payload schemas: download from `https://raw.githubusercontent.com/apple/device-management/release/mdm/profiles/<payloadtype>.yaml` and save to `references/`. Large schemas (wifi, SSO, restrictions) exceed the 300-line guideline — fetch on-demand rather than storing locally.

## Step 4: Create or Review

### Creating a New Profile

**IMPORTANT DEFAULTS:**
- **Always use `PayloadScope: System`** unless explicitly asked for User scope
- **Always include `PayloadOrganization`** - this is REQUIRED, not optional
- **Always generate real UUIDs** with `uuidgen` - never use placeholders

1. **Gather requirements**:
   - Settings to manage (firewall, TCC, system extensions, etc.)
   - Scope: **`System` (default)** for device-wide settings, `User` only if explicitly requested for per-user settings
   - Organization name (e.g., "Fleet Device Management") - **REQUIRED**
   - Descriptive profile name (e.g., "Firewall - Block All Incoming")

2. **Generate UUIDs**: Run `uuidgen` for each dict (top-level + each inner payload)
   ```bash
   uuidgen  # Use output directly - uppercase hex with dashes
   # Example output: 7A3B9C4D-5E6F-4A7B-8C9D-0E1F2A3B4C5D
   # NEVER use: 12345678-1234-1234-1234-123456789ABC (placeholder)
   ```

3. **Build from template**: Use `references/template.mobileconfig` as starting point

4. **REQUIRED top-level keys** (all profiles MUST have these):
   - `PayloadIdentifier`: `com.<org>.profiles.<descriptive-name>` (e.g., `com.fleetdm.profiles.firewall-block-incoming`)
   - `PayloadUUID`: Unique UUID from `uuidgen` (**NOT a placeholder**)
   - `PayloadType`: Always `Configuration`
   - `PayloadVersion`: Always `<integer>1</integer>`
   - `PayloadDisplayName`: Human-readable name (shows in System Settings)
   - `PayloadScope`: **`System`** (default unless user explicitly asks for `User`)
   - `PayloadOrganization`: **REQUIRED** - Organization name (e.g., "Fleet Device Management")
   - `PayloadDescription`: Recommended - Brief explanation of profile's purpose

5. **Inner payload keys** (each dict in PayloadContent array):
   - `PayloadType`: Specific type (e.g., `com.apple.security.firewall`)
   - `PayloadIdentifier`: `<top-level-id>.<uuid>` (e.g., `com.fleetdm.profiles.firewall-block-incoming.A1B2C3D4-...`)
   - `PayloadUUID`: Unique UUID from `uuidgen` (different from top-level)
   - `PayloadVersion`: Always `<integer>1</integer>`
   - Payload-specific keys (see `references/apple-schema-<type>.yaml`)

6. **Validate** in order: `contour validate` → `plutil -lint` → manual checklist

### Reviewing an Existing Profile
1. Parse the file
2. Check: PayloadIdentifier (reverse-DNS), PayloadUUID (valid hex), PayloadVersion (exists everywhere), PayloadType (known + non-deprecated), plist format
3. Flag deprecated patterns with exact modern replacements
4. Offer to generate a fixed version

## Step 5: Fleet-Specific Conventions

When in a Fleet GitOps context:
- Org prefix: `com.fleetdm`
- Profile ID pattern: `com.fleetdm.profiles.<descriptive-kebab-name>`
- CIS profiles: `com.fleetdm.<cis-benchmark-id>.check`
- Test profiles still need valid structure
- Validate against: Apple device-management repo + ProfileManifests

## Step 6: Capture Learnings

After every session, update `learnings.md`:
- **Failures** → new Issue entry (what broke, root cause, fix)
- **Successes** → new Observation entry (what worked, when to reuse)
- Always read `learnings.md` at start of next session

---

## Failure Patterns

Observable warning signs that indicate problems:

| Pattern | Why It's Wrong | Fix |
|---------|----------------|-----|
| Bare UUID in PayloadIdentifier | `<string>12345678-1234-...</string>` | Use reverse-DNS: `com.org.profiles.name.uuid` |
| `<real>1.0</real>` for PayloadVersion | Apple expects integer | Change to `<integer>1</integer>` |
| Placeholder UUIDs (12345678-1234...) | Test values left in production | Run `uuidgen` for each dict |
| Missing PayloadVersion in inner payload | Validation fails | Add `<key>PayloadVersion</key><integer>1</integer>` |
| Deprecated `com.apple.systempreferences` | Removed in macOS 13+ | Use `com.apple.systempreferences` payload for lock-only or remove |
| Missing PayloadScope | Profile applies to wrong context | **Always add** `<key>PayloadScope</key><string>System</string>` (default) |
| PayloadScope set to User | Most settings require System scope | Use `System` unless explicitly requested otherwise |
| Duplicate PayloadUUIDs | UUIDs must be globally unique | Generate new UUID for each occurrence |
| Missing PayloadOrganization | **REQUIRED** - ownership unclear in MDM | **Always add** `<key>PayloadOrganization</key><string>Fleet Device Management</string>` |
| Malformed UUID (lowercase, wrong format) | Must be uppercase `[0-9A-F]` with dashes | Use `uuidgen` output directly |

**Common slip-ups:**
- Copying example profiles without regenerating UUIDs
- Forgetting PayloadVersion on inner payloads (only checking top-level)
- Using deprecated PayloadTypes without checking Apple device-management repo
- Not setting PayloadScope when profile targets system-level settings

---

## Standard Verification

**Validation order** (run in this sequence):

### 1. contour validation (optional, if available)
```bash
# Check if contour is installed
command -v contour >/dev/null 2>&1 && contour profile validate <file>.mobileconfig
```

**What contour catches:**
- XML schema violations against Apple device-management specs
- Deprecated PayloadTypes
- Missing required keys
- Invalid key types (string vs integer vs boolean)
- Payload-specific validation rules
- Convention violations (identifier format, UUID format)

**If contour catches issues, fix them before proceeding to plutil.**

### 2. plutil validation (REQUIRED - built-in safety check)
```bash
# macOS built-in plist validator - always run this
plutil -lint <file>.mobileconfig
```

**What plutil catches:**
- XML syntax errors
- Malformed plist structure
- Invalid DOCTYPE
- Basic plist format violations

**plutil must pass before proceeding to manual checks.**

### 3. Manual skill checklist

After automated validation passes, verify:

- [ ] **PayloadIdentifiers**: All use reverse-DNS format (no bare UUIDs)
- [ ] **PayloadUUIDs**: All are unique, uppercase hex, RFC 4122 format (`uuidgen` output)
- [ ] **PayloadVersion**: Present on EVERY dict (top-level + each inner payload) as `<integer>1</integer>`
- [ ] **PayloadScope**: **REQUIRED** - Set to `System` (default) unless user explicitly requested `User`
- [ ] **PayloadOrganization**: **REQUIRED** - Present at top level (e.g., `Fleet Device Management`)
- [ ] **PayloadDescription**: Recommended - Brief explanation of profile purpose
- [ ] **No placeholder UUIDs**: No `12345678-1234-1234-1234-123456789ABC` or `00000000-0000-0000-0000-000000000000` patterns
- [ ] **PayloadDisplayName**: Present and human-readable (shows in System Settings)

### 4. Production readiness

- [ ] Profile tested in MDM preview/test environment before fleet deployment
- [ ] Profile scoped correctly (device channel vs user channel)
- [ ] PayloadIdentifier follows org naming convention (e.g., `com.fleetdm.profiles.<name>`)
- [ ] Documented in Fleet GitOps YAML if applicable
- [ ] Reviewed against `references/validation-checklist.md`
