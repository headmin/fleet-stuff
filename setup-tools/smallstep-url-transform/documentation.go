package main

import (
	"fmt"
	"os"
	"strings"
	"time"
)

// writeProfileDocumentation generates markdown documentation for a profile
func writeProfileDocumentation(docType string, config DocumentationConfig) error {
	var content string

	switch docType {
	case "scep":
		content = generateSCEPDocumentation(config)
	case "trust":
		content = generateTrustDocumentation(config)
	case "wifi":
		content = generateWiFiDocumentation(config)
	case "vpn":
		content = generateVPNDocumentation(config)
	default:
		return fmt.Errorf("unknown documentation type: %s", docType)
	}

	// Get filename without .mobileconfig extension
	docFilename := strings.TrimSuffix(config.ProfileName, ".mobileconfig") + ".md"

	return os.WriteFile(docFilename, []byte(content), 0644)
}

// generateSCEPDocumentation generates documentation for SCEP profiles
func generateSCEPDocumentation(config DocumentationConfig) string {
	var doc strings.Builder

	doc.WriteString(fmt.Sprintf("# SCEP Profile: %s\n\n", config.CAName))
	doc.WriteString(fmt.Sprintf("**Profile Name:** `%s`  \n", config.ProfileName))
	doc.WriteString(fmt.Sprintf("**Generated:** %s  \n", config.Timestamp))
	doc.WriteString("**Purpose:** Issue device identity certificates via SCEP from Smallstep CA\n\n")
	doc.WriteString("---\n\n")

	// Fleet Configuration
	doc.WriteString("## Fleet Configuration\n\n")
	doc.WriteString("### 1. Add CA Configuration in Fleet\n\n")
	doc.WriteString("Navigate to **Settings → Integrations → Certificate Authorities**\n\n")
	doc.WriteString("| Field | Value |\n")
	doc.WriteString("|-------|-------|\n")
	doc.WriteString(fmt.Sprintf("| **Name** | `%s` |\n", config.CAName))
	doc.WriteString(fmt.Sprintf("| **SCEP URL** | `%s` |\n", config.FleetVariables["ProxyURL"]))
	doc.WriteString(fmt.Sprintf("| **Challenge URL** | `%s` |\n", config.FleetVariables["ChallengeURL"]))
	doc.WriteString("\n")

	// Upload instructions
	doc.WriteString("### 2. Upload This Profile\n\n")
	doc.WriteString("1. Go to **Controls → Configuration profiles → Add profile**\n")
	doc.WriteString(fmt.Sprintf("2. Upload `%s`\n", config.ProfileName))
	doc.WriteString("3. Select target teams/hosts\n")
	doc.WriteString("4. Deploy\n\n")

	// Fleet Variables
	doc.WriteString("### 3. Fleet Variables Required\n\n")
	doc.WriteString("This profile uses the following Fleet variables:\n\n")
	doc.WriteString("| Variable Name | Description |\n")
	doc.WriteString("|---------------|-------------|\n")
	doc.WriteString(fmt.Sprintf("| `%s` | SCEP challenge password |\n", config.FleetVariables["ChallengeVar"]))
	doc.WriteString(fmt.Sprintf("| `%s` | Fleet SCEP proxy URL |\n", config.FleetVariables["ProxyURLVar"]))
	doc.WriteString(fmt.Sprintf("| `%s` | Certificate renewal ID |\n", config.FleetVariables["RenewalVar"]))
	doc.WriteString("\n")
	doc.WriteString("✅ These variables are **automatically populated** by Fleet when the CA is configured.\n\n")

	// Profile Details
	doc.WriteString("---\n\n")
	doc.WriteString("## Profile Details\n\n")
	doc.WriteString("### PayloadUUIDs\n\n")
	doc.WriteString(fmt.Sprintf("- **Profile UUID:** `%s`\n", config.PayloadUUIDs["profile"]))
	doc.WriteString(fmt.Sprintf("- **SCEP Payload UUID:** `%s`\n\n", config.SCEPPayloadUUID))

	doc.WriteString("### Certificate Details\n\n")
	doc.WriteString("- **Key Type:** RSA 2048-bit\n")
	doc.WriteString("- **Key Usage:** `5` (digitalSignature + keyEncipherment)\n")
	doc.WriteString("- **Extended Key Usage:** TLS Web Client Authentication (clientAuth)\n")
	doc.WriteString("- **Subject O:** Fleet\n")
	doc.WriteString("- **Subject CN:** %HardwareUUID%\n")
	doc.WriteString(fmt.Sprintf("- **Subject OU:** %s (enables auto-renewal)\n\n", config.FleetVariables["RenewalVar"]))

	// Verification
	doc.WriteString("---\n\n")
	doc.WriteString("## Verification & Troubleshooting\n\n")
	doc.WriteString("### Check Profile Installation (macOS)\n\n")
	doc.WriteString("```bash\n")
	doc.WriteString("# List installed profiles\n")
	doc.WriteString("sudo profiles list\n\n")
	doc.WriteString("# Show specific profile details\n")
	doc.WriteString("sudo profiles show -type configuration\n")
	doc.WriteString("```\n\n")

	doc.WriteString("### Check Certificate Installation\n\n")
	doc.WriteString("```bash\n")
	doc.WriteString("# List certificates with private keys\n")
	doc.WriteString("security find-identity -v -p ssl-client\n\n")
	doc.WriteString("# Should show: \"Fleet\" certificate\n")
	doc.WriteString("```\n\n")

	// Monitoring
	doc.WriteString("### Monitor SCEP Enrollment\n\n")
	doc.WriteString("```bash\n")
	doc.WriteString("# Monitor SCEP enrollment process\n")
	doc.WriteString("log stream --predicate 'subsystem == \"com.apple.ManagedClient\" AND eventMessage CONTAINS \"SCEP\"' --level info\n\n")
	doc.WriteString("# Watch for certificate events\n")
	doc.WriteString("log stream --predicate 'process == \"securityd\" AND eventMessage CONTAINS \"SCEP\"' --level info\n")
	doc.WriteString("```\n\n")

	// Deployment Order
	doc.WriteString("---\n\n")
	doc.WriteString("## Deployment Order\n\n")
	doc.WriteString("1. ✅ Install Trust Profile (CA certificates - install first!)\n")
	doc.WriteString("2. ✅ Install SCEP Profile (this profile - device identity)\n")
	doc.WriteString("3. Install WiFi/VPN profiles (reference SCEP certificate)\n\n")

	// Resources
	doc.WriteString("---\n\n")
	doc.WriteString("## Additional Resources\n\n")
	doc.WriteString("- [Fleet SCEP Documentation](https://fleetdm.com/docs/using-fleet/mdm-macos-setup#step-3-enforce-certificate-based-authentication)\n")
	doc.WriteString("- [Smallstep CA Documentation](https://smallstep.com/docs/step-ca)\n")
	doc.WriteString("- [Apple Configuration Profile Reference](https://developer.apple.com/documentation/devicemanagement/profile)\n")
	doc.WriteString("- [Key Usage Reference](./SCEP/KEY-USAGE-REFERENCE.md)\n")

	return doc.String()
}

