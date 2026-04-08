# Learnings & Rules

Observations from real-world Fleet GitOps authoring. Update this file as new patterns emerge — both failures and successes.

---

## Rules (Hard Constraints)

### Rule #1: Missing Keys = Silent Deletion

**What failed**: Omitting a key like `software:` from a fleet YAML caused all existing software for that fleet to be deleted on next GitOps run.
**Fix**: Always include all required top-level keys in every YAML file, even if the value is empty (`software:` with nothing below it).
**How to apply**: Before saving any fleet YAML, run through the required keys checklist: `name`, `policies`, `reports`, `agent_options`, `controls`, `software`, `settings`.

### Rule #2: Misspelled Keys Silently Reset

**What failed**: Typing `policy:` instead of `policies:` caused all policies to be deleted. No error from `fleetctl gitops`.
**Fix**: Always use exact key names from the schema. Copy from reference, don't type from memory.
**How to apply**: Validate YAML keys against `references/yaml-schema.md` before committing.

### Rule #3: Fleet Rename = Fleet Deletion

**What failed**: Renaming a fleet in YAML only (without first renaming in UI) caused the old fleet to be deleted and hosts moved to "Unassigned", losing all their settings.
**Fix**: Always rename in the Fleet UI first, then update YAML to match.
**How to apply**: When user asks to rename a fleet, warn them about this ordering requirement.

### Rule #4: Labels Must Be Declared Before Referenced

**What failed**: Referencing a label in `labels_include_any` on a policy, but not defining it in the `labels:` section, caused a GitOps error.
**Fix**: Any label used in policies, reports, or software MUST also appear in the `labels:` section of the same file or global config.
**How to apply**: After adding label targeting to any section, verify the label exists in `labels:`.

### Rule #5: Array vs Object Path Syntax

**What failed**: Using `- path:` (with dash) for `agent_options` caused a parse error. Using `path:` (without dash) for `policies` also failed.
**Fix**: Arrays (policies, reports, labels) use `- path:`. Objects (agent_options) use `path:` without dash.
**How to apply**: Check the type before writing the reference pattern.

### Rule #6: Policy Automations Scope

**What failed**: Adding `install_software` or `run_script` to a global policy (in `default.yml`) caused an error.
**Fix**: Policy automations can only be configured for fleet-level or unassigned policies.
**How to apply**: If the user wants policy automations, the policy must be in `fleets/fleet-name.yml` or `fleets/unassigned.yml`.

### Rule #7: app_store_id Must Be Quoted

**What failed**: `app_store_id: 1091189122` (without quotes) was interpreted as an integer, causing a type error.
**Fix**: Always quote `app_store_id: "1091189122"`.
**How to apply**: Any numeric-looking string value in YAML should be quoted.

### Rule #8: version Must Be Quoted

**What failed**: `version: 4.47.65` was parsed as a float, truncating the patch version.
**Fix**: Always quote version strings: `version: "4.47.65"`.
**How to apply**: Quote all version numbers in YAML.

### Rule #9: hostname Identifier is Deprecated

**What failed**: Using `hostname` in manual labels triggered a deprecation warning and may fail in future Fleet versions.
**Fix**: Use `id`, `hardware_serial`, or `uuid` instead.
**How to apply**: When creating manual labels, always use hardware_serial or uuid.

### Rule #10: Single install_software Package Syntax

**What failed**: Specifying a single package without a list for `install_software` triggered a deprecation warning.
**Fix**: Always use a list even for a single package (as of Fleet 4.73+).
**How to apply**: Use `package_path` pointing to a YAML file, and ensure the YAML uses list format.

### Rule #11: teams→fleets, queries→reports Rename (v4.82+)

**What changed**: Fleet 4.82 (Mar 2026) renamed "teams" to "fleets" and "queries" to "reports" across the entire product — UI, API, CLI, and GitOps YAML. The old API field names are deprecated.
**Fix**: Use `fleets/` directory names, `reports:` key in YAML, and new API field names. Old names will trigger deprecation warnings and may break in future versions.
**How to apply**: When reviewing or creating GitOps YAML, always use the new terminology. If a user mentions "teams" or "queries", translate to "fleets" and "reports".

### Rule #12: no-team.yml Deprecated → Use unassigned.yml

**What changed**: `no-team.yml` was deprecated in v4.82 in favor of `unassigned.yml`. Removing `no-team.yml` from the repo now correctly clears those settings.
**Fix**: Rename `no-team.yml` to `unassigned.yml` in the GitOps repo.
**How to apply**: Always use `unassigned.yml` for hosts not assigned to any fleet. Warn users if they still reference `no-team.yml`.

### Rule #13: Label Rename = Label Deletion

**What changed**: v4.82 added a warning that renaming a label in GitOps implies a delete operation. The old label is deleted and a new one is created.
**Fix**: Warn users explicitly before renaming labels that hosts will lose the old label and need to re-match the new one.
**How to apply**: When a user asks to rename a label, explain the deletion implication first.

### Rule #14: Software Fields Moved to Fleet Level

**What changed**: v4.81+ moved `self_service`, `labels_include_any`, `labels_exclude_any`, `categories`, and `setup_experience` from package-level YAML to fleet-level. Setting them at package level in a separate YAML file while also setting at fleet level causes silent ignore.
**Fix**: Set these fields at the fleet level (in the fleet YAML), not inside individual software package YAML files.
**How to apply**: When creating software entries, always place targeting/category fields at fleet level.

