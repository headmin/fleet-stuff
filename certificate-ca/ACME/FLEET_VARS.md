A quick list of all Fleet variables with the FLEET_VAR_ prefix, as defined in the schema and codebase. These variables are used for dynamic substitution in configuration profiles, scripts, and other contexts. The list includes both exact variables and prefix variables (for CA-specific or custom values):

Exact variables:

FLEET_VAR_NDES_SCEP_CHALLENGE
FLEET_VAR_NDES_SCEP_PROXY_URL
FLEET_VAR_HOST_END_USER_EMAIL_IDP (legacy, avoid in new configs)
FLEET_VAR_HOST_HARDWARE_SERIAL
FLEET_VAR_HOST_END_USER_IDP_USERNAME
FLEET_VAR_HOST_END_USER_IDP_USERNAME_LOCAL_PART
FLEET_VAR_HOST_END_USER_IDP_GROUPS
FLEET_VAR_HOST_END_USER_IDP_DEPARTMENT
FLEET_VAR_HOST_UUID
FLEET_VAR_HOST_END_USER_IDP_FULL_NAME
FLEET_VAR_SCEP_RENEWAL_ID
FLEET_VAR_SCEP_WINDOWS_CERTIFICATE_ID
FLEET_VAR_HOST_PLATFORM
Prefix variables (require a suffix, e.g. CA name):

FLEET_VAR_DIGICERT_DATA_
FLEET_VAR_DIGICERT_PASSWORD_
FLEET_VAR_CUSTOM_SCEP_CHALLENGE_
FLEET_VAR_CUSTOM_SCEP_PROXY_URL_
FLEET_VAR_SMALLSTEP_SCEP_CHALLENGE_
FLEET_VAR_SMALLSTEP_SCEP_PROXY_URL_
These variables are registered in the fleet_variables table and are referenced throughout the codebase for substitution and validation. Prefix variables are used for CA-specific values, so you must append the CA name (e.g., FLEET_VAR_DIGICERT_DATA_MyCA).

For more details, see:

[server/fleet/mdm.go](https://github.com/fleetdm/fleet/blob/main/server/fleet/mdm.go)
[server/datastore/mysql/schema.sql](https://github.com/fleetdm/fleet/blob/main/server/datastore/mysql/schema.sql)
[Fleet documentation on GitOps](https://fleetdm.com/docs/configuration/yaml-files)