// generateTrustDocumentation generates documentation for Trust profiles
func generateTrustDocumentation(config DocumentationConfig) string {
	var doc strings.Builder

	doc.WriteString(fmt.Sprintf("# Trust Profile: %s\n\n", config.CAName))
	doc.WriteString(fmt.Sprintf("**Profile Name:** `%s`  \n", config.ProfileName))
	doc.WriteString(fmt.Sprintf("**Generated:** %s  \n", config.Timestamp))
	doc.WriteString("**Purpose:** Install Smallstep CA certificates as trusted roots\n\n")
	doc.WriteString("---\n\n")

	// Fleet Configuration
	doc.WriteString("## Fleet Configuration\n\n")
	doc.WriteString("### Upload This Profile\n\n")
	doc.WriteString("1. Go to **Controls → Configuration profiles → Add profile**\n")
	doc.WriteString(fmt.Sprintf("2. Upload `%s`\n", config.ProfileName))
	doc.WriteString("3. ⚠️ **Device Channel:** This profile MUST be deployed via **Device Channel** (not User Channel)\n")
	doc.WriteString("4. Select target teams/hosts\n")
	doc.WriteString("5. Deploy\n\n")
	doc.WriteString("⚠️ **IMPORTANT:** Deploy this profile **BEFORE** SCEP, WiFi, or VPN profiles!\n\n")

	// Profile Details
	doc.WriteString("---\n\n")
	doc.WriteString("## Profile Details\n\n")
	doc.WriteString("### Included Certificates\n\n")

	if config.HasRootCA {
		doc.WriteString("✅ **Root CA Certificate**\n")
		doc.WriteString(fmt.Sprintf("- PayloadUUID: `%s`\n", config.RootCertUUID))
		doc.WriteString("- Type: `com.apple.security.root`\n\n")
	}

	if config.HasIntermediateCA {
		doc.WriteString("✅ **Intermediate CA Certificate**\n")
		doc.WriteString(fmt.Sprintf("- PayloadUUID: `%s`\n", config.IntermediateCertUUID))
		doc.WriteString("- Type: `com.apple.security.pkcs1`\n\n")
	}

	if config.HasRADIUSCA {
		doc.WriteString("✅ **RADIUS CA Certificate**\n")
		doc.WriteString(fmt.Sprintf("- PayloadUUID: `%s`\n", config.RADIUSCertUUID))
		doc.WriteString("- Type: `com.apple.security.root`\n")
		doc.WriteString("- Purpose: Trust WiFi RADIUS server certificates\n\n")
	}

	// Verification
	doc.WriteString("---\n\n")
	doc.WriteString("## Verification & Troubleshooting\n\n")
	doc.WriteString("### Check Trust Installation (macOS)\n\n")
	doc.WriteString("```bash\n")
	doc.WriteString("# Check for certificates in System keychain\n")
	doc.WriteString("security find-certificate -a -c \"Smallstep\" /Library/Keychains/System.keychain\n\n")
	doc.WriteString("# Verify certificate trust settings\n")
	doc.WriteString("security dump-trust-settings\n")
	doc.WriteString("```\n\n")

	doc.WriteString("### Monitor Certificate Installation\n\n")
	doc.WriteString("```bash\n")
	doc.WriteString("# Watch for certificate installation events\n")
	doc.WriteString("log stream --predicate 'process == \"ManagedClient\" AND eventMessage CONTAINS \"certificate\"' --level info\n")
	doc.WriteString("```\n\n")

	// Deployment Order
	doc.WriteString("---\n\n")
	doc.WriteString("## Deployment Order\n\n")
	doc.WriteString("1. ✅ Install Trust Profile (this profile - FIRST!)\n")
	doc.WriteString("2. Install SCEP Profile (device identity)\n")
	doc.WriteString("3. Install WiFi/VPN profiles (reference trusted CAs)\n\n")

	return doc.String()
}

