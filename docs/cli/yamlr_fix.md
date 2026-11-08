# yamlr fix
**Instant Zero-Configuration Auto-Repair**

The `fix` command is the zero-configuration auto-repair pathway for Kubernetes manifests, applying safe, non-destructive schema upgrades, deprecation migrations, and syntax fixes without requiring complex flags.

## Usage
```bash
yamlr fix [PATH]... [FLAGS]
```

## Description
Equivalent to running `yamlr heal --apply` with conservative, deterministic defaults:
*   **Deprecation Upgrades**: Automatically transitions deprecated API groups to current stable versions (e.g. `extensions/v1beta1` -> `apps/v1`, `policy/v1beta1` -> `policy/v1`).
*   **Floating Tag Pinning**: Detects dangerous `:latest` floating container tags and converts them to pinned references.
*   **Zero-Comment Loss**: AST token-level rewrites ensure developer comments, Helm template blocks, and annotations remain 100% intact.
*   **Atomic Invariant Rollback**: Verifies the mutated document before writing to disk; rolls back immediately if any syntax invariant is violated.

## Flags
*   `-k, --k8s-version <VERSION>`: Target Kubernetes version (default: `1.30`).
*   `--diff`: Display colorized inline word diff before applying mutations.
*   `-h, --help`: Display help information for `fix`.

## Examples
```bash
# Instantly heal all manifests in the current directory in-place
yamlr fix .

# Fix a specific deployment manifest
yamlr fix ./k8s/deployment.yaml
```
