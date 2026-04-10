#!/bin/bash
# Extract scriptContents from Jamf Pro YAML exports into standalone script files.
# Uses Python 3 + PyYAML — handles all YAML scalar styles correctly.
#
# Usage:  ./extract-scripts-py.sh [source_dir] [output_dir]
#   source_dir  — directory containing .yaml files (default: same dir as this script)
#   output_dir  — where to write extracted scripts  (default: ./extracted)
#
# Requires: python3 with PyYAML (pip3 install pyyaml)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_DIR="${1:-$SCRIPT_DIR}"
OUTPUT_DIR="${2:-$SCRIPT_DIR/extracted}"

mkdir -p "$OUTPUT_DIR"

count=0

for yamlfile in "$SOURCE_DIR"/*.yaml; do
    [ -f "$yamlfile" ] || continue

    # Use Python+PyYAML to correctly parse all YAML scalar styles
    python3 - "$yamlfile" "$OUTPUT_DIR" <<'PYEOF'
import sys, os, yaml

yaml_path = sys.argv[1]
out_dir   = sys.argv[2]

with open(yaml_path, "r") as f:
    doc = yaml.safe_load(f)

contents = doc.get("scriptContents")
if not contents or not contents.strip():
    print(f"  SKIP (no scriptContents): {os.path.basename(yaml_path)}")
    sys.exit(0)

# Derive filename from the 'name' field, falling back to yaml filename
name = doc.get("name", os.path.splitext(os.path.basename(yaml_path))[0])

# Detect extension from shebang
first_line = contents.strip().splitlines()[0] if contents.strip() else ""
if "python" in first_line:
    ext = ".py"
elif "zsh" in first_line:
    ext = ".zsh"
elif "sh" in first_line or "bash" in first_line:
    ext = ".sh"
else:
    ext = ".sh"

# Clean up the name: strip existing extension if present, then add detected one
base = name
for e in (".sh", ".py", ".zsh", ".bash"):
    if base.lower().endswith(e):
        base = base[:-len(e)]
        break

out_name = base + ext
out_path = os.path.join(out_dir, out_name)

with open(out_path, "w") as f:
    f.write(contents)
    # Ensure trailing newline
    if not contents.endswith("\n"):
        f.write("\n")

os.chmod(out_path, 0o755)
print(f"  OK: {os.path.basename(yaml_path)}  ->  {out_name}")
PYEOF

    count=$((count + 1))
done

echo ""
echo "Processed $count YAML files. Extracted scripts are in: $OUTPUT_DIR"
