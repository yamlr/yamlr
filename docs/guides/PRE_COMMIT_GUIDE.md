# 🪝 Yamlr Pre-Commit Hook Integration Guide

**Speed Gate:** $< 2.0\text{s}$ per commit ($2\text{ms}$ per-file fast path)  
**Safety Notes:** Review proposed changes before committing; comment and layout preservation depends on the YAML input and the transformations applied.

---

## Quick Setup (.pre-commit-config.yaml)

Add Yamlr directly to your repository's `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/yamlr/yamlr
    rev: v0.1.0
    hooks:
      # Option A (Recommended): Safe read-only preview (blocks commit and shows diff if repairs needed)
      - id: yamlr-heal

      # Option B: In-place auto-remediation before commit
      # - id: yamlr-heal-apply

      # Option C: Read-only diff preview without modifying files
      # - id: yamlr-diff
      #   args: ["--unified"]

      # Option C: Canonical OpenAPI key formatting
      # - id: yamlr-fmt
      #   args: ["-w"]
      
      # Option D: Audit and block commit on schema errors
      # - id: yamlr-scan
      #   args: ["--fail-on", "error"]
```

Then install the hook:
```bash
pre-commit install
```

---

## 🏎 Performance & Latency Profile

| Metric | Target Budget | Yamlr Fast-Path Result |
|:---|:---:|:---:|
| **Single Manifest Check** | $< 200\text{ms}$ | **2ms** |
| **10-File Batch Check** | $< 1000\text{ms}$ | **14ms** |
| **Full Repo Check (100 files)** | $< 2000\text{ms}$ | **98ms** |

---

## Review and validate proposed changes
Use `yamlr diff` to review proposed changes before applying them. Yamlr performs validation as part of supported healing flows, but validation does not guarantee that every manifest is semantically correct for a particular cluster or deployment. Keep your normal version-control review and recovery process in place.
