# 🛠 Yamlr CLI Command Manifest

Yamlr is the **Autonomous Manifest Control Plane** for Kubernetes. This document provides a comprehensive index of all commands, subcommands, flags, and their licensing context.

---

## 📊 Feature Tiering (Free vs Pro)

| Command / Capability | Free Desktop | Yamlr Pro | Description |
| :--- | :---: | :---: | :--- |
| **`scan` / `audit` / `check`** | ✅ | ✅ | Deep safety audit & SARIF reporting. |
| **`heal` (Basic)** | ✅ | ✅ | Semantic indention, deprecation fixes, schema repair. |
| **`heal --fix-refs`** | — | ✅ | **Cross-Resource Fixes**: corrective surgery across files. |
| **`secure` / `--harden`** | — | ✅ | **Security Hardening**: Auto-remediation of pods/network. |
| **`dna` / `receipt`** | — | ✅ | **PRO: Semantic DNA**: SHA-256 intent preservation receipts. |
| **`mcp`** | — | ✅ | **PRO: Agentic Safety**: MCP Server for AI IDE/Agent integration. |
| **`evidence`** | — | ✅ | **Auditor-Ready Reports**: PDF/JSON compliance bundles. |
| **`baseline`** | ✅ | ✅ | **GitOps Guard**: Snapshot violations to ignore legacy debt. |
| **`auth`** | — | ✅ | **Enterprise Auth**: SSO/JWT login for team features. |

---

## 🏗 Core Operation Commands

### 🔍 `yamlr scan` / `audit`
**Purpose**: Perform a deep safety audit without modifying files.
**Syntax**: `yamlr scan [PATH] [FLAGS]`
**Examples**:
- `yamlr scan .` (Scan current directory)
- `yamlr scan manifests/ --output sarif` (Generate CI-ready report)
- `yamlr audit --bench` (Run scientific benchmark against labeled corpus)

### 🏥 `yamlr diagnose`
**Purpose**: Run a deep-audit scan with full debug logs.
**Example**: `yamlr diagnose . --output json`

---

### 🚦 `yamlr check`
**Purpose**: Fast syntax and schema validation gate (Perfect for PRs).
**Example**: `yamlr check .`

---

### 🔧 `yamlr heal`
**Purpose**: Propose and apply surgical repairs to manifests.
**Syntax**: `yamlr heal [PATH] [FLAGS]`
**Examples**:
- `yamlr heal .` (Interactive repair with diff preview)
- `yamlr heal . -y` (Auto-confirm all safe repairs)
- `yamlr heal . --fix-refs` (💎 **PRO**: Correct relational errors between Services and Pods)
- `yamlr heal . --dry-run` (Show what *would* change without writing)

---

### `yamlr secure`
**Purpose**: **PRO**. Automatically suggest and apply security hardening (runAsNonRoot, privileged: false, etc.).
**Syntax**: `yamlr secure [PATH] [FLAGS]`
**Example**:
- `yamlr secure . --diff` (Preview hardening suggestions)

---

### `yamlr upgrade` / `migrate`
**Purpose**: Migrate deprecated Kubernetes APIs to the latest supported versions.
**Syntax**: `yamlr upgrade --to <VERSION>`
**Example**:
- `yamlr upgrade --to 1.31` (Rewrites Networking v1beta1 to v1, etc.)

---

### 🧊 `yamlr dna`
**Purpose**: **PRO**. Calculate or verify the mathematical "Semantic DNA" (SHA-256) of a manifest. Use for compliance receipts.
**Syntax**: `yamlr dna [PATH] [--hash <EXPECTED>]`
**Example**:
- `yamlr dna deploy.yaml` (Generate DNA signature)

---

## 🔌 Integration & IDE Tooling

### 🛠 `yamlr mcp`
**Purpose**: **PRO**. Start the Model Context Protocol (MCP) server for integration with IDE and editor environments (such as VS Code, Neovim, JetBrains).
**Syntax**: `yamlr mcp`
**Feature**: Exposes `scan_manifest`, `heal_manifest`, and `why` tools to connected development environments.

---

### 🗃 `yamlr baseline`
**Purpose**: snapshot existing violations into a baseline file to prevent "inherited noise" in CI/CD.
**Syntax**: `yamlr baseline`
**Example**:
- `yamlr scan . --fail-on error` (Will now ignore baselined issues)

---

## 📊 Intelligence & ROI

### 📈 `yamlr stats` / `roi`
**Purpose**: Display surgical ROI, time saved, and cumulative healing metrics.
**Variants**:
- `stats`: Focuses on surgical efficiency and engineering mastery.
- `roi`: **PRO**. Focuses on executive wealth reclamation and budget justification.
**Syntax**: `yamlr stats` | `yamlr roi`

