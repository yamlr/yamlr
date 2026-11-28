# Yamlr Native Acceleration

## Overview
Yamlr leverages a high-performance Rust engine (`yamlr-native`) to accelerate the most compute-intensive parts of the healing pipeline. This "Native-First" approach ensures that Yamlr can handle hyperscale Kubernetes environments (10,000+ resources) with sub-second latency.

## Accelerated Components

### 1. Lexical Sharding (`native_shard`)
- **What**: Converts raw YAML streams into a flat list of `NativeShard` objects.
- **Performance**: ~10x faster than pure-Python regex-based tokenization.
- **Why**: Standard parsers (PyYAML, ruamel) are slow for massive files. Native sharding allows us to pre-index the entire file in a single pass.

### 2. Dependency Graph (`build_graph_edges`)
- **What**: Builds the cross-resource relationship graph using Rust's `HashMap` and `Rayon` (for future parallelization).
- **Complexity**: Reduced from O(N²) in Python to O(N) for most common K8s relationship lookups.
- **Security**: The Rust engine enforces strict semantic rules for Service-to-Pod selector matching.

### 3. Forensic Hashing (`calculate_integrity_score`)
- **What**: Uses SHA-256 to compute a semantic DNA hash of resources.
- **Why**: Prevents "Silent Drift" by ensuring that only logical changes affect the integrity score, ignoring harmless formatting deltas.

## Build Pipeline
Yamlr's native components are built using `maturin` and distributed as platform-specific `.pyd` (Windows), `.so` (Linux), and `.dylib` (macOS) extensions.

### Standalone Binary
For CI/CD environments where Python overhead is undesirable, Yamlr provides a standalone `yamlr-native` binary that can be invoked directly:
```bash
yamlr-native scan ./manifests
```

## Security & Transparency
- **Zero-CGO**: We use pure Rust to avoid C-related memory safety issues.
- **Deterministic**: The Rust engine is strictly deterministic; same input always produces the same graph/shards.
- **Audit Ready**: All native code is contained in `src/yamlr_native` for easy security review.
