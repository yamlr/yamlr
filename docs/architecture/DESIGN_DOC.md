# Design Doc: Yamlr v1.0 “The Autonomous Manifest Control Plane”

**Author:** Nishar A Sunkesala
**Status:** In Review
**Last Updated:** 2026-02-10

---

## 1. Context & Problem Statement
DevOps teams are drowning in "YAML Hell"—manually fixing malformed Kubernetes manifests and resolving cross-resource mismatches. Existing tools (linters, OPA) **detect** but do not **heal**. Yamlr provides a "Zero-Failure" auto-healing engine that preserves developer intent (comments) and ensures production-ready manifests.

## 2. Goals & Non-Goals
### 2.1 Goals
*   **Safe Auto-Repair:** Automatically fix 70%+ of common K8s schema/semantic errors.
*   **Zero-Data Loss:** 100% preservation of comments and formatting via Round-Trip Lexer.
*   **Determinism:** Identical input + version ⇒ Identical output.

### 2.2 Success Metrics
*   **Adoption:** 50+ repos with Yamlr in CI/CD by Month 6.
*   **Reliability:** <0.1% of runs fail due to internal bugs; zero documented data-loss incidents in Month 1-6.
*   **Performance:** <2s latency for pre-commit verification on delta change.

## 3. Proposed Architecture
Yamlr implements a 9-stage linear pipeline: Ingestion → Lexer → Scanner → Shadowing → Graph → Schema → HealEngine → Determinism → Atomic Writer.

## 4. Reliability, Security & Privacy
To earn "Google-level" trust, Yamlr codifies the following:

### 4.1 SRE Pillars (Reliability)
*   **🛡 Safety Gate:** Atomic writes (`fsync`) + UUID-hashed backups to prevent multiprocess races.
*   **🧊 Determinism Gate:** Stable sorting of findings and output keys to prevent CI "flicker."

### 4.2 Security & Privacy (Threat Model)
*   **Zero-Exfiltration:** Manifest content never leaves the local environment. Telemetry is opt-in, anonymized, and excludes code snippets.
*   **Secret-Safe:** Healers are barred from modifying `Secret.data` or sensitive fields.
*   **Path Protection:** Absolute path write-barriers to prevent directory traversal or unexpected writes outside the workspace.

## 5. Rollout & Compatibility
*   **New Rule Rollout:** New healers default to **Warn-Only** (S1 Preview) for one minor release before being promoted to auto-fix.
*   **Deprecation Plan:** Flags/Config options follow a "Warn-then-Expire" policy (one major version deprecation period).
*   **Canary Deployment:** Test releases are validated against 2+ "Canary Repos" before stable tagging.

## 6. Performance Regression Guardrail
*   A benchmark suite runs in CI on a fixed fixture set (1k manifests).
*   Tracks p50/p95 latency.
*   CI fails if regression exceeds 10% on the stable core.

## 7. Observability
*   **Error Classification:** Unique error codes (IO_*, PARSE_*, SCHEMA_*) for rapid troubleshooting.
*   **ROI Stats:** `yamlr stats` tracks cumulative time saved and incident prevention count.
