# Learnings & Rules

Observations from real-world Fleet Windows CSP profile authoring. Update this file as new patterns emerge.

---

## Rules (Hard Constraints)

### Rule #1: No XML Declaration

**What failed**: Starting a Windows profile with `<?xml version="1.0"?>` caused Fleet to classify it as a macOS profile.
**Fix**: Never include XML declarations. Start directly with `<Replace>`, `<Add>`, `<Atomic>`, or `<!-- comment -->`.
**How to apply**: First line of every Windows profile must be a SyncML command element, not an XML prolog.

### Rule #2: No SyncML Envelope

**What failed**: Wrapping profile content in `<SyncML><SyncBody>...</SyncBody></SyncML>` caused rejection.
**Fix**: Fleet wraps the fragment into a SyncML message itself. Only provide the body content (Replace/Add/Atomic/Exec elements).
**How to apply**: Never include SyncML, SyncHdr, or SyncBody elements.

### Rule #3: BitLocker LocURIs Are Reserved

**What failed**: Custom profile with `/Vendor/MSFT/BitLocker` LocURIs was rejected by Fleet.
**Fix**: Use Fleet's built-in `enable_disk_encryption` setting instead of custom BitLocker CSP profiles.
**How to apply**: Always check the reserved LocURI list before creating a profile.

### Rule #4: Atomic Must Be Sole Top-Level Element

**What failed**: Profile with `<Atomic>` followed by `<Replace>` at top level was rejected.
**Fix**: If `<Atomic>` is the first element, it must contain ALL other elements. No siblings allowed.
**How to apply**: Choose either all-atomic or all-non-atomic. Don't mix.

### Rule #5: No Delete Command

**What failed**: Using `<Delete>` in a profile to remove a setting was rejected.
**Fix**: `<Delete>` is not valid in Fleet profiles — neither at top level nor inside `<Atomic>`.
**How to apply**: To remove settings, remove the profile entirely or use `<Replace>` with a default/empty value.

### Rule #6: Format Namespace Required

**What failed**: `<Format>int</Format>` without namespace caused parsing issues.
**Fix**: Always include the full namespace: `<Format xmlns="syncml:metinf">int</Format>`.
**How to apply**: Every `<Meta>` block with a Format element needs the syncml:metinf namespace.

---

## Observations (Soft Learnings)

### Observation #1: Fleet Has 43 Example Profiles

**What worked**: The Fleet repo at `docs/solutions/windows/configuration-profiles/` contains 43 production-ready Windows profiles covering firewall, Defender, security policies, and more.
**When to apply**: Always check these examples before authoring a new profile from scratch.

### Observation #2: Non-Atomic Is Usually Fine

**What worked**: Most Fleet Windows profiles in the docs use non-atomic (multiple `<Replace>` at top level). Atomic is only needed when settings must succeed or fail together.
**When to apply**: Default to non-atomic unless the user specifically needs all-or-nothing semantics.

---

## Template

```markdown
### Rule/Observation #N: Short Title

**What failed/worked**: Description.
**Fix/When to apply**: How to prevent/replicate.
**How to apply**: When this applies.
```
