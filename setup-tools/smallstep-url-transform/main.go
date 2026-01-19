package main

import (
	"bufio"
	"crypto/md5"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

// ANSI color codes
const (
	Reset   = "\033[0m"
	Bold    = "\033[1m"
	Dim     = "\033[2m"
	Cyan    = "\033[36m"
	Green   = "\033[32m"
	Yellow  = "\033[33m"
	Blue    = "\033[34m"
	Magenta = "\033[35m"
	White   = "\033[37m"
)

func main() {
	reader := bufio.NewReader(os.Stdin)

	fmt.Printf("%s%sSmallstep -> Fleet SCEP URL transformer%s\n\n", Bold, Cyan, Reset)

	// 1. Get SCEP URL
	scepURL := prompt(reader, fmt.Sprintf("%sEnter Smallstep SCEP URL:%s ", Yellow, Reset))
	for !strings.HasPrefix(scepURL, "https://") {
		fmt.Printf("%sPlease include scheme (https://). Try again.%s\n", Dim, Reset)
		scepURL = prompt(reader, fmt.Sprintf("%sEnter Smallstep SCEP URL:%s ", Yellow, Reset))
	}

	// 2. Get Challenge URL
	challengeURL := prompt(reader, fmt.Sprintf("%sEnter Smallstep Challenge URL:%s ", Yellow, Reset))
	for !strings.HasPrefix(challengeURL, "https://") {
		fmt.Printf("%sPlease include scheme (https://). Try again.%s\n", Dim, Reset)
		challengeURL = prompt(reader, fmt.Sprintf("%sEnter Smallstep Challenge URL:%s ", Yellow, Reset))
	}

	// 3. Get Root CA certificate (optional)
	fmt.Println()
	fmt.Printf("%sEnter path to Smallstep ROOT CA certificate PEM file (press Enter to skip)%s\n", Dim, Reset)
	fmt.Printf("%s(Download from Smallstep dashboard or use: step ca root root_ca.crt --ca-url <URL> --fingerprint <FP>)%s\n", Dim, Reset)
	rootCertPEM := ""
	rootCertPath := prompt(reader, fmt.Sprintf("%sRoot CA certificate file path:%s ", Yellow, Reset))
	if rootCertPath != "" {
		rootCertPath = expandPath(rootCertPath)
		content, err := os.ReadFile(rootCertPath)
		if err != nil {
			fmt.Printf("%sError reading file: %v%s\n", Yellow, err, Reset)
		} else if !strings.Contains(string(content), "BEGIN CERTIFICATE") {
			fmt.Printf("%sFile does not appear to be a PEM certificate.%s\n", Yellow, Reset)
		} else {
			rootCertPEM = string(content)
			fmt.Printf("%sRoot CA certificate loaded.%s\n", Green, Reset)
		}
	} else {
		fmt.Printf("%sSkipping root CA (no cert provided).%s\n", Dim, Reset)
	}

	// 4. Get Intermediate CA certificate (optional, only if root was provided)
	intermediateCertPEM := ""
	if rootCertPEM != "" {
		fmt.Println()
		fmt.Printf("%sEnter path to Smallstep INTERMEDIATE CA certificate PEM file (press Enter to skip)%s\n", Dim, Reset)
		intermediateCertPath := prompt(reader, fmt.Sprintf("%sIntermediate CA certificate file path:%s ", Yellow, Reset))
		if intermediateCertPath != "" {
			intermediateCertPath = expandPath(intermediateCertPath)
			content, err := os.ReadFile(intermediateCertPath)
			if err != nil {
				fmt.Printf("%sError reading file: %v%s\n", Yellow, err, Reset)
			} else if !strings.Contains(string(content), "BEGIN CERTIFICATE") {
				fmt.Printf("%sFile does not appear to be a PEM certificate.%s\n", Yellow, Reset)
			} else {
				intermediateCertPEM = string(content)
				fmt.Printf("%sIntermediate CA certificate loaded.%s\n", Green, Reset)
			}
		} else {
			fmt.Printf("%sSkipping intermediate CA (no cert provided).%s\n", Dim, Reset)
		}
	}

	// Parse URLs
	teamName, integrationID := parseURLs(scepURL, challengeURL)
	if teamName == "" || integrationID == "" {
		fmt.Printf("\n%sCould not parse team and integration ID from URLs.%s\n", Yellow, Reset)
		teamName = prompt(reader, fmt.Sprintf("%sEnter SMALLSTEP_TEAM_NAME:%s ", Yellow, Reset))
		integrationID = prompt(reader, fmt.Sprintf("%sEnter INTEGRATION_ID:%s ", Yellow, Reset))
	}

	// Build Fleet proxy URL
	fleetProxyURL := fmt.Sprintf("https://%s.scep.smallstep.com/p/agents/%s", teamName, integrationID)

	// CA name loop
	for {
		fmt.Println()
		caName := prompt(reader, fmt.Sprintf("%sEnter Fleet CA name%s [SMALLSTEP_CA]: ", Yellow, Reset))
		if caName == "" {
			caName = "SMALLSTEP_CA"
		}
		caNameUpper := normalizeCaName(caName)

		// Ask about SCEP mobileconfig
		genConfig := prompt(reader, fmt.Sprintf("%sGenerate SCEP mobileconfig file?%s (y/N): ", Yellow, Reset))
		wantConfig := strings.ToLower(genConfig) == "y" || strings.ToLower(genConfig) == "yes"

		var payloadID, outputFile, profileUUID, scepUUID string
		if wantConfig {
			defaultID := fmt.Sprintf("com.fleetdm.scep.%s", strings.ToLower(caNameUpper))
			payloadID = prompt(reader, fmt.Sprintf("%sEnter PayloadIdentifier%s [%s]: ", Yellow, Reset, defaultID))
			if payloadID == "" {
				payloadID = defaultID
			}

			defaultFile := fmt.Sprintf("smallstep-scep-%s.mobileconfig", strings.ToLower(caNameUpper))
			outputFile = prompt(reader, fmt.Sprintf("%sOutput filename%s [%s]: ", Yellow, Reset, defaultFile))
			if outputFile == "" {
				outputFile = defaultFile
			}

			profileUUID = generateUUID(payloadID)
			scepUUID = generateUUID("com.apple.security.scep." + payloadID)
		}

		// Output results
		varPrefix := "FLEET_VAR_SMALLSTEP_SCEP"
		challengeVar := fmt.Sprintf("$%s_CHALLENGE_%s", varPrefix, caNameUpper)
		proxyVar := fmt.Sprintf("$%s_PROXY_URL_%s", varPrefix, caNameUpper)
		renewalVar := "$FLEET_VAR_SCEP_RENEWAL_ID"

		fmt.Println()
		fmt.Printf("%s%s============================================%s\n", Bold, Cyan, Reset)
		fmt.Printf("%s%sFleet CA Settings (copy-paste these values)%s\n", Bold, Cyan, Reset)
		fmt.Printf("%s%s============================================%s\n", Bold, Cyan, Reset)
		fmt.Println()
		fmt.Printf("%sName%s\n", Dim, Reset)
		fmt.Printf("%s%s%s\n", Bold+Green, caNameUpper, Reset)
		fmt.Println()
		fmt.Printf("%sSCEP URL%s\n", Dim, Reset)
		fmt.Printf("%s%s%s\n", Green, fleetProxyURL, Reset)
		fmt.Println()
		fmt.Printf("%sChallenge URL%s\n", Dim, Reset)
		fmt.Printf("%s%s%s\n", Green, challengeURL, Reset)
		fmt.Println()
		fmt.Printf("%s%s--------------------------------------------%s\n", Bold, Blue, Reset)
		fmt.Printf("%s%sFleet Variable Names (for profiles)%s\n", Bold, Blue, Reset)
		fmt.Printf("%s%s--------------------------------------------%s\n", Bold, Blue, Reset)
		fmt.Println()
		fmt.Printf("%sChallenge:%s   %s%s%s\n", Dim, Reset, Magenta, challengeVar, Reset)
		fmt.Printf("%sProxy URL:%s   %s%s%s\n", Dim, Reset, Magenta, proxyVar, Reset)
		fmt.Printf("%sRenewal ID:%s  %s%s%s\n", Dim, Reset, Magenta, renewalVar, Reset)
		fmt.Println()
		fmt.Printf("%s%s--------------------------------------------%s\n", Bold, Blue, Reset)
		fmt.Printf("%s%sNotes%s\n", Bold, Blue, Reset)
		fmt.Printf("%s%s--------------------------------------------%s\n", Bold, Blue, Reset)
		fmt.Printf("%s* Add %s%s%s to the OU field for automatic certificate renewal.%s\n", Dim, Magenta, renewalVar, Dim, Reset)
		fmt.Printf("%s* Original Smallstep SCEP URL: %s%s\n", Dim, scepURL, Reset)
		fmt.Printf("%s* Detected team: %s, integration: %s%s\n", Dim, teamName, integrationID, Reset)

		// Generate SCEP mobileconfig if requested
		if wantConfig {
			if err := writeSCEPMobileconfig(outputFile, payloadID, caNameUpper, challengeVar, proxyVar, renewalVar, profileUUID, scepUUID); err != nil {
				fmt.Printf("\n%sError writing mobileconfig: %v%s\n", Yellow, err, Reset)
			} else {
				fmt.Println()
				fmt.Printf("%s%s--------------------------------------------%s\n", Bold, Green, Reset)
				fmt.Printf("%s%sGenerated SCEP mobileconfig%s\n", Bold, Green, Reset)
				fmt.Printf("%s%s--------------------------------------------%s\n", Bold, Green, Reset)
				fmt.Println()
				fmt.Printf("  %sFile:%s %s%s%s\n", Dim, Reset, Green, outputFile, Reset)
				fmt.Println()
				fmt.Printf("  %sProfile PayloadIdentifier:%s %s\n", Dim, Reset, payloadID)
				fmt.Printf("  %sProfile PayloadUUID:%s       %s\n", Dim, Reset, profileUUID)
				fmt.Printf("  %sSCEP PayloadIdentifier:%s    com.apple.security.scep.%s\n", Dim, Reset, scepUUID)
				fmt.Printf("  %sSCEP PayloadUUID:%s          %s\n", Dim, Reset, scepUUID)
			}
		}

		// Generate Trust mobileconfig if CA certs provided
		if rootCertPEM != "" {
			genTrust := prompt(reader, fmt.Sprintf("\n%sGenerate CA trust mobileconfig?%s (y/N): ", Yellow, Reset))
			if strings.ToLower(genTrust) == "y" || strings.ToLower(genTrust) == "yes" {
				defaultTrustFile := fmt.Sprintf("smallstep-trust-%s.mobileconfig", strings.ToLower(caNameUpper))
				trustFile := prompt(reader, fmt.Sprintf("%sTrust profile filename%s [%s]: ", Yellow, Reset, defaultTrustFile))
				if trustFile == "" {
					trustFile = defaultTrustFile
				}

				// Use same payloadID base or generate one
				trustPayloadID := payloadID
				if trustPayloadID == "" {
					trustPayloadID = fmt.Sprintf("com.fleetdm.scep.%s", strings.ToLower(caNameUpper))
				}

				trustProfileUUID := generateUUID("trust." + trustPayloadID)
				rootCertUUID := generateUUID("com.apple.security.root." + trustPayloadID)
				intermediateCertUUID := ""
				if intermediateCertPEM != "" {
					intermediateCertUUID = generateUUID("com.apple.security.pkcs1.intermediate." + trustPayloadID)
				}

				if err := writeTrustMobileconfig(trustFile, trustPayloadID, caNameUpper, rootCertPEM, intermediateCertPEM, trustProfileUUID, rootCertUUID, intermediateCertUUID); err != nil {
					fmt.Printf("\n%sError writing trust mobileconfig: %v%s\n", Yellow, err, Reset)
				} else {
					fmt.Println()
					fmt.Printf("%s%s--------------------------------------------%s\n", Bold, Green, Reset)
					fmt.Printf("%s%sGenerated CA Trust mobileconfig (Device Channel)%s\n", Bold, Green, Reset)
					fmt.Printf("%s%s--------------------------------------------%s\n", Bold, Green, Reset)
					fmt.Println()
					fmt.Printf("  %sFile:%s %s%s%s\n", Dim, Reset, Green, trustFile, Reset)
					fmt.Println()
					fmt.Printf("  %sProfile PayloadIdentifier:%s trust.%s\n", Dim, Reset, trustPayloadID)
					fmt.Printf("  %sProfile PayloadUUID:%s       %s\n", Dim, Reset, trustProfileUUID)
					fmt.Printf("  %sRoot CA PayloadUUID:%s       %s\n", Dim, Reset, rootCertUUID)
					if intermediateCertUUID != "" {
						fmt.Printf("  %sIntermediate CA PayloadUUID:%s %s\n", Dim, Reset, intermediateCertUUID)
					}
				}
			}
		}

		fmt.Println()
		again := prompt(reader, fmt.Sprintf("%sTry another CA name?%s (y/N): ", Yellow, Reset))
		if strings.ToLower(again) != "y" && strings.ToLower(again) != "yes" {
			break
		}
	}

	fmt.Printf("\n%s%sDone.%s\n", Bold, Green, Reset)
}

func prompt(reader *bufio.Reader, msg string) string {
	fmt.Print(msg)
	input, _ := reader.ReadString('\n')
	return strings.TrimSpace(input)
}

func expandPath(path string) string {
	if strings.HasPrefix(path, "~/") {
		home, err := os.UserHomeDir()
		if err == nil {
			return filepath.Join(home, path[2:])
		}
	}
	return path
}

func normalizeCaName(name string) string {
	name = strings.ReplaceAll(name, " ", "_")
	name = strings.ReplaceAll(name, "-", "_")
	return strings.ToUpper(name)
}

func parseURLs(scepURL, challengeURL string) (team, integration string) {
	// Try SCEP URL patterns
	scepPatterns := []*regexp.Regexp{
		regexp.MustCompile(`^https://agents\.([^/]+)\.ca\.smallstep\.com/scep/([^/]+)$`),
		regexp.MustCompile(`^https://agents\.([^/]+)\.smallstep\.com/scep/([^/]+)$`),
	}

	scepURL = strings.TrimSuffix(scepURL, "/pkiclient.exe")
	scepURL = strings.TrimSuffix(scepURL, "/")

	for _, re := range scepPatterns {
		if m := re.FindStringSubmatch(scepURL); m != nil {
			return m[1], m[2]
		}
	}

	// Try Challenge URL patterns
	challengePatterns := []*regexp.Regexp{
		regexp.MustCompile(`^https://([^/]+)\.scep\.smallstep\.com/[^/]+/([^/]+)/challenge$`),
		regexp.MustCompile(`^https://agents\.([^/]+)\.ca\.smallstep\.com/challenge/([^/]+)`),
		regexp.MustCompile(`^https://agents\.([^/]+)\.smallstep\.com/challenge/([^/]+)`),
	}

	challengeURL = strings.TrimSuffix(challengeURL, "/")

	for _, re := range challengePatterns {
		if m := re.FindStringSubmatch(challengeURL); m != nil {
			return m[1], m[2]
		}
	}

	return "", ""
}

func generateUUID(input string) string {
	hash := md5.Sum([]byte(input))
	return strings.ToUpper(fmt.Sprintf("%x-%x-%x-%x-%x",
		hash[0:4], hash[4:6], hash[6:8], hash[8:10], hash[10:16]))
}

func pemToBase64(pem string) string {
	// Strip PEM headers and join lines
	lines := strings.Split(pem, "\n")
	var b64Lines []string
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" || strings.Contains(line, "BEGIN CERTIFICATE") || strings.Contains(line, "END CERTIFICATE") {
			continue
		}
		b64Lines = append(b64Lines, line)
	}
	return strings.Join(b64Lines, "")
}

