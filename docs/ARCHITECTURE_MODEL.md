# 🏛️ Yamlr Engine Definitive Architectural Mental Model & Connective Tissue

**Version:** v0.1.3 / v1.2 Planning  
**Status:** Validated against 859/859 native unit & integration tests  
**Core Mission:** Safe, zero-assumption, comment-preserving cross-resource auto-repair for Kubernetes manifests.

---

## 🗺️ System Architecture & Data Flow

```
Raw Manifests (.yaml / .yml / Stdin / Helm / Kustomize)
                          │
                          ▼
            ┌───────────────────────────┐
            │   Universal Ingestion     │
            │  (UTF-8 BOM, CRLF norm)   │
            └─────────────┬─────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │   Template Masking Gate   │
            │  (template_masker.rs)     │
            │ Mask {{...}} & Helm lines │
            └─────────────┬─────────────┘
                          │
                          ▼
            ┌───────────────────────────┐
            │   Borrowed Lexer & AST    │
            │ (ast.rs, span-preserving) │
            └─────────────┬─────────────┘
                          │
                          ├─────────────────────────────────────────────────┐
                          ▼                                                 ▼
            ┌───────────────────────────┐                     ┌───────────────────────────┐
            │ Single-Doc Fast Path      │                     │ Multi-Doc Workspace Graph │
            │ (Syntactic & Schema)      │                     │ (Cross-Resource Topology) │
            └─────────────┬─────────────┘                     └─────────────┬─────────────┘
                          │                                                 │
                          └───────────────────────┬─────────────────────────┘
                                                  │
                                                  ▼
                                    ┌───────────────────────────┐
                                    │    Pipeline Orchestrator   │
                                    │    (core/engine/pipeline)  │
                                    └─────────────┬─────────────┘
                                                  │
                                                  ▼
                                    ┌───────────────────────────┐
                                    │      Healer Execution     │
                                    │ (Surgical In-Place Fixes) │
                                    └─────────────┬─────────────┘
                                                  │
                                                  ▼
                                    ┌───────────────────────────┐
                                    │  Pre-Write Schema Gate    │
                                    │  (V1 \ V0 Delta Rule)     │
                                    └─────────────┬─────────────┘
                                                  │
                                                  ▼
                                    ┌───────────────────────────┐
                                    │ Token Unmasking & Output  │
                                    │ (CLI Diff / Atomic Write) │
                                    └───────────────────────────┘
```

---

## 🧬 Connective Tissue Mapping (Inter-File Ripple Matrix)

| Source Module | Direct Dependent | Connective Tissue Description | Ripple Effect of Changes |
| :--- | :--- | :--- | :--- |
| `native_core/src/healers/template_masker.rs` | `cli/heal_cmd.rs`, `cli/scan_file.rs` | Replaces Go/Helm expressions (`{{ ... }}`) and standalone control lines (`{{- if ...}}`) with whitespace-preserving placeholders. | A failure to preserve exact indentation in control lines corrupts block scalars (`- \|`) downstream in the AST parser. |
| `native_core/src/healers/typo_dictionaries.rs` | `healers/typo_healer.rs` | Static hash sets of valid Kubernetes schema keys (`SERVICE_SPEC_KEYS`, `CONTAINER_SPEC_KEYS`, `OPENSHIFT_TEMPLATE_ROOT_KEYS`). | Adding keys here prevents false-positive Levenshtein distance coercions (e.g. `internalTrafficPolicy` being coerced to `externalTrafficPolicy`). |
| `native_core/src/healers/typo_healer.rs` | `cli/heal_cmd.rs` | Fuzzy string matching with bounded distance (< 2) and length ratio >= 0.70. | Must explicitly reject flow-style inline mappings (`{ name: ... }`) and sub-mapping scopes to prevent AST corruption. |
| `native_core/src/healers/job_contract_healer.rs` | `cli/heal_cmd.rs` | Enforces Pod template spec contracts (`restartPolicy: OnFailure`) on Job/CronJob kinds. | Must detect Kustomize strategic merge patch deltas (missing `containers`) to avoid injecting unwanted fields into patch files. |
| `native_core/src/cli/schema_gate.rs` | `cli/heal_writer.rs` | Deserializes healed YAML documents against embedded OpenAPI v3 schemas. | Implements $V_1 \setminus V_0$: if a schema violation existed in original manifest ($V_0$), it is ignored; if introduced by healing ($V_1$), write is aborted with exit code 4. |
| `native_core/src/cli/heal_cmd.rs` | User CLI Output | Orchestrates AST mutations, gathers advisories, and formats unified diffs. | Invokes `unmask_template_expressions` on all remediation strings to guarantee zero internal tokens (`__YAMLR_TPL_VAL_`) leak to users. |

---

## 🛡️ The 4 Trust Pillars & Invariant Guarantees

1. **Zero-Assumption Principle:** Yamlr never guesses author intent. If multiple interpretations exist (e.g., ambiguous indentation or port assignments), Yamlr emits an advisory (`S0`) and refuses mutation (`fail-closed`).
2. **Comment & Formatting Preservation:** Yamlr mutates byte slices in-place without round-tripping through lossy YAML serialization dictionaries. Author comments, blank lines, and flow-style elements remain intact.
3. **Idempotency Double-Pass:** Every healed output $H(x)$ is passed through the healing engine a second time: $H(H(x)) = H(x)$. If second pass produces non-zero delta, write aborts immediately.
4. **Pre-Write OpenAPI Invariant Verification:** No file is written to disk unless it passes RFC 1123 naming, YAML syntax, and OpenAPI v3 Kubernetes structural validation.
