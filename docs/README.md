# yamlr — Kubernetes Manifest Safety & Healing Engine

![Version](https://img.shields.io/badge/version-0.1.4-blue?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Kubernetes-lightgrey?style=flat-square)
![Engine](https://img.shields.io/badge/core-Rust--Native-orange?style=flat-square)
![License](https://img.shields.io/badge/license-Proprietary-blue?style=flat-square)

**Kubernetes validates syntax. Yamlr ensures cross-resource integrity and safe, comment-preserving auto-repair.**

`kubectl apply` checks schema syntax for individual resources in isolation. Yamlr builds a complete relational model across your workloads, services, ingresses, and policies to catch silent outages before they reach production.

Built with a native Rust core, Yamlr scans and repairs Kubernetes manifests. Its source-aware processing is designed to retain comments and formatting for supported transformations; review and validate changes before applying them.

---

## Key Capabilities

- **Cross-Resource Outage Prevention** — Catches Service-to-Workload port mismatches, orphaned Ingress backends, and selector collisions.
- **Source-Aware Auto-Repair (`yamlr heal`)** — Applies supported manifest repairs while aiming to retain comments and layout; review and validate the resulting changes.
- **Local-First** — Local scan and heal use local manifests and bundled schemas. Optional integrations can make network requests when enabled; review telemetry, license-renewal, registry, and CI reporting settings for air-gapped use.
- **Reproducible Performance** — Sub-50ms scans for 100 files; sub-500ms for 1,000 files via the native binary.
- **SARIF & CI/CD Native** — Emits standard SARIF 2.1.0 for GitHub Code Scanning, GitLab CI, and pre-commit hooks.

---

## Quickstart

```bash
# Scan manifests against Kubernetes 1.36 schema
yamlr scan ./k8s --k8s-version 1.36

# Preview safe auto-repairs with visual diff
yamlr heal ./k8s

# Apply repairs in-place (atomic write-and-rename)
yamlr heal ./k8s --apply
```

---

## Why Yamlr?

Yamlr is architected for **Safe Automation**:

* **Layout-Aware YAML Processing**: Tracks comments, whitespace, and scalar formatting to support focused repairs; preservation depends on the input and repair applied.
* **Topological Dependency Graph**: Validates relationships across ConfigMaps, Secrets, RBAC, Services, and Deployments.
* **Post-Repair Validation**: Supported healing flows validate repaired manifests; this does not replace validation against the target cluster and deployment environment.

---

## CLI Overview

```bash
yamlr scan ./k8s      # Audit manifests for syntax and semantic bugs
yamlr heal ./k8s      # Preview or apply comment-preserving repairs
yamlr graph ./k8s     # Render topological dependency graph
yamlr drift ./k8s     # Detect multi-version API drift
yamlr doctor          # Self-diagnostic check for local environment
```

---

## Engineering Standards

Yamlr is built with strict systems engineering principles:
- **Rust Native Core**: Memory-safe execution with `#![forbid(unsafe_code)]`.
- **Idempotency**: All heal operations produce identical SHA-256 hashes across consecutive runs.
- **Open Standards**: SARIF 2.1.0, OpenAPI v3, and standard Linux exit codes (0 = pass, 1 = violations).

---

**yamlr** — Kubernetes manifest safety & healing engine.  
Documentation: https://yamlr.dev  
Copyright (c) 2026 Yamlr Inc. All Rights Reserved.
