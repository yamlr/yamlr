# yamlr diagnose
**Validate Native Engine Integrity & Environment Health**

The `yamlr diagnose` command (canonical alias for `yamlr doctor`) validates native engine integrity, embedded schema availability, license tier state, and local workspace health.

It performs self-tests on the borrowed document slice streaming parser, verifies OpenAPI v3 schema caches, and ensures the runtime environment is properly configured.

## Usage

```bash
# Standard engine diagnostics
yamlr diagnose

# Verbose system check
yamlr diagnose --verbose
```

## Options & Flags

* `-v, --verbose`: Show detailed health check output, schema counts, and engine subsystem statuses.
* `-h, --help`: Display help information.

## Diagnostics Performed

1. **Native Engine Integrity**: Verifies the compiled standalone binary status, CST/AST models, and memory limits.
2. **Schema Cache Health**: Checks embedded Kubernetes OpenAPI v3 schemas (v1.21 through v1.37+) and local CRD caches.
3. **Licensing & Entitlements**: Validates license public keys, air-gapped activation status, and active tier capabilities.
4. **Environment Check**: Verifies read/write permissions for temporary directories and Write-Ahead Log (WAL) journal paths.

## Exit Codes

* `0` (`EXIT_SUCCESS`): All diagnostic checks passed; engine is healthy.
* `1` (`EXIT_VIOLATIONS`): One or more diagnostic self-tests failed or an issue was detected.

## Related Commands

* [`yamlr doctor`](yamlr_doctor.md) — Canonical doctor command.
* [`yamlr status`](yamlr_status.md) — Inspect workspace and license status.
