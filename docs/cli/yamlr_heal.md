# yamlr heal
**Autonomous Kubernetes Manifest Reconciler & Auto-Repair Engine**

The `yamlr heal` command safely auto-remediates Kubernetes manifests, repairing schema violations, selector mismatches, deprecated API versions, and broken references while strictly preserving original comments, key ordering, and formatting layout.

Safe by default: running `yamlr heal` without `--apply` runs in preview mode (`--dry-run`/`--diff`), ensuring zero unsolicited disk modifications.

## Usage

```bash
# Preview proposed repairs with unified color diff (safe preview default)
yamlr heal ./k8s --diff

# Apply all safe remediations in-place with atomic WAL snapshot
yamlr heal ./k8s --apply

# Synthesize missing referenced ConfigMaps/Secrets during healing
yamlr heal ./manifests --apply --generate-stubs

# Upgrade manifests to a target Kubernetes version
yamlr heal ./manifests --apply -k 1.30

# Output remediation summary count table
yamlr heal ./k8s --summary
```

## Options & Flags

### Positional Arguments
* `[PATH]`: Manifest file or directory to heal (defaults to `.`).

### Execution & Safety Controls
* `-a, --apply`: Atomically commit healed changes to disk and record a Write-Ahead Log (WAL) transaction entry.
* `-d, --dry-run`: Preview healed manifests without modifying files on disk. Exits with code `1` if changes are needed.
* `--diff`: Display a unified, colorized diff comparing original file content with proposed repairs.
* `--explain-gate`: Print detailed diagnostic explanations if a pre-write safety gate blocks an in-place write.
* `--summary`: Output a condensed remediation count summary instead of individual document diffs.
* `--exit-zero`: Always exit with code `0`, even when changes are pending in dry-run mode.

### Schema & Workspace
* `-k, --k8s-version <VERSION>`: Target Kubernetes OpenAPI release version (e.g. `1.28`, `1.30`, `1.36`). Visible alias: `--kube-version`. Defaults to `1.36`.
* `--workspace <DIR>`: Explicit workspace root directory for cross-resource identity indexing. Visible alias: `--workspace-dir`.

### Policy & Topology Synthesis
* `--generate-stubs`: Automatically synthesize placeholder definitions for missing referenced resources (such as missing `Secret` or `ConfigMap` objects). Visible alias: `--create-stubs`.
* `--ingest-opa <PATH>`: Ingest an external JSON policy constraint report file and synthesize matching auto-remediation rules.
* `--ingest-kyverno <PATH>`: Ingest a Kyverno admission policy report and synthesize matching auto-remediations.
* `--verify-kubectl`: Pipe candidate healed manifests through local `kubectl --dry-run=client` to provide secondary kernel validation before writing.

### Source Adapters
* `--helm`: Adapt and heal Helm chart manifests in-memory.
* `--kustomize`: Adapt and heal Kustomize overlays in-memory.
* `--reconcile-kustomize`: Perform cross-resource relational reconciliation across Kustomize overlays.

### Output & Telemetry
* `-o, --output <FORMAT>`: Output format (`text`, `json`, `sarif`). Defaults to `text`.
* `--otel`: Export OpenTelemetry Prometheus exposition metrics. Visible alias: `--export-metrics`.

## Pre-Write Safety Gates

Before committing any modification to disk under `--apply`, the native engine enforces 6 mandatory in-memory safety gates:
1. **YAML Syntax Gate**: Ensures healed output parses cleanly without errors.
2. **Non-Empty AST Gate**: Rejects empty shards, preventing file truncation.
3. **Comment Preservation Gate**: Verifies zero comment loss (`healed_comments >= orig_comments`).
4. **Data Immutability Gate**: ConfigMap and Secret payloads are 100% byte-for-byte immutable.
5. **Idempotency Gate**: Second in-memory pass must yield zero further mutations (`heal(heal(M)) == heal(M)`).
6. **Filesystem Concurrency Guard**: Aborts write if the file was modified on disk between read and commit.

## Examples

**Preview remediations with color diff:**
```bash
yamlr heal ./manifests --diff
```

**Apply remediations safely with stub generation:**
```bash
yamlr heal ./deploy --apply --generate-stubs
```

**Verify changes against local kubectl before committing:**
```bash
yamlr heal ./k8s --apply --verify-kubectl
```
