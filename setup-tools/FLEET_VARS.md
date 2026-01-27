# Fleet Variables Reference

A quick list of all Fleet variables with the `FLEET_VAR_` prefix, as defined in the schema and codebase. These variables are used for dynamic substitution in configuration profiles, scripts, and other contexts.

## Exact Variables

| Variable | Description |
|----------|-------------|
| `FLEET_VAR_NDES_SCEP_CHALLENGE` | NDES SCEP challenge value |
| `FLEET_VAR_NDES_SCEP_PROXY_URL` | NDES SCEP proxy URL |
| `FLEET_VAR_HOST_END_USER_EMAIL_IDP` | End user email from IdP *(legacy, avoid in new configs)* |
| `FLEET_VAR_HOST_HARDWARE_SERIAL` | Host hardware serial number |
| `FLEET_VAR_HOST_END_USER_IDP_USERNAME` | End user IdP username |
| `FLEET_VAR_HOST_END_USER_IDP_USERNAME_LOCAL_PART` | Local part of IdP username (before @) |
| `FLEET_VAR_HOST_END_USER_IDP_GROUPS` | End user IdP groups |
| `FLEET_VAR_HOST_END_USER_IDP_DEPARTMENT` | End user IdP department |
| `FLEET_VAR_HOST_UUID` | Host UUID |
| `FLEET_VAR_HOST_END_USER_IDP_FULL_NAME` | End user full name from IdP |
| `FLEET_VAR_SCEP_RENEWAL_ID` | SCEP certificate renewal ID |
| `FLEET_VAR_SCEP_WINDOWS_CERTIFICATE_ID` | Windows SCEP certificate ID |
| `FLEET_VAR_HOST_PLATFORM` | Host platform (darwin, windows, linux) |

## Prefix Variables

These require a suffix (e.g., CA name). Append the CA name to complete the variable (e.g., `FLEET_VAR_DIGICERT_DATA_MyCA`).

| Variable Prefix | Description |
|-----------------|-------------|
| `FLEET_VAR_DIGICERT_DATA_` | DigiCert certificate data for specified CA |
| `FLEET_VAR_DIGICERT_PASSWORD_` | DigiCert password for specified CA |
| `FLEET_VAR_CUSTOM_SCEP_CHALLENGE_` | Custom SCEP challenge for specified CA |
| `FLEET_VAR_CUSTOM_SCEP_PROXY_URL_` | Custom SCEP proxy URL for specified CA |
| `FLEET_VAR_SMALLSTEP_SCEP_CHALLENGE_` | Smallstep SCEP challenge for specified CA |
| `FLEET_VAR_SMALLSTEP_SCEP_PROXY_URL_` | Smallstep SCEP proxy URL for specified CA |

## Notes

These variables are registered in the `fleet_variables` table and are referenced throughout the codebase for substitution and validation.

## References

- [server/fleet/mdm.go](https://github.com/fleetdm/fleet/blob/main/server/fleet/mdm.go)
- [server/datastore/mysql/schema.sql](https://github.com/fleetdm/fleet/blob/main/server/datastore/mysql/schema.sql)
- [Fleet documentation on GitOps](https://fleetdm.com/docs/configuration/yaml-files)
