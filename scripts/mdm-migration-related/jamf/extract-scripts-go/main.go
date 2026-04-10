// Extract scriptContents from Jamf Pro YAML exports into standalone script files.
//
// Usage:  extract-scripts [source_dir] [output_dir]
//   source_dir  — directory containing .yaml files (default: current directory)
//   output_dir  — where to write extracted scripts  (default: ./extracted)
package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"gopkg.in/yaml.v3"
)

// jamfScript holds only the fields we care about from each YAML export.
type jamfScript struct {
	Name           string `yaml:"name"`
	ScriptContents string `yaml:"scriptContents"`
}

func main() {
	sourceDir := "."
	if len(os.Args) > 1 {
		sourceDir = os.Args[1]
	}

	outputDir := filepath.Join(sourceDir, "extracted")
	if len(os.Args) > 2 {
		outputDir = os.Args[2]
	}

	if err := os.MkdirAll(outputDir, 0o755); err != nil {
		fmt.Fprintf(os.Stderr, "error creating output dir: %v\n", err)
		os.Exit(1)
	}

	files, err := filepath.Glob(filepath.Join(sourceDir, "*.yaml"))
	if err != nil {
		fmt.Fprintf(os.Stderr, "error globbing: %v\n", err)
		os.Exit(1)
	}

	count := 0
	for _, yamlPath := range files {
		if err := processFile(yamlPath, outputDir); err != nil {
			fmt.Fprintf(os.Stderr, "  ERROR: %s: %v\n", filepath.Base(yamlPath), err)
		}
		count++
	}

	fmt.Printf("\nProcessed %d YAML files. Extracted scripts are in: %s\n", count, outputDir)
}

func processFile(yamlPath, outputDir string) error {
	data, err := os.ReadFile(yamlPath)
	if err != nil {
		return err
	}

	var doc jamfScript
	if err := yaml.Unmarshal(data, &doc); err != nil {
		return fmt.Errorf("parse yaml: %w", err)
	}

	if strings.TrimSpace(doc.ScriptContents) == "" {
		fmt.Printf("  SKIP (no scriptContents): %s\n", filepath.Base(yamlPath))
		return nil
	}

	// Fall back to the YAML filename (without extension) if name is empty.
	name := doc.Name
	if name == "" {
		name = strings.TrimSuffix(filepath.Base(yamlPath), filepath.Ext(yamlPath))
	}

	ext := detectExt(doc.ScriptContents)
	base := stripScriptExt(name)
	outName := base + ext
	outPath := filepath.Join(outputDir, outName)

	contents := doc.ScriptContents
	if !strings.HasSuffix(contents, "\n") {
		contents += "\n"
	}

	if err := os.WriteFile(outPath, []byte(contents), 0o755); err != nil {
		return err
	}

	fmt.Printf("  OK: %s  ->  %s\n", filepath.Base(yamlPath), outName)
	return nil
}

// detectExt guesses the file extension from the shebang line.
func detectExt(contents string) string {
	firstLine := strings.SplitN(strings.TrimSpace(contents), "\n", 2)[0]

	switch {
	case strings.Contains(firstLine, "python"):
		return ".py"
	case strings.Contains(firstLine, "zsh"):
		return ".zsh"
	case strings.Contains(firstLine, "sh") || strings.Contains(firstLine, "bash"):
		return ".sh"
	default:
		return ".sh"
	}
}

// stripScriptExt removes a known script extension from the end of a filename.
func stripScriptExt(name string) string {
	for _, ext := range []string{".sh", ".py", ".zsh", ".bash"} {
		if strings.HasSuffix(strings.ToLower(name), ext) {
			return name[:len(name)-len(ext)]
		}
	}
	return name
}
