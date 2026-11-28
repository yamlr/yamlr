# Compliance, Evidence & Semantic DNA

In enterprise environments governed by SOC2 Type II, ISO 27001, FedRAMP, and PCI-DSS, verifying that configurations deploy cleanly is insufficient—platform teams must provide **mathematical proof** that deployed manifests satisfy strict security baselines, that no unauthorized mutations occurred in CI/CD, and that automated fixes did not inject unintended operational side effects.

Yamlr provides an institutional compliance architecture centered on **Cryptographic Semantic DNA Fingerprinting**, **Automated Evidence Generation**, and **Offline Air-Gapped Licensing**.

---

## Table of Contents

1. [The Problem with Raw SHA-256 Hashing](#1-the-problem-with-raw-sha-256-hashing)
2. [Cryptographic Semantic DNA Architecture](#2-cryptographic-semantic-dna-architecture)
3. [The Sovereign DNA Seal (`yamlr.dev/dna-seal`)](#3-the-sovereign-dna-seal-yamlrdevdna-seal)
4. [Continuous Baseline Auditing & Drift Verification](#4-continuous-baseline-auditing--drift-verification)
5. [Automated Compliance Evidence & SARIF Aggregation](#5-automated-compliance-evidence--sarif-aggregation)
6. [Air-Gapped Operation & Cryptographic Provenance](#6-air-gapped-operation--cryptographic-provenance)

---

## 1. The Problem with Raw SHA-256 Hashing

In traditional CI/CD pipelines, security checks often attempt to lock manifest integrity using standard raw cryptographic hashes (e.g., `sha256sum deployment.yaml`).

However, standard byte hashes are **syntactically fragile**:
* A developer adding a harmless `# Updated for Jira-1234` comment invalidates the hash.
* A formatting linter adjusting 4-space indentation to 2-space indentation invalidates the hash.
* Reordering map keys (e.g., placing `metadata.labels` before `metadata.annotations`) invalidates the hash.

This fragility forces teams to disable cryptographic gating in GitOps repositories, creating security blind spots.

---

## 2. Cryptographic Semantic DNA Architecture

Yamlr computes an order-invariant, comment-invariant **Semantic DNA Hash** (`native_calculate_dna_hash()`, `compute_semantic_dna()`):

```
Raw YAML Manifest (with arbitrary whitespace & comments)
                     │
                     ▼
       Concrete Syntax Tree (CST) Parser
                     │
                     ▼
       Semantic Normalization Engine
       - Strips whitespace & formatting noise
       - Filters out `# comments` and empty lines
       - Alphabetizes dictionary & mapping keys
       - Ignores existing `yamlr.dev/dna-seal`
                     │
                     ▼
          Canonical AST Serialization
         (Deterministic key-value stream)
                     │
                     ▼
       SHA-256 Cryptographic Hash Engine
                     │
                     ▼
64-Character Hexadecimal Semantic DNA Fingerprint
```

### Key Invariants of Semantic DNA

1. **Comment Invariance:** Adding, updating, or deleting `# comments` does not alter the DNA hash.
2. **Key-Order Invariance:** `apiVersion: apps/v1` before or after `kind: Deployment` produces identical DNA.
3. **Indentation Invariance:** Switching between 2-space and 4-space indentation does not alter the DNA hash.
4. **Semantic Sensitivity:** Modifying a single replica count, changing a container port, altering an image digest, or modifying an environment variable produces a completely different DNA hash.

---

## 3. The Sovereign DNA Seal (`yamlr.dev/dna-seal`)

During autonomous healing (`yamlr heal --apply`), Yamlr can stamp a cryptographic attestation directly into the manifest's metadata:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-processor
  namespace: production
  annotations:
    yamlr.dev/dna-seal: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    yamlr.dev/healed-at: "2026-10-19T04:45:00Z"
spec:
  replicas: 3
  ...
```

### Self-Referential Hash Safety
The DNA calculation engine explicitly excludes `yamlr.dev/dna-seal` during canonical serialization, preventing infinite hash-invalidation loops.

### Inspecting DNA in the Terminal
```bash
# Calculate Semantic DNA fingerprints across a directory of manifests
yamlr dna ./manifests

# Output:
# FILE                          KIND         NAME                SEMANTIC DNA
# deploy/payment-service.yaml   Deployment   payment-processor   e3b0c44298fc1c14...
# deploy/payment-ingress.yaml   Ingress      payment-gateway     8f4b23a109ec2d33...
```

---

## 4. Continuous Baseline Auditing & Drift Verification

Security and platform teams can snapshot authorized manifest baselines and continuously verify that subsequent pull requests or GitOps synchronizations have not drifted:

```bash
# 1. Snapshot the current authorized manifest state
yamlr baseline snapshot ./manifests --out baseline.json

# 2. In CI/CD PR verification, assert that no unauthorized drift occurred
yamlr baseline verify baseline.json --fail-on high
```

If unauthorized functional changes (such as escalated privileges or unpinned image digests) are detected, the pipeline fails with a clear diff showing the semantic drift.

---

## 5. Automated Compliance Evidence & SARIF Aggregation

For external auditors (SOC2, ISO 27001), platform teams must provide proof of remediation and policy enforcement.

```bash
# Generate structured compliance evidence
yamlr evidence ./manifests --output json

# Export standard SARIF 2.1.0 for GitHub Advanced Security
yamlr scan ./manifests -o sarif -f results.sarif
```

### SARIF Control Mapping
Yamlr's SARIF export conforms to OASIS SARIF v2.1.0 standards, integrating directly into the GitHub Code Scanning tab, GitLab Security Dashboard, and enterprise SIEMs (Datadog, Splunk).

Every emitted finding references:
* Canonical Rule ID (e.g., `SEC-001`, `NET-001`).
* Official CIS Kubernetes Benchmark citation (e.g., `CIS-5.7.3`).
* Exact file path, line number, and column span.
* Remediation advice and automatic fix command.

---

## 6. Air-Gapped Operation & Cryptographic Provenance

Yamlr is designed to operate in highly secure, air-gapped banking, defense, and healthcare environments:

* **Zero Outbound Telemetry by Default:** Set `--no-telemetry` or define `no_telemetry: true` in `.yamlr.yaml`.
* **Zero Network Calls:** Embedded schemas and catalogs eliminate runtime downloads from GitHub or Kubernetes repositories.
* **Cryptographic License Verification:** Team and Enterprise licenses are validated offline using Ed25519 asymmetric cryptography (`yamlr auth activate <SIGNED_TOKEN>`).
* **Cryptographic Manifest Signing:** Manifest sets can be signed using `yamlr sign` and verified in GitOps pipelines using `yamlr verify` before admission to the cluster.
