# Diagnostic Code & Detector Catalog

Yamlr operates an institutional-grade forensic analysis engine powered by native Rust CST pattern matchers. The engine continuously evaluates manifests across physical syntax, Kubernetes OpenAPI schemas, relational topology, and CIS security benchmarks.

Every finding emitted by `yamlr scan`, `yamlr check`, and `yamlr heal` maps to a canonical diagnostic code. This catalog is the complete, 100% code-verified specification of all active detectors, deprecation tables, CIS benchmark mappings, and autonomous remediation behaviors.

---

## Table of Contents

1. [Diagnostic Code Schema & Severity Levels](#diagnostic-code-schema--severity-levels)
2. [Physical Syntax & CST Invariants (`SYN`, `TYP`)](#physical-syntax--cst-invariants-syn-typ)
3. [Relational Topology & Networking (`NET`, `TOP`)](#relational-topology--networking-net-top)
4. [Workload Reliability & Autoscaling (`REL`, `RES`, `AUT`)](#workload-reliability--autoscaling-rel-res-aut)
5. [Pod Security & CIS Benchmarks (`SEC`, `BST`)](#pod-security--cis-benchmarks-sec-bst)
6. [GitOps & Controller Synchronization (`GTO`, `OPS`)](#gitops--controller-synchronization-gto-ops)
7. [Storage & Volume Contracts (`STO`, `VOL`)](#storage--volume-contracts-sto-vol)
8. [Governance, Hygiene & RBAC (`GOV`, `HYG`)](#governance-hygiene--rbac-gov-hyg)
9. [Kubernetes API Deprecation & Removal Matrix (`DEP`)](#kubernetes-api-deprecation--removal-matrix-dep)

---

## Diagnostic Code Schema & Severity Levels

Yamlr diagnostic codes follow a standardized, predictable alphanumeric taxonomy:
`[CATEGORY]-[NUMBER]`.

### Severity Classifications

| Severity | CLI Rendering | CI Gating Default | Operational Meaning |
|:---|:---|:---|:---|
| **`CRITICAL`** | `[CRITICAL]` Red | Fails build (`exit 1`) | **Immediate Outage Hazard**: Guaranteed cluster rejection, routing blackhole, recursive DNS loop, or severe privilege escalation. |
| **`ERROR`** | `[ERROR]` Orange/Red | Fails build (`exit 1`) | **Schema or Specification Violation**: Mismatched types, required fields missing, deadlocked affinity, or invalid cross-resource binding. |
| **`WARNING`** | `[WARN]` Yellow | Warning (`exit 0` unless `--fail-on warning`) | **Reliability / Operational Anti-Pattern**: Non-deterministic sync flapping, missing resource boundaries, floating tags, or soft deprecation. |
| **`INFO`** | `[INFO]` Blue | Non-blocking | **Hygiene & Optimization**: Dangling unreferenced objects, orphaned ServiceAccounts, or style deviations. |

---

## Physical Syntax & CST Invariants (`SYN`, `TYP`)

These rules audit the raw YAML structure, indentation boundaries, and data types before or during Concrete Syntax Tree (CST) normalization.

| Code | Name | Severity | Remediation Behavior (`yamlr heal --apply`) |
|:---|:---|:---|:---|
| **`SYN-001`** | Malformed Key-Value Syntax & Missing Colons | `ERROR` | Reconstructs missing colon delimiters and realigns indentation to canonical 2-space Kubernetes YAML hierarchy. |
| **`SYN-008`** | Dangling Empty Sequence | `WARNING` | Prunes dangling null arrays or orphaned sequence markers left behind by commented-out blocks. |
| **`SYN-009`** | Map vs. Array Schema Mismatch | `ERROR` | Lifts and converts invalid maps into valid list-of-maps (e.g., converting `env: { KEY: "VAL" }` into canonical `env: [{ name: "KEY", value: "VAL" }]`). |
| **`SYN-015`** | Block Scalar Indentation Trap | `ERROR` | Fixes improper indentation in literal (`\|`) and folded (`>`) multiline block scalar payloads without corrupting whitespace. |
| **`SYN-016`** | Orphaned Indented Block | `ERROR` | Re-aligns orphaned child lines whose parent keys were removed or improperly indented. |
| **`SYN-017`** | Over-Indented Sequence Item | `WARNING` | Normalizes irregular 4-space or 6-space list items back to Kubernetes standard 2-space sequence indentation. |
| **`SYN-018`** | Malformed Anchor Declaration | `ERROR` | Repairs illegal standalone YAML anchors (`&anchor`) missing associated node targets. |
| **`SYN-019`** | Empty Flow Map with Indented Children | `ERROR` | Resolves syntax traps where `{}` is followed by unexpectedly indented child keys. |
| **`TYP-002`** | Quoted Integer Normalization | `WARNING` | Strips quotes from strict integer schema properties (e.g., `containerPort: "8080"` -> `containerPort: 8080`). |
| **`TYP-003`** | Scientific Notation Float Hazard | `ERROR` | Converts scientific float exponents (e.g., `1e3`) into standard integers or string scalars to prevent Kubernetes API parser panics. |
| **`TYP-004`** | NodeSelector Sequence Misrepresentation | `ERROR` | Flattens invalid sequence list syntax under `nodeSelector` into a canonical key-value map. |

---

## Relational Topology & Networking (`NET`, `TOP`)

These rules audit cross-resource networking contracts, selector relationships, and traffic routing consistency between `Service`, `Ingress`, `Gateway`, and `Deployment` manifests.

| Code | Name | Severity | CIS / Standard | Remediation Behavior |
|:---|:---|:---|:---|:---|
| **`NET-001`** | Invisible Outage (Port Mismatch) | `CRITICAL` | CIS-5.3.1 | Synchronizes `targetPort` on the `Service` with the actual `containerPort` declared in matching Pod manifests. |
| **`NET-002`** | Orphaned Backend / Ingress Mismatch | `CRITICAL` | Kubernetes API | Detects Ingress routing rules pointing to non-existent Services or unregistered ports. |
| **`NET-003`** | Localhost Traffic Trap | `ERROR` | Best Practice | Detects container configurations binding services to `127.0.0.1` inside pods, preventing inter-pod communication. |
| **`NET-004`** | Service Shadowing / Collision | `WARNING` | CIS-5.7.1 | Flags multiple Services in the same namespace declaring identical label selectors, which causes unintended split-brain traffic distribution. |
| **`NET-005`** | Shadowing Endpoint Overwrite | `ERROR` | Kubernetes API | Flags manually configured `Endpoints` resources whose parent `Service` declares a selector (which triggers the kube-controller to overwrite them). |
| **`NET-006`** | Circular Service Ref / ExternalName Loop | `CRITICAL` | CoreDNS Resiliency | Identifies recursive DNS aliases in `ExternalName` services that can saturate cluster CoreDNS resolvers and cause cluster-wide outages. |
| **`NET-007`** | Protocol Contract Mismatch | `ERROR` | Kubernetes 1.20+ | Automatically injects `appProtocol: grpc` or `appProtocol: http` and required Ingress annotations for modern microservice protocols. |
| **`NET-008`** | Ingress Path Shadowing Blackhole | `ERROR` | Ingress Specs | Flags broad catch-all prefix paths (e.g., `/`) declared before specific sub-paths (e.g., `/api/v1`), causing routing blackholes. |
| **`NET-009`** | Dual-Stack IPv6 Service CIDR Clash | `WARNING` | Dual-Stack Networking | Reconciles missing `ipFamilyPolicy` (defaults to `PreferDualStack` or `RequireDualStack`) to prevent silent IPv6 traffic blackholes. |
| **`NET-010`** | HostPort Anti-Affinity Collision | `ERROR` | Node Port Allocation | Injects required `podAntiAffinity` when `hostPort` is used to prevent scheduling multiple instances onto the same physical node. |
| **`NET-012`** | Headless Service ClusterIP Misconfiguration | `ERROR` | Headless Specs | Enforces `clusterIP: None` when Service type is designed for stateful direct-pod DNS addressing. |
| **`NET-013`** | SessionAffinity Timeout Hazard | `WARNING` | Service Contracts | Reconciles `ClientIP` session affinity missing `sessionAffinityConfig.clientIP.timeoutSeconds`. |
| **`NET-016`** | PublishNotReadyAddresses Invariant | `WARNING` | Service Contracts | Reconciles `publishNotReadyAddresses` on headless StatefulSet services for DNS endpoint discovery. |
| **`NET-021`** | Cross-Zone Topology Routing Omission | `LOW` | Cost & Latency | Audits Services for `service.kubernetes.io/topology-mode: auto` to prevent cross-zone cloud data transfer costs. |
| **`TOP-001`** | Topology Spread Deadlock | `ERROR` | Scheduling Specs | Detects `maxSkew: 1` combined with strict `whenUnsatisfiable: DoNotSchedule` on small clusters (e.g., 2 nodes), which halts deployments. |

---

## Workload Reliability & Autoscaling (`REL`, `RES`, `AUT`)

These rules prevent silent crash loops, resource exhaustion, and competing controller autoscaling loops.

| Code | Name | Severity | Remediation Behavior |
|:---|:---|:---|:---|
| **`REL-001`** | Webhook Brownout Risk | `WARNING` | Flags Admission Webhooks with missing `timeoutSeconds` or `failurePolicy: Fail` on control-plane paths. |
| **`REL-002`** | Webhook Target Collision | `ERROR` | Flags multiple mutating or validating webhooks intercepting the identical API path with conflicting mutation orders. |
| **`REL-003`** | Scaling War (Replicas vs HPA) | `ERROR` | Prunes static `spec.replicas` in Deployments/StatefulSets when an active `HorizontalPodAutoscaler` is targeting the resource. |
| **`REL-004`** | Anti-Affinity Hard Deadlock | `ERROR` | Converts unsatisfiable `requiredDuringSchedulingIgnoredDuringExecution` anti-affinity into `preferredDuringScheduling`. |
| **`REL-005`** | PDB Eviction Overlap Deadlock | `WARNING` | Flags overlapping `PodDisruptionBudget` resources selecting the same pods, which prevents node drain operations. |
| **`REL-006`** | Inverted Resource Limits | `ERROR` | Reconciles inverted configurations where container `requests` exceed `limits`. |
| **`REL-007`** | Aggressive Liveness Probe | `WARNING` | Adjusts `initialDelaySeconds` and `failureThreshold` to prevent early CrashLoopBackOff before heavy JVM/Node runtimes finish initialization. |
| **`REL-008`** | Sidecar Draining Race Condition | `WARNING` | Injects preStop sleep hooks into proxy sidecars (e.g., Envoy/Istio) so they outlive terminating application containers. |
| **`REL-009`** | Termination Grace Period Mismatch | `WARNING` | Aligns `terminationGracePeriodSeconds` with internal application shutdown timeouts. |
| **`REL-010`** | Proportional Resource Hazard | `WARNING` | Flags high CPU limits paired with disproportionately low memory limits, which leads to Burst OOM terminations. |
| **`REL-011`** | Single-Zone HA Fake-Out | `WARNING` | Injects `topologySpreadConstraints` across `topology.kubernetes.io/zone` to prevent simultaneous failure during cloud zone outages. |
| **`RES-003`** | BestEffort QoS Eviction Hazard | `WARNING` | Injects baseline resource requests/limits to lift critical pods out of low-priority BestEffort QoS eviction status. |
| **`RES-004`** | Fatal Millibyte / Memory Unit Typo | `ERROR` | Sanitizes invalid memory units like `500m` (millibytes) or `500mb` into canonical Kubernetes units (`500Mi`). |
| **`AUT-002`** | HPA vs VPA Metric Contention | `ERROR` | Detects simultaneous HPA and VPA controllers scaling on the same metric (e.g., CPU/Memory), which causes destabilizing thrashing loops. |
| **`PRB-007`** | Probe Cascade Restart Hazard | `HIGH` | Audits identical endpoint paths shared between liveness and readiness probes, risking cascading restart storms. |
| **`REL-014`** | LivenessProbe CrashLoop Safeguard | `WARNING` | Adjusts `initialDelaySeconds` on liveness probes to prevent early pod restart loops during container startup. |
| **`REL-015`** | Graceful Drain PreStop Hook Omission | `MEDIUM` | Audits or injects safe `preStop: sleep` hooks to eliminate HTTP 502/504 errors during rolling updates under `yamlr.dev/drain-hook`. |

---

## Pod Security & CIS Benchmarks (`SEC`, `BST`)

Yamlr enforces the official **CIS Kubernetes Benchmark v1.8.0** and **Kubernetes Pod Security Standards (Restricted Profile)**.

| Code | Name | Severity | CIS Citation | Remediation Behavior (`yamlr heal --apply`) |
|:---|:---|:---|:---|:---|
| **`SEC-001`** | Identity Context Gap | `WARNING` | **CIS-5.7.3** | Synthesizes a non-root `securityContext` (`runAsNonRoot: true`, `runAsUser: 10001`). |
| **`SEC-002`** | Mutable Pull-Safe Hazard | `ERROR` | **CIS-5.2.2** | Enforces `imagePullPolicy: Always` for `:latest` tags or pins images by immutable SHA-256 digest. |
| **`SEC-003`** | Default Namespace Pollution | `WARNING` | **CIS-5.4.1** | Flags resources deployed without an explicit `metadata.namespace` (which dumps workloads in `default`). |
| **`SEC-004`** | RBAC Subject Escalation Conflict | `ERROR` | CIS-5.1.1 | Audits `RoleBinding` / `ClusterRoleBinding` subjects for unintended cross-namespace privilege escalation. |
| **`SEC-005`** | Redundant Role Collision | `WARNING` | RBAC Hygiene | Identifies duplicate Roles defining identical verbs/resources in the same namespace. |
| **`SEC-006`** | Unencoded Secret Data | `ERROR` | **CIS-5.1.1** | Moves unencoded plaintext string values from `data` into `stringData` (or base64-encodes them). |
| **`SEC-007`** | Privilege Escalation Enabled | `ERROR` | **CIS-5.1.4** | Sets `allowPrivilegeEscalation: false` across all container security contexts. |
| **`SEC-008`** | Root Execution Hazard | `ERROR` | **CIS-5.1.2** | Sets `runAsNonRoot: true` and defines a deterministic non-zero UID. |
| **`SEC-009`** | Host Network Namespace Exposure | `CRITICAL` | **CIS-5.1.3** | Enforces `hostNetwork: false` to isolate pod network traffic from the underlying host node. |
| **`SEC-010`** | Host Path Filesystem Exposure | `CRITICAL` | **CIS-5.1.5** | Flags or restricts `hostPath` mounts, recommending persistent volumes or emptyDir. |
| **`SEC-011`** | Host PID / IPC Exposure | `CRITICAL` | **CIS-5.1.6** | Sets `hostPID: false` and `hostIPC: false` to prevent container-to-host process inspection. |
| **`SEC-012`** | Writable Root Filesystem | `INFO` | **CIS-5.2.5** | Configures `readOnlyRootFilesystem: true` and automatically synthesizes `/tmp` `emptyDir` scratch volumes. |
| **`SEC-014`** | Missing Default-Deny NetworkPolicy Baseline | `WARNING` | **CIS-5.3.2** | Identifies unprotected namespaces and generates default-deny NetworkPolicy baselines. |
| **`SEC-016`** | Sensitive Plaintext in ConfigMap | `CRITICAL` | Secret Safety | Scans ConfigMaps for private keys, AWS tokens, database passwords, and API credentials. |
| **`SEC-017`** | ServiceAccount Token Auto-Mount | `INFO` | **CIS-5.1.5** | Sets `automountServiceAccountToken: false` on pods that do not interact with the Kubernetes API. |
| **`BST-005`** | Sensitive Linux Capabilities Added | `WARNING` | CIS-5.2.7 | Drops dangerous capabilities (`SYS_ADMIN`, `NET_ADMIN`) and sets `capabilities.drop: [ALL]`. |

---

## GitOps & Controller Synchronization (`GTO`, `OPS`)

These rules ensure manifests sync cleanly through GitOps controllers (ArgoCD, FluxCD) without perpetual diff loops or race conditions.

| Code | Name | Severity | Remediation Behavior |
|:---|:---|:---|:---|
| **`GTO-001`** | Controller Default Drift Flapping | `WARNING` | Harmonizes omitted fields that Kubernetes controllers inject by default (e.g., default probes, service ports) to stop sync loops. |
| **`GTO-002`** | Unordered CRD Sync-Wave Hazard | `ERROR` | Stamps ArgoCD / Flux sync-waves so foundational resources (CRDs, Namespaces) apply before CustomResources. |
| **`GTO-003`** | Live Cluster Export Artifact Clutter | `WARNING` | Purges server-assigned metadata (`resourceVersion`, `uid`, `creationTimestamp`, and `status: {}` blocks) from manifests exported via `kubectl get -o yaml`. |
| **`OPS-001`** | Immutable Field Mutation Drift | `ERROR` | Flags attempted modifications to immutable Kubernetes fields (such as `spec.selector` on Deployments) that cause deployment failures. |
| **`OPS-002`** | Floating Image Tag Hazard | `WARNING` | Warns against non-deterministic tags like `:v1`, `:master`, or `:staging` that prevent reproducible rollbacks. |
| **`OPS-003`** | Volume Mount Path Collision | `ERROR` | Detects multiple `volumeMounts` targeting the exact same `mountPath`, which hides underlying data. |

---

## Storage & Volume Contracts (`STO`, `VOL`)

| Code | Name | Severity | Description & Remediation |
|:---|:---|:---|:---|
| **`STO-001`** | Orphaned StorageClass | `INFO` | Identifies `StorageClass` definitions not referenced by any active PersistentVolumeClaims. |
| **`STO-002`** | Dangling PersistentVolume | `WARNING` | Flags `PersistentVolume` resources with no matching `PersistentVolumeClaim`. |
| **`STO-003`** | StatefulSet Volume Claim Immutability Crash | `ERROR` | Detects mutations to `volumeClaimTemplates` in existing StatefulSets that trigger fatal admission rejections. |
| **`VOL-001`** | Volume Contract & Medium Normalization | `WARNING` | Normalizes invalid `emptyDir.medium` specifications and validates storage claim access modes. |
| **`STO-006`** | RWX Volume Attachment Conflict | `ERROR` | Flags EBS/GCP persistent disks configured with ReadWriteMany (RWX), preventing volume attachment deadlocks. |
| **`STO-007`** | Illegal Leading Slash in Volume SubPath | `WARNING` | Sanitizes illegal leading slashes in `volumeMounts[].subPath` that cause container creation failure. |
| **`STO-008`** | POSIX Octal Mode Sanitizer | `WARNING` | Normalizes invalid POSIX octal file permission modes in `defaultMode` and `items[].mode`. |
| **`STO-009`** | Unbounded EmptyDir Node Pressure Hazard | `MEDIUM` | Audits or injects `sizeLimit: 1Gi` on `emptyDir` volumes to protect host root filesystem from disk pressure evictions under `yamlr.dev/safe-storage`. |

---

## Governance, Hygiene & RBAC (`GOV`, `HYG`)

| Code | Name | Severity | Description & Remediation |
|:---|:---|:---|:---|
| **`GOV-001`** | Reserved Label Pollution | `WARNING` | Flags custom user metadata attempting to declare `kubernetes.io/` or `k8s.io/` prefix labels. |
| **`GOV-002`** | PriorityClass Value Collision | `WARNING` | Detects multiple `PriorityClass` definitions with identical integer values, causing non-deterministic scheduling. |
| **`GOV-003`** | Cluster-Scope Resource Leak | `ERROR` | Prevents namespace-scoped resources from being mistakenly referenced inside cluster-scoped RBAC bindings. |
| **`HYG-001`** | Dangling CustomResourceDefinition | `INFO` | Flags CRDs that have zero deployed CustomResource instances in the workspace. |
| **`HYG-002`** | Dangling Identity / ServiceAccount | `INFO` | Flags `ServiceAccount` resources that are never mounted or referenced by workloads. |

---

## Kubernetes API Deprecation & Removal Matrix (`DEP`)

Yamlr maintains an authoritative embedded catalog of Kubernetes API removals and modernizations (`catalog/k8s_deprecations.json`) spanning Kubernetes v1.16 through v1.35+. During `yamlr heal` and `yamlr migrate`, deprecated APIs are safely and surgically upgraded to their stable GA replacements.

| Kind | Deprecated API | Modern Replacement API | Removed in K8s | Auto-Healing & Migration Strategy |
|:---|:---|:---|:---:|:---|
| **`Deployment`** | `extensions/v1beta1`, `apps/v1beta1`, `apps/v1beta2` | `apps/v1` | **v1.16** | Upgrades `apiVersion` and synthesizes required `spec.selector.matchLabels` preserving template hierarchy. |
| **`DaemonSet`** | `extensions/v1beta1`, `apps/v1beta1`, `apps/v1beta2` | `apps/v1` | **v1.16** | Upgrades `apiVersion` and synthesizes required `spec.selector.matchLabels`. |
| **`ReplicaSet`** | `extensions/v1beta1`, `apps/v1beta1`, `apps/v1beta2` | `apps/v1` | **v1.16** | Upgrades `apiVersion` and synthesizes required `spec.selector.matchLabels`. |
| **`StatefulSet`** | `apps/v1beta1`, `apps/v1beta2` | `apps/v1` | **v1.16** | Upgrades `apiVersion` and synthesizes required `spec.selector.matchLabels`. |
| **`NetworkPolicy`** | `extensions/v1beta1` | `networking.k8s.io/v1` | **v1.16** | Direct in-place `apiVersion` upgrade. |
| **`Ingress`** | `extensions/v1beta1`, `networking.k8s.io/v1beta1` | `networking.k8s.io/v1` | **v1.22** | Upgrades API, converts backends to `service.name` / `service.port`, and injects required `pathType: Prefix`. |
| **`CustomResourceDefinition`** | `apiextensions.k8s.io/v1beta1` | `apiextensions.k8s.io/v1` | **v1.22** | Upgrades API and validates structural OpenAPI v3 schemas. |
| **`ValidatingWebhookConfiguration`** | `admissionregistration.k8s.io/v1beta1` | `admissionregistration.k8s.io/v1` | **v1.22** | Upgrades API and verifies `sideEffects` declaration. |
| **`MutatingWebhookConfiguration`** | `admissionregistration.k8s.io/v1beta1` | `admissionregistration.k8s.io/v1` | **v1.22** | Upgrades API and verifies `sideEffects` declaration. |
| **`Role`, `ClusterRole`** | `rbac.authorization.k8s.io/v1beta1` | `rbac.authorization.k8s.io/v1` | **v1.22** | Direct in-place `apiVersion` upgrade. |
| **`RoleBinding`, `ClusterRoleBinding`** | `rbac.authorization.k8s.io/v1beta1` | `rbac.authorization.k8s.io/v1` | **v1.22** | Direct in-place `apiVersion` upgrade. |
| **`CertificateSigningRequest`** | `certificates.k8s.io/v1beta1` | `certificates.k8s.io/v1` | **v1.22** | Upgrades API and verifies `signerName`. |
| **`CSINode`** | `storage.k8s.io/v1beta1` | `storage.k8s.io/v1` | **v1.24** | Direct in-place `apiVersion` upgrade. |
| **`StorageClass`** | `storage.k8s.io/v1beta1` | `storage.k8s.io/v1` | **v1.24** | Direct in-place `apiVersion` upgrade. |
| **`VolumeAttachment`** | `storage.k8s.io/v1beta1` | `storage.k8s.io/v1` | **v1.24** | Direct in-place `apiVersion` upgrade. |
| **`PodSecurityPolicy`** | `policy/v1beta1` | *Removed in v1.25* | **v1.25** | Emits advisory [PRO-001] guiding migration to Pod Security Admission (PSA) without blind mutation. |
| **`PodDisruptionBudget`** | `policy/v1beta1` | `policy/v1` | **v1.25** | Direct in-place `apiVersion` upgrade. |
| **`RuntimeClass`** | `node.k8s.io/v1beta1` | `node.k8s.io/v1` | **v1.25** | Direct in-place `apiVersion` upgrade. |
| **`CronJob`** | `batch/v1beta1`, `batch/v2alpha1` | `batch/v1` | **v1.25** | Upgrades API and normalizes concurrency policy. |
| **`EndpointSlice`** | `discovery.k8s.io/v1beta1` | `discovery.k8s.io/v1` | **v1.25** | Upgrades API and verifies address type declarations. |
| **`HorizontalPodAutoscaler`** | `autoscaling/v2beta1`, `autoscaling/v2beta2` | `autoscaling/v2` | **v1.25/v1.26** | Upgrades API and normalizes metric spec definitions. |
| **`CSIStorageCapacity`** | `storage.k8s.io/v1beta1` | `storage.k8s.io/v1` | **v1.27** | Direct in-place `apiVersion` upgrade. |
| **`FlowSchema`** | `flowcontrol.apiserver.k8s.io/v1beta1`, `v1beta2`, `v1beta3` | `flowcontrol.apiserver.k8s.io/v1` | **v1.29/v1.32** | Upgrades API to GA schema. |
| **`PriorityLevelConfiguration`** | `flowcontrol.apiserver.k8s.io/v1beta1`, `v1beta2`, `v1beta3` | `flowcontrol.apiserver.k8s.io/v1` | **v1.29/v1.32** | Direct in-place GA upgrade. |
