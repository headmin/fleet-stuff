package main

import (
	"fmt"
	"os"
	"strings"
)

// writeTrustProfileEnhanced creates trust profile with Root, Intermediate, and RADIUS CAs
func writeTrustProfileEnhanced(
	filename string,
	payloadID string,
	caName string,
	config TrustConfig,
	profileUUID string,
) error {
	payloads := []string{}

	// Root CA payload
	if config.RootCertPEM != "" {
		rootCertBase64 := pemToBase64(config.RootCertPEM)
		rootPayload := fmt.Sprintf(`        <dict>
            <key>PayloadCertificateFileName</key>
            <string>smallstep-root-ca.cer</string>
            <key>PayloadContent</key>
            <data>%s</data>
            <key>PayloadDisplayName</key>
            <string>Smallstep Root CA</string>
            <key>PayloadIdentifier</key>
            <string>com.apple.security.root.%s</string>
            <key>PayloadType</key>
            <string>com.apple.security.root</string>
            <key>PayloadUUID</key>
            <string>%s</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
        </dict>`, rootCertBase64, config.RootCertUUID, config.RootCertUUID)
		payloads = append(payloads, rootPayload)
	}

	// Intermediate CA payload
	if config.IntermediateCertPEM != "" {
		intermediateCertBase64 := pemToBase64(config.IntermediateCertPEM)
		intermediatePayload := fmt.Sprintf(`        <dict>
            <key>PayloadCertificateFileName</key>
            <string>smallstep-intermediate-ca.cer</string>
            <key>PayloadContent</key>
            <data>%s</data>
            <key>PayloadDisplayName</key>
            <string>Smallstep Intermediate CA</string>
            <key>PayloadIdentifier</key>
            <string>com.apple.security.pkcs1.%s</string>
            <key>PayloadType</key>
            <string>com.apple.security.pkcs1</string>
            <key>PayloadUUID</key>
            <string>%s</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
        </dict>`, intermediateCertBase64, config.IntermediateCertUUID, config.IntermediateCertUUID)
		payloads = append(payloads, intermediatePayload)
	}

	// RADIUS CA payload
	if config.RADIUSCertPEM != "" {
		radiusCertBase64 := pemToBase64(config.RADIUSCertPEM)
		radiusPayload := fmt.Sprintf(`        <dict>
            <key>PayloadCertificateFileName</key>
            <string>radius-ca.cer</string>
            <key>PayloadContent</key>
            <data>%s</data>
            <key>PayloadDisplayName</key>
            <string>RADIUS CA Certificate</string>
            <key>PayloadIdentifier</key>
            <string>com.apple.security.root.%s</string>
            <key>PayloadType</key>
            <string>com.apple.security.root</string>
            <key>PayloadUUID</key>
            <string>%s</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
        </dict>`, radiusCertBase64, config.RADIUSCertUUID, config.RADIUSCertUUID)
		payloads = append(payloads, radiusPayload)
	}

	if len(payloads) == 0 {
		return fmt.Errorf("no certificates provided for trust profile")
	}

	payloadContent := strings.Join(payloads, "\n")

	profile := fmt.Sprintf(`<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <array>
%s
    </array>
    <key>PayloadDisplayName</key>
    <string>Smallstep CA Trust - %s</string>
    <key>PayloadIdentifier</key>
    <string>trust.%s</string>
    <key>PayloadScope</key>
    <string>System</string>
    <key>PayloadType</key>
    <string>Configuration</string>
    <key>PayloadUUID</key>
    <string>%s</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
</dict>
</plist>
`, payloadContent, caName, payloadID, profileUUID)

	return os.WriteFile(filename, []byte(profile), 0644)
}

