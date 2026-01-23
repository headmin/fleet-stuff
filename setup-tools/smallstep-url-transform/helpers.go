package main

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// promptBool prompts user for yes/no with default
func promptBool(reader *bufio.Reader, msg string, defaultVal bool) bool {
	defaultStr := "y/N"
	if defaultVal {
		defaultStr = "Y/n"
	}

	input := prompt(reader, fmt.Sprintf("%s%s (%s): %s", Yellow, msg, defaultStr, Reset))
	input = strings.ToLower(strings.TrimSpace(input))

	if input == "" {
		return defaultVal
	}

	return input == "y" || input == "yes"
}

// promptWithDefault prompts user with a default value
func promptWithDefault(reader *bufio.Reader, msg string, defaultVal string) string {
	input := prompt(reader, fmt.Sprintf("%s%s%s [%s]: ", Yellow, msg, Reset, defaultVal))
	if input == "" {
		return defaultVal
	}
	return input
}

// promptList prompts user for comma-separated list
func promptList(reader *bufio.Reader, msg string) []string {
	input := prompt(reader, fmt.Sprintf("%s%s%s ", Yellow, msg, Reset))
	if input == "" {
		return []string{}
	}

	items := strings.Split(input, ",")
	result := []string{}
	for _, item := range items {
		trimmed := strings.TrimSpace(item)
		if trimmed != "" {
			result = append(result, trimmed)
		}
	}
	return result
}

// loadPEMFile loads and validates PEM certificate
func loadPEMFile(reader *bufio.Reader, promptMsg string) (string, error) {
	certPath := prompt(reader, fmt.Sprintf("%s%s%s ", Yellow, promptMsg, Reset))
	if certPath == "" {
		return "", nil
	}

	certPath = expandPath(certPath)
	content, err := os.ReadFile(certPath)
	if err != nil {
		return "", fmt.Errorf("reading file: %w", err)
	}

	pemStr := string(content)
	if !strings.Contains(pemStr, "BEGIN CERTIFICATE") {
		return "", fmt.Errorf("file does not appear to be a PEM certificate")
	}

	return pemStr, nil
}

// generatePayloadUUIDs generates multiple UUIDs from base
func generatePayloadUUIDs(base string, suffixes []string) map[string]string {
	uuids := make(map[string]string)
	for _, suffix := range suffixes {
		uuids[suffix] = generateUUID(base + "." + suffix)
	}
	return uuids
}

// boolToString converts bool to "true" or "false" string for XML
func boolToString(b bool) string {
	if b {
		return "true"
	}
	return "false"
}

// validateSSID validates WiFi SSID
func validateSSID(ssid string) error {
	if ssid == "" {
		return fmt.Errorf("SSID cannot be empty")
	}
	if len(ssid) > 32 {
		return fmt.Errorf("SSID cannot exceed 32 characters")
	}
	return nil
}

// validateHostname validates hostname or IP address
func validateHostname(hostname string) error {
	if hostname == "" {
		return fmt.Errorf("hostname cannot be empty")
	}
	// Basic validation - could be enhanced
	if strings.Contains(hostname, " ") {
		return fmt.Errorf("hostname cannot contain spaces")
	}
	return nil
}

// ensureDirectoryExists creates directory if it doesn't exist
func ensureDirectoryExists(path string) error {
	dir := filepath.Dir(path)
	if dir == "." || dir == "" {
		return nil
	}
	return os.MkdirAll(dir, 0755)
}

// stringArrayToXML converts string array to XML array format
func stringArrayToXML(items []string, indent string) string {
	if len(items) == 0 {
		return ""
	}

	var result strings.Builder
	result.WriteString(fmt.Sprintf("%s<array>\n", indent))
	for _, item := range items {
		result.WriteString(fmt.Sprintf("%s    <string>%s</string>\n", indent, xmlEscape(item)))
	}
	result.WriteString(fmt.Sprintf("%s</array>", indent))
	return result.String()
}

// xmlEscape escapes special XML characters
func xmlEscape(s string) string {
	s = strings.ReplaceAll(s, "&", "&amp;")
	s = strings.ReplaceAll(s, "<", "&lt;")
	s = strings.ReplaceAll(s, ">", "&gt;")
	s = strings.ReplaceAll(s, "'", "&apos;")
	s = strings.ReplaceAll(s, "\"", "&quot;")
	return s
}

// printSuccess prints a success message
func printSuccess(msg string) {
	fmt.Printf("%s✓ %s%s\n", Green, msg, Reset)
}

// printError prints an error message
func printError(msg string) {
	fmt.Printf("%s✗ %s%s\n", Yellow, msg, Reset)
}

// printInfo prints an info message
func printInfo(msg string) {
	fmt.Printf("%s→ %s%s\n", Cyan, msg, Reset)
}

// printSection prints a section header
func printSection(title string) {
	fmt.Printf("\n%s%s═══════════════════════════════════════════════%s\n", Bold, Cyan, Reset)
	fmt.Printf("%s%s %s%s\n", Bold, Cyan, title, Reset)
	fmt.Printf("%s%s═══════════════════════════════════════════════%s\n\n", Bold, Cyan, Reset)
}

// confirmAction asks user to confirm an action
func confirmAction(reader *bufio.Reader, msg string) bool {
	return promptBool(reader, msg, false)
}

// getFilenameBase returns the base filename without extension
func getFilenameBase(filename string) string {
	base := filepath.Base(filename)
	ext := filepath.Ext(base)
	return strings.TrimSuffix(base, ext)
}

// sanitizeFilename sanitizes a string for use in filename
func sanitizeFilename(s string) string {
	s = strings.ToLower(s)
	s = strings.ReplaceAll(s, " ", "-")
	s = strings.ReplaceAll(s, "_", "-")
	// Remove any characters that aren't alphanumeric or dash
	var result strings.Builder
	for _, r := range s {
		if (r >= 'a' && r <= 'z') || (r >= '0' && r <= '9') || r == '-' {
			result.WriteRune(r)
		}
	}
	return result.String()
}
