# Fleet GitOps Repository Structure

## Recommended Layout (v4.82+)

Top-level `platforms/`, `labels/`, and `fleets/` directories. Clean separation of concerns.

```
it-and-security/
├── default.yml                              # Global org settings
├── fleets/                                  # One YAML per fleet
│   ├── workstations.yml
│   ├── servers.yml
│   ├── company-owned-mobile-devices.yml
│   ├── personal-mobile-devices.yml
│   ├── testing-and-qa.yml
│   └── unassigned.yml                       # Was no-team.yml (deprecated)
├── labels/                                  # All labels at top level
│   ├── department-engineering.yml
│   ├── department-sales.yml
│   ├── apple-silicon-macos-hosts.yml
│   └── virtual-machines.yml
├── platforms/                               # Resources grouped by platform
│   ├── all/                                 # Cross-platform shared resources
│   │   ├── agent-options.yml
│   │   ├── icons/
│   │   │   └── fleet-desktop-icon.png
│   │   └── queries/
│   │       └── collect-fleetd-information.yml
│   ├── android/
│   │   └── configuration-profiles/
│   ├── ios/
│   │   ├── configuration-profiles/
│   │   │   ├── lock-screen-message.mobileconfig
│   │   │   └── self-service.mobileconfig
│   │   └── declaration-profiles/
│   │       ├── Passcode settings.json
│   │       └── Software Update settings.json
│   ├── ipados/
│   │   ├── configuration-profiles/
│   │   │   └── lock-screen-message.mobileconfig
│   │   └── declaration-profiles/
│   │       ├── Passcode settings.json
│   │       └── Software Update settings.json
│   ├── linux/
│   │   ├── policies/
│   │   │   ├── disk-encryption-check.yml
│   │   │   └── check-fleet-desktop-extension.yml
│   │   ├── queries/
│   │   │   ├── all-deb-hosts.yml
│   │   │   └── all-rpm-hosts.yml
│   │   ├── scripts/
│   │   │   ├── install-fleet-desktop-extension.sh
│   │   │   └── uninstall-fleetd-linux.sh
│   │   └── software/
│   │       ├── slack-deb.yml
│   │       ├── slack-rpm.yml
│   │       ├── zoom-deb.yml
│   │       └── zoom-rpm.yml
│   ├── macos/
│   │   ├── configuration-profiles/          # .mobileconfig files
│   │   │   ├── firewall.mobileconfig
│   │   │   ├── disable-guest-account.mobileconfig
│   │   │   ├── enable-gatekeeper.mobileconfig
│   │   │   ├── full-disk-access-for-fleetd.mobileconfig
│   │   │   └── nudge-configuration.mobileconfig
│   │   ├── declaration-profiles/            # DDM .json files (macOS 14+)
│   │   │   ├── Passcode settings.json
│   │   │   └── Software Update settings.json
│   │   ├── enrollment-profiles/
│   │   │   └── automatic-enrollment.dep.json
│   │   ├── commands/
│   │   │   └── macos-send-fleetd.xml
│   │   ├── policies/
│   │   │   ├── disk-encryption-check.yml
│   │   │   ├── latest-macos.yml
│   │   │   └── all-software-updates-installed.yml
│   │   ├── queries/
│   │   │   └── detect-apple-intelligence.yml
│   │   ├── scripts/
│   │   │   ├── install-nudge.sh
│   │   │   ├── system-maintenance.sh
│   │   │   └── uninstall-fleetd-macos.sh
│   │   ├── software/
│   │   │   ├── 1password.yml
│   │   │   ├── mozilla-firefox.yml
│   │   │   └── zoom.yml
│   │   └── misc/
│   │       └── eula.pdf
│   └── windows/
│       ├── configuration-profiles/          # .xml CSP files
│       │   ├── Enable firewall.xml
│       │   ├── Password settings.xml
│       │   └── Windows Defender compliance settings.xml
│       ├── policies/
│       │   ├── disk-encryption-check.yml
│       │   └── antivirus-signatures-up-to-date.yml
│       ├── scripts/
│       │   ├── enable-ms-defender.ps1
│       │   └── uninstall-fleetd-windows.ps1
│       └── software/
│           ├── 1password.yml
│           └── zoom.yml
└── README.md
```

