# DDM Declaration Types

All `com.apple.configuration.*` types from Apple's device-management repo. Types marked **BLOCKED** cannot be used in Fleet.

## Allowed in Fleet

| Type | Description | Platforms |
|------|-------------|-----------|
| `app.managed` | Managed app configuration | iOS 17+, macOS 15+ |
| `audio-accessory.settings` | Audio accessory settings | tvOS 18+ |
| `diskmanagement.settings` | Disk management settings | macOS 15+ |
| `external-intelligence.settings` | External intelligence settings | macOS 15.4+ |
| `intelligence.settings` | Apple Intelligence settings | iOS 18.4+, macOS 15.4+ |
| `keyboard.settings` | Keyboard settings | iOS 18.2+, macOS 15.2+ |
| `legacy` | Wrap legacy .mobileconfig as DDM | iOS 15+, macOS 13+ |
| `legacy.interactive` | Interactive legacy profile | iOS 15+, macOS 13+ |
| `math.settings` | Math notes settings | iPadOS 18.2+ |
| `migration-assistant.settings` | Migration assistant | macOS 15.4+ |
| `package` | Package installation | macOS 15.4+ |
| `passcode.settings` | Passcode complexity/length | iOS 15+, macOS 13+ |
| `safari.bookmarks` | Safari bookmark management | iOS 18.4+, macOS 15.4+ |
| `safari.extensions.settings` | Safari extension management | iOS 18.4+, macOS 15.4+ |
| `safari.settings` | Safari configuration | iOS 18.4+, macOS 15.4+ |
| `screensharing.host.settings` | Screen sharing host settings | macOS 15+ |
| `services.background-tasks` | Background task configuration | macOS 15.4+ |
| `siri.settings` | Siri configuration | iOS 18.4+, macOS 15.4+ |
| `softwareupdate.enforcement.specific` | Force specific OS update | iOS 17+, macOS 14+ (RESTRICTED — requires flag) |
| `softwareupdate.settings` | Automatic update behavior | iOS 18+, macOS 15+ |

## Blocked in Fleet (require asset references)

| Type | Reason |
|------|--------|
| `account.caldav` | Needs credential asset |
| `account.carddav` | Needs credential asset |
| `account.exchange` | Needs credential asset |
| `account.google` | Needs credential asset |
| `account.ldap` | Needs credential asset |
| `account.mail` | Needs credential asset |
| `screensharing.connection` | Needs identity asset |
| `security.certificate` | Needs credential asset |
| `security.identity` | Needs credential asset |
| `security.passkey.attestation` | Needs credential asset |
| `services.configuration-files` | Needs data asset |
| `watch.enrollment` | Needs identity asset |

## Always Blocked

| Type | Reason |
|------|--------|
| `management.status-subscriptions` | Fleet uses queries/policies instead |

## Non-Configuration Types (Not supported by Fleet)

Fleet only accepts `com.apple.configuration.*`. These categories are rejected:
- `com.apple.activation.*` — device activation triggers
- `com.apple.asset.*` — credential and data assets
- `com.apple.management.*` — server capability declarations
