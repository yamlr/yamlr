# 📖 Yamlr Command-Line Interface (CLI) Reference Manual

**Binary:** `yamlr` (Native Rust Core)  
**Version:** v0.1.4  
**Speed Profile:** Hook (< 2s), CI (< 15s/1000 files), IDE (< 50ms)

---

## 📌 Global Synopsis

```bash
yamlr [SUBCOMMAND] [OPTIONS] [PATH]
```

### Core Subcommands Overview

| Subcommand | Primary Purpose | Default Behavior |
| :--- | :--- | :--- |
| `heal` | Autonomous manifest auto-repair | Dry-run preview (`--diff`); requires `--apply` to write |
| `scan` | Read-only static analysis & policy audit | Emits structured findings to stdout |
| `check` | Ultra-fast syntax and schema linting | Network-disabled CI gate |
| `migrate` | Targeted Kubernetes API modernization | Upgrades deprecated API groups (e.g., RBAC, Ingress) |
| `diagnose` | Forensic debug wrapper & trace export | Verbose diagnostic bundle generation |
| `catalog` | Browse embedded rule taxonomy | Displays rule definitions, severity, and gates |
| `explain` | Detailed rationale for specific rule | Prints why, k8s constraints, and safe remediation |
| `init` | Scaffold local repository configuration | Generates `.yamlr.yaml` baseline |

---

## 🛠️ Subcommand Details

### 1. `yamlr heal`
Autonomous manifest repair engine. Employs byte-span AST surgery to fix syntax, deprecations, and schema errors while preserving comments and formatting.

```bash
yamlr heal [OPTIONS] [PATH]
```

#### Key Options:
- `-a, --apply`: In-place mutation. Writes healed manifests directly to disk. (Creates `.yamlr.bak` rollback file unless `--no-backup` is passed).
- `--diff`: Unified colored diff preview of proposed remediations without modifying files.
- `--workspace <DIR>`: Explicit workspace root for multi-resource graph indexing (ConfigMaps, Services, Ingresses, PVCs).
- `--explain-gate`: Emits forensic pre-write schema gate evaluation details.
- `-o, --output <FORMAT>`: Output format: `text` (default), `json`, or `sarif` (GitHub Code Scanning).
- `-k, --k8s-version <VER>`: Target Kubernetes version (default: embedded schema version, e.g. `1.31`).
- `--helm`: Enables Go template masking for unrendered Helm charts (`{{ ... }}`).
- `--kustomize`: Reconciles Kustomize overlays and strategic merge patches.
- `--exit-zero`: Forces exit code 0 even if remediations were applied (useful for permissive pipelines).

#### Examples:
```bash
# Preview changes on a single manifest
yamlr heal --diff manifests/deployment.yaml

# Apply fixes in-place across an entire repository with cross-resource graph indexing
yamlr heal --apply --workspace . manifests/

# Generate SARIF report for GitHub Code Scanning
yamlr heal --output sarif manifests/ > report.sarif
```

---

### 2. `yamlr scan`
High-performance read-only static analysis and cross-resource policy auditing.

```bash
yamlr scan [OPTIONS] [PATH]
```

#### Key Options:
- `--workspace <DIR>`: Aggregates identities across all files to detect orphan resources and broken bindings.
- `-o, --output <FORMAT>`: Format options: `text`, `json`, `sarif`.
- `--fail-on <SEVERITY>`: Exit with code 1 if issues $\ge$ specified severity (`low`, `medium`, `high`, `critical`).
- Stdin input: Read stream directly via `cat manifest.yaml | yamlr scan -`.

---

### 3. `yamlr migrate`
Targeted Kubernetes API modernization engine.

```bash
yamlr migrate [OPTIONS] [PATH]
```

#### Key Options:
- `--to <VERSION>`: Target Kubernetes version (e.g. `1.28`, `1.30`).
- `--apply`: Mutates files to modernized API schemas.
- `--dry-run`: Emits migration summary without writing to disk.

---

### 4. `yamlr check`
Ultra-fast offline validator optimized for pre-commit git hooks.

```bash
yamlr check [FILES...]
```
- Sub-50ms execution.
- Validates RFC 1123 naming, YAML grammar, and structural integrity.

---

### 5. `yamlr catalog` & `yamlr explain`
Inspect the embedded rule dictionary and understand healing mechanics.

```bash
# List all registered rules and their active status
yamlr catalog

# Deep dive into a specific rule
yamlr explain TOPO-001
yamlr explain NET-020
```

---

## 🚦 Standard Process Exit Codes

| Code | State | Meaning |
| :---: | :--- | :--- |
| `0` | Clean | Success. No syntax, schema, or safety violations. |
| `1` | Findings | Scan detected policy violations or heal proposed modifications. |
| `2` | Warning | Advisory issues found (non-blocking). |
| `4` | Fatal Schema Regress | Healed output failed pre-write schema gate ($V_1 \setminus V_0$). Aborted fail-closed. |
| `127` | Usage Error | Invalid CLI flag or missing file argument. |

---

## ⚙️ Configuration File (`.yamlr.yaml`)

Place `.yamlr.yaml` at repository root:

```yaml
version: 1
kubernetes_version: "1.31"
schema_gate: enforce # enforce | shadow | off
rules:
  TOPO-001: true
  SEC-011: true
  ECO-001: true
  ING-002: true
  NET-020: true
  REF-006: true
exclude:
  - "**/tests/**"
  - "**/vendor/**"
```
