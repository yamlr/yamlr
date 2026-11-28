
# Yamlr User Guide

**Kubernetes Configuration Safety Engine**

Yamlr is a deterministic Kubernetes configuration resolution plane built in native Rust with embedded OpenAPI schemas and offline execution.

### 🌗 Tier Architecture
*   **Individual Tier (Free & Open Community):** Unlimited, 100% offline manifest scanning (`yamlr scan`), autonomous healing (`yamlr heal`), canonical formatting (`yamlr fmt`), instant repair (`yamlr fix`), and standard SARIF report generation.
*   **Team Tier:** Adds multi-repository GitOps fleet reconciliation (`yamlr fleet`), PR automation, and custom ValidatingAdmissionPolicy export (`yamlr vap`).
*   **Enterprise Tier:** Adds cryptographic compliance evidence bundles (`yamlr evidence`), HMAC-SHA256 manifest signing and verification (`yamlr sign`, `yamlr verify`), air-gapped offline distribution, and OpenTelemetry exposition (`--otel`).

> [!IMPORTANT]
> **Audit mode (`yamlr scan`) never modifies files. Active Healing (`yamlr heal`) only changes manifests when explicitly invoked and backed by Global Atomic Sessions and automatic backups.**

Runs 100% locally. No data leaves your machine.

---

# 60-Second Quick Start

### 1⃣ Download Binary

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
Run `yamlr manual` to read this entire guide or specific command help (e.g., `yamlr manual scan`) directly in your terminal.

---

# 🏗 Architectural Primitives (Industrial Strength)

Yamlr is built on three first-class primitives that enable global reasoning:

| Primitive | Role | Why It Matters |
|:--|:--|:--|
| **CatalogManager** | Dynamic Knowledge Base | Handles 150+ K8s resource types and their relational affinity. |
| **RuleManager** | Policy Orchestration | Manages the "Trust Gate" — ensuring every fix is safe and explainable. |
| **ResourceGraph** | Dependency Engine | Unlocks the "Blast Radius" feature by mapping complex cross-resource links. |

For deep technical details on extending these primitives, see the [Developer Guide](DEV_GUIDE.md).

---

# Your First Safety Scan

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

Yamlr validates system integrity using the **Yamlr Healing Engine** architecture:

```text
  [ Yamlr Healing Engine ]
         |
    +----+----+
    |         |
[ Guard ] [ Surgeon ]
 (Audit)   (Heal)
```

## Top “Magic Moments”

Yamlr is powered by a high-performance **standalone native Rust engine** designed for sub-15ms execution on single manifests and parallel analysis of repositories with 10,000+ manifests.
*   **Zero-Dependency Binary:** Distributed as a single compiled executable with embedded Kubernetes OpenAPI schemas (v1.21 through v1.37+).
*   **Preserves 100% of Comments:** Non-destructive CST token stream guarantees zero comment loss and layout preservation.
*   **Pre-Write Schema Gate:** Automatically prevents invalid or regressive fixes by validating candidate repairs before committing them.

## Hyperscale Streaming Architecture
Yamlr features a **Zero-Copy Streaming** architecture engineered in native Rust for enterprise repositories:
*   **Constant Bounded Memory**: Employs borrowed document-slice parsing to stream manifests with deterministic memory consumption.
*   **Parallel Multithreading**: Utilizes Rayon-based work-stealing parallelism for fast directory tree traversals across multi-core systems.
*   **Embedded Schemas**: Hermetic v1.21 through v1.37+ OpenAPI v3 catalogs compile directly into the native binary, requiring zero network access.

---

### 0.5⃣ Cross-Domain Safety (The Cloud Gap) 🌍

Yamlr bridges the gap between your Kubernetes manifests and your cloud infrastructure. 
It parses **Terraform (.tf)** files to ensure that your `PersistentVolumes` actually match your `aws_ebs_volume` and that your `Secrets` correctly link to your `aws_db_instance` credentials.

---

### 1⃣ Ghost Services

Detects Services whose selectors match zero Pods.

`kubectl apply` succeeds.
Traffic silently fails.
Yamlr catches it.

---

### 2⃣ Cross-Resource Port Mismatch

Aligns:

Ingress → Service → Container ports

Schema passes.
Cluster applies.
Traffic breaks.

Yamlr detects and fixes.

---

### 3⃣ Deprecated API Migration

Upgrade cluster → manifests break.

```bash
yamlr upgrade . --to 1.31  # Also: yamlr migrate . --to 1.31
```

