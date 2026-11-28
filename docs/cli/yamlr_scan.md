# yamlr scan
**Manifest Audit & Schema Validation Gate**

The `yamlr scan` command audits Kubernetes manifests, Helm templates, Kustomize overlays, and directory trees for schema violations, deprecated APIs, security misconfigurations, and cross-resource topological integrity faults.

Execution is **100% local and read-only**: `yamlr scan` never modifies files on disk.

## Usage

```bash
# Audit manifests in the current directory
yamlr scan .

# Audit a specific manifest or subdirectory
yamlr scan ./manifests/deployment.yaml

# Validate against specific Kubernetes release schema
yamlr scan ./k8s --k8s-version 1.30

# CI/CD Quality Gate: fail on errors
yamlr scan ./deploy --fail-on error

# Output SARIF directly for GitHub Code Scanning
yamlr scan ./manifests --sarif -f results.sarif
```

## Options & Flags

### Positional Arguments
* `[PATH]`: Manifest file or directory to scan (defaults to `.`).

### Schema & Versions
* `-k, --k8s-version <VERSION>`: Target Kubernetes OpenAPI schema version (e.g. `1.28`, `1.30`, `1.36`). Visible alias: `--kube-version`. Defaults to `1.36`.
* `--crd <PATH>`: Path to custom CRD definitions file or directory to extend schema validation.

### Output Formatting
* `-o, --output <FORMAT>`: Output format (`text`, `json`, `sarif`). Defaults to `text`.
* `-f, --output-file <PATH>`: Write output directly to specified file path instead of stdout.
* `-j, --json`: Shorthand for `--output json`.
* `--sarif`: Shorthand for `--output sarif` (OASIS SARIF v2.1.0 standard for GitHub Security code scanning).
* `-q, --quiet`: Minimal output mode; suppresses banners and informational progress.

### CI/CD Quality Gates & Monitoring
* `--fail-on <SEVERITY>`: Minimum violation severity that triggers non-zero exit code (`1`). Allowed values: `error` (or `high`), `warning` (or `medium`), `note` (or `low`, `info`, `any`), or `none`. Defaults to `error`.
* `--exit-zero`: Force exit code `0` even when policy violations are detected (useful for non-blocking advisory runs in CI).
* `-w, --watch`: Continuous filesystem watcher mode; automatically triggers instant scans whenever files change on disk.
* `--workspace <DIR>`: Explicit workspace root directory for cross-resource identity indexing. Visible alias: `--workspace-dir`.

### Ingestion Adapters
* `--helm`: Render Helm charts into flat manifests in-memory before scanning.
* `--kustomize`: Execute Kustomize overlays in-memory before scanning.
* `--oci-layer <PATH>`: Scan Kubernetes manifests extracted from an OCI container layer tarball.

### Telemetry & Observability
* `--otel`: Export OpenTelemetry Prometheus exposition metrics. Visible alias: `--export-metrics`.
* `--push-telemetry`: Explicitly send an Enterprise scan-completion event.
* `--no-telemetry`: Disable all telemetry collection (air-gapped compliance). Visible alias: `--disable-telemetry`.

## Exit Codes

* `0` (`EXIT_SUCCESS`): Manifests conform to schema and policy rules, or `--exit-zero` was passed.
* `1` (`EXIT_VIOLATIONS`): Violations found meeting or exceeding the `--fail-on` threshold.
* `2` (`EXIT_USAGE`): Invalid arguments or unknown option passed.
* `4` (`EXIT_SYNTAX_ERROR`): Malformed YAML syntax or non-existent target path.
* `124` (`EXIT_SYSTEM_ERROR`): I/O or filesystem error.

## Examples

**Run in GitHub Actions with SARIF upload:**
```bash
yamlr scan ./manifests --sarif -f results.sarif
```

**Validate Helm chart templates in-memory:**
```bash
yamlr scan ./charts/my-app --helm --fail-on warning
```

**Continuous live validation while editing:**
```bash
yamlr scan ./manifests --watch
```