// writeWiFiSCEPProfile creates combined WiFi + SCEP profile
func writeWiFiSCEPProfile(
	filename string,
	payloadID string,
	caName string,
	wifiConfig WiFiConfig,
	scepConfig SCEPConfig,
	profileUUID string,
) error {
	// SCEP Payload
	scepPayload := fmt.Sprintf(`        <dict>
            <key>PayloadContent</key>
            <dict>
                <key>Challenge</key>
                <string>%s</string>
                <key>Key Type</key>
                <string>RSA</string>
                <key>Key Usage</key>
                <integer>5</integer>
                <key>Keysize</key>
                <integer>2048</integer>
                <key>Subject</key>
                <array>
                    <array>
                        <array>
                            <string>O</string>
                            <string>Fleet</string>
                        </array>
                    </array>
                    <array>
                        <array>
                            <string>CN</string>
                            <string>%%HardwareUUID%%</string>
                        </array>
                    </array>
                    <array>
                        <array>
                            <string>OU</string>
                            <string>%s</string>
                        </array>
                    </array>
                </array>
                <key>URL</key>
                <string>%s</string>
                <key>AllowAllAppsAccess</key>
                <true/>
            </dict>
            <key>PayloadDisplayName</key>
            <string>SCEP (%s)</string>
            <key>PayloadIdentifier</key>
            <string>com.apple.security.scep.%s</string>
            <key>PayloadType</key>
            <string>com.apple.security.scep</string>
            <key>PayloadUUID</key>
            <string>%s</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
        </dict>`,
		scepConfig.ChallengeVar,
		scepConfig.RenewalVar,
		scepConfig.ProxyURLVar,
		caName,
		wifiConfig.SCEPPayloadUUID,
		wifiConfig.SCEPPayloadUUID,
	)

	// Build EAP configuration
	eapConfig := buildEAPConfig(wifiConfig)

	// WiFi Payload
	wifiPayload := fmt.Sprintf(`        <dict>
            <key>AutoJoin</key>
            <%s/>
            <key>SSID_STR</key>
            <string>%s</string>
            <key>HIDDEN_NETWORK</key>
            <%s/>
            <key>EncryptionType</key>
            <string>%s</string>
            <key>PayloadCertificateUUID</key>
            <string>%s</string>
            <key>EAPClientConfiguration</key>
            <dict>
%s
            </dict>
            <key>PayloadDisplayName</key>
            <string>WiFi (%s)</string>
            <key>PayloadIdentifier</key>
            <string>com.apple.wifi.managed.%s</string>
            <key>PayloadType</key>
            <string>com.apple.wifi.managed</string>
            <key>PayloadUUID</key>
            <string>%s</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
        </dict>`,
		boolToString(wifiConfig.AutoJoin),
		xmlEscape(wifiConfig.SSID),
		boolToString(wifiConfig.Hidden),
		wifiConfig.EncryptionType,
		wifiConfig.SCEPPayloadUUID,
		eapConfig,
		xmlEscape(wifiConfig.SSID),
		wifiConfig.WiFiPayloadUUID,
		wifiConfig.WiFiPayloadUUID,
	)

	// Combine payloads
	profile := fmt.Sprintf(`<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <array>
%s
%s
    </array>
    <key>PayloadDisplayName</key>
    <string>WiFi + SCEP - %s (%s)</string>
    <key>PayloadIdentifier</key>
    <string>%s</string>
    <key>PayloadScope</key>
    <string>System</string>
    <key>PayloadType</key>
    <string>Configuration</string>
    <key>PayloadUUID</key>
    <string>%s</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
</dict>
</plist>
`, scepPayload, wifiPayload, wifiConfig.SSID, caName, payloadID, profileUUID)

	return os.WriteFile(filename, []byte(profile), 0644)
}

// buildEAPConfig generates EAP-TLS configuration XML
func buildEAPConfig(config WiFiConfig) string {
	parts := []string{}

	// Accept EAP Types (13 = EAP-TLS)
	acceptEAPTypes := `                <key>AcceptEAPTypes</key>
                <array>
                    <integer>13</integer>
                </array>`
	parts = append(parts, acceptEAPTypes)

	// Trusted certificate anchors
	if len(config.CertificateAnchorUUIDs) > 0 {
		anchors := []string{}
		for _, uuid := range config.CertificateAnchorUUIDs {
			anchors = append(anchors, fmt.Sprintf("                    <string>%s</string>", uuid))
		}
		certAnchors := fmt.Sprintf(`                <key>PayloadCertificateAnchorUUID</key>
                <array>
%s
                </array>`, strings.Join(anchors, "\n"))
		parts = append(parts, certAnchors)
	}

	// Trusted server names
	if len(config.TrustedServerNames) > 0 {
		names := []string{}
		for _, name := range config.TrustedServerNames {
			names = append(names, fmt.Sprintf("                    <string>%s</string>", xmlEscape(name)))
		}
		serverNames := fmt.Sprintf(`                <key>TLSTrustedServerNames</key>
                <array>
%s
                </array>`, strings.Join(names, "\n"))
		parts = append(parts, serverNames)
	}

	// TLS minimum/maximum version
	tlsVersions := `                <key>TLSMinimumVersion</key>
                <string>1.2</string>
                <key>TLSMaximumVersion</key>
                <string>1.3</string>`
	parts = append(parts, tlsVersions)

	return strings.Join(parts, "\n")
}