Covers K8s 1.9 → 1.31. Automatically migrates deprecated APIs safely.

---

### 4⃣ Orphan ConfigMaps & Secrets

Finds unused or dangling resources polluting your cluster definitions.

---

### 5⃣ Non-Destructive Preview & Diff

```bash
yamlr diff .
yamlr diff deploy.yaml -u  # Unified diff format
```

Provides an instant side-by-side or unified preview of proposed remediations and schema alignments with zero disk writes.

---

### 6⃣ Deterministic Healing

```bash
yamlr heal .
```

Shows visual diff before applying changes.

Backups are automatically created.

No silent rewrites.

---

### 6⃣ Resource Topology & Blast Radius

Visualize complex dependencies and audit the "Blast Radius" of a potential failure.

```bash
yamlr graph topo
yamlr graph blast-radius --resource Deployment/my-app
yamlr graph export --format mermaid
```

---

# 🧬 Semantic DNA & Restoration

Yamlr is designed to preserve source context during supported repairs. Review the proposed diff and validate the resulting manifests before applying changes.

### `yamlr dna`
Verify configuration integrity in CI to ensure no unauthorized changes were made:
```bash
yamlr dna deployment.yaml
yamlr dna deployment.yaml --hash <expected_hash> # Enforce immutability
```

### `yamlr restore`
Instant rollback to previous configurations from the automatic backup vault:
```bash
yamlr restore <file_path> # Restore the specific file from its most recent backup
```

---

# Safety Guarantees

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
yamlr restore <path> # Restore a single file
yamlr rollback       # Revert an entire atomic session
```

---

## Non-Destructive Formatting

Yamlr preserves:

* Quote style
* Field ordering
* Whitespace where possible

Use **`--canonical`** [Pro] for enterprise aesthetics, including schema-aware key sorting (apiVersion, kind, metadata at top) and comment grafting to preserve annotations during reformatting.

Clean diffs. GitOps-friendly.

---

# 🛠 Core Commands

## Read-Only Safety Analysis

```bash
yamlr scan .   # Also: yamlr audit .
yamlr check .  # Strict validation
Perfect for GitHub Actions / GitLab CI.

### GitOps Guard (Regression Testing)

Adopting Yamlr on a legacy repository can be noisy if you have hundreds of pre-existing violations. Use the **Baseline** command to snapshot existing issues and only block on **new** regressions.

```bash
# 1. Establish Baseline Snapshot
yamlr baseline . --create --file .yamlr-baseline.json

# 2. Verify Drift in CI (Exit 1 on unauthorized changes)
yamlr baseline . --check --file .yamlr-baseline.json
```

Yamlr calculates a stable SHA-256 fingerprint for every finding. If a finding is already in the baseline, it is ignored and won't trigger a non-zero exit code.

### Auditor-Ready Evidence

```bash
yamlr evidence . -o compliance-evidence.tar.gz
```

Generate mathematical proof of compliance. See [yamlr_evidence.md](cli/yamlr_evidence.md) for details.

---

## Healing & Remediation

```bash
yamlr heal .
```

Interactive by default. 

> [!NOTE]
> **Community Usage:** Manifest scanning (`yamlr scan`) and local manifest healing (`yamlr heal`) are 100% free and unlimited in the Individual tier. Run `yamlr heal . --diff` to preview changes or `yamlr heal . --apply` to commit fixes in-place.

### Advanced Remediation Flags

| Flag | Effect | Tier |
|:--|:--|:--|
| `-a, --apply` | Atomically commit healed changes to disk with WAL snapshot | ✅ Free |
| `-d, --dry-run` | Preview changes without modifying files on disk | ✅ Free |
| `--diff` | Display unified color diff of proposed changes | ✅ Free |
| `-k, --k8s-version <V>` | Target Kubernetes version for API upgrades (e.g. `1.30`) | ✅ Free |
| `--workspace <DIR>` | Explicit workspace root directory for resource indexing | ✅ Free |
| `--generate-stubs` | Synthesize placeholder definitions for missing refs | ✅ Free |
| `--ingest-opa <PATH>` | Ingest external OPA constraint report for auto-healing | ✅ Free |
| `--ingest-kyverno <PATH>` | Ingest Kyverno policy report for auto-healing | ✅ Free |
| `--verify-kubectl` | Validate candidate output via client dry-run | ✅ Free |
| `--explain-gate` | Explain pre-write safety gate diagnostics if blocked | ✅ Free |
| `--summary` | Output condensed remediation count table | ✅ Free |
| `-o, --output <FMT>` | Output format (`text`, `json`, `sarif`) | ✅ Free |
| `--otel` | Export OpenTelemetry Prometheus exposition metrics | 💎 Enterprise |