---

### 📋 `yamlr evidence`
**Purpose**: **PRO**. Compile mathematical DNA receipts into Auditor-Ready Compliance PDF/JSON reports.
**Syntax**: `yamlr evidence [DIR] [FLAGS]`
**Example**:
- `yamlr evidence ./receipts --format pdf --output audit_report.pdf`

---

---

### 📚 `yamlr catalog` / `rules`
**Purpose**: Browse and manage the rule catalog.
**Syntax**: `yamlr catalog [update|list|status]`
**Example**: `yamlr rules --verbose` (Show rationale for all rules)

---

### ❓ `yamlr explain`
**Purpose**: Get a deep-dive explanation for a specific Rule ID.
**Syntax**: `yamlr explain <RULE_ID>`
**Example**: `yamlr explain rules/no-latest-tag`

---

### 🎛 `yamlr status`
**Purpose**: SRE Dashboard view of repository health and K8s version compatibility.
**Syntax**: `yamlr status`

---

## 📗 User Experience & Onboarding

### 👋 `yamlr welcome`
**Purpose**: Start a guided visual tour and feature dashboard for new users.

---

### ⌨ `yamlr completion`
**Purpose**: Install shell autocompletion for Yamlr.
**Syntax**: `yamlr completion [bash|zsh|fish|powershell]`

---

### 📖 `yamlr manual`
**Purpose**: Comprehensive terminal-based User Guide.
**Syntax**: `yamlr manual [TOPIC]`

---

### 🎮 `yamlr demo`
**Purpose**: Spawns a "Broken Playground" to test healing scenarios risk-free.

---

## 🔑 Utility & Infrastructure

### 🆔 `yamlr auth`
**Purpose**: **PRO**. Login to Yamlr Enterprise.
**Syntax**: `yamlr auth [login|logout|status]`

---

### 🛠 `yamlr init`
**Purpose**: Scaffolds a `.yamlr.yaml` configuration for the current workspace.

---

### `yamlr rollback`
**Purpose**: Revert an entire atomic multi-file healing session. 
**Syntax**: `yamlr rollback [SESSION_ID]`

---

### `yamlr rollback`
**Purpose**: Revert an entire atomic multi-file healing session. 
**Syntax**: `yamlr rollback [SESSION_ID]`

---

### ♻ `yamlr restore`
**Purpose**: Restore a file from the automated backups managed by Yamlr.
**Syntax**: `yamlr restore [PATH]`

---

### Expert Diagnostic Assets (PII-Redacted Forensics)
- `--expert`: Unlock advanced UI details, deep forensic insights, and surgical breakdown.
- `--forensic-debug`: [EXPERT] Enable PII-redacted forensic logging (tree_dna.log, pe_debug.log).
- `--debug-stages`: Display detailed execution timing and state for every pipeline execution stage.
- `--session-id ID`: Target a specific healing session for audit or rollback.
- `--timing`: **PERFORMANCE**: Output a surgical breakdown of environmental bootstrap vs. execution time.
- `--timing-file FILE`: [PERFORMANCE] Save performance profiling data to a JSON file.


- `--kube-version`: Target a specific K8s minor version (e.g. 1.31).
- `--all`: Show all hidden and Meta commands in help output.
- `--fail-on [error|warning|any]`: CI/CD Gate: Exit 1 for files containing issues of this level.
- `--risk-threshold [high|medium|low]`: CI/CD Gate: Exit 1 based on minimum issue impact level.
- `--quiet`: Minimal output for CI/CD pipelines (Silent by default).
- `--clinical`: Force silent stdout; all interactive UI elements move to stderr.
- `--plain`: ASCII-only output (Disable colors and emoji).
- `--verbose`: Show full internal engine logic audit logs and stage transitions.
- `--no-backup`: Skip safety backups (⚠ Dangerous).
- `--diff` / `--dry-run`: Unified diff preview of proposed changes.
- `--compact`: Minify output for high-density environments.
- `--max-depth N`: Limit directory recursion depth (default: 10).
- `--ext`. EXT: Comma-separated list of extensions to process (default: .yaml,.yml).
- `--stream-to FILE`: **ULTRA-SCALE**: Stream results to NDJSON for constant-memory processing (100k+ files).
- `--concurrency N`: Number of parallel workers for rapid scanning.
- `--engine [python|native|rust]`: Select an engine tier where supported. Processing speed depends on workload, cache state, and platform; no fixed throughput is guaranteed.
- `--identity-mode [infer|strict]`: Set identity detection style.
- `version`: Display version, build, and platform architecture information.

