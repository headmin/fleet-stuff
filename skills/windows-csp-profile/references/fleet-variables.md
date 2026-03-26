# Fleet Variables for Windows Profiles

Fleet supports variable substitution in Windows CSP profile `<Data>` elements. Use `$FLEET_VAR_*` or `${FLEET_VAR_*}` syntax.

## Available Variables

| Variable | Description |
|----------|-------------|
| `$FLEET_VAR_HOST_UUID` | Host unique identifier |
| `$FLEET_VAR_HOST_HARDWARE_SERIAL` | Hardware serial number |
| `$FLEET_VAR_HOST_END_USER_IDP_USERNAME` | IdP username |
| `$FLEET_VAR_HOST_END_USER_IDP_DEPARTMENT` | IdP department |
| `$FLEET_VAR_HOST_END_USER_IDP_FULL_NAME` | IdP full name |
| `$FLEET_VAR_HOST_PLATFORM` | Host platform |

## SCEP-Specific Variables

| Variable | Description |
|----------|-------------|
| `$FLEET_VAR_SCEP_WINDOWS_CERTIFICATE_ID` | SCEP certificate identifier (required in SCEP LocURIs) |
| `$FLEET_VAR_NDES_SCEP_CHALLENGE` | NDES SCEP challenge password |
| `$FLEET_VAR_NDES_SCEP_PROXY_URL` | NDES SCEP proxy URL |

## Usage Example

```xml
<Replace>
  <Item>
    <Meta>
      <Format xmlns="syncml:metinf">chr</Format>
    </Meta>
    <Target>
      <LocURI>./Device/Vendor/MSFT/SomeCSP/UserName</LocURI>
    </Target>
    <Data>$FLEET_VAR_HOST_END_USER_IDP_USERNAME</Data>
  </Item>
</Replace>
```

## Notes

- Variables are a Fleet Premium feature
- Variables inside `$FLEET_SECRET_*` are validated at apply time, not during dry-run
- CA-dependent variables (`$FLEET_VAR_DIGICERT_*`) may pass dry-run but fail on actual run if the CA is not configured