### MCP for IDE Integrations (Pro)

Connect Yamlr to your IDE or editor environment (such as VS Code, Neovim, JetBrains, or automated developer tools) for surgical manifest analysis.

```bash
# Start the MCP stdio server
yamlr mcp
```

Yamlr exposes `scan_manifest`, `heal_manifest`, and `why` tools to connected editors, ensuring manifest remediations are safe and deterministic.

---

---

## Kubernetes Upgrade Migration

```bash
yamlr upgrade . --to 1.31  # Also: yamlr migrate . --to 1.31
```

Covers K8s 1.9 through 1.31 (forward-looking to 1.32).
Forward-only safe migration.

---

## 🔗 Cross-Domain ResourceGraph

Yamlr builds a **ResourceGraph** of your manifests and cloud infrastructure — **26 typed edge relationships**:

*   **OwnerReference:** (Deployment → RS → Pod). Crucial for "Auto-Cleanup" and "Blast Radius" mapping.
*   **VolumeMount → Container:** Internal resource binding (finding which container is starving which PVC).
*   **Service → EndpointSlice:** The literal traffic path that OPA often misses.
*   **ResourceQuota → Namespace:** Mapping application appetite to cluster availability.
*   **KMS → Secret:** Mapping the security chain for compliance audits (SOC2/FedRAMP).
*   **VPA → Workload:** Vertical pod autoscaling dependencies.
*   **Gateway → GatewayClass:** Full Gateway API depth.
* Service → Pod (selector match)
* Ingress → Service (backend)
* PersistentVolume → Cloud Storage (EBS/S3)
* Secret → Cloud Database (RDS/IAM)
* ConfigMap/Secret → Pod (volume/env)
* HPA → Deployment (scale target)
* NetworkPolicy → Pod (isolation)
* PDB → Pod (disruption budget)
* PriorityClass, RuntimeClass, CRD instances, Gateway routes

This enables **blast radius analysis** — knowing which resources are affected when one breaks.

---

# 🏗 Architectural Primitives
Yamlr is built on three core pillars that ensure its surgical precision and reliability:

### 1. CatalogManager
The **CatalogManager** is the central schema engine of Yamlr's K8s awareness. It manages the lifecycle of Kubernetes OpenAPI schemas, ensuring that every scan is performed against the exact API definitions of your target cluster. It supports version switching across 16 Kubernetes releases (v1.21 to v1.36+).

### 2. RuleManager
The **RuleManager** orchestrates the 100+ diagnostic rules that power Yamlr's analysis. It handles rule discovery, severity weighting, and risk classification, allowing Yamlr to provide consistent, explainable feedback across all environments.

### 3. ResourceGraph
The **ResourceGraph** is the connective tissue of your infrastructure. Unlike simple linters that look at files in isolation, Yamlr builds a directed acyclic graph (DAG) of your entire repository, mapping hidden dependencies like service selectors to pod labels and ingress backends to service ports.

---

## Risk Classification (Safety Engine)

Every finding is processed by the **Risk Classifier**, which uses heuristic scoring to categorize risks into one of **15 safety buckets**:

* Traffic Routing Failure
* Data Dependency Risk
* Resource Exhaustion Risk
* Security Posture Weakness
* Network Isolation Risk
* Image Pull Failure Risk
* And 9 more (Version, RBAC, Scheduling, etc.)

Each category has an impact scope (cluster/namespace) and risk level (HIGH/MEDIUM/LOW).

---

## Cross-Resource Relational Healing

```bash
# Preview cross-resource remediations with diff
yamlr heal . --diff

# Apply fixes in-place and stub missing ConfigMaps/Secrets
yamlr heal . --apply --generate-stubs
```

Corrects selector typos (Service ↔ Pod), aligns port mismatches (Ingress ↔ Service ↔ Container), and stubs missing ConfigMaps/Secrets referenced in volumes.

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

### Safe Preview (`--diff`)
Preview all proposed remediations safely without modifying any files on disk:
```bash
yamlr heal yamlr-demo/ --diff
```

---

# 📊 Project Health & ROI

Yamlr tracks its impact locally and provides per-application safety scoring.

```bash
yamlr stats
yamlr stats --apps    # Detailed per-app safety report
```

Shows:

* Fixes applied
* Time saved
* Detection coverage
* **App Safety Score** (0-100)
* Top Risk Categories (Security, Availability, etc.)

No telemetry leaves your machine.

---

# 📈 Executive ROI & Safety Dashboards

Yamlr provides high-level diagnostics for engineering leaders and founders to justify budgets and track ecosystem health.

```bash
yamlr roi              # Business Value: Engineering hours saved & project rank
yamlr roi --badge      # Generate a Shields.io ROI badge for your README
yamlr stats            # Local telemetry: Files healed & ROI summary
yamlr stats --apps     # Detailed per-app safety report & blast-radius
yamlr pulse            # Founder Intelligence: Aggregate rule efficacy & coverage
```

---

# Diagnostic & Support

### `yamlr diagnose`
Deep-dive analysis with elevated verbosity for environment-specific debugging.
```bash
yamlr diagnose .
yamlr diagnose . --output json  # Machine-readable debug output
yamlr diagnose . --bundle       # [PRO] Export anonymized founder-ready support zip
```

The `--bundle` command creates a `yamlr-bundle-<timestamp>.zip` containing anonymized telemetry, configuration summaries, and environment data to help with strategic review.

---

# IDP Integration & Exports

Yamlr acts as a "Supplier of Truth" for your internal developer portals.

```bash
yamlr idp-export --format backstage
yamlr idp-export --format prometheus
```

Supported formats:
* **Backstage**: JSON component annotations.
* **Prometheus**: OpenMetrics text for Grafana dashboards.
* **JSON**: Raw internal safety spec.

### `yamlr idp-export init`
Generate opinionated integration templates for your IDP:
```bash
yamlr idp-export init --format backstage --output catalog-info.yaml
yamlr idp-export init --format prometheus --output prometheus-scrape.yml
```

---

# ⚙ Common Power Flags

| Flag | Purpose | Tier |
|:--|:--|:--|
| `--diff` / `--dry-run` | Show proposed changes without modifying disk | ✅ Free |
| `--apply` | Commit healed changes in-place with WAL journal | ✅ Free |
| `--fail-on <SEVERITY>` | CI/CD Quality Gate: exit 1 on error, warning, note | ✅ Free |
| `--exit-zero` | Enforce exit 0 for non-blocking CI advisory passes | ✅ Free |
| `-k, --k8s-version <V>` | Target Kubernetes OpenAPI version (default: 1.36) | ✅ Free |
| `-o, --output <FORMAT>` | Standard output formatter (`text`, `json`, `sarif`) | ✅ Free |
| `-f, --output-file <PATH>` | Write output directly to destination file | ✅ Free |
| `-q, --quiet` | Minimal output for CI/CD and GitOps pipelines | ✅ Free |
| `-w, --watch` | Continuous filesystem watcher mode | ✅ Free |
| `--workspace <DIR>` | Explicit workspace root directory | ✅ Free |
| `--helm` | Render Helm chart templates in-memory | ✅ Free |
| `--kustomize` | Execute Kustomize overlays in-memory | ✅ Free |
| `--generate-stubs` | Synthesize placeholder definitions for missing refs | ✅ Free |
| `--no-telemetry` | Disable telemetry reporting (air-gapped compliance) | ✅ Free |
| `--otel` | Export OpenTelemetry Prometheus metrics | 💎 Enterprise |

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

# 🔐 Zero-Trust Security & Network Policy Synthesis

Audit workloads against CIS benchmarks and synthesize least-privilege network policies.

```bash
yamlr audit .                     # Forensic compliance & CIS benchmark audit
yamlr secure . -o netpol.yaml     # Synthesize least-privilege NetworkPolicies
```

Inspects:

* runAsNonRoot & privilege escalation
* Read-only root filesystem
* Linux capability drops
* Least-privilege ingress and egress network boundaries

---

# 🧠 Philosophy

Kubernetes validates structure.

Yamlr validates system integrity.

Schema errors are obvious.

Logical misconfigurations are silent.

Yamlr exists to eliminate silent failures.

---

# 🏢 Feature Tiers & Capabilities

Yamlr uses a clean, transparent tiered model to support open-source developers while providing enterprise-grade governance at fleet scale.

