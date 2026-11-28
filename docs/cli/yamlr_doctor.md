# yamlr doctor

**Environment Health & Diagnostics**

The `doctor` command runs a suite of diagnostic checks to ensure the Yamlr Engine, native PyO3 core, cluster toolchain (`kubectl`), and local Kubernetes schema caches are healthy and functioning correctly.

## Usage
```bash
yamlr doctor [OPTIONS]
```

## Argument Groups

### Diagnostic Options
*   `--fix`: Automatically repair local environment drift (e.g., initialize local schema cache).

### Targeting & Environment
*   `--k8s-version <VERSION>`: Target Kubernetes schema version to diagnose (e.g., `1.30`, `1.31`).
*   `--crd <PATH>`: Path to CustomResourceDefinition manifests to validate against the engine parser.

## Verification Checklist
*   **Native Core**: Linkage status and AVX2/NEON SIMD vector optimization.
*   **Cluster CLI**: Verification of `kubectl` binary presence in system `PATH`.
*   **Schema Cache**: Integrity and presence of offline schema definitions in `~/.yamlr/schemas`.
*   **Environment & Runtime**: Host operating system, architecture, and Python runtime version.

## Examples
```bash
# Run diagnostics
yamlr doctor

# Automatically provision missing local schema cache
yamlr doctor --fix
```