// writeVPNProfile creates IKEv2 VPN profile
func writeVPNProfile(
	filename string,
	payloadID string,
	caName string,
	vpnConfig VPNConfig,
	profileUUID string,
) error {
	// Build IKEv2 configuration
	ikev2Config := buildIKEv2Config(vpnConfig)

	// VPN Payload
	vpnPayload := fmt.Sprintf(`        <dict>
            <key>UserDefinedName</key>
            <string>%s</string>
            <key>VPNType</key>
            <string>IKEv2</string>
            <key>VPNSubType</key>
            <string></string>
            <key>IKEv2</key>
            <dict>
%s
            </dict>
            <key>PayloadDisplayName</key>
            <string>VPN (%s)</string>
            <key>PayloadIdentifier</key>
            <string>com.apple.vpn.managed.%s</string>
            <key>PayloadType</key>
            <string>com.apple.vpn.managed</string>
            <key>PayloadUUID</key>
            <string>%s</string>
            <key>PayloadVersion</key>
            <integer>1</integer>
        </dict>`,
		xmlEscape(vpnConfig.UserDefinedName),
		ikev2Config,
		xmlEscape(vpnConfig.UserDefinedName),
		vpnConfig.VPNPayloadUUID,
		vpnConfig.VPNPayloadUUID,
	)

	// Complete profile
	profile := fmt.Sprintf(`<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <array>
%s
    </array>
    <key>PayloadDisplayName</key>
    <string>VPN - %s (%s)</string>
    <key>PayloadIdentifier</key>
    <string>%s</string>
    <key>PayloadScope</key>
    <string>System</string>
    <key>PayloadType</key>
    <string>Configuration</string>
    <key>PayloadUUID</key>
    <string>%s</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
</dict>
</plist>
`, vpnPayload, vpnConfig.UserDefinedName, caName, payloadID, profileUUID)

	return os.WriteFile(filename, []byte(profile), 0644)
}

// buildIKEv2Config generates IKEv2 configuration XML
func buildIKEv2Config(config VPNConfig) string {
	parts := []string{}

	// Basic IKEv2 settings
	basicSettings := fmt.Sprintf(`                <key>RemoteAddress</key>
                <string>%s</string>
                <key>LocalIdentifier</key>
                <string>%s</string>
                <key>RemoteIdentifier</key>
                <string>%s</string>
                <key>AuthenticationMethod</key>
                <string>Certificate</string>
                <key>PayloadCertificateUUID</key>
                <string>%s</string>`,
		xmlEscape(config.ServerAddress),
		xmlEscape(config.LocalIdentifier),
		xmlEscape(config.RemoteIdentifier),
		config.SCEPPayloadUUID,
	)
	parts = append(parts, basicSettings)

	// Server certificate validation
	if config.ServerCertCommonName != "" {
		serverCertCN := fmt.Sprintf(`                <key>ServerCertificateCommonName</key>
                <string>%s</string>`, xmlEscape(config.ServerCertCommonName))
		parts = append(parts, serverCertCN)
	}

	// Dead Peer Detection
	dpdRate := config.DeadPeerDetectionRate
	if dpdRate == "" {
		dpdRate = "Medium"
	}
	dpd := fmt.Sprintf(`                <key>DeadPeerDetectionRate</key>
                <string>%s</string>`, dpdRate)
	parts = append(parts, dpd)

	// On-Demand configuration
	if config.OnDemandEnabled {
		onDemand := `                <key>OnDemandEnabled</key>
                <integer>1</integer>`
		parts = append(parts, onDemand)

		if len(config.OnDemandRules) > 0 {
			rulesXML := buildOnDemandRules(config.OnDemandRules)
			parts = append(parts, rulesXML)
		}
	}

	// Include/Exclude Networks
	if config.IncludeAllNetworks {
		includeAll := `                <key>IncludeAllNetworks</key>
                <integer>1</integer>`
		parts = append(parts, includeAll)

		if config.ExcludeLocalNetworks {
			excludeLocal := `                <key>ExcludeLocalNetworks</key>
                <integer>1</integer>`
			parts = append(parts, excludeLocal)
		}
	}

	// IKE Security Association Parameters
	ikeParams := `                <key>IKESecurityAssociationParameters</key>
                <dict>
                    <key>EncryptionAlgorithm</key>
                    <string>AES-256-GCM</string>
                    <key>IntegrityAlgorithm</key>
                    <string>SHA2-256</string>
                    <key>DiffieHellmanGroup</key>
                    <integer>14</integer>
                    <key>LifeTimeInMinutes</key>
                    <integer>1440</integer>
                </dict>`
	parts = append(parts, ikeParams)

	// Child Security Association Parameters
	childParams := `                <key>ChildSecurityAssociationParameters</key>
                <dict>
                    <key>EncryptionAlgorithm</key>
                    <string>AES-256-GCM</string>
                    <key>IntegrityAlgorithm</key>
                    <string>SHA2-256</string>
                    <key>DiffieHellmanGroup</key>
                    <integer>14</integer>
                    <key>LifeTimeInMinutes</key>
                    <integer>1440</integer>
                </dict>`
	parts = append(parts, childParams)

	return strings.Join(parts, "\n")
}

