# yamlr audit
**Forensic Compliance, CIS Benchmark & Security Audit**

The `yamlr audit` command conducts deep forensic compliance audits on Kubernetes manifests. It audits workloads against the Center for Internet Security (CIS) Kubernetes benchmarks, an embedded deprecation database, and high-entropy secret leakage detectors.

Execution is strictly read-only and local: manifests are analyzed in memory without modifying files on disk.

## Usage

```bash
# Audit manifests in the current directory
yamlr audit .

# Audit a specific manifest file
yamlr audit ./deploy/production.yaml

# Output audit findings in JSON
yamlr audit ./manifests -o json

# Export SARIF for GitHub Security code scanning
yamlr audit ./k8s -o sarif
```

## Options & Flags

### Positional Arguments
* `[PATH]`: Manifest file or directory to audit (defaults to `.`).

### Output Formatting
* `-o, --output <FORMAT>`: Output format (`text`, `json`, `sarif`). Defaults to `text`.

## Audit Scope & Security Rules

The audit engine inspects:
1. **CIS Kubernetes Benchmarks**: Checks for privileged containers, missing security contexts, host namespace sharing (`hostPID`, `hostIPC`, `hostNetwork`), and root execution (`runAsNonRoot`).
2. **Kubernetes API Deprecations**: Detects retired or deprecated API groups across Kubernetes releases.
3. **Secret Leakage Detection**: Scans manifests for plain-text credentials, high-entropy API tokens, private keys, and hardcoded connection strings.

## Exit Codes

* `0` (`EXIT_SUCCESS`): Zero compliance findings or policy violations detected.
* `1` (`EXIT_VIOLATIONS`): One or more audit violations or security findings were identified.
* `2` (`EXIT_USAGE`): Invalid arguments or unsupported output format.
* `124` (`EXIT_SYSTEM_ERROR`): Target unreadable or I/O failure.

## Related Commands

* [`yamlr catalog`](yamlr_catalog.md) — Browse the built-in forensic security and deprecation rule catalog.
* [`yamlr scan`](yamlr_scan.md) — General schema and topological integrity validation.
* [`yamlr secure`](yamlr_secure.md) — Synthesize least-privilege network policies.
