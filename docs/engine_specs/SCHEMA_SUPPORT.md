# Kubernetes Schema Support Matrix

Yamlr validates manifests against official Kubernetes OpenAPI v3 specifications.
This document tracks which versions are supported and tested.

## Supported Versions

| K8s Version | OpenAPI Spec | Test Status | Notes |
| :--- | :--- | :--- | :--- |
| 1.21 | v3 | ✅ Tested | Minimum supported version |
| 1.22 | v3 | ✅ Tested | |
| 1.23 | v3 | ✅ Tested | |
| 1.24 | v3 | ✅ Tested | |
| 1.25 | v3 | ✅ Tested | PodSecurityPolicy removed |
| 1.26 | v3 | ✅ Tested | |
| 1.27 | v3 | ✅ Tested | |
| 1.28 | v3 | ✅ Tested | |
| 1.29 | v3 | ✅ Tested | |
| 1.30 | v3 | ✅ Tested | |
| 1.31 | v3 | ✅ Tested | |
| 1.32+ | v3 | 🔄 Forward-compatible | Unknown fields are allowed, not rejected |

## API Deprecation Tracking

Yamlr detects and auto-heals deprecated API versions:

| Deprecated API | Removed In | Replacement | Auto-Heal? |
| :--- | :--- | :--- | :--- |
| `extensions/v1beta1 Ingress` | 1.22 | `networking.k8s.io/v1` | ✅ Yes |
| `extensions/v1beta1 Deployment` | 1.16 | `apps/v1` | ✅ Yes |
| `policy/v1beta1 PodSecurityPolicy` | 1.25 | N/A (removed) | ⚠ Warns |
| `rbac.authorization.k8s.io/v1beta1` | 1.22 | `rbac.authorization.k8s.io/v1` | ✅ Yes |
| `admissionregistration.k8s.io/v1beta1` | 1.22 | `admissionregistration.k8s.io/v1` | ✅ Yes |
| `batch/v1beta1 CronJob` | 1.25 | `batch/v1` | ✅ Yes |

## CRD Support

Yamlr validates Custom Resource Definitions (CRDs) by:
1. Reading the CRD spec from the same directory or cluster
2. Extracting the OpenAPI v3 validation schema
3. Applying the same structural validation as built-in resources

If no CRD schema is available, Yamlr treats unknown `apiVersion/kind`
combinations as valid (forward-compatible).

## Schema Update Process

When a new Kubernetes version is released:
1. Download the OpenAPI spec from `https://raw.githubusercontent.com/kubernetes/kubernetes/release-1.XX/api/openapi-spec/v3/`
2. Add to `native_core/catalog/`
3. Run `cargo test` to validate all existing fixtures pass
4. Update this table