### Key conventions
- `platforms/` at top level — NOT `lib/` (legacy)
- `labels/` at top level — NOT nested under `platforms/all/labels/`
- `fleets/` at top level — NOT `teams/` (renamed in v4.82)
- `unassigned.yml` — NOT `no-team.yml` (deprecated in v4.82)
- Each platform has consistent subdirs: `configuration-profiles/`, `declaration-profiles/`, `policies/`, `queries/`, `scripts/`, `software/`
- Declaration profiles (DDM `.json`) are separate from configuration profiles (`.mobileconfig`/`.xml`)
- Fleet YAMLs reference `../platforms/` paths (relative from `fleets/` dir)
- Linux software splits by package manager: `slack-deb.yml`, `slack-rpm.yml`

### Legacy layout (pre-v4.82)
Older repos may use `lib/` instead of `platforms/` and `teams/` instead of `fleets/`. Both still work but the recommended structure above is preferred for new repos. Key differences:
- `lib/` → `platforms/`
- `lib/all/labels/` → top-level `labels/`
- `teams/` → `fleets/`
- `no-team.yml` → `unassigned.yml`

## Minimal default.yml

```yaml
agent_options:
  path: ./platforms/all/agent-options.yml
org_settings:
  features:
    enable_host_users: true
    enable_software_inventory: true
  fleet_desktop:
    transparency_url: https://fleetdm.com/transparency
  org_info:
    org_name: My Company
    contact_url: https://support.mycompany.com
  secrets:
    - secret: $ENROLL_SECRET
  server_settings:
    server_url: https://fleet.mycompany.com
policies:
reports:
controls:
software:
labels:
```

## Minimal fleets/fleet-name.yml

```yaml
name: Workstations
settings:
  features:
    enable_host_users: true
    enable_software_inventory: true
  secrets:
    - secret: $WORKSTATIONS_ENROLL_SECRET
agent_options:
  config:
    options:
      distributed_interval: 10
      logger_tls_period: 10
controls:
  enable_disk_encryption: true
  macos_settings:
    custom_settings:
      - path: ../platforms/macos/configuration-profiles/firewall.mobileconfig
      - path: ../platforms/macos/configuration-profiles/enable-gatekeeper.mobileconfig
      - path: ../platforms/macos/configuration-profiles/disable-guest-account.mobileconfig
        labels_include_any:
          - "Department: Engineering"
      - path: ../platforms/macos/declaration-profiles/Software Update settings.json
  windows_settings:
    custom_settings:
      - path: ../platforms/windows/configuration-profiles/Enable firewall.xml
  macos_updates:
    deadline: "2026-06-30"
    minimum_version: "15.4"
    update_new_hosts: true
  windows_updates:
    deadline_days: 5
    grace_period_days: 2
policies:
  - path: ../platforms/macos/policies/disk-encryption-check.yml
  - path: ../platforms/macos/policies/latest-macos.yml
  - path: ../platforms/windows/policies/disk-encryption-check.yml
reports:
  - path: ../platforms/all/queries/collect-fleetd-information.yml
software:
  fleet_maintained_apps:
    - slug: slack/darwin
      self_service: true
      categories:
        - Communication
  packages:
    - path: ../platforms/macos/software/mozilla-firefox.yml
      self_service: true
      categories:
        - Browsers
  app_store_apps:
    - app_store_id: "1091189122"
labels:
  - path: ../labels/department-engineering.yml
```

## Software Package YAML (e.g., platforms/macos/software/mozilla-firefox.yml)

```yaml
url: https://download-installer.cdn.mozilla.net/pub/firefox/releases/latest/mac/en-US/Firefox.dmg
install_script:
  path: ../scripts/install-firefox.sh
uninstall_script:
  path: ../scripts/uninstall-firefox.sh
pre_install_query: >-
  SELECT 1 FROM apps WHERE name = 'Firefox.app'
  AND version_compare(bundle_short_version, '130.0') < 0;
```

## Label YAML (e.g., labels/department-engineering.yml)

```yaml
name: "Department: Engineering"
description: "Hosts belonging to the Engineering department"
query: >-
  SELECT 1 FROM mdm_bridge
  WHERE department = 'Engineering'
  OR group_name LIKE '%Engineering%';
platform: ""
```

## Declaration Profile (DDM) JSON

```json
{
  "Type": "com.apple.configuration.passcode.settings",
  "Identifier": "com.fleetdm.passcode-settings",
  "Payload": {
    "MinimumLength": 10,
    "RequireComplexPasscode": true
  }
}
```
