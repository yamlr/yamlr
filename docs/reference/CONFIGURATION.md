# Workspace Configuration (`.yamlr.yaml`)

This document is the definitive specification for `.yamlr.yaml`, the repository configuration file that controls the behavior of the Yamlr Safety & Healing Engine.

By committing `.yamlr.yaml` to the root of your repository, you guarantee that every engineer on your team, as well as automated CI/CD runners, evaluates Kubernetes manifests against identical schema targets, severity thresholds, and architectural guardrails.

---

## Table of Contents

1. [Bootstrapping Configuration (`yamlr init`)](#1-bootstrapping-configuration-yamlr-init)
2. [Complete Annotated Reference Specification](#2-complete-annotated-reference-specification)
3. [Configuration Resolution Order](#3-configuration-resolution-order)
4. [Autonomous Healing Policies](#4-autonomous-healing-policies)
5. [CRD & Custom Schema Ingestion](#5-crd--custom-schema-ingestion)
6. [Resetting Configuration (`yamlr admin config-reset`)](#6-resetting-configuration-yamlr-admin-config-reset)

---

## 1. Bootstrapping Configuration (`yamlr init`)

To bootstrap a production-ready `.yamlr.yaml` file tailored to your repository:

```bash
yamlr init
```

The `init` engine automatically inspects the workspace directory:
* Detects Helm charts (`Chart.yaml`, `values.yaml`, `charts/`).
* Detects Kustomize overlays (`kustomization.yaml`).
* Detects standard flat Kubernetes manifests.
* Generates a `.yamlr.yaml` file with sensible defaults and target Kubernetes version `1.30`.

To overwrite an existing configuration file:
```bash
yamlr init --force
```

---

## 2. Complete Annotated Reference Specification

Below is the complete specification of all configuration keys recognized by the native Rust engine:

```yaml
# Yamlr Manifest Safety & Autonomous Resolution Configuration
# Schema: https://yamlr.dev/schema/v1.json

version: 1
project_type: "Standard Kubernetes Manifests" # Detected project type

# Target Kubernetes version for schema validation and API deprecation checks.
# Supported versions: "1.21" through "1.37+" (Defaults to "1.30").
k8s_version: "1.30"

# CI/CD Gate Threshold: error, warning, info
# Scan/check commands return exit code 1 if violations meet or exceed this level.
fail_on: "error"

# Autonomous Healing Policies
healing:
  # Global toggle for automated AST repairs
  enabled: true

  # Guarantees 100% preservation of comments, inline docs, and whitespace layout
  preserve_comments: true

  # Normalizes ':latest' tags or enforces imagePullPolicy: Always (SEC-002)
  pin_latest_tags: true

  # Drops dangerous Linux capabilities (SYS_ADMIN, NET_ADMIN) and sets drop: [ALL] (BST-005)
  drop_all_capabilities: true

  # Enforces read-only root filesystems and synthesizes /tmp emptyDir mounts (SEC-012)
  enforce_read_only_root_fs: true

  # Re-orders multi-document streams and stamps ArgoCD/Flux sync waves (GTO-002)
  gitops_wave_stamping: true

# Schema & Custom Resource Definition (CRD) Settings
schemas:
  # Dynamically ingest custom CRDs discovered in the workspace during scan/heal
  auto_ingest_crds: true

  # Directory containing custom CRD YAML files
  custom_crds_dir: "./crds"

# Telemetry & Compliance
telemetry:
  # Anonymous operational metrics (time saved, outages prevented).
  # Defaults to false for strict air-gapped zero-data egress compliance.
  enabled: false

# Fine-grained Rule Configuration & Suppression
rules:
  # Minimum health score (0-100) required to pass CI
  threshold: 80

  # Specific Rule IDs to silence across the repository
  ignore:
    - "SEC-003" # Ignore namespace pollution if targeting single-namespace cluster
    - "REL-010" # Ignore proportional resource warnings for dedicated batch jobs

# Cross-Resource Reference Alignment (Rules REF-006 & NET-020)
# By default, misspelled ConfigMap/Secret keys and Ingress port names produce explainable
# S0 Advisories (catching CreateContainerConfigError and 502 Bad Gateway without risk).
# Set to true to authorize autonomous S2 in-place alignment for unambiguous distance-1 typos.
allow-reference-alignment: false
```

---

## 3. Configuration Resolution Order

When resolving configuration settings (such as the target Kubernetes schema version or CI failure thresholds), Yamlr applies a strict hierarchy of precedence:

```
┌────────────────────────────────────────────────────────┐
│ 1. CLI Explicit Flags (e.g. -k 1.31, --fail-on warning)│ (Highest Precedence)
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 2. Environment Variables (e.g. YAMLR_K8S_VERSION=1.31) │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 3. Workspace Configuration File (`.yamlr.yaml`)        │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ 4. Built-in Native Defaults (K8s 1.30, fail-on: error) │ (Lowest Precedence)
└────────────────────────────────────────────────────────┘
```

---

## 4. Autonomous Healing Policies

### `preserve_comments: true`
Instructs the Concrete Syntax Tree (CST) engine to maintain every `# comment`, inline developer remark, and licensing header with byte-level fidelity during AST rewriting.

### `drop_all_capabilities: true`
Configures workloads according to CIS Kubernetes Benchmark v1.8.0 Section 5.2.7 and Pod Security Standards (PSS Restricted profile):
```yaml
securityContext:
  capabilities:
    drop:
      - ALL
```

### `enforce_read_only_root_fs: true`
Configures `readOnlyRootFilesystem: true` across container security contexts, while automatically synthesizing `/tmp` `emptyDir` scratch volumes so applications can write temporary cache files without failure.

### `gitops_wave_stamping: true`
Stamps standard ArgoCD and Flux synchronization waves (`argocd.argoproj.io/sync-wave` or `fluxcd.io/sync-wave`) to ensure foundational resources (`CustomResourceDefinition`, `Namespace`, `ConfigMap`) are applied before dependent workloads (`Deployment`, `CustomResource`).

---

## 5. CRD & Custom Schema Ingestion

To validate Custom Resources (e.g., Cert-Manager `Certificate`, Prometheus `ServiceMonitor`, Istio `VirtualService`), Yamlr can ingest CRDs dynamically:

```yaml
schemas:
  auto_ingest_crds: true
  custom_crds_dir: "./manifests/crds"
```

You can also pass custom CRDs on the fly via the CLI:
```bash
yamlr scan ./manifests --crd ./manifests/crds/cert-manager-crd.yaml
```

---

## 6. Resetting Configuration (`yamlr admin config-reset`)

To restore your repository to zero-config defaults without manual file deletion:

```bash
yamlr admin config-reset
```

Output:
```text
[OK] Removed local .yamlr.yaml configuration file.
```