// buildOnDemandRules generates On-Demand rules XML
func buildOnDemandRules(rules []OnDemandRule) string {
	if len(rules) == 0 {
		return ""
	}

	ruleStrings := []string{}
	for _, rule := range rules {
		ruleXML := buildOnDemandRule(rule)
		ruleStrings = append(ruleStrings, ruleXML)
	}

	return fmt.Sprintf(`                <key>OnDemandRules</key>
                <array>
%s
                </array>`, strings.Join(ruleStrings, "\n"))
}

// buildOnDemandRule generates a single On-Demand rule XML
func buildOnDemandRule(rule OnDemandRule) string {
	parts := []string{}

	// Action
	action := fmt.Sprintf(`                        <key>Action</key>
                        <string>%s</string>`, rule.Action)
	parts = append(parts, action)

	// DNS Domain Match
	if len(rule.DNSDomainMatch) > 0 {
		domains := []string{}
		for _, domain := range rule.DNSDomainMatch {
			domains = append(domains, fmt.Sprintf("                            <string>%s</string>", xmlEscape(domain)))
		}
		dnsDomain := fmt.Sprintf(`                        <key>DNSDomainMatch</key>
                        <array>
%s
                        </array>`, strings.Join(domains, "\n"))
		parts = append(parts, dnsDomain)
	}

	// DNS Server Match
	if len(rule.DNSServerMatch) > 0 {
		servers := []string{}
		for _, server := range rule.DNSServerMatch {
			servers = append(servers, fmt.Sprintf("                            <string>%s</string>", xmlEscape(server)))
		}
		dnsServer := fmt.Sprintf(`                        <key>DNSServerAddressMatch</key>
                        <array>
%s
                        </array>`, strings.Join(servers, "\n"))
		parts = append(parts, dnsServer)
	}

	// SSID Match
	if len(rule.SSIDMatch) > 0 {
		ssids := []string{}
		for _, ssid := range rule.SSIDMatch {
			ssids = append(ssids, fmt.Sprintf("                            <string>%s</string>", xmlEscape(ssid)))
		}
		ssidMatch := fmt.Sprintf(`                        <key>SSIDMatch</key>
                        <array>
%s
                        </array>`, strings.Join(ssids, "\n"))
		parts = append(parts, ssidMatch)
	}

	// Interface Type Match
	if rule.InterfaceTypeMatch != "" {
		interfaceType := fmt.Sprintf(`                        <key>InterfaceTypeMatch</key>
                        <string>%s</string>`, rule.InterfaceTypeMatch)
		parts = append(parts, interfaceType)
	}

	// URL String Probe
	if rule.URLStringProbe != "" {
		urlProbe := fmt.Sprintf(`                        <key>URLStringProbe</key>
                        <string>%s</string>`, xmlEscape(rule.URLStringProbe))
		parts = append(parts, urlProbe)
	}

	return fmt.Sprintf(`                    <dict>
%s
                    </dict>`, strings.Join(parts, "\n"))
}