### Rule #15: $FLEET_SECRET in XML Profiles Must Be Escaped

**What failed**: GitOps failed when `$FLEET_SECRET` contained XML special characters (`<`, `>`, `&`, `"`, `'`) inside `.mobileconfig` XML files.
**Fix**: Fixed in v4.78+ — Fleet now properly escapes XML characters. But `<data>` field secrets also had issues (fixed in v4.78).
**How to apply**: Ensure you're on Fleet 4.78+ if using `$FLEET_SECRET` in XML profiles.

### Rule #16: Dry Run Skips Secret Validation

**What changed**: v4.82 stopped validating Fleet secrets in install/uninstall scripts during `fleetctl gitops --dry-run`. Secrets are validated on the GitOps side.
**Fix**: Dry runs will now succeed even if `$FLEET_SECRET_*` variables are not yet configured.
**How to apply**: Don't rely on dry-run to catch missing secrets — verify secrets are configured separately.

### Rule #17: FMA Overrides Allowed in GitOps

**What changed**: v4.78+ allows overriding install/uninstall scripts and specifying pre-install queries and post-install scripts for Fleet-maintained apps in GitOps.
**Fix**: Use the standard software package fields (`install_script`, `uninstall_script`, `pre_install_query`, `post_install_script`) alongside the FMA `slug`.
**How to apply**: When a user needs custom behavior for an FMA, they can override scripts without creating a custom package.

### Rule #18: Profile Removal From default.yml Now Works

**What changed**: v4.82 fixed a bug where removing custom profiles from `default.yml` and running `fleetctl gitops` wouldn't actually delete the profiles.
**Fix**: Profiles are now correctly removed when deleted from YAML. This is the expected behavior.
**How to apply**: No workaround needed on v4.82+. On older versions, profiles may need to be manually deleted via API.

### Rule #19: Non-Atomic Windows Profiles

**What changed**: v4.81 added support for specifying non-atomic Windows MDM profiles in GitOps YAML.
**Fix**: Use the profile-level setting to mark Windows profiles as non-atomic when needed.
**How to apply**: For Windows profiles that need granular payload-level error handling, use the non-atomic flag.

### Rule #20: update_new_hosts for macOS Updates

**What changed**: v4.82 fixed GitOps not respecting `update_new_hosts` for macOS updates. Also defaults to the correct value if not explicitly set.
**Fix**: The field now works as documented. Set it explicitly to avoid relying on default behavior.
**How to apply**: When configuring macOS OS update enforcement, always set `update_new_hosts` explicitly.

### Rule #21: enable_software_inventory Defaults to True

**What changed**: v4.78+ defaults `enable_software_inventory` to `true` if missing from GitOps config, preventing accidental disable.
**Fix**: You no longer need to explicitly set it unless you want to disable it.
**How to apply**: Safe to omit from config; it defaults to enabled.

### Rule #22: FLEET_MDM_ALLOW_ALL_DECLARATIONS (v4.83+)

**What changed**: v4.83 added `FLEET_MDM_ALLOW_ALL_DECLARATIONS` server flag (#38366). When enabled, bypasses all DDM type restrictions — the 12 forbidden types (account.mail, security.certificate, etc.), activations, assets, and management declarations are all accepted. Default behavior unchanged (forbidden types still blocked).
**Fix**: Self-hosted users set the env var. Cloud customers must request Fleet enable it. Follow-up #38986 plans to allow all types by default.
**How to apply**: If a user's DDM declaration is rejected with "Only configuration declarations that don't require an asset reference are supported" and they genuinely need that type, suggest this flag. Otherwise, keep using .mobileconfig as a fallback.

---

## Observations (Soft Learnings)

### Observation #1: Fleet-Maintained Apps Save Time

**What worked**: Using `fleet_maintained_apps` with a `slug` instead of custom packages for common software (Slack, Chrome, Firefox). Fleet handles install/uninstall scripts and auto-updates.
**When to apply**: Always check the Fleet-maintained app catalog before creating custom packages.

### Observation #2: Dry Runs Catch Most Errors

**What worked**: Running `fleetctl gitops --dry-run` before applying catches YAML errors, missing labels, scope violations.
**When to apply**: Always recommend dry run before applying changes.

### Observation #3: Separate Files Are Easier to Review

**What worked**: Splitting policies, reports, and labels into separate `platforms/*.yml` files made PRs more reviewable and reduced merge conflicts.
**When to apply**: For repos with >5 policies or >3 fleets, recommend separate files.

### Observation #4: CA Variables Pass Dry-Run But Fail on Apply

**What worked around**: If `$FLEET_VAR_DIGICERT_DATA_<CA_NAME>` or other CA variables don't exist, dry runs succeed but actual runs fail.
**When to apply**: Warn users that CA-dependent profiles will fail silently in dry run if the CA isn't configured. See also Rule #16 (dry run skips secret validation).

### Observation #5: labels Key Deletion Behavior

**What worked**: Omitting the `labels:` key entirely (not present in YAML) leaves existing labels untouched. Including an empty `labels:` deletes all labels.
**When to apply**: If the user doesn't want to manage labels via GitOps, omit the key completely.

---

## Template: Adding New Learnings

When something fails or succeeds unexpectedly, add it here:

```markdown
### Rule/Observation #N: Short Title

**What failed/worked**: Description of what happened.
**Fix/When to apply**: How to prevent/replicate this.
**How to apply**: When this rule should be checked.
```
