# 🛡️ Yamlr Rule Catalog & Autonomous Healing Reference

**Version:** v0.1.4  
**Engine:** Standalone Rust Core (`native_core`) with OpenAPI v3 Embedded Validation  
**Core Directive:** Safe, zero-assumption, comment-preserving cross-resource auto-repair.

---

## 📐 Rule Categories & Classification

Yamlr rules are categorized into 10 deterministic domains:

| Prefix | Domain | Focus Area |
| :--- | :--- | :--- |
| `SYN-` | Syntactic & Lexical | Indentation, quote balance, colons, flow mappings, block scalars |
| `SEC-` | Pod Security & Identity | ServiceAccount deprecations, privileged flags, security contexts |
| `NET-` | Networking & Service Mesh | Port alignment, Ingress rules, AppProtocol, service discovery |
| `TOPO-` | Topology & Scheduling | NodeSelector GA labels, node affinity, tolerations |
| `ECO-` | Cloud-Native Ecosystem | Istio, Tekton, Knative, Cert-Manager, Argo CRD modernization |
| `SCHEMA-` | OpenAPI Schema Integrity | Enum casing (`protocol: TCP`), closed structs, type coercion |
| `REF-` | Cross-Resource References | ConfigMap/Secret data keys, PVC claims, Service selector matching |
| `ING-` | Ingress Specifications | `spec.ingressClassName` promotion, pathType validation |
| `STO-` | Storage & Volume Contracts | POSIX permission string unquoting, subPath leading slashes |
| `GTO-` | GitOps Hygiene | Pruning cluster-dump artifacts (`status:`, `resourceVersion`, `uid`) |

---

## 🌟 Tier 0: Core Production Healing Rules

### 1. `TOPO-001`: Modernize Legacy NodeSelector Topology Labels
- **Category:** Topology & Scheduling (`TOPO`)
- **Trigger:** `nodeSelector` or `nodeAffinity` using `beta.kubernetes.io/os` or `beta.kubernetes.io/arch`.
- **Why:** `beta.kubernetes.io/os` was deprecated in Kubernetes v1.14 and replaced by `kubernetes.io/os`. Modern nodes (v1.18+) label nodes with GA keys; legacy labels cause scheduling deadlocks on new nodepools.
- **Safety Gate:** Replaces only known deprecated topology keys; never mutates custom user labels.
- **Example:**
  ```yaml
  # Before:
  nodeSelector:
    beta.kubernetes.io/os: linux
  # After:
  nodeSelector:
    kubernetes.io/os: linux
  ```

---

### 2. `SEC-011`: Modernize Deprecated ServiceAccount Reference
- **Category:** Pod Security & Identity (`SEC`)
- **Trigger:** Pod template spec declaring `serviceAccount: <name>`.
- **Why:** In Kubernetes `PodSpec`, `serviceAccount` was deprecated in v1.0 in favor of `serviceAccountName`.
- **Safety Gate:** Rewrites field key to `serviceAccountName` while preserving exact value and surrounding indentation. If `serviceAccountName` already exists with the same value, removes redundant `serviceAccount`.
- **Example:**
  ```yaml
  # Before:
  spec:
    serviceAccount: runner-sa
  # After:
  spec:
    serviceAccountName: runner-sa
  ```

---

### 3. `ECO-001`: Istio Modernization (`networking.istio.io/v1alpha3` -> `v1`)
- **Category:** Cloud-Native Ecosystem (`ECO`)
- **Trigger:** Istio `Gateway`, `VirtualService`, `ServiceEntry`, or `DestinationRule` using `v1alpha3`.
- **Why:** Istio promoted traffic management APIs to GA in `networking.istio.io/v1`. Older alpha versions trigger deprecation warnings and API rejections in Istio 1.20+.
- **Safety Gate:** Upgrades API version cleanly without modifying routing rules or TLS configurations.
- **Example:**
  ```yaml
  # Before:
  apiVersion: networking.istio.io/v1alpha3
  kind: Gateway
  # After:
  apiVersion: networking.istio.io/v1
  kind: Gateway
  ```

---

