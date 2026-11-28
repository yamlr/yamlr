# Understanding Yamlr: The Kubernetes Configuration Safety Engine

Yamlr is not just a YAML linter; it is a **Kubernetes Configuration Safety Engine** designed to heal "High-Gravity" (severely corrupted) manifests where standard tools simply fail.

## 🌌 The "High-Gravity" Problem
Standard YAML parsers (PyYAML, ruamel) are "brittle"—a single missing quote or mixed indentation causes a fatal error. In large-scale Kubernetes environments, this leads to:
1. **Broken CI/CD**: One malformed file stops the entire pipeline.
2. **Schema Trauma**: Valid YAML that violates K8s structural rules (e.g., providing a string where a list is expected).
3. **Relationship Decay**: Valid manifests that reference non-existent Secrets, PVCs, or Services.

---

## 🛠️ Core Healing Pillars

### 1. Trauma Healing (Structural Surgery)
Yamlr's **Epistemic Reconstruction** engine doesn't just fix syntax; it understands *intent*.
*   **Type Transformation**: If K8s expects a list but receives a scalar, Yamlr automatically wraps it.
*   **Lexical Repair**: Fixes unclosed quotes, double-dash collisions, and "impossible" indentation without losing comments or layout.
*   **Prophetic Migration**: Automatically upgrades legacy API versions (e.g., `extensions/v1beta1`) to their modern equivalents during the healing process.

### 2. Relationship Surgery (Semantic Healing)
Yamlr performs **Cross-Resource Referential Integrity** checks.
*   **Ghost Detection**: Identifies references to non-existent resources.
*   **Fuzzy Anchoring**: If a Deployment references `secret-v1` but only `secret-v1-final` exists, Yamlr uses fuzzy matching to suggest or apply a "Relationship Repair."

### 3. Epistemic Reconstruction (The Pipeline)
Yamlr processes files in 9 distinct stages:
1.  **Lexer Sharding**: Breaks YAML into recoverable tokens.
2.  **Layout Pinning**: Captures whitespace and comments as first-class citizens.
3.  **Identity Inference**: Detects Kind/API even if the `kind` field is missing or misspelled.
4.  **Schema Matching**: Links the manifest to the official Kubernetes Schema Catalog.
5.  **Reconstruction**: Rebuilds the document "from the DNA up" while preserving your original formatting.

---

## 🛡 TRUST GUARANTEE

### Scientific Mode & HAS Score
How do you trust an engine that modifies your code? You use **Scientific Mode**.
*   **HAS (Healing Accuracy Score)**: A metric measuring how close a repaired manifest is to the "Ground Truth" Kubernetes schema.
*   **Scientific Audit**: Generates a forensic trail (JSON) of every change made, including the "Reconstruction Depth."

### Safety Signaling (Entropy Protection)
Yamlr calculates the **Entropy** of every repair.
*   **Low Entropy**: Clear fix, high confidence (Applied automatically).
*   **High Entropy**: Ambiguous corruption (Engine skips the fix to prevent "Hallucinations").
*   This is why Yamlr rarely reaches a 100% score on "Torture" datasets—it prioritizes **Safety over Aggressiveness**.

---

## 🚀 Key Commands
*   `yamlr audit --bench`: Run a scientific benchmark on your entire cluster.
*   `yamlr check [file] --verbose`: View the 9-stage forensic audit trail for a single file.
*   `yamlr status`: View your cluster's "Gamified" health score.

> [!TIP]
> Use the `Yamlr_PRO=1` environment variable to unlock Enterprise Identity v3, including advanced Relationship Surgery and High-Gravity Lexical Repair.
