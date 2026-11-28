# Yamlr Developer Guide (Agent & External Contributor Edition)

Welcome to the Yamlr core engine. This guide is designed to help engineers understand how to extend Yamlr's healing and auditing capabilities.

## 🏁 Core Mission
Yamlr is a **Deterministic K8s Healing Engine**. Every contribution must prioritize:
1. **Trust**: Use DNA guards and dry-run defaults.
2. **Persistence**: Preserving user comments and formatting is non-negotiable.
3. **Speed**: Analysis must be sub-second for single files.

---

## 🏗 Architecture Overview

Yamlr uses a **Tiered Execution** model:
- **Infrastructure (`core/managers/`)**: Handles I/O, persistence, and external state.
- **Transformation (`core/stages/`)**: Pure, testable logic. No filesystem side-effects.
- **Orchestration (`core/pipeline.py`)**: Chains stages into a deterministic sequence.

### The 10-Second Ingestability Rule
All modules must be < 500 lines. If a feature pushes a file over 800 lines, it **MUST** be refactored into smaller stages.

---

## 🧪 How to Add a New Rule

Rules live in `src/yamlr/core/analyzers/`. To add a new audit rule:

1. **Define the Model**: Add the rule metadata to `yamlr/models.py`.
2. **Implement the Logic**: Create a discrete function in an appropriate analyzer.
3. **Register in Pipeline**: Ensure your analyzer is called by the `StageAnalysis` in `core/stages/`.
4. **Test**: Add a test case in `tests/analyzers/` with a sample broken manifest.

## 🛠 How to Add a New Healer

Healers are the "Surgeons" of Yamlr. They live in `src/yamlr/core/healers/`.

1. **Deterministic Input**: Healers must use the `HealContext` and `AnalysisResult`.
2. **Non-Destructive Write**: Always use the `ruamel.yaml` API to preserve comments.
3. **DNA Guard**: Ensure that any structural change is reflected in the `dna_integrity` check.

---

## Safety & Security standards

### subprocess usage
**NEVER** use `shell=True` or raw string formatting for subprocess commands. Use `yamlr.core.safe_exec` wrappers.

### Path Masking
Always use `yamlr.core.telemetry.PathMasker` when logging paths to prevent data leakage in CI logs.

### DNA Integrity
If a healer modifies a resource, it must verify that the **Semantic DNA** of the resulting YAML still matches the intended intent (excluding formatting/comments).

---

## 📈 Performance Targets

| Operation | Target Latency |
|:--|:--|
| Single File Audit | < 250ms |
| Batch Scan (100 files) | < 2.0s |
| Global Resolve (Graph) | < 500ms |

---

## 🛠 Contributor Engineering Checklist

When developing or refactoring Yamlr core modules:
1. **Architectural Separation**: Keep parser transformation pure and separate from filesystem I/O.
2. **Comment Preservation**: Ensure all healing stages preserve human comments, blank lines, and formatting invariants.
3. **Targeted Changes**: Keep changes atomic and accompany every stage with dedicated unit test coverage.
4. **Validation Suite**: Run `pytest` and `cargo test --manifest-path native_core/Cargo.toml` to verify engine stability.
