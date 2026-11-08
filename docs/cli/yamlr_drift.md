# yamlr drift
**Live-Manifest Reconciliation Engine (PRO)**

The `yamlr drift` command audits your live Kubernetes cluster against your local YAML manifests to detect undocumented changes and out-of-band configurations.

## Usage

```bash
# Basic Drift Detection (All Namespaces)
yamlr drift .

# Reconcile Local Manifests with Cluster (S2 Apply Mode)
yamlr drift . --apply

# Fleet View: Scan across all available Kubeconfig contexts
yamlr drift . --all-contexts

# Filter by Specific Namespace
yamlr drift . --namespace production
```

## How it works

Yamlr analyzes the "Live Truth" from your cluster and compares it with the "Proposed Truth" in your local directory using its **Semantic DNA** engine. It ignores non-vital mutations (like status timestamps or system annotations) and focuses on structural drift (image tags, replicas, resource limits).

## Enterprise Features

### 1. Loop-Closing Sync (`--apply`)
Transforms Yamlr into a reconciliation engine. When `--apply` is passed, Yamlr will update your local manifests to match the live cluster state (after cleaning transient metadata), ensuring your GitOps source of truth is perfectly aligned with reality.

### 2. Fleet View (`--all-contexts`)
Orchestrate drift analysis across your entire fleet. Yamlr will cycle through every context in your kubeconfig and aggregate a global drift report, identifying inconsistencies across dev, staging, and production clusters.

### 3. Namespace Scoping (`--namespace`)
Limit the audit to a specific namespace to reduce noise and analysis latency in multi-tenant clusters.

### 4. Reporting Tiers
*   **Missing**: Local manifests that are not found in the cluster.
*   **Shadow**: Live resources that have no local manifest counterpart.
*   **Mutated**: Structural differences between local and live state.

---

> [!IMPORTANT]
> **Safety First:** The `--apply` mode will modify your local files. It is recommended to run a dry-run (default) first and ensure your local workspace is under version control (Git) before applying cluster-wide synchronization.

> [!NOTE]
> This feature requires a [PRO] license. Run `yamlr auth login` to activate your enterprise tier.
