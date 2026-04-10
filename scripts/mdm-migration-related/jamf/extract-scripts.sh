#!/bin/bash
# Extract scriptContents from Jamf Pro YAML exports into standalone script files.
# Pure shell + awk — no Python or external dependencies.
#
# Usage:  ./extract-scripts.sh [source_dir] [output_dir]
#   source_dir  — directory containing .yaml files (default: same dir as this script)
#   output_dir  — where to write extracted scripts  (default: ./extracted)
#
# Handles both YAML scalar styles produced by the Jamf CLI:
#   - Block scalars:   scriptContents: |-  /  scriptContents: |
#   - Quoted strings:  scriptContents: "...\n..."

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_DIR="${1:-$SCRIPT_DIR}"
OUTPUT_DIR="${2:-$SCRIPT_DIR/extracted}"

mkdir -p "$OUTPUT_DIR"

count=0
ok=0

for yamlfile in "$SOURCE_DIR"/*.yaml; do
    [ -f "$yamlfile" ] || continue
    count=$((count + 1))

    # --- Extract the 'name' field ------------------------------------------------
    script_name=$(awk '
        /^name:/ {
            sub(/^name: */, "")
            gsub(/^"|"$/, "")   # strip quotes if present
            print
            exit
        }
    ' "$yamlfile")
    [ -z "$script_name" ] && script_name=$(basename "$yamlfile" .yaml)

    # --- Extract scriptContents --------------------------------------------------
    content=$(awk '
    BEGIN {
        PH = sprintf("%c", 1)   # placeholder for literal backslash during unescape
        in_block = 0
        indent   = 0
    }

    # ── Block scalar: scriptContents: |- or scriptContents: | ──
    /^scriptContents: *\|[-]? *$/ {
        in_block = 1
        next
    }

    in_block == 1 {
        # first content line sets the indentation level
        if (indent == 0 && $0 ~ /^[[:space:]]/) {
            tmp = $0; gsub(/[^ ].*/, "", tmp)
            indent = length(tmp)
        }

        # non-empty line with less indentation → end of block
        if ($0 !~ /^[[:space:]]*$/ && indent > 0) {
            leading = $0
            gsub(/[^ ].*/, "", leading)
            if (length(leading) < indent) exit
        }

        # strip indentation and emit
        if (indent > 0 && length($0) >= indent) {
            print substr($0, indent + 1)
        } else {
            print ""
        }
        next
    }

    # ── Quoted string: scriptContents: "..." ──
    /^scriptContents: "/ {
        s = $0
        sub(/^scriptContents: "/, "", s)
        sub(/"[[:space:]]*$/, "", s)

        # unescape YAML double-quoted escapes (order matters)
        gsub(/\\\\/, PH, s)    # \\\\ → placeholder  (literal backslash)
        gsub(/\\n/,  "\n", s)  # \\n  → newline
        gsub(/\\t/,  "\t", s)  # \\t  → tab
        gsub(/\\"/, "\"", s)   # \\"  → literal quote
        gsub(PH, "\\", s)      # placeholder → backslash
        printf "%s", s
        exit
    }
    ' "$yamlfile")

    # skip if empty
    if [ -z "$content" ]; then
        echo "  SKIP (empty scriptContents): $(basename "$yamlfile")"
        continue
    fi

    # --- Detect file extension from shebang --------------------------------------
    first_line="${content%%
*}"
    case "$first_line" in
        *python*) ext=".py"  ;;
        *zsh*)    ext=".zsh" ;;
        *bash*)   ext=".sh"  ;;
        *sh*)     ext=".sh"  ;;
        *)        ext=".sh"  ;;
    esac

    # Strip any existing script extension from name, then apply detected one
    base=$(printf '%s' "$script_name" | sed 's/\.[a-zA-Z]*$//')
    out_name="${base}${ext}"

    # --- Write the extracted script ----------------------------------------------
    out_path="${OUTPUT_DIR}/${out_name}"
    printf '%s\n' "$content" > "$out_path"
    chmod +x "$out_path"

    ok=$((ok + 1))
    echo "  OK: $(basename "$yamlfile")  ->  ${out_name}"
done

echo ""
echo "Done: ${ok}/${count} scripts extracted to ${OUTPUT_DIR}"
