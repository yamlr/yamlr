# Core Concepts & Architecture

Yamlr is a configuration resolution plane for Kubernetes. While standard linters check isolated YAML files against static schemas, Yamlr analyzes the relational topology across your entire fleet of manifests before deployment.

In production Kubernetes environments, schema validation (`kubectl --dry-run=client`) passes even when manifests contain broken relational contracts—such as mismatched Service selector labels, orphaned Ingress backends, invalid port targets, or resource conflicts. Yamlr identifies these cross-resource failures and repairs them safely.

---

## Table of Contents

1. [The Configuration Resolution Plane](#1-the-configuration-resolution-plane)
2. [Cross-Resource Relational Topology](#2-cross-resource-relational-topology)
3. [Lossless Concrete Syntax Tree (CST) Preservation](#3-lossless-concrete-syntax-tree-cst-preservation)
4. [The 3-Tier Verification Gate (`[PHY]`, `[KBS]`, `[SEM]`)](#4-the-3-tier-verification-gate-phy-kbs-sem)
5. [Operational Risk & Impact Classification](#5-operational-risk--impact-classification)
6. [Detection Linters vs. Resolution Planes](#6-detection-linters-vs-resolution-planes)

---

## 1. The Configuration Resolution Plane

Yamlr operates between your GitOps source repository and cluster deployment engines. It validates structural syntax, official API schemas, and inter-resource contracts prior to commit.

```text
                    +----------------------------------------------+
                    |            GitOps Manifest Source            |
                    |   (Helm Charts, Kustomize, Flat YAML)        |
                    +----------------------+-----------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                       CONFIGURATION RESOLUTION PLANE                              |
|                                                                                   |
|  [Layout Sharder]        [Relational Graph]            [3-Tier Gate]              |
|  Comment, spacing, and   Cross-resource bindings       [PHY] Indentation & Syntax |
|  formatting preservation (Service -> Workload,         [KBS] OpenAPI Schemas      |
|  during modification     Ingress -> Service, HPA)      [SEM] Cross-Resource Graph |
|                                                                                   |
|  [Deterministic Healer]  [Cryptographic Seal]          [Write-Ahead Log]          |
|  Lossless AST repair     Order-invariant SHA-256       Transactional rollback     |
|  across 53+ rules        manifest verification         journal for zero risk      |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
                    +----------------------------------------------+
                    |       Verified & Healed K8s Manifests        |
                    |   (Production Deploy, ArgoCD, Flux, CI)      |
                    +----------------------------------------------+
```

Traditional tools operate purely in detection mode: they generate warning reports that require manual developer triage. Yamlr offers both strict detection and autonomous remediation, repairing invalid fields directly while preserving all comments, indentation, and structure.

---

## 2. Cross-Resource Relational Topology

Kubernetes applications are distributed systems composed of dependent resources. A single deployment requires multiple coordinated manifests:

```text
[Ingress / Gateway]
        | (rules.http.paths[*].backend.service)
        v
    [Service]
        | (spec.selector == template.metadata.labels)
        v
   [Deployment] <----+ [HorizontalPodAutoscaler] (scaleTargetRef)
        |
   (spec.template.spec)
        +---> [ConfigMap / Secret] (envFrom, valueFrom, volumes)
        +---> [PersistentVolumeClaim] (persistentVolumeClaim.claimName)
        +---> [ServiceAccount] (spec.serviceAccountName)
        +---> [NetworkPolicy] (podSelector, ingress.from, egress.to)
```

### Key Relational Contracts Verified

1. **Service to Workload (`NET-001`):** Verifies that `spec.selector` matches target Pod labels and synchronizes `service.spec.ports[*].targetPort` with declared `containerPort` values.
2. **Ingress to Service (`NET-002`, `NET-008`):** Verifies that backend services exist within the same namespace, target ports exist, and route prefixes avoid routing conflicts.
3. **Workload to ConfigMap and Secret (`SEC-016`):** Audits container environment variable bindings (`configMapKeyRef`, `secretKeyRef`) to verify keys exist before pods crash at startup.
4. **HPA to Workload (`REL-003`, `AUT-002`):** Detects conflicts between static `replicas` declarations in Deployments and active HorizontalPodAutoscalers scaling workloads dynamically.
5. **Workload to Storage Claims (`STO-001`, `STO-002`):** Ensures `claimName` references match declared PersistentVolumeClaims and flags orphaned storage definitions.
6. **NetworkPolicy to Pod:** Evaluates pod isolation boundaries to prevent accidental traffic blackholes.
7. **PodDisruptionBudget to Workload (`REL-005`):** Confirms `minAvailable` or `maxUnavailable` disruption budgets do not exceed total replica counts, avoiding node drain deadlocks.

---

## 3. Lossless Concrete Syntax Tree (CST) Preservation

Standard YAML parsers convert YAML documents into generic dictionary representations. When writing modified data back to disk, generic serializers typically:
- Strip all comments (`#`) and header annotations.
- Remove whitespace, blank lines, and visual section grouping.
- Re-order dictionary keys alphabetically or nondeterministically.
- Corrupt multiline string scalar formats (`|`, `>`).

### Preserving Layout Integrity

Yamlr uses a Concrete Syntax Tree (CST) engine that maintains the complete layout structure of the original file alongside the semantic model. 

When a remediation is applied, the engine modifies only the targeted tokens and values. Surrounding comments, line breaks, indentation levels, and custom formatting remain completely intact, producing clean, human-readable Git diffs.

---

## 4. The 3-Tier Verification Gate (`[PHY]`, `[KBS]`, `[SEM]`)

Before any remediation is written to disk, Yamlr evaluates the proposed changes against three independent verification gates:

```text
Proposed Remediation
        |
        v
 Tier 1: [PHY] Physical Syntax Layer
 (Validates raw indentation, list markers, quotes, and YAML structure)
        |
        +---> Passed
        v
 Tier 2: [KBS] Kubernetes Schema Layer
 (Validates against official OpenAPI schema for target version v1.21 - v1.37+)
        |
        +---> Passed
        v
 Tier 3: [SEM] Cross-Resource Semantic Layer
 (Validates relational graph consistency, selector contracts, and port mappings)
        |
        +---> Passed ---> Commit write atomically via Write-Ahead Log (WAL)
        v
      Failed
 (Transaction Aborted: File remains untouched, diagnostic error emitted)
```

If a proposed change fails **any** of these three layers, Yamlr aborts the transaction immediately. The target file is left untouched, and a diagnostic report is produced.

---

## 5. Operational Risk & Impact Classification

Yamlr classifies every issue by its operational blast radius in production clusters:

| Failure Domain | Impact Level | Diagnostic Examples | Production Outage Mechanism |
|:---|:---|:---|:---|
| **Traffic Blackholes** | `CRITICAL` | `NET-001`, `NET-002`, `NET-006` | Ingress routes to nonexistent ports; Service selectors mismatch workload labels; recursive DNS loops. |
| **Startup CrashLoops** | `CRITICAL` / `ERROR` | `SYN-001`, `RES-004`, `REL-006` | Malformed YAML syntax; memory unit typos (e.g. `500m` RAM); inverted resource limits. |
| **Scheduling Deadlocks** | `ERROR` | `REL-004`, `TOP-001`, `REL-005` | Unsatisfiable pod anti-affinity; restrictive topology skew constraints; PDB eviction blocks. |
| **Privilege Escalation** | `CRITICAL` / `ERROR` | `SEC-007`, `SEC-008`, `SEC-009` | Unrestricted root execution (UID 0); privilege escalation enabled; host namespace exposure. |
| **GitOps Sync Flapping** | `WARNING` | `GTO-001`, `GTO-002`, `GTO-003` | Missing controller defaults; un-sequenced CRD dependencies; cluster-applied metadata noise. |

---

## 6. Detection Linters vs. Resolution Planes

Understanding the difference between passive policy scanners and Yamlr's active resolution model:

| Capability | Traditional Linters & Policy Scanners | Yamlr Resolution Plane |
|:---|:---|:---|
| **Primary Output** | Warning reports, text logs, CI comments | Verified, production-ready manifest files |
| **Cross-Resource Topology** | Single-file inspection or requires live cluster query | Full offline directed graph analysis across multi-file sets |
| **AST Mutation** | None (read-only detection) | Deterministic Concrete Syntax Tree (CST) auto-healing |
| **Comment Preservation** | Not applicable (cannot safely write back) | 100% comment, layout, and whitespace preservation |
| **Transaction Safety** | Not applicable | Atomic Write-Ahead Log (WAL) with instant rollback |
| **Cryptographic Provenance** | External signing tools | Order-invariant semantic DNA hash verification |
| **Execution Performance** | 5s - 30s per run | Native compiled binary (< 25ms execution time) |