| Capability | Individual Tier (Free) | Team Tier | Enterprise Tier |
|:---|:---:|:---:|:---:|
| **Scanning & Validation (`scan`, `check`)** | Unlimited | Unlimited | Unlimited |
| **Autonomous Remediation (`heal`, `fix`, `fmt`)** | Unlimited | Unlimited | Unlimited |
| **API Version Migration (`migrate`)** | Unlimited | Unlimited | Unlimited |
| **SARIF & GitHub Code Scanning** | Included | Included | Included |
| **Multi-Repo GitOps Fleet (`fleet`)** | Manual | **Automated** | **Automated** |
| **ValidatingAdmissionPolicy Export (`vap`)** | Manual | **Automated** | **Automated** |
| **Cryptographic Evidence Bundles (`evidence`)** | Manual | Manual | **Automated** |
| **HMAC Manifest Signatures (`sign`, `verify`)** | Manual | Manual | **Automated** |
| **Air-Gapped License Activation (`auth`)** | Manual | Manual | **Automated** |
| **OpenTelemetry Observability (`--otel`)** | Manual | Manual | **Automated** |

License Management:

```bash
yamlr auth status
yamlr auth activate --token <SIGNED_TOKEN>
```

---

# Catalog & Schema Management

Yamlr ships with embedded Kubernetes OpenAPI v3 catalogs (v1.21 through v1.37+).

Inspect rule and deprecation catalog:

```bash
yamlr catalog
yamlr catalog --category deprecation
```

Manage schemas:

```bash
yamlr schema list
yamlr schema fetch 1.31
yamlr schema ingest ./crds
```

---

# 🔧 Additional Commands

## Compliance Evidence & Policy Ingestion

```bash
# Ingest external OPA constraint report for automated healing
yamlr heal . --apply --ingest-opa opa-violations.json

# Ingest Kyverno policy report for automated healing
yamlr heal . --apply --ingest-kyverno kyverno-report.yaml

# Export cryptographic audit evidence bundle
yamlr evidence . -o compliance-evidence.tar.gz
```

Aggregates cryptographic DNA fingerprints, WAL journals, and system state into an auditor-ready tarball bundle.

## SRE Dashboard & Engine Health

```bash
yamlr status                     # Workspace and license status view
yamlr doctor                     # Validate engine integrity and loaded schemas
yamlr doctor -v                  # Verbose diagnostics
```

Displays the system health dashboard, including configuration status, schema counts, and engine status.

## Deep Diagnostics

```bash
yamlr diagnose
yamlr diagnose -v                # Verbose diagnostic self-tests
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

---

# 🕵 Security Model & Guarantees

Yamlr is designed for "A+" security grade compliance. Our safety architecture prioritizes **Information Anonymity** and **Supply Chain Integrity**.

### 1. Information Anonymity (Path Masking)
To prevent accidental information disclosure in CI/CD logs or portable audit reports, Yamlr aggressively masks system-specific absolute paths:
*   **`~`**: User home directory paths are redacted.
*   **`[TMP]`**: System temporary directories are masked.
*   **`.`**: Current Working Directory is localized to promote environment-neutral results.
*   **Standard Roots**: Common sensitive Linux/K8s paths are audited but never leaked in raw form.

### 2. Supply Chain & I/O Safety
*   **YAML Bomb Protection**: Standard depth limits prevent "Billion Laughs" Denial of Service attacks during manifest parsing.
*   **SSRF Mitigation**: Remote policy fetching (`--data http://...`) includes size limits and timeout gates to prevent internal network scanning.
- **TOCTOU Hardening**: All file writes use atomic `fsync` + `rename` cycles within a protected, permissioned backup vault.
*   **Memory Hygiene**: Sensitive environment variables like `Yamlr_LICENSE_KEY` are scrubbed from memory immediately after verification.

### 3. Verification & Trust
*   **Signatures**: Pro features utilize HMAC-SHA256 JWT validation with constant-time cryptographic comparisons.
*   **Local-First**: 100% of analysis happens locally. No source code or manifest content is ever transmitted to Yamlr servers.

---

### 4. Expert Diagnostic Assets (PII-Redacted Forensics)
For deep forensic analysis, Yamlr provides expert-level logs that are redacted by default:
*   **--forensic-debug**: Enables 	ree_dna.log and pe_debug.log.
*   **Redaction**: System paths (CWD, HOME, TMP) and sensitive keys are masked to ensure zero PII leaks during forensic debugging.
*   **Off-by-Default**: These assets are only generated when explicitly requested for deep-dive support cycles.

--

# 🏁 Summary

Yamlr is not a linter.

It is a Kubernetes configuration safety engine.

It complements your existing toolchain.

It prevents silent deployment failures before they reach production.

Runs locally.
Deterministic.
Safe.

---