### 4. `ECO-003`: Tekton Pipeline Task Modernization (`tekton.dev/v1beta1` -> `v1`)
- **Category:** Cloud-Native Ecosystem (`ECO`)
- **Trigger:** Tekton `Task` or `Pipeline` declared under `tekton.dev/v1beta1`.
- **Why:** Tekton removed `v1beta1` in v0.50+. In `tekton.dev/v1`, Task parameters require explicit `type: string` declarations.
- **Safety Gate:** Upgrades apiVersion and injects `type: string` only under parameters lacking an explicit type.
- **Example:**
  ```yaml
  # Before:
  apiVersion: tekton.dev/v1beta1
  kind: Task
  spec:
    params:
      - name: source
  # After:
  apiVersion: tekton.dev/v1
  kind: Task
  spec:
    params:
      - name: source
        type: string
  ```

---

### 5. `SCHEMA-003`: Container Port Protocol Enum Casing
- **Category:** OpenAPI Schema Integrity (`SCHEMA`)
- **Trigger:** Container port `protocol: tcp` or `protocol: udp` in lowercase.
- **Why:** Kubernetes OpenAPI enum validation strictly requires uppercase (`TCP`, `UDP`, `SCTP`).
- **Safety Gate:** Coerces lowercase ASCII string to canonical uppercase enum.
- **Example:**
  ```yaml
  # Before:
  ports:
    - containerPort: 8080
      protocol: tcp
  # After:
  ports:
    - containerPort: 8080
      protocol: TCP
  ```

---

### 6. `ING-002`: Promote Ingress Class Annotation to Spec Field
- **Category:** Ingress Specifications (`ING`)
- **Trigger:** Ingress resource using `metadata.annotations['kubernetes.io/ingress.class']`.
- **Why:** Kubernetes v1.18 deprecated the ingress class annotation in favor of the formal `spec.ingressClassName` field (GA in v1.19).
- **Safety Gate:** Injects `spec.ingressClassName` and removes the deprecated annotation only if `spec.ingressClassName` was not already set.
- **Example:**
  ```yaml
  # Before:
  metadata:
    annotations:
      kubernetes.io/ingress.class: nginx
  # After:
  spec:
    ingressClassName: nginx
  ```

---

### 7. `REF-006`: ConfigMap & Secret Key Reference Alignment
- **Category:** Cross-Resource References (`REF`)
- **Trigger:** Pod volume mount or `env[].valueFrom.configMapKeyRef.key` references a key that has a typo compared to the target ConfigMap `data:` keys in the workspace graph.
- **Why:** Typoed config keys cause pods to fail startup with `CreateContainerConfigError`.
- **Safety Gate:** Fuzzy matching requires similarity >= 0.85; skips optional references (`optional: true`) and template expressions (`{{ ... }}`).

---

### 8. `NET-020`: Ingress-to-Service Port Alignment
- **Category:** Networking & Service Mesh (`NET`)
- **Trigger:** Ingress backend port points to a named port with a minor typo compared to the Service port name in the workspace graph.
- **Why:** Mismatched backend port names cause Ingress controllers to route traffic to dead blackholes (503 Service Unavailable).
- **Safety Gate:** Strictly ZERO numeric port rewrites. Typo alignment applies only to named ports with similarity >= 0.75.

---

### 9. `STO-008`: POSIX Octal Permission Quoting Sanitization
- **Category:** Storage & Volume Contracts (`STO`)
- **Trigger:** `defaultMode` or `items[].mode` specified as a quoted string (`"0755"`, `"644"`).
- **Why:** Kubernetes OpenAPI schema expects integer scalars; quoted strings trigger schema validation failure (`expected integer, got string`).
- **Safety Gate:** Only mutates quoted strings that violate OpenAPI integer validation. Preserves unquoted octal literals (`0555`, `0755`) to maintain human POSIX readability.

---

### 10. `PRO-001`: Kubernetes RBAC v1beta1 API Migration
- **Category:** Core Modernization (`PRO`)
- **Trigger:** `ClusterRole`, `ClusterRoleBinding`, `Role`, or `RoleBinding` using `rbac.authorization.k8s.io/v1beta1`.
- **Why:** RBAC `v1beta1` was removed in Kubernetes v1.22+. Deploying on modern clusters yields hard admission rejections.
- **Safety Gate:** Modernizes apiVersion to `rbac.authorization.k8s.io/v1`.
