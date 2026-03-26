# Common Windows CSP Settings

Quick reference for frequently deployed CSP settings. OMA-URI paths and data types.

## Firewall

| Setting | LocURI | Format | Values |
|---------|--------|--------|--------|
| Enable domain firewall | `./Vendor/MSFT/Firewall/MdmStore/DomainProfile/EnableFirewall` | bool | `true`/`false` |
| Enable private firewall | `./Vendor/MSFT/Firewall/MdmStore/PrivateProfile/EnableFirewall` | bool | `true`/`false` |
| Enable public firewall | `./Vendor/MSFT/Firewall/MdmStore/PublicProfile/EnableFirewall` | bool | `true`/`false` |
| Block inbound (domain) | `./Vendor/MSFT/Firewall/MdmStore/DomainProfile/DefaultInboundAction` | int | `0`=allow, `1`=block |
| Block inbound (public) | `./Vendor/MSFT/Firewall/MdmStore/PublicProfile/DefaultInboundAction` | int | `0`=allow, `1`=block |

Doc: https://learn.microsoft.com/en-us/windows/client-management/mdm/firewall-csp

## Defender Antivirus

| Setting | LocURI | Format | Values |
|---------|--------|--------|--------|
| Real-time monitoring | `./Device/Vendor/MSFT/Policy/Config/Defender/AllowRealtimeMonitoring` | int | `0`=off, `1`=on |
| Cloud protection | `./Device/Vendor/MSFT/Policy/Config/Defender/AllowCloudProtection` | int | `0`=off, `1`=on |
| Signature update interval | `./Device/Vendor/MSFT/Policy/Config/Defender/SignatureUpdateInterval` | int | Hours (0-24) |
| PUA protection | `./Device/Vendor/MSFT/Policy/Config/Defender/PUAProtection` | int | `0`=off, `1`=audit, `2`=block |
| Enable file hash computation | `./Device/Vendor/MSFT/Defender/Configuration/EnableFileHashComputation` | int | `0`=off, `1`=on |

Doc: https://learn.microsoft.com/en-us/windows/client-management/mdm/defender-csp

## DeviceLock (Password Policy)

| Setting | LocURI | Format | Values |
|---------|--------|--------|--------|
| Require password | `./Device/Vendor/MSFT/Policy/Config/DeviceLock/DevicePasswordEnabled` | int | `0`=required, `1`=not required |
| Min length | `./Device/Vendor/MSFT/Policy/Config/DeviceLock/MinDevicePasswordLength` | int | 4-16 |
| Max inactivity lock | `./Device/Vendor/MSFT/Policy/Config/DeviceLock/MaxInactivityTimeDeviceLock` | int | Minutes (0=never) |
| Complex chars required | `./Device/Vendor/MSFT/Policy/Config/DeviceLock/MinDevicePasswordComplexCharacters` | int | 1-4 |
| Password history | `./Device/Vendor/MSFT/Policy/Config/DeviceLock/DevicePasswordHistory` | int | 0-50 |

Doc: https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-devicelock

## Security (Local Policies)

| Setting | LocURI | Format | Values |
|---------|--------|--------|--------|
| Disable guest account | `./Device/Vendor/MSFT/Policy/Config/LocalPoliciesSecurityOptions/Accounts_EnableGuestAccountStatus` | int | `0`=disabled, `1`=enabled |
| Rename admin account | `./Device/Vendor/MSFT/Policy/Config/LocalPoliciesSecurityOptions/Accounts_RenameAdministratorAccount` | chr | New name |
| UAC admin prompt | `./Device/Vendor/MSFT/Policy/Config/LocalPoliciesSecurityOptions/UserAccountControl_BehaviorOfTheElevationPromptForAdministrators` | int | 0-5 |
| UAC standard prompt | `./Device/Vendor/MSFT/Policy/Config/LocalPoliciesSecurityOptions/UserAccountControl_BehaviorOfTheElevationPromptForStandardUsers` | int | 0-3 |

## System

| Setting | LocURI | Format | Values |
|---------|--------|--------|--------|
| Allow telemetry | `./Device/Vendor/MSFT/Policy/Config/System/AllowTelemetry` | int | `0`=off, `1`=basic, `2`=enhanced, `3`=full |
| Allow experiments | `./Device/Vendor/MSFT/Policy/Config/System/AllowExperimentation` | int | `0`=off, `1`=on |
| Disable OneDrive sync | `./Device/Vendor/MSFT/Policy/Config/System/DisableOneDriveFileSync` | int | `0`=allow, `1`=block |

## Reserved by Fleet (DO NOT USE in custom profiles)

| CSP | LocURI Prefix | Use Instead |
|-----|---------------|-------------|
| BitLocker | `/Vendor/MSFT/BitLocker` | Fleet's built-in `enable_disk_encryption` |
| Windows Update | `/Vendor/MSFT/Policy/Config/Update` | Fleet's `windows_updates` setting |

## Data Type Reference

| Format | Description | Example values |
|--------|-------------|----------------|
| `int` | Integer | `0`, `1`, `100` |
| `bool` | Boolean | `true`, `false` |
| `chr` | String | `"some text"` |
| `xml` | XML payload | ADMX `<![CDATA[<enabled/>]]>` |
| `node` | Container (no data) | — |
| `bin` | Binary (base64) | — |
| `null` | Null/empty | — |
