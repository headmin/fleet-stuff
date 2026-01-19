package main

import (
	"bufio"
	"crypto/md5"
	"fmt"
	"os"
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

		// Ask about mobileconfig
		genConfig := prompt(reader, fmt.Sprintf("%sGenerate mobileconfig file?%s (y/N): ", Yellow, Reset))
		wantConfig := strings.ToLower(genConfig) == "y" || strings.ToLower(genConfig) == "yes"

		var payloadID, outputFile, rootUUID, scepUUID string
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

			rootUUID = generateUUID(payloadID)
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
		fmt.Printf("%s%s%s\n", Bold, Green, caNameUpper)
		fmt.Printf("%s\n", Reset)
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

		// Generate mobileconfig if requested
		if wantConfig {
			if err := writeMobileconfig(outputFile, payloadID, caNameUpper, challengeVar, proxyVar, renewalVar, rootUUID, scepUUID); err != nil {
				fmt.Printf("\n%sError writing mobileconfig: %v%s\n", Yellow, err, Reset)
			} else {
				fmt.Println()
				fmt.Printf("%s%s--------------------------------------------%s\n", Bold, Green, Reset)
				fmt.Printf("%s%sGenerated mobileconfig%s\n", Bold, Green, Reset)
				fmt.Printf("%s%s--------------------------------------------%s\n", Bold, Green, Reset)
				fmt.Println()
				fmt.Printf("  %sFile:%s %s%s%s\n", Dim, Reset, Green, outputFile, Reset)
				fmt.Println()
				fmt.Printf("  %sRoot PayloadIdentifier:%s %s\n", Dim, Reset, payloadID)
				fmt.Printf("  %sRoot PayloadUUID:%s       %s\n", Dim, Reset, rootUUID)
				fmt.Printf("  %sSCEP PayloadIdentifier:%s com.apple.security.scep.%s\n", Dim, Reset, scepUUID)
				fmt.Printf("  %sSCEP PayloadUUID:%s       %s\n", Dim, Reset, scepUUID)
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

func writeMobileconfig(filename, payloadID, caName, challengeVar, proxyVar, renewalVar, rootUUID, scepUUID string) error {
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
    <key>PayloadType</key>
    <string>Configuration</string>
    <key>PayloadUUID</key>
    <string>%s</string>
    <key>PayloadVersion</key>
    <integer>1</integer>
</dict>
</plist>
`, challengeVar, renewalVar, proxyVar, caName, scepUUID, scepUUID, caName, payloadID, rootUUID)

	return os.WriteFile(filename, []byte(content), 0644)
}
