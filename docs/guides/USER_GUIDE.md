
# Yamlr User Guide

**Kubernetes Configuration Safety Engine**

Yamlr is a deterministic Kubernetes configuration resolution plane built in native Rust with embedded OpenAPI schemas and offline execution.

### 🌗 Tier Architecture
*   **Individual Tier (Free & Open Community):** Unlimited, 100% offline manifest scanning (`yamlr scan`), autonomous healing (`yamlr heal`), canonical formatting (`yamlr fmt`), instant repair (`yamlr fix`), and standard SARIF report generation.
*   **Team Tier:** Adds multi-repository GitOps fleet reconciliation (`yamlr fleet`), PR automation, and custom ValidatingAdmissionPolicy export (`yamlr vap`).
*   **Enterprise Tier:** Adds cryptographic compliance evidence bundles (`yamlr evidence`), HMAC-SHA256 manifest signing and verification (`yamlr sign`, `yamlr verify`), air-gapped offline distribution, and OpenTelemetry exposition (`--otel`).

Runs 100% locally. Zero telemetry phoning home by default, and no data leaves your machine.

---

# 🚀 60-Second Quick Start

### 1️⃣ Download Binary

Download the latest release for your OS:

* Linux (x86_64)
* macOS (Intel / Apple Silicon)
* Windows (PowerShell supported)

Make it executable and move it to your PATH:

```bash
chmod +x yamlr
sudo mv yamlr /usr/local/bin/
```

Verify installation:

```bash
yamlr version
```

### 🆕 New User?
Run `yamlr welcome` for an interactive dashboard and guided tour of all capabilities.
Run `yamlr manual` to read this entire guide directly in your terminal.

---

# ⚡ Your First Safety Scan

```bash
yamlr scan .
```

Yamlr will:

* Parse all Kubernetes manifests
* Build a cross-resource graph
* Detect semantic failures
* Provide deterministic remediation guidance

Nothing is modified in `scan` mode.

---

# 🧠 What Makes Yamlr Different

Most tools validate structure.

Yamlr validates system integrity.

---

## 🔥 Top “Magic Moments”

### 1️⃣ Ghost Services

Detects Services whose selectors match zero Pods.

`kubectl apply` succeeds.
Traffic silently fails.
Yamlr catches it.

---

### 2️⃣ Cross-Resource Port Mismatch

Aligns:

Ingress → Service → Container ports

Schema passes.
Cluster applies.
Traffic breaks.

Yamlr detects and fixes.

---

### 3️⃣ Deprecated API Migration

Upgrade cluster → manifests break.

```bash
yamlr upgrade . --to 1.31
```

Covers K8s 1.9 → 1.31. Automatically migrates deprecated APIs safely.

---

### 4️⃣ Orphan ConfigMaps & Secrets

Finds unused or dangling resources polluting your cluster definitions.

---

### 5️⃣ Deterministic Healing

```bash
yamlr heal .
```

Shows visual diff before applying changes.

Backups are automatically created.

No silent rewrites.

---

# 🛡 Safety Guarantees

Yamlr is designed for production environments.

## Semantic DNA Integrity

Every manifest has a computed semantic hash.

If healing accidentally changes meaning beyond intended repair,
Yamlr aborts the write.

No accidental production drift.

---

## Automatic Backup Rotation

Before any modification:

```
.yamlr/backups/
```

* Timestamped snapshots
* Last 5 versions retained
* Instant rollback via:

```bash
yamlr restore <path>
```

---

## Non-Destructive Formatting

Yamlr preserves:

* Quote style
* Field ordering
* Whitespace where possible

Clean diffs. GitOps-friendly.

---

# 🛠 Core Commands

## Read-Only Safety Analysis

```bash
yamlr scan .
yamlr check .
yamlr audit .
```

### CI Gate Mode

```bash
yamlr scan . --fail-on error
```

Exit code 1 if violations found.
Use `--risk-threshold` for safety-based gating:
```bash
yamlr scan . --risk-threshold high
```
Perfect for GitHub Actions / GitLab CI.

---

## Healing & Remediation

```bash
yamlr heal .
```

Interactive by default.

> [!NOTE]
> **Community Usage:** Manifest scanning (`yamlr scan`) and local manifest healing (`yamlr heal`) are 100% free and unlimited in the Individual tier. Run `yamlr heal . --diff` to preview changes or `yamlr heal . --apply` to commit fixes in-place.

### Fully Automatic Mode (Surgeon)

```bash
yamlr heal . --apply
```

---

## Kubernetes Upgrade Migration

```bash
yamlr upgrade . --to 1.31
```

Covers K8s 1.9 through 1.31 (forward-looking to 1.32).
Forward-only safe migration.

---

## 🔗 Cross-Resource Dependency Graph

Yamlr builds a **ResourceGraph** of your manifests — 17 typed edge relationships:

* Service → Pod (selector match)
* Ingress → Service (backend)
* ConfigMap/Secret → Pod (volume/env)
* HPA → Deployment (scale target)
* NetworkPolicy → Pod (isolation)
* PDB → Pod (disruption budget)
* PriorityClass, RuntimeClass, CRD instances, Gateway routes

This enables **blast radius analysis** — knowing which resources are affected when one breaks.

---

## ⚡ Risk Classification (Safety Engine)

Every finding is processed by the **Risk Classifier**, which uses heuristic scoring to categorize risks into distinct safety buckets based on their impact:

* Traffic Routing Failure
* Data Dependency Failure
* API Deprecation Risk
* Security Policy Violation
* Network Isolation Risk
* Image Pull Failure Risk
* And 9 more...

Each category has an impact scope (cluster/namespace) and risk level (HIGH/MEDIUM/LOW).

---

## Cross-Resource Auto-Fix (Pro)

```bash
yamlr heal . --fix-refs
```

Used to correct selector typos (Service ↔ Pod), fix port mismatches (Ingress ↔ Service ↔ Container), and stub missing ConfigMaps/Secrets referenced in volumes.

Includes:

* Selector alignment
* Port correction
* Missing reference stubs

---

# 🧪 Demo Mode

Instant playground:

```bash
yamlr demo
```

Creates intentionally broken manifests.

Run:

```bash
yamlr heal yamlr-demo/
```

Experience the “magic moment” safely.

### Enterprise Demo (`--pro-preview`)
Try out all Enterprise features without a license and without modifying any files to see exactly what Yamlr Pro would fix for you:
```bash
yamlr heal . --pro-preview
```

---

# 📊 Project Health & ROI

Yamlr tracks its impact locally.

```bash
yamlr stats
```

Shows:

* Fixes applied
* Time saved
* Detection coverage
* Project health score

No telemetry leaves your machine.

---

# ⚙ Common Power Flags

| Flag                         | Purpose                      |
| ---------------------------- | ---------------------------- |
| `--diff` / `--dry-run`       | Show changes without writing |
| `--pro-preview`              | [Heal] Simulate PRO fixes safely |
| `--fail-on {error,warning,any}` | CI/CD Gate: Exit 1 if issues found |
| `--risk-threshold {high,medium,low}` | Exit 1 based on risk impact |
| `--kube-version`             | Target K8s version (e.g. 1.31) |
| `--strict`                   | [Check] Treat warnings as errors |
| `--summary-only`             | Batch mode: show aggregate only |
| `--quiet`                    | Minimal output for CI/CD     |
| `--concurrency N`            | Parallel worker count        |
| `--stream-to FILE`           | Ultra-scale: Stream to NDJSON |
| `--identity-mode {infer,strict}` | Identity detection style |

---

# 🧬 Semantic DNA Verification (Pro)

Verify configuration integrity in CI:

```bash
yamlr dna deployment.yaml
```

Invariant to:

* Comments
* Field order
* Formatting

Use `--hash` to enforce immutability.

---

# 🔐 Zero-Trust Hardening (Pro)

Analyze and suggest security hardening automatically.

```bash
yamlr secure .          # Read-only security audit
yamlr heal . --harden   # Interactive repair
```

Injects:

* runAsNonRoot
* Read-only FS
* Drop capabilities
* Default deny NetworkPolicy

---

# 🧠 Philosophy

Kubernetes validates structure.

Yamlr validates system integrity.

Schema errors are obvious.

Logical misconfigurations are silent.

Yamlr exists to eliminate silent failures.

---

# 🏢 Free vs Pro (Enterprise)

Yamlr uses a tiered model to support small teams while providing enterprise-grade automation at scale.

| Feature | Free Tier | Pro (Surgeon) |
| :--- | :--- | :--- |
| **Scanning & Diagnostics** | Unlimited | Unlimited |
| **Risk Auditing (SARIF)** | Unlimited | Unlimited |
| **Automated Healing** | 5 files / day | **Unlimited** |
| **Security Hardening** | Manual | **Automated (`--harden`)** |
| **DNA Verification** | Manual | **Automated (`--hash`)** |
| **Ecosystem Adapters** | N/A | **OPA & Kyverno** |

Upgrade:

```bash
yamlr auth login
```

---

# 📦 Catalog Management

Yamlr ships with embedded Kubernetes OpenAPI catalogs.

Check active version:

```bash
yamlr catalog status
```

Update:

```bash
yamlr catalog update --kube-version 1.32
```

---

# 🔧 Additional Commands

## Compliance Evidence & Auto-Remediation (Pro)

```bash
# Ingest Kyverno reports and apply Yamlr auto-fixes
yamlr heal . --kyverno-report policy-report.json

# Generate cryptographic DNA receipts
yamlr evidence ./receipts --format pdf --output report.pdf
```

Aggregates cryptographic DNA receipts into auditor-ready PDF reports.

## SRE Dashboard (Health)

```bash
yamlr status
```

Displays the system health dashboard, including configuration status, catalog info, and backup usage.

## Deep Diagnostics

```bash
yamlr diagnose .
```

Runs a deep audit with DEBUG logging. Use to trace engine decisions.

## Rule Discovery

```bash
yamlr rules                    # Dashboard of all protections
yamlr explain <rule_id>        # Detail on a specific rule
```

## Project Initialization

```bash
yamlr init                     # Create .yamlr.yaml config
```

## Shell Autocompletion

```bash
yamlr completion bash --install   # Also: zsh, fish, powershell
```

---

# ❓ Troubleshooting

**“Missing path argument”**

Specify target:

```bash
yamlr scan .
```

**CI passes even when broken?**

Ensure you are using:

```bash
yamlr scan . --fail-on error
```

---

# 🏁 Summary

Yamlr is not a linter.

It is a Kubernetes configuration safety engine.

It complements your existing toolchain.

It prevents silent deployment failures before they reach production.

Runs locally.
Deterministic.
Safe.

---
