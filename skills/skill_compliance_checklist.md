# Skill Compliance Checklist

Tracks conformance of all skills against the Claude Code skills format specification.

## Format Specification

### Three-Tier Progressive Disclosure

| Tier | What | Loaded When | Constraint |
|------|------|-------------|------------|
| **1. Frontmatter** | YAML `name:`, `description:`, `allowed-tools:`, `effort:` | Always (auto-loaded) | 15,000 chars total across ALL skills |
| **2. SKILL.md Body** | Constraint-driven SOP with `$ARGUMENTS` directive | When skill triggers | < 200 lines (500 max) |
| **3. References** | Deep docs, templates, schemas | On-demand per step | < 200–300 lines each |

### Required Frontmatter Fields

```yaml
---
name: skill-name
description: One-line summary (< 100 chars recommended)
allowed-tools: Comma-separated tool list
effort: low|medium|high
---
```

### Required Structure

```
skill-name/
├── SKILL.md              # Required — with YAML frontmatter + $ARGUMENTS directive
├── learnings.md          # Recommended — rules and observations from real sessions
├── references/           # Optional — deep docs, templates, examples
└── scripts/              # Optional — executable validation/discovery tools
```

### Rules
- SKILL.md must open with `You are helping with X: $ARGUMENTS` directive
- No README.md — SKILL.md is the single source of truth
- No "When to Activate" section — handled by frontmatter `description`
- Flat topic headers (not numbered steps)
- Empty optional directories must NOT exist
- Reference files should be self-contained and loadable independently
- `learnings.md` captures rules (hard constraints) and observations (soft learnings)
- Scripts should be validation/discovery tools, not core logic
- Deprecated scripts get a `# DEPRECATED` header explaining the replacement

---

## Compliance Matrix

### mobileconfig-profile

| Criterion | Status | Detail |
|-----------|--------|--------|
| Frontmatter fields | ✅ | name, description, allowed-tools, effort |
| $ARGUMENTS directive | ✅ | `You are helping with Apple configuration profiles (.mobileconfig): $ARGUMENTS` |
| SKILL.md line count | ✅ | 155 lines (< 200) |
| Flat topic headers | ✅ | Core Rules, Contour CLI, Local References, etc. |
| Reference files < 300 lines | ⚠️ | apple-schema-com.apple.TCC = ~330 lines (acceptable for schema) |
| learnings.md present | ✅ | 67 lines, 7 issues documented |
| Failure Patterns table | ✅ | 9 patterns |
| Standard Verification | ✅ | contour → plutil → manual checklist |
| References footer with URLs | ✅ | Apple device-management, ProfileManifests, Fleet docs |
| scripts/ | ⚠️ | 1 script (validate-profile.sh) — DEPRECATED, use `contour profile validate` |
| No README.md | ✅ | Removed |

### ddm-declaration

| Criterion | Status | Detail |
|-----------|--------|--------|
| Frontmatter fields | ✅ | name, description, allowed-tools, effort |
| $ARGUMENTS directive | ✅ | `You are helping with Apple DDM declaration profiles (.json): $ARGUMENTS` |
| SKILL.md line count | ✅ | 161 lines (< 200) |
| Flat topic headers | ✅ | Core Rules, Contour CLI, Local References, etc. |
| Reference files < 300 lines | ✅ | All within limits |
| learnings.md present | ✅ | 52 lines, 4 rules + 1 observation |
| Failure Patterns table | ✅ | 10 patterns |
| Standard Verification | ✅ | contour → jq → manual checklist |
| References footer with URLs | ✅ | Apple DDM schemas, DDM Explorer, Fleet docs |
| scripts/ | ⚠️ | 1 script (validate-ddm-declaration.sh) — DEPRECATED, use `contour profile ddm validate` |
| No README.md | ✅ | Removed |

### windows-csp-profile

| Criterion | Status | Detail |
|-----------|--------|--------|
| Frontmatter fields | ✅ | name, description, allowed-tools, effort |
| $ARGUMENTS directive | ✅ | `You are helping with Windows MDM configuration profiles (SyncML XML): $ARGUMENTS` |
| SKILL.md line count | ✅ | 151 lines (< 200) |
| Flat topic headers | ✅ | Core Rules, Local References, etc. |
| Reference files < 300 lines | ✅ | All within limits |
| learnings.md present | ✅ | 69 lines, 6 rules + 2 observations |
| Failure Patterns table | ✅ | 10 patterns |
| Standard Verification | ✅ | xmllint → script → manual checklist |
| References footer with URLs | ✅ | Microsoft CSP docs (3 URLs), Fleet docs |
| scripts/ | ✅ | 1 script (validate-windows-profile.sh) — ACTIVE, no contour equivalent |
| No README.md | ✅ | Removed |

### fleet-gitops

| Criterion | Status | Detail |
|-----------|--------|--------|
| Frontmatter fields | ✅ | name, description, allowed-tools, effort |
| $ARGUMENTS directive | ✅ | `You are helping with Fleet GitOps configuration files: $ARGUMENTS` |
| SKILL.md line count | ✅ | 157 lines (< 200) |
| Flat topic headers | ✅ | Core Rules, Contour and fleetctl, Local References, etc. |
| Reference files < 300 lines | ✅ | yaml-schema.md = 284 lines (largest, within limit) |
| learnings.md present | ✅ | 176 lines, 21 rules + 5 observations (most extensive) |
| Failure Patterns table | ✅ | 11 patterns |
| Standard Verification | ✅ | fleetctl dry-run → contour → manual checklist |
| References footer with URLs | ✅ | Fleet docs, Fleet tables, Apple, Microsoft, Android |
| scripts/ | ⚠️ | 1 script (validate-gitops-yaml.sh) — DEPRECATED, use `fleetctl apply --dry-run` |
| Templates | ✅ | 9 templates in references/templates/ |
| No README.md | ✅ | Removed |

