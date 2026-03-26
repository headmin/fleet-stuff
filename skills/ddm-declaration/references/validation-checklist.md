# DDM Declaration Validation Checklist

Run through before delivering any declaration JSON file.

## Structure
- [ ] Valid JSON (parseable)
- [ ] Has `Type` key (string)
- [ ] Has `Identifier` key (string)
- [ ] Has `Payload` key (object)
- [ ] No `ServerToken` key (Fleet generates this)
- [ ] No extra top-level keys beyond Type, Identifier, Payload

## Type
- [ ] Starts with `com.apple.configuration.`
- [ ] Not in forbidden list (account.*, screensharing.connection, security.*, services.configuration-files, watch.enrollment)
- [ ] Not `management.status-subscriptions` (always blocked)
- [ ] If `softwareupdate.enforcement.specific` — confirm `allowCustomOSUpdatesAndFileVault` is enabled

## Identifier
- [ ] Reverse-DNS format (e.g., `com.fleetdm.config.passcode.settings`)
- [ ] Max 64 UTF-8 bytes
- [ ] Unique within the fleet/team

## Payload
- [ ] Keys are PascalCase (DDM convention)
- [ ] Values match expected types from Apple schema (string, integer, boolean, array, dictionary)
- [ ] No unknown keys (check against Apple's schema YAML)

## Fleet Integration
- [ ] File has `.json` extension
- [ ] Referenced in GitOps YAML under `controls.macos_settings.custom_settings` (or ios/ipados equivalent)
- [ ] Path in YAML is relative-correct
- [ ] Labels referenced in profile are defined in `labels:` section

## Automated validation
```bash
scripts/validate-ddm-declaration.sh <file.json>
```
