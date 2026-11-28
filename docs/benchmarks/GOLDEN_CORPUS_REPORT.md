# Yamlr Golden Corpus — Real-World Ecosystem Regression Report

**Date:** September 2026  
**Evaluation Scope:** Real Production Kubernetes Manifests Downloaded from Upstream GitHub Repositories  
**Target Ecosystems:** `kubernetes/ingress-nginx`, `cert-manager/cert-manager`, `argoproj/argo-rollouts`, `prometheus-operator`  

---

## 1. Executive Summary & Verification Metrics

| Metric | Empirical Result | Gate Standard | Verification Status |
| :--- | :--- | :--- | :--- |
| **Production Ecosystems** | **4/4 Upstream Projects** | Multi-vendor | ✅ Verified |
| **Total Raw YAML Evaluated** | **7.79 Megabytes** (8,173,132 bytes) | High-volume scale | ✅ Verified |
| **Distinct K8s Documents** | **95 Resources** | CRDs, Deploys, RBAC, Services | ✅ Verified |
| **Panic / Crash Rate** | **0 (0.0%)** | 0.0% (Zero Panics) | ✅ PASS |
| **Resource Idempotency (Per-Document)** | **95/95 (100.0%)** | 100.0% (`heal(heal(M)) == heal(M)`) | ✅ PASS |
| **Stream Idempotency (Full Manifest)** | **4/4 (100.0%)** | 100.0% End-to-end stream stability | ✅ PASS |
| **Comment Preservation (Exhaustive)** | **115/115 (100.0%)** | 100.0% (Zero dropped comments, no sampling) | ✅ PASS |
| **Safe Remediations Applied** | **239 Auto-Fixes** | Non-destructive schema/links | ✅ PASS |
| **Total Pipeline Latency (Native Core)** | **Unverified** | < 15.0s / 10MB | Pending reproducible harness per `docs/BENCHMARK_REPORT.md` |
| **Legacy Python Prototype Runner** | **110.16 seconds** | < 15.0s / 10MB | ⚠️ FAIL (Exceeded gate in Python prototype; replaced by native core) |

---

## 2. Real-World Ecosystem Audit Dossier

| Repository / Ecosystem | Documents | Document Idempotency | Stream Idempotency | Comments Preserved | Size (KB) | SHA256 (Prefix) | Status | Action |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| [`kubernetes/ingress-nginx`](https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/baremetal/deploy.yaml) | 19 | 19/19 (100%) | ✅ PASS | N/A (0 comments) | 15.9 KB | `16b9b62df45b` | **✅ PASS** | Remediated & Verified |
| [`cert-manager/cert-manager`](https://github.com/cert-manager/cert-manager/releases/download/v1.14.4/cert-manager.yaml) | 46 | 46/46 (100%) | ✅ PASS | 114/114 (100%) | 461.6 KB | `fcaaf51002a5` | **✅ PASS** | Remediated & Verified |
| [`argoproj/argo-rollouts`](https://raw.githubusercontent.com/argoproj/argo-rollouts/stable/manifests/install.yaml) | 15 | 15/15 (100%) | ✅ PASS | 1/1 (100%) | 2977.0 KB | `be25242c55ba` | **✅ PASS** | Remediated & Verified |
| [`prometheus-operator/prometheus-operator`](https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml) | 15 | 15/15 (100%) | ✅ PASS | N/A (0 comments) | 4527.1 KB | `14948e73145f` | **✅ PASS** | Remediated & Verified |

---

## 3. Upstream Provenance & Reproduction

Every manifest in this regression suite is sourced directly from public production releases:
1. **`kubernetes/ingress-nginx`**: `deploy/static/provider/baremetal/deploy.yaml` (Official Baremetal Deployment Controller).
2. **`cert-manager/cert-manager`**: Release v1.14.4 `cert-manager.yaml` (Production ACME Controllers and CRD Schemas).
3. **`argoproj/argo-rollouts`**: Stable `manifests/install.yaml` (Progressive Delivery Canary Controllers and Workloads).
4. **`prometheus-operator/prometheus-operator`**: Main `bundle.yaml` (Monitoring Operator and PrometheusRule CRD definitions).

### Reproduction Command
```bash
# Runs the automated Golden Corpus against all cached/fetched upstream manifests
python scripts/run_golden_corpus.py
```
