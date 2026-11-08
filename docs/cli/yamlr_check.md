# yamlr check
**Strict Read-Only Manifest Validation Gate**

The `yamlr check` command is a strict, read-only validation gate engineered for CI/CD pipelines and pre-commit hooks. It guarantees zero filesystem mutations and produces deterministic process exit codes: `0` for clean manifests, `1` for schema or policy violations meeting the threshold, and `2` for malformed arguments or syntax errors.

## Usage

```bash
# Check current directory with default strict gate
yamlr check .

# Check a single file
yamlr check ./k8s/deployment.yaml

# Fail on warnings as well as errors
yamlr check ./manifests --fail-on warning

# Run quietly in CI pipelines
yamlr check ./k8s -q --fail-on error
```

## Options & Flags

### Positional Arguments
* `[PATH]`: Manifest file or directory to check (defaults to `.`).

### Schema & Severity Gates
* `-k, --k8s-version <VERSION>`: Target Kubernetes OpenAPI schema version (e.g. `1.28`, `1.30`, `1.36`). Visible alias: `--kube-version`. Defaults to `1.36`.
* `--fail-on <SEVERITY>`: Minimum violation severity that triggers a failure exit code (`1`). Allowed values: `error` (or `high`), `warning` (or `medium`), `note` (or `low`, `info`, `any`), or `none`. Defaults to `error`.
* `-q, --quiet`: Suppress informational headers, ASCII banners, and progress metrics. Emits only errors.

## Exit Codes

* `0` (`EXIT_SUCCESS`): All manifests strictly conform to Kubernetes OpenAPI schemas and safety rules.
* `1` (`EXIT_VIOLATIONS`): Manifest violations detected meeting or exceeding the `--fail-on` threshold.
* `2` (`EXIT_USAGE`): Unsupported `--fail-on` value or invalid Kubernetes version.
* `4` (`EXIT_SYNTAX_ERROR`): Specified file or directory does not exist.
* `124` (`EXIT_SYSTEM_ERROR`): Schema bundle validation or manifest processing error.

## Examples

**Use in Git Pre-Commit Hook:**
```bash
yamlr check . --fail-on error --quiet
```

**Verify upcoming Kubernetes 1.32 compatibility in CI:**
```bash
yamlr check ./k8s -k 1.32 --fail-on warning
```