// generateWiFiDocumentation generates documentation for WiFi+SCEP profiles
func generateWiFiDocumentation(config DocumentationConfig) string {
	var doc strings.Builder

	doc.WriteString(fmt.Sprintf("# WiFi + SCEP Profile: %s\n\n", config.CAName))
	doc.WriteString(fmt.Sprintf("**Profile Name:** `%s`  \n", config.ProfileName))
	doc.WriteString(fmt.Sprintf("**Generated:** %s  \n", config.Timestamp))
	doc.WriteString("**Purpose:** Issue SCEP certificate and configure enterprise WiFi with EAP-TLS\n\n")
	doc.WriteString("---\n\n")

	// Prerequisites
	doc.WriteString("## Prerequisites\n\n")
	doc.WriteString("✅ **Required profiles (install first):**\n")
	doc.WriteString(fmt.Sprintf("1. Trust Profile: `smallstep-trust-%s.mobileconfig`\n\n", strings.ToLower(config.CAName)))
	doc.WriteString("✅ **Fleet CA Configuration:**\n")
	doc.WriteString(fmt.Sprintf("- CA Name: `%s`\n", config.CAName))
	doc.WriteString("- SCEP URL configured in Fleet\n\n")

	// WiFi Configuration
	doc.WriteString("---\n\n")
	doc.WriteString("## WiFi Configuration\n\n")
	doc.WriteString("### Network Settings\n\n")
	doc.WriteString("| Setting | Value |\n")
	doc.WriteString("|---------|-------|\n")
	doc.WriteString(fmt.Sprintf("| **SSID** | `%s` |\n", config.WiFiSSID))
	doc.WriteString(fmt.Sprintf("| **Hidden Network** | `%t` |\n", config.WiFiHidden))
	doc.WriteString(fmt.Sprintf("| **Auto-Join** | `%t` |\n", config.WiFiAutoJoin))
	doc.WriteString(fmt.Sprintf("| **Encryption** | `%s` |\n", config.WiFiEncryption))
	doc.WriteString("| **Security** | WPA2/WPA3 Enterprise |\n\n")

	doc.WriteString("### EAP Configuration\n\n")
	doc.WriteString("| Setting | Value |\n")
	doc.WriteString("|---------|-------|\n")
	doc.WriteString("| **EAP Type** | EAP-TLS (13) |\n")
	doc.WriteString("| **Authentication** | Certificate-based |\n")
	doc.WriteString("| **Identity Certificate** | SCEP-issued device certificate |\n")
	if len(config.TrustedServers) > 0 {
		doc.WriteString(fmt.Sprintf("| **Trusted Server Names** | `%s` |\n", strings.Join(config.TrustedServers, ", ")))
	}
	doc.WriteString("| **Trusted CA Certificates** | Root CA + RADIUS CA |\n\n")

	// Payloads
	doc.WriteString("---\n\n")
	doc.WriteString("## Profile Details\n\n")
	doc.WriteString("### Payloads Included\n\n")
	doc.WriteString("1. **SCEP Payload** (`com.apple.security.scep`)\n")
	doc.WriteString(fmt.Sprintf("   - UUID: `%s`\n", config.SCEPPayloadUUID))
	doc.WriteString("   - Issues device identity certificate\n\n")
	doc.WriteString("2. **WiFi Payload** (`com.apple.wifi.managed`)\n")
	doc.WriteString(fmt.Sprintf("   - UUID: `%s`\n", config.WiFiPayloadUUID))
	doc.WriteString("   - References SCEP certificate for authentication\n\n")

	// Verification
	doc.WriteString("---\n\n")
	doc.WriteString("## Verification & Troubleshooting\n\n")
	doc.WriteString("### Check WiFi Connection (macOS)\n\n")
	doc.WriteString("```bash\n")
	doc.WriteString("# Show current WiFi info\n")
	doc.WriteString("/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I\n\n")
	doc.WriteString("# Check WiFi logs\n")
	doc.WriteString("log show --predicate 'subsystem == \"com.apple.wifi\"' --last 5m\n")
	doc.WriteString("```\n\n")

	doc.WriteString("### Monitor 802.1X Authentication (macOS)\n\n")
	doc.WriteString("```bash\n")
	doc.WriteString("# Monitor 802.1X authentication process (DETAILED)\n")
	doc.WriteString("log stream --predicate 'subsystem == \"com.apple.eapol\" OR subsystem == \"com.apple.securityd\"' --level debug\n\n")
	doc.WriteString("# Watch EAP-TLS specifically\n")
	doc.WriteString("log stream --predicate 'process == \"eapolclient\" AND eventMessage CONTAINS \"TLS\"' --level info\n\n")
	doc.WriteString("# Full 802.1X debug log (very verbose!)\n")
	doc.WriteString("log stream --predicate 'subsystem BEGINSWITH \"com.apple.80211\" OR subsystem == \"com.apple.eapol\" OR subsystem == \"com.apple.securityd\"' --level debug\n")
	doc.WriteString("```\n\n")

	doc.WriteString("### Common Issues\n\n")
	doc.WriteString("**Problem:** WiFi shows \"Unable to join network\"\n")
	doc.WriteString("- **Solution:** Check SCEP certificate was issued successfully\n")
	doc.WriteString("- **Log check:** `log stream --predicate 'subsystem == \"com.apple.eapol\"' --level debug`\n\n")

	doc.WriteString("**Problem:** \"EAP authentication failed\"\n")
	doc.WriteString("- **Solution:** Verify RADIUS server certificate is trusted\n")
	doc.WriteString("- **Check:** Trust profile includes RADIUS CA certificate\n\n")

	doc.WriteString("**Problem:** \"Identity not found\"\n")
	doc.WriteString("- **Solution:** Verify SCEP certificate is in System keychain with private key\n")
	doc.WriteString("- **Check:** `security find-identity -v`\n\n")

	// Deployment Order
	doc.WriteString("---\n\n")
	doc.WriteString("## Deployment Order\n\n")
	doc.WriteString("1. Install Trust Profile (CA certificates)\n")
	doc.WriteString("2. ✅ Install WiFi + SCEP Profile (this profile)\n")
	doc.WriteString("3. Device automatically connects to WiFi\n\n")

	// Resources
	doc.WriteString("---\n\n")
	doc.WriteString("## Additional Resources\n\n")
	doc.WriteString("- [Apple 802.1X Documentation](https://support.apple.com/guide/deployment/802-1x-dep8ba64f0c)\n")
	doc.WriteString("- [EAP-TLS Configuration](https://support.apple.com/guide/deployment/extensible-authentication-protocol-dep0e2b3b75)\n")
	doc.WriteString("- [802.1X Troubleshooting Guide](./SCEP/TROUBLESHOOTING-802.1X.md)\n")

	return doc.String()
}

