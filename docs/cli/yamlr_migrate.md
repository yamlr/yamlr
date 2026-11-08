# yamlr migrate

**Standalone Kubernetes API Migration Engine**

The `migrate` command performs safe, surgical modernization of deprecated and retired Kubernetes API versions (such as `extensions/v1beta1`, `networking.k8s.io/v1beta1`, `policy/v1beta1`, `autoscaling/v2beta1`, `batch/v1beta1`) across single files or large repository directory trees.

Unlike full healing, `migrate` enforces a strict **zero-side-effect mandate**: it *only* upgrades deprecated API versions and required companion schema shifts (such as Ingress `pathType: Prefix` and Deployment `spec.selector.matchLabels` synthesis), strictly refusing to inject unrequested resource limits, probes, or security contexts.

---

## Usage

```bash
# Preview proposed API migrations in colored unified diff (default safe preview)
yamlr migrate ./k8s --to 1.30 --diff

# Apply migrations in-place across manifests
yamlr migrate ./k8s --to 1.30 --apply

# Apply migrations in CI without generating .bak backup files
yamlr migrate ./k8s --to 1.30 --apply --no-backup

# Process multi-document streams and preserve document boundaries (---)
yamlr migrate ./manifests/bundle.yaml --to 1.32 --diff
```

---

## Options

| Flag | Short | Description |
|:---|:---:|:---|
| `[PATH]` | | Manifest file or directory tree to migrate (defaults to `.`). |
| `--to <VERSION>` | | Target Kubernetes version for modern APIs (e.g. `1.30`, `1.35`). |
| `--k8s-version <V>` | | Alias for `--to`. |
| `--apply` | `-a` | Apply migrations in-place to disk with pre-write safety verification. |
| `--diff` | `-d` | Display colored unified diff showing exact proposed line changes. |
| `--dry-run` | | Preview proposed migrations without writing to disk (default). |
| `--no-backup` | | Disable creation of `.bak` safety backup files (recommended in CI/CD). |
| `--quiet` | `-q` | Suppress banners and progress; print only migrated file records. |

---

## Supported API Migrations

The engine contains an authoritative catalog of Kubernetes API removals and migrations across Kubernetes releases:

| Kind | Deprecated API | Modern Replacement API | Removed In | Companion Schema Shifts |
|:---|:---|:---|:---:|:---|
| `Deployment`, `DaemonSet`, `ReplicaSet`, `StatefulSet` | `extensions/v1beta1`, `apps/v1beta1`, `apps/v1beta2` | `apps/v1` | v1.16 | Synthesizes `spec.selector.matchLabels` from template labels when missing |
| `NetworkPolicy` | `extensions/v1beta1` | `networking.k8s.io/v1` | v1.16 | In-place version upgrade |
| `Ingress` | `extensions/v1beta1`, `networking.k8s.io/v1beta1` | `networking.k8s.io/v1` | v1.22 | Migrates `serviceName`/`servicePort` to `service.name`/`service.port`, `spec.backend` to `defaultBackend`, and injects required `pathType: Prefix` |
| `CustomResourceDefinition` | `apiextensions.k8s.io/v1beta1` | `apiextensions.k8s.io/v1` | v1.22 | Structural schema conformance |
| `ValidatingWebhookConfiguration`, `MutatingWebhookConfiguration` | `admissionregistration.k8s.io/v1beta1` | `admissionregistration.k8s.io/v1` | v1.22 | In-place version upgrade |
| `Role`, `ClusterRole`, `RoleBinding`, `ClusterRoleBinding` | `rbac.authorization.k8s.io/v1beta1` | `rbac.authorization.k8s.io/v1` | v1.22 | In-place version upgrade |
| `CertificateSigningRequest` | `certificates.k8s.io/v1beta1` | `certificates.k8s.io/v1` | v1.22 | Validates signerName |
| `CSINode`, `StorageClass`, `VolumeAttachment` | `storage.k8s.io/v1beta1` | `storage.k8s.io/v1` | v1.24 | In-place version upgrade |
| `CronJob` | `batch/v1beta1`, `batch/v2alpha1` | `batch/v1` | v1.25 | In-place version upgrade |
| `EndpointSlice` | `discovery.k8s.io/v1beta1` | `discovery.k8s.io/v1` | v1.25 | In-place version upgrade |
| `HorizontalPodAutoscaler` | `autoscaling/v2beta1`, `autoscaling/v2beta2` | `autoscaling/v2` | v1.25/1.26 | In-place version upgrade |
| `FlowSchema`, `PriorityLevelConfiguration` | `flowcontrol.apiserver.k8s.io/v1beta1`, `v1beta2`, `v1beta3` | `flowcontrol.apiserver.k8s.io/v1` | v1.29/1.32 | In-place version upgrade |
| `PodSecurityPolicy` | `policy/v1beta1` | *Removed in v1.25* | v1.25 | Emits advisory [PRO-001] guiding PSA migration without blind mutation |

---

## Safety Guarantees & Contract

1. **Surgical API Upgrades Only:** Only retired and deprecated Kubernetes API groups are upgraded to their stable successors (`apps/v1`, `networking.k8s.io/v1`, `batch/v1`).
2. **Zero Unsolicited Mutation:** No automated probe injection, container limits alteration, or label mutator runs during `migrate`.
3. **Multi-Document & CRLF Preservation:** Multi-document YAML streams separated by `---` are migrated document-by-document, preserving document boundaries, comments, and Windows (`\r\n`) or Unix (`\n`) line endings.
4. **Pre-Write Verification Gates:** Every migrated manifest must pass syntax validation, comment invariance, non-empty AST check, and OpenAPI schema verification before disk mutation.

---

## Backup & Version Control Best Practices

- **Explicit `.bak` Safety Suffix:** When `--apply` runs without `--no-backup`, yamlr creates a safety snapshot named `<filename>.bak` (for example, `deploy.yaml.bak`, never `deploy.bak.yaml`). This intentional suffix naming ensures directory-level Kubernetes tools (e.g., `kubectl apply -f .`) will not parse or deploy the backup copy.
- **Recommended `.gitignore`:** Add `*.bak` to your project's `.gitignore` to prevent accidentally committing local backup snapshots.
- **CI/CD & GitOps Workflows:** In continuous integration and automated GitOps pipelines where full version history is maintained in Git, pass `--no-backup` to keep workspaces clean without generating snapshot files.
