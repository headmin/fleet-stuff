# Jamf Pro Script Extractor

Quick how to extract standalone scripts from Jamf Pro YAML backup exports.
Exporting `.mobileconfig` profiles works the same way, requires the contour tool (ETA ): https://github.com/headmin/contour 

## Steps for Scripts 

### 1. Export scripts from Jamf Pro

1. Install the [jamf-cli](https://github.com/Jamf-Concepts/jamf-cli) tool 
2. Connect with Jamf Pro instance `jamf-cli pro setup --url https://jamf.company.com` (readonly) 
3. Run the command below will extract scripts to a /backup folder

```bash
jamf-cli pro backup --output ./backup --resources scripts
```

### 2. Run the extractor

```bash
# Pure shell (no dependencies)
./extract-scripts.sh ./backup/scripts ./extracted

# Or with Python/PyYAML fallback
./extract-scripts-py.sh ./backup/scripts ./extracted
```

Both arguments are optional — defaults to the current directory for input and `./extracted` for output.

### 3. Find your scripts in `./extracted`

```
extracted/
├── Installomator.zsh
├── tempAdmin.sh
├── WindowsDefenderATPOnboarding.py
└── ...
```

Each script is `chmod +x` and named after the `name` field in the YAML, with the extension detected from the shebang line (`#!/bin/bash` → `.sh`, `#!/usr/bin/python` → `.py`, `#!/bin/zsh` → `.zsh`).