// generateVPNDocumentation generates documentation for VPN profiles
func generateVPNDocumentation(config DocumentationConfig) string {
	var doc strings.Builder

	doc.WriteString(fmt.Sprintf("# VPN Profile: %s\n\n", config.CAName))
	doc.WriteString(fmt.Sprintf("**Profile Name:** `%s`  \n", config.ProfileName))
	doc.WriteString(fmt.Sprintf("**Generated:** %s  \n", config.Timestamp))
	doc.WriteString("**Purpose:** Configure IKEv2 VPN with certificate authentication\n\n")
	doc.WriteString("---\n\n")

	// Prerequisites
	doc.WriteString("## Prerequisites\n\n")
	doc.WriteString("✅ **Required profiles (install first):**\n")
	doc.WriteString(fmt.Sprintf("1. Trust Profile: `smallstep-trust-%s.mobileconfig`\n", strings.ToLower(config.CAName)))
	doc.WriteString(fmt.Sprintf("2. SCEP Profile: `smallstep-scep-%s.mobileconfig`\n\n", strings.ToLower(config.CAName)))

	// VPN Configuration
	doc.WriteString("---\n\n")
	doc.WriteString("## VPN Configuration\n\n")
	doc.WriteString("### Connection Settings\n\n")
	doc.WriteString("| Setting | Value |\n")
	doc.WriteString("|---------|-------|\n")
	doc.WriteString("| **VPN Type** | IKEv2 |\n")
	doc.WriteString(fmt.Sprintf("| **Server Address** | `%s` |\n", config.VPNServer))
	doc.WriteString(fmt.Sprintf("| **Remote Identifier** | `%s` |\n", config.VPNRemoteID))
	doc.WriteString(fmt.Sprintf("| **Local Identifier** | `%s` |\n", config.VPNLocalID))
	doc.WriteString("| **Authentication** | Certificate (SCEP-issued) |\n\n")

	if config.VPNOnDemand {
		doc.WriteString("### On-Demand Settings\n\n")
		doc.WriteString("| Setting | Value |\n")
		doc.WriteString("|---------|-------|\n")
		doc.WriteString("| **On-Demand Enabled** | Yes |\n\n")
	}

	// Verification
	doc.WriteString("---\n\n")
	doc.WriteString("## Verification & Troubleshooting\n\n")
	doc.WriteString("### Monitor VPN Connection (macOS)\n\n")
	doc.WriteString("```bash\n")
	doc.WriteString("# Watch VPN connection events\n")
	doc.WriteString("log stream --predicate 'subsystem == \"com.apple.ipsec\" OR subsystem == \"com.apple.NetworkExtension\"' --level debug\n\n")
	doc.WriteString("# IKEv2 specific logs\n")
	doc.WriteString("log stream --predicate 'process == \"nesessionmanager\" OR process == \"neagent\"' --level info\n")
	doc.WriteString("```\n\n")

	doc.WriteString("### Common Issues\n\n")
	doc.WriteString("**Problem:** VPN connection fails with \"authentication failed\"\n")
	doc.WriteString("- **Solution:** Verify SCEP certificate has correct Extended Key Usage (clientAuth)\n")
	doc.WriteString("- **Check:** `security find-identity -v -p ssl-client`\n\n")

	doc.WriteString("**Problem:** \"Server certificate validation failed\"\n")
	doc.WriteString("- **Solution:** Ensure VPN server certificate is signed by trusted CA\n")
	doc.WriteString("- **Check:** Trust profile installed on device\n\n")

	// Deployment Order
	doc.WriteString("---\n\n")
	doc.WriteString("## Deployment Order\n\n")
	doc.WriteString("1. Install Trust Profile (CA certificates)\n")
	doc.WriteString("2. Install SCEP Profile (device identity)\n")
	doc.WriteString("3. ✅ Install VPN Profile (this profile)\n\n")

	// Resources
	doc.WriteString("---\n\n")
	doc.WriteString("## Additional Resources\n\n")
	doc.WriteString("- [Apple VPN Documentation](https://support.apple.com/guide/deployment/vpn-dep4b52d203)\n")
	doc.WriteString("- [IKEv2 Configuration](https://developer.apple.com/documentation/devicemanagement/vpn)\n")

	return doc.String()
}

// buildDocumentationConfig creates a DocumentationConfig with common values
func buildDocumentationConfig(profileType, profileName, caName string, fleetVars, payloadUUIDs map[string]string) DocumentationConfig {
	return DocumentationConfig{
		ProfileType:    profileType,
		ProfileName:    profileName,
		CAName:         caName,
		Timestamp:      time.Now().Format(time.RFC3339),
		FleetVariables: fleetVars,
		PayloadUUIDs:   payloadUUIDs,
	}
}
