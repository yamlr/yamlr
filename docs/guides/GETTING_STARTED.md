# Getting Started

Yamlr is the **Kubernetes Configuration Resolution Plane**. It audits, validates, and autonomously heals Kubernetes manifests, Helm charts, and Kustomize overlays before they reach your cluster or GitOps repository.

Yamlr executes **100% locally and offline**. Zero cluster credentials required, zero telemetry phoning home by default, and zero manifest data egressing your environment.

---

## Table of Contents

1. [Installation](#1-installation)
2. [Quick Verification](#2-quick-verification)
3. [Your First Manifest Audit (`yamlr scan`)](#3-your-first-manifest-audit-yamlr-scan)
4. [Previewing Fixes Without Risk (`yamlr diff`)](#4-previewing-fixes-without-risk-yamlr-diff)
5. [Autonomous Remediation (`yamlr heal`)](#5-autonomous-remediation-yamlr-heal)
6. [Interactive Onboarding (`yamlr welcome` & `yamlr demo`)](#6-interactive-onboarding-yamlr-welcome--yamlr-demo)
7. [Next Steps](#7-next-steps)

---

## 1. Installation

Yamlr is distributed as a standalone native binary compiled in Rust with zero runtime dependencies.

### Standalone Binary (Linux / macOS)
```bash
# Download and install the latest release directly to /usr/local/bin
curl -fsSL https://get.yamlr.dev/install.sh | bash
```

### Windows (PowerShell)
```powershell
# Install standalone native binary
irm https://get.yamlr.dev/install.ps1 | iex
```

### Homebrew (macOS / Linux)
```bash
brew install yamlr/tap/yamlr
```

### Python Environments (The Ruff Model)
If your engineering organization manages developer tooling through Python virtual environments:
```bash
pip install yamlr
# or isolated via pipx:
pipx install yamlr
```

### Container Image (Docker / Podman / CI)
```bash
docker pull ghcr.io/yamlr-dev/yamlr:latest
```

---

## 2. Quick Verification

Confirm that the native engine is functional:

```bash
# Check installed binary version
yamlr version

# Run the built-in system doctor to verify embedded schemas and local write permissions
yamlr doctor
```

Output:
```text
=== Yamlr System & Environment Doctor ===
Platform:     linux / x86_64
Version:      0.1.0 (Rust Native Standalone Core)
-----------------------------------------
[Check] Embedded K8s OpenAPI Schemas: PASSED (v1.21 - v1.37+ loadable, default v1.36)
[Check] Forensic Catalogs & CIS Rules: PASSED (79 production traps, 16 deprecations)
[Check] External Toolchains on PATH: PASSED (helm: OK, kustomize: OK)
[Check] Workspace Configuration: PASSED (using built-in zero-config defaults)
[Check] Healing Engine Self-Test: PASSED (healing engine functional)
[Check] Journal / WAL Write Access: PASSED
-----------------------------------------
Doctor Result: ALL CHECKS PASSED. Engine is production-ready.
```

---

## 3. Your First Manifest Audit (`yamlr scan`)

Navigate to any directory containing Kubernetes YAML files and execute:

```bash
yamlr scan .
```

### What Happens Behind the Scenes:
1. **Concrete Syntax Tree (CST) Sharding:** Slices all YAML streams into `NativeShard` tokens, preserving comments, line breaks, and whitespace.
2. **Topological ResourceGraph Assembly:** Reconciles cross-resource references (matching `Service.spec.selector` against `Deployment.spec.template.metadata.labels`, verifying `Ingress` routes, and checking `ConfigMap` keys).
3. **Forensic Inspection:** Tests workloads against 79 native detectors, Kubernetes OpenAPI v1.36 schemas, and CIS Benchmark v1.8.0 standards.
4. **Zero-Side-Effect Guarantee:** `yamlr scan` is strictly read-only. It will never modify a single byte on disk.

### Target Specific Kubernetes Versions
Auditing against upcoming API deprecations (e.g., validating against Kubernetes 1.31):
```bash
yamlr scan ./k8s -k 1.31
```

---

## 4. Previewing Fixes Without Risk (`yamlr diff`)

Before letting any automated tool modify your files, verify its proposed changes visually:

```bash
yamlr diff ./manifests
# or:
yamlr heal ./manifests --dry-run --diff
```

Yamlr displays a colorized, unified POSIX diff showing the exact AST mutations proposed:

```diff
--- deploy/payment-service.yaml (original)
+++ deploy/payment-service.yaml (healed)
@@ -10,7 +10,7 @@
   ports:
   - name: http
     port: 80
-    targetPort: 8080 # [NET-001] Mismatched containerPort (pod declares 3000)
+    targetPort: 3000 # [NET-001] Synchronized with payment-api containerPort
   selector:
     app: payment-processor
```

---

## 5. Autonomous Remediation (`yamlr heal`)

When you are ready to apply verified remediations:

```bash
yamlr heal ./manifests --apply
```

### What Happens During Healing:
1. **Comment-Preserving CST Mutation:** Repairs schema typos, deprecations, and selector mismatches while keeping 100% of `# comments` and indentation intact.
2. **Topological Multi-Doc Ordering:** Reorders multi-document streams so foundational resources (`CRD`, `Namespace`) precede dependents (`CustomResource`, `Deployment`).
3. **Write-Ahead Log (WAL) Journaling:** Records pre-mutation byte snapshots in `.yamlr/wal/` prior to writing to disk.

### Instant Single-Command Rollback
If you ever need to revert applied remediations:
```bash
yamlr rollback ./manifests
```

---

## 6. Interactive Onboarding (`yamlr welcome` & `yamlr demo`)

To explore Yamlr's comment-preserving remediation interactively:

```bash
# Run the built-in walkthrough demo
yamlr demo

# Display the onboarding quick start guide
yamlr welcome
```

---

## 7. Next Steps

- **Configure Repository Defaults:** [Configuration Guide (`.yamlr.yaml`)](/docs/configuration)
- **CI/CD Integration:** [Automate Pre-commit & GitHub Actions](/docs/ci-cd-integration)
- **Review All Detectors:** [Diagnostic Code Catalog](/docs/diagnostic-codes)
- **Deep-Dive Architecture:** [Core Concepts & ResourceGraph](/docs/core-concepts)
