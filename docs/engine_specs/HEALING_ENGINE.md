# The Autonomous Healing Engine

The Yamlr Healing Engine is an ultra-high performance, deterministic mutation engine compiled in native Rust (`native_core/src/healing.rs`). It acts as the execution backbone of the Kubernetes Configuration Resolution Plane, converting diagnostic findings into mathematically verified, comment-preserving manifest repairs.

---

## Table of Contents

1. [Architectural Philosophy: Safe Autonomous Repair](#1-architectural-philosophy-safe-autonomous-repair)
2. [The 4-Stage Execution Pipeline](#2-the-4-stage-execution-pipeline)
3. [Lossless CST Mutation & Shard Splicing](#3-lossless-cst-mutation--shard-splicing)
4. [Atomic Write-Ahead Log (WAL) & Crash Resilience](#4-atomic-write-ahead-log-wal--crash-resilience)
5. [Visual Diffing & Non-Destructive Dry-Run Modes](#5-visual-diffing--non-destructive-dry-run-modes)
6. [Multi-Document Stream Topological Ordering](#6-multi-document-stream-topological-ordering)
7. [Enterprise Policy Ingestion & Remediation](#7-enterprise-policy-ingestion--remediation)

---

## 1. Architectural Philosophy: Safe Autonomous Repair

The industry standard for Kubernetes configuration management has historically been reactive: linters identify issues, dump hundreds of warnings into CI logs, and leave developers to manually remediate complex schema and relational errors.

Yamlr inverts this paradigm with **Autonomous Deterministic Healing**:

* **Zero-Failure Trust Pillar:** A healing engine that introduces regressions is worse than no healing engine. If a proposed fix cannot be verified against the official Kubernetes OpenAPI schema and relational graph, the fix is automatically aborted.
* **Comment & Whitespace Immutability:** Developer comments (`# TODO`, architectural justifications, licensing headers) are treated as first-class citizens and preserved with byte-level fidelity.
* **Local-First & Offline:** 100% of schema definitions (Kubernetes 1.21 through 1.37+) and forensic detectors are compiled directly into the binary. Zero data egress, zero network calls to external APIs.

---

## 2. The 4-Stage Execution Pipeline

When `yamlr heal` is invoked, the engine processes manifests through a structured four-stage transformation pipeline:

```
Raw Manifest Stream (or File on Disk)
                  │
                  ▼
┌────────────────────────────────────────────────────────┐
│ STAGE 1: Physical Pre-Heal & Syntax Normalization      │
│  - Strip Byte Order Marks (BOM)                        │
│  - Heal block scalar body indentation (SYN-015)        │
│  - Realign orphaned indented blocks (SYN-016)          │
│  - Normalize over-indented sequence items (SYN-017)    │
│  - Repair standalone anchor declarations (SYN-018)     │
│  - Mask Helm / Go template expressions ({{ ... }})     │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│ STAGE 2: Multi-Document Sharding & Identity Indexing   │
│  - Split document slices by `---` boundaries           │
│  - Extract local & workspace identities                │
│  - Index `Kind`, `namespace`, `name`, `labels`, `ports`│
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│ STAGE 3: Semantic AST Remediation Gauntlet             │
│  - Correct schema property & enum typos                │
│  - Lift misnested structural fields (e.g. env map->list)│
│  - Infer and upgrade deprecated `apiVersions`          │
│  - Reconcile Service ports with workload containerPorts │
│  - Inject non-root securityContext & /tmp emptyDir     │
│  - Reconcile HPA replicas & PDB disruption deadlocks   │
│  - Harmonize GitOps controller defaults                │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│ STAGE 4: Reassembly, Verification & WAL Commit         │
│  - Unmask Helm/Go template expressions                 │
│  - Sort multi-doc stream to prevent CRD inversions     │
│  - Verify against OpenAPI schema target version        │
│  - Stamp Sovereign DNA Seal (`yamlr.dev/dna-seal`)     │
│  - Journal pre-state to WAL (`.yamlr/wal/`)            │
│  - Atomically commit healed manifest to disk           │
└────────────────────────────────────────────────────────┘
```

---

## 3. Lossless CST Mutation & Shard Splicing

Traditional YAML libraries convert text into generic hash tables, losing all formatting and comments during serialization.

Yamlr employs a **Concrete Syntax Tree (CST) Sharder** combined with **Shadow Splicing**:

1. **Sharding:** The source document is sliced into `NativeShard` tokens representing exact lines, keys, values, comments, and preceding layout sequences.
2. **Shadow Representation:** A lightweight semantic overlay (`SemanticManifest`) mirrors the hierarchy of Kubernetes objects (`metadata`, `spec`, `template`, `containers`).
3. **Targeted Mutation:** When a rule triggers (e.g., `NET-001` fixing a mismatched port), the healer mutates only the targeted shard's value without modifying surrounding lines.
4. **Layout Reconstruction:** The reconstructed YAML is generated by splicing mutated values directly back into the original line buffer, preserving all indentation, trailing spaces, and comments.

---

## 4. Atomic Write-Ahead Log (WAL) & Crash Resilience

Before any byte is written to disk, Yamlr executes a transactional Write-Ahead Log commit to guarantee zero data loss:

```bash
# Example WAL entry recorded in .yamlr-journal.jsonl / .yamlr/wal/
{
  "tx_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "timestamp": "2026-10-19T04:45:00Z",
  "file_path": "deploy/production.yaml",
  "target_kind": "Deployment",
  "target_name": "web-api",
  "field_path": "spec.template.spec.containers[0].securityContext.runAsNonRoot",
  "previous_value": null,
  "new_value": "true",
  "status": "COMMITTED"
}
```

### Unconditional Single-Command Rollback
If a team lead, developer, or automated pipeline wishes to revert any healed change:

```bash
# Instantly revert files to their exact pre-healed state
yamlr rollback ./manifests

# View complete forensic log of past mutations
yamlr rollback --list
```

### Administrative WAL Hygiene
To prevent WAL files from accumulating on CI worker machines:

```bash
# Prune old WAL journal snapshots
yamlr admin journal-prune
```

---

## 5. Visual Diffing & Non-Destructive Dry-Run Modes

Yamlr enforces the principle that **preview is default**:

```bash
# 1. Preview changes in memory with a colorized unified diff (exits 1 if fixes proposed)
yamlr heal manifests/ --diff
# or dedicated command:
yamlr diff manifests/

# 2. Preview remediation summary table without diff detail
yamlr heal manifests/ --dry-run --summary

# 3. Commit mutations atomically to disk with automatic WAL journaling
yamlr heal manifests/ --apply
```

### Sample Unified Diff Output
```diff
--- deploy/web-service.yaml (original)
+++ deploy/web-service.yaml (healed)
@@ -10,7 +10,7 @@
   ports:
   - name: http
     port: 80
-    targetPort: 8080 # [NET-001] Mismatched containerPort (pod declares 3000)
+    targetPort: 3000 # [NET-001] Synchronized with web-app containerPort
   selector:
     app: web
```

---

## 6. Multi-Document Stream Topological Ordering

In multi-document YAML files (separated by `---`), Kubernetes admission controllers fail if a dependent CustomResource is defined before its `CustomResourceDefinition`, or if a `Namespace` appears after workloads targeting it.

Yamlr evaluates the **topological apply priority** of every document slice in the stream:

1. `Namespace`
2. `ResourceQuota` / `LimitRange`
3. `CustomResourceDefinition`
4. `ServiceAccount` / `Secret` / `ConfigMap`
5. `StorageClass` / `PersistentVolume` / `PersistentVolumeClaim`
6. `Role` / `ClusterRole` / `RoleBinding` / `ClusterRoleBinding`
7. `Service` / `Endpoints`
8. `Deployment` / `StatefulSet` / `DaemonSet` / `Job`
9. `Ingress` / `HTTPRoute` / `Gateway`
10. `HorizontalPodAutoscaler` / `PodDisruptionBudget`

If a critical topological inversion is detected (`has_critical_topological_inversion()`), Yamlr safely reorganizes the document stream so foundational resources precede dependents.

---

## 7. Enterprise Policy Ingestion & Remediation

Yamlr functions as an autonomous remediation layer for your organization's security and admission policies. Instead of treating policies as passive failure gates that block CI pipelines, Yamlr ingests external policy constraint definitions and automatically synthesizes matching concrete syntax tree repairs.

```bash
# Ingest constraint definitions and automatically synthesize matching manifest repairs
yamlr heal ./k8s --ingest-opa policies/constraints.json --apply

# Ingest cluster policy definitions and automatically heal non-compliant manifests
yamlr heal ./k8s --ingest-kyverno policies/disallow-root.yaml --apply
```

By ingesting external policies directly into the healing pipeline, platform teams eliminate manual remediation tickets and allow developers to automatically meet compliance baselines locally.