### fleet-api

| Criterion | Status | Detail |
|-----------|--------|--------|
| Frontmatter fields | ✅ | name, description, allowed-tools, effort |
| $ARGUMENTS directive | ✅ | `You are helping with Fleet REST API usage and automation: $ARGUMENTS` |
| SKILL.md line count | ✅ | 124 lines (< 200) |
| Flat topic headers | ✅ | Core Rules, fleetctl CLI, Local References, etc. |
| Reference files < 300 lines | ⚠️ | endpoint-index.md = 330 lines (lookup table, acceptable) |
| learnings.md present | ✅ | 74 lines, 6 rules + 3 observations |
| Failure Patterns table | ✅ | 7 patterns |
| Standard Verification | ✅ | Inline (dry-run, status codes, content-type) |
| References footer with URLs | ✅ | Fleet API docs, Fleet tables, Fleet GitOps docs |
| scripts/ | ✅ | 2 scripts — ACTIVE (update-endpoint-index.sh, validate-endpoints.sh) |
| No README.md | ✅ | Removed |

---

## Global Constraints

| Metric | Value | Limit | Status |
|--------|-------|-------|--------|
| Total skills | 5 | — | — |
| Combined frontmatter description chars | ~550 | 15,000 | ✅ |
| Largest SKILL.md | 161 lines (ddm-declaration) | 200 | ✅ |
| Largest reference file | 330 lines (endpoint-index.md) | 300 | ⚠️ |
| Total reference files | 29 | — | — |
| Total template files | 9 | — | — |
| Total scripts | 6 (3 deprecated, 3 active) | — | — |

---

## Inventory

### mobileconfig-profile (12 files)
- `SKILL.md` — 155 lines
- `learnings.md` — 67 lines
- `references/apple-schema-toplevel.yaml` — 105 lines
- `references/apple-schema-common-payload-keys.yaml` — 60 lines
- `references/apple-schema-com.apple.security.firewall.yaml` — 114 lines
- `references/apple-schema-com.apple.servicemanagement.yaml` — 65 lines
- `references/apple-schema-com.apple.system-extension-policy.yaml` — 245 lines
- `references/apple-schema-com.apple.systempreferences.yaml` — 141 lines
- `references/apple-schema-com.apple.TCC.configuration-profile-policy.yaml` — 330 lines
- `references/common-payload-types.md` — 128 lines
- `references/template.mobileconfig` — 78 lines
- `references/validation-checklist.md` — 59 lines
- `scripts/validate-profile.sh` — 78 lines (DEPRECATED)

### ddm-declaration (9 files)
- `SKILL.md` — 161 lines
- `learnings.md` — 52 lines
- `references/declaration-types.md` — 59 lines
- `references/passcode.settings.yaml` — 258 lines
- `references/softwareupdate.enforcement.specific.yaml` — 140 lines
- `references/softwareupdate.settings.yaml` — 380 lines
- `references/template.json` — 7 lines
- `references/validation-checklist.md` — 39 lines
- `scripts/validate-ddm-declaration.sh` — 91 lines (DEPRECATED)

### windows-csp-profile (9 files)
- `SKILL.md` — 151 lines
- `learnings.md` — 69 lines
- `references/common-csp-settings.md` — 40 lines
- `references/fleet-variables.md` — 45 lines
- `references/template-single.xml` — 15 lines
- `references/template-multi.xml` — 26 lines
- `references/template-atomic.xml` — 29 lines
- `references/validation-checklist.md` — 42 lines
- `scripts/validate-windows-profile.sh` — 103 lines (ACTIVE)

### fleet-gitops (18 files)
- `SKILL.md` — 157 lines
- `learnings.md` — 176 lines
- `references/yaml-schema.md` — 284 lines
- `references/scope-rules.md` — 85 lines
- `references/file-structure-template.md` — 242 lines
- `references/fleet-variables.md` — 91 lines
- `references/certificate-authorities.md` — 89 lines
- `references/templates/default.yml` — 34 lines
- `references/templates/fleet.yml` — 61 lines
- `references/templates/unassigned.yml` — 31 lines
- `references/templates/label.yml` — 26 lines
- `references/templates/policy.yml` — 25 lines
- `references/templates/report.yml` — 16 lines
- `references/templates/software-package.yml` — 32 lines
- `references/templates/agent-options.yml` — 22 lines
- `references/templates/ddm-declaration.json` — 8 lines
- `scripts/validate-gitops-yaml.sh` — 140 lines (DEPRECATED)

### fleet-api (5 files)
- `SKILL.md` — 124 lines
- `learnings.md` — 74 lines
- `references/endpoint-index.md` — 330 lines
- `scripts/update-endpoint-index.sh` — 92 lines (ACTIVE)
- `scripts/validate-endpoints.sh` — 67 lines (ACTIVE)

---

## Last Checked

**2026-04-08**

---

## Changelog

| Date | Change |
|------|--------|
| 2026-03-26 | Initial setup. Created 3 skills (fleet-api, fleet-gitops, mobileconfig-profile). |
| 2026-04-08 | Added ddm-declaration and windows-csp-profile skills. Restructured all SKILL.md files to Fleet canonical format (allowed-tools, effort, $ARGUMENTS directive, flat headers, Failure Patterns, References footer). Deprecated 3 scripts superseded by contour/fleetctl. Removed 5 README.md files (redundant). Removed .DS_Store junk. Cleaned stale user-level duplicates. Updated this checklist. |
