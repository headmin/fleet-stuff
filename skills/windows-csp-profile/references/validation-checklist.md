# Windows CSP Profile Validation Checklist

Run through before delivering any Windows CSP profile XML file.

## Structure
- [ ] No `<?xml version="1.0"?>` declaration (Fleet would classify as macOS)
- [ ] No `<SyncML>`, `<SyncHdr>`, or `<SyncBody>` envelope
- [ ] No XML processing instructions (`<?target?>`)
- [ ] Only valid top-level elements: `<Replace>`, `<Add>`, `<Atomic>`, `<Exec>` (SCEP only)
- [ ] If `<Atomic>` is first, it is the ONLY top-level element
- [ ] No `<Delete>` elements anywhere (not valid in Fleet profiles)
- [ ] Well-formed XML

## OMA-URI
- [ ] Every `<LocURI>` starts with `./Device/Vendor/MSFT/`, `./User/Vendor/MSFT/`, or `./Vendor/MSFT/`
- [ ] Paths are case-sensitive and correct
- [ ] No trailing slashes
- [ ] No reserved Fleet LocURIs (`/Vendor/MSFT/BitLocker`, `/Vendor/MSFT/Policy/Config/Update`)

## Data
- [ ] Every `<Item>` with `<Replace>` or `<Add>` has a `<Data>` element
- [ ] `<Format xmlns="syncml:metinf">` includes the namespace declaration
- [ ] Format type matches CSP expectation (`int`, `bool`, `chr`, `xml`)
- [ ] ADMX-backed policies use `<![CDATA[<enabled/>...]]>` in Data element

## SCEP (if applicable)
- [ ] Uses `$FLEET_VAR_SCEP_WINDOWS_CERTIFICATE_ID` in LocURIs
- [ ] Does not mix `./Device` and `./User` scope LocURIs
- [ ] Has exactly one `<Exec>` element with `/Install/Enroll` LocURI
- [ ] Includes all required LocURIs (ServerURL, Challenge, CAThumbprint, etc.)

## Fleet Integration
- [ ] File has `.xml` extension
- [ ] Referenced in GitOps YAML under `controls.windows_settings.custom_settings`
- [ ] Path in YAML is relative-correct
- [ ] Labels referenced in profile are defined in `labels:` section

## Automated validation
```bash
scripts/validate-windows-profile.sh <file.xml>
```
