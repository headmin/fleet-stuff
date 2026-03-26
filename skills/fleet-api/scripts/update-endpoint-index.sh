#!/bin/bash
# update-endpoint-index.sh
#
# Fetches the latest Fleet REST API docs and regenerates the endpoint index.
# Usage: ./update-endpoint-index.sh [path-to-rest-api.md]
#
# If no path given, fetches from GitHub main branch.
# Output: references/endpoint-index.md (overwritten)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT="$SKILL_DIR/references/endpoint-index.md"
TMPFILE=$(mktemp)

# Get the source file
if [ -n "${1:-}" ]; then
  SOURCE="$1"
  echo "Using local file: $SOURCE"
else
  echo "Fetching latest REST API docs from GitHub..."
  SOURCE="$TMPFILE"
  curl -sL "https://raw.githubusercontent.com/fleetdm/fleet/main/docs/REST%20API/rest-api.md" -o "$SOURCE"
  if [ ! -s "$SOURCE" ]; then
    echo "ERROR: Failed to download API docs. Provide a local path instead."
    rm -f "$TMPFILE"
    exit 1
  fi
  echo "Downloaded $(wc -l < "$SOURCE") lines."
fi

# Extract endpoints and generate index
python3 -c "
import re, sys

with open(sys.argv[1]) as f:
    lines = f.read().split('\n')

current_section = ''
current_subsection = ''
seen = set()
results = {}

for line in lines:
    line = line.rstrip()
    if line.startswith('## ') and not line.startswith('### '):
        current_section = line[3:]
    elif line.startswith('### '):
        current_subsection = line[4:]
    m = re.match(r'^\x60(GET|POST|PUT|PATCH|DELETE) (/api/v1/[^\x60\?]+)\x60\$', line)
    if m:
        method = m.group(1)
        path = m.group(2)
        # Skip example lines with specific IDs/values
        if not re.search(r'/\d+[/)]|/\d+\$|abcdef|392547|6d3e95|AA598E|f663713|b15ce|abc-def|cve-|ubuntu_label|foo\$', path):
            key = f'{method} {path}'
            if key not in seen:
                seen.add(key)
                results.setdefault(current_section, []).append((current_subsection, method, path))

output = [
    '# Fleet API Endpoint Index',
    '',
    'Auto-generated from Fleet REST API docs. Re-run scripts/update-endpoint-index.sh to update.',
    '',
]

total = 0
for section, endpoints in results.items():
    if not endpoints:
        continue
    output.append(f'## {section}')
    output.append('')
    output.append('| Endpoint | Method | Path |')
    output.append('|---|---|---|')
    for sub, method, path in endpoints:
        output.append(f'| {sub} | \x60{method}\x60 | \x60{path}\x60 |')
        total += 1
    output.append('')

output.append(f'---')
output.append(f'Total: {total} endpoints')

with open(sys.argv[2], 'w') as f:
    f.write('\n'.join(output))

print(f'Generated {total} endpoints in {len(output)} lines -> {sys.argv[2]}')
" "$SOURCE" "$OUTPUT"

rm -f "$TMPFILE"
echo "Done."
