# Learnings & Rules

Observations from real-world Fleet DDM declaration authoring. Update this file as new patterns emerge.

---

## Rules (Hard Constraints)

### Rule #1: No ServerToken in User-Authored Files

**What failed**: Including `ServerToken` in a DDM JSON file caused Fleet to reject or mishandle the declaration.
**Fix**: Never include `ServerToken`. Fleet generates it automatically from a hash of the JSON contents plus secrets timestamp.
**How to apply**: Validate every declaration JSON before delivery — the validation script checks for this.

### Rule #2: Only com.apple.configuration.* Types

**What failed**: Submitting a `com.apple.activation.simple` declaration was rejected by Fleet.
**Fix**: Fleet only accepts `com.apple.configuration.*` types. Activations, assets, and management declarations are not supported.
**How to apply**: Always verify the Type prefix before creating a declaration.

### Rule #3: DDM and .mobileconfig Share the Same GitOps Key

**What failed**: Looking for a separate `declarations:` key in GitOps YAML.
**Fix**: DDM JSON files go in the same `configuration_profiles` list as .mobileconfig files. Fleet differentiates by file content (JSON vs XML), not by config key.
**How to apply**: Add DDM declarations to `controls.macos_settings.custom_settings` alongside .mobileconfig paths.

### Rule #4: PascalCase Payload Keys

**What failed**: Using `require_alphanumeric_passcode` (snake_case) instead of `RequireAlphanumericPasscode` (PascalCase).
**Fix**: DDM payload keys are always PascalCase. Check against Apple's schema YAML files.
**How to apply**: When looking up keys, always use the Apple schema as the source of truth.

---

## Observations (Soft Learnings)

### Observation #1: DDM Combine Semantics

**What worked**: Understanding that multiple DDM declarations of the same Type merge their payloads using per-key combine rules (boolean-or, number-max, etc.). This is different from .mobileconfig where last profile wins.
**When to apply**: When a user asks about conflicting declarations — explain the merge behavior.

### Rule #5: FLEET_MDM_ALLOW_ALL_DECLARATIONS (v4.83+)

**What changed**: Fleet 4.83 added `FLEET_MDM_ALLOW_ALL_DECLARATIONS` server flag (#38366). When enabled, all Apple declaration types are accepted — including the 12 forbidden types, activations, assets, and management declarations.
**Fix**: Default behavior is unchanged (forbidden types still blocked). Only mention this flag when a user specifically needs a forbidden type. Cloud customers must request Fleet enable it.
**How to apply**: If a user hits "Only configuration declarations that don't require an asset reference are supported" error and genuinely needs that type, suggest the flag. A follow-up (#38986) plans to make all types available by default.

---

## Template

```markdown
### Rule/Observation #N: Short Title

**What failed/worked**: Description.
**Fix/When to apply**: How to prevent/replicate.
**How to apply**: When this applies.
```