func writeSCEPMobileconfig(filename, payloadID, caName, challengeVar, proxyVar, renewalVar, profileUUID, scepUUID string) error {
	content := fmt.Sprintf(`<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>PayloadContent</key>
    <array>
        <dict>
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
        </dict>
    </array>
    <key>PayloadDisplayName</key>
    <string>Smallstep SCEP - %s</string>
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
`, challengeVar, renewalVar, proxyVar, caName, scepUUID, scepUUID, caName, payloadID, profileUUID)

	return os.WriteFile(filename, []byte(content), 0644)
}

func writeTrustMobileconfig(filename, payloadID, caName, rootCertPEM, intermediateCertPEM, profileUUID, rootCertUUID, intermediateCertUUID string) error {
	rootCertBase64 := pemToBase64(rootCertPEM)

	// Build payload content
	payloadContent := fmt.Sprintf(`        <dict>
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
        </dict>`, rootCertBase64, rootCertUUID, rootCertUUID)

	// Add intermediate cert if provided
	if intermediateCertPEM != "" {
		intermediateCertBase64 := pemToBase64(intermediateCertPEM)
		payloadContent += fmt.Sprintf(`
        <dict>
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
        </dict>`, intermediateCertBase64, intermediateCertUUID, intermediateCertUUID)
	}

	content := fmt.Sprintf(`<?xml version="1.0" encoding="UTF-8"?>
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

	return os.WriteFile(filename, []byte(content), 0644)
}
