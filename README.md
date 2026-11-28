# Yamlr: The Kubernetes Configuration Resolution Plane

> Linters report warnings. Yamlr deterministically repairs them before they ship.

[![CI Matrix](https://github.com/yamlr/yamlr/actions/workflows/release-binaries.yml/badge.svg)](https://github.com/yamlr/yamlr/actions)
[![Release](https://img.shields.io/badge/release-v0.1.4-blue?style=flat-square)](https://github.com/yamlr/yamlr/releases/tag/v0.1.4)
[![Tests](https://img.shields.io/badge/tests-844%20passed-brightgreen?style=flat-square)](https://github.com/yamlr/yamlr)
[![Traps](https://img.shields.io/badge/traps%20cataloged-79%20handled-purple?style=flat-square)](docs/HEALING_RULES.md)
[![VS Code](https://img.shields.io/badge/VS%20Code-yamlr--k8s-blue?logo=visualstudiocode)](https://marketplace.visualstudio.com/items?itemName=yamlr.yamlr-k8s)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-blue)](https://get.yamlr.dev)
[![License](https://img.shields.io/badge/license-Proprietary%20Commercial-blue.svg)](LICENSE)

Yamlr resolves schema deviations, cross-resource topology breaks, and breaking API deprecations before manifests reach the cluster. Built on a native Rust Concrete Syntax Tree (CST) engine, Yamlr validates configurations offline against official Kubernetes OpenAPI schemas (`v1.21` through `v1.37`), preserves 100% of human comments and formatting, and delivers deterministic, idempotent auto-repairs in under 35ms.

---

## Quick Install

### Homebrew (macOS & Linux)
```bash
brew install yamlr/tap/yamlr
```

### One-Line Install Script
**Linux & macOS:**
```bash
curl -fsSL https://get.yamlr.dev/install.sh | sh
```

**Windows (PowerShell):**
```powershell
irm https://get.yamlr.dev/install.ps1 | iex
```

### VS Code Extension
Install directly from the Visual Studio Marketplace or run:
```bash
code --install-extension yamlr.yamlr-k8s
```

### Container Image (GHCR)
```bash
docker run --rm -v $(pwd):/work ghcr.io/yamlr/yamlr:v0.1.4 scan /work
```

### Pre-Built Binaries
Multi-platform static binaries with SHA-256 checksums are published on [GitHub Releases](https://github.com/yamlr/yamlr/releases/tag/v0.1.4):
* **Linux:** `x86_64` (glibc / musl), `aarch64` (ARM64)
* **macOS:** Apple Silicon (`aarch64`), Intel (`x86_64`)
* **Windows:** `x86_64` (`yamlr.exe`)

---

## 5-Minute Quickstart

### 1. Audit manifests against embedded Kubernetes schemas
```bash
yamlr scan ./k8s
```
*Validates offline against pre-compiled Kubernetes OpenAPI schemas (`v1.21`–`v1.37`), with forward-compatible baseline fallback and dynamic fetch for `v1.38+`.*

### 2. Preview proposed repairs in unified color diff
```bash
yamlr heal ./k8s --diff
```
*Inspect exact proposed changes before touching disk. Zero data loss and 100% comment preservation guaranteed.*

### 3. Apply repairs in-place
```bash
yamlr heal ./k8s --apply
```
*Deterministically resolves broken selectors, typo fields, port name mismatches, deprecated API versions, and RBAC bindings.*

### 4. Format manifests according to official Kubernetes schema hierarchy
```bash
yamlr fmt -w ./k8s
```

---

## 🛡️ Upstream Production Evidence

Yamlr's Concrete Syntax Tree (CST) engine is battle-tested against real-world production configurations across tier-1 CNCF repositories. Yamlr changes have been reviewed and merged upstream by project maintainers with **zero regressions, zero dropped comments, and zero spurious mutations**:

* **Prometheus Operator** ([#7810](https://github.com/prometheus-operator/prometheus-operator/pull/7810), [#7815](https://github.com/prometheus-operator/prometheus-operator/pull/7815)): Resolved ingress schema shifts and relative ExternalName trailing-dot DNS queries.
* **Rook Ceph** ([#16462](https://github.com/rook/rook/pull/16462)): Repaired volume mount specifications and storage contracts.
* **Spinnaker** ([#7084](https://github.com/spinnaker/spinnaker/pull/7084)): Fixed container lifecycle probe contracts and port misalignments.
* **Fluentd** ([#1709](https://github.com/fluent/fluentd-kubernetes-daemonset/pull/1709)): Resolved daemonset update strategies and schema deprecations.
* **Google Cloud Demos** (Microservices-demo, Container-engine-accelerators): Aligned resource constraints and port names.

👉 **Inspect the full verification dossier and merged pull requests:** [https://yamlr.dev/evidence](https://yamlr.dev/evidence)

---

## The 79 Production Traps Handled by Yamlr

Yamlr isolates and automatically repairs **79 structural, semantic, and cross-resource production traps** across 130 forensic rules:

* **Cross-Resource Topology Traps (Traps 10, 11, 42, 47, 55, 68):** Mismatched Service `spec.selector` vs. Deployment pod template labels, Service `targetPort` name vs. container `containerPort` discrepancies, orphaned ConfigMap/Secret mounts, and headless Service `clusterIP` invariants.
* **API Version Deprecations & Semantic Shifts (Traps 52, 54, 76, 77):** Safe migration of retired Kubernetes APIs (`policy/v1beta1`, `networking.k8s.io/v1beta1`) with semantic guards (e.g. blocking PDB `policy/v1` upgrades when an empty selector would unintentionally match all pods in the namespace).
* **Syntax & Encoding Traps (Traps 1, 19–24, 69–75):** Tab indentation errors, unspaced colon delimiters (`memory:256Mi`), UTF-16 byte order mark (BOM) transcoding, glued boundary comments (`---#`), and multiline block scalar formatting (`|`, `>`).
* **Resource Sanity & Units (Traps 4–6, 60, 67):** Resource requests exceeding limits, fatal millibyte units (`500m` -> `500Mi`), non-standard suffixes (`1gb` -> `1Gi`), and inverted HPA replica bounds (`minReplicas > maxReplicas`).
* **Security & CIS Benchmarks (Traps 13–18, 48, 61, 65):** Enforcing non-root container UIDs, synthesizing in-memory `/tmp` `emptyDir` volumes on `readOnlyRootFilesystem: true`, pruning `/var/run/docker.sock` exposures, and normalizing `safe-to-evict` annotations.

👉 **Review the complete rule specifications:** [Master Healing Rules Catalog](docs/HEALING_RULES.md)

---

## Integrations

### Pre-Commit Hook
Enforce clean, self-healed manifests before every Git commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/yamlr/yamlr
    rev: v0.1.4
    hooks:
      # Safe read-only preview (fails commit and displays diff if repairs needed)
      - id: yamlr-heal
      # To auto-repair manifests in-place before commit instead:
      # - id: yamlr-heal-apply
      - id: yamlr-scan
        args: ["--fail-on", "error"]
```

### GitHub Actions CI
Run schema audits and upload native SARIF reports to GitHub Code Scanning:

```yaml
name: Kubernetes Manifest Gate
on: [push, pull_request]

jobs:
  yamlr-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Verify Manifests with Yamlr
        uses: yamlr/yamlr-action@v0.1.4
        with:
          path: ./manifests
          k8s-version: '1.36'
          output: sarif
          output-file: yamlr.sarif

      - name: Upload SARIF to GitHub Code Scanning
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: yamlr.sarif
```

### Model Context Protocol (MCP) Server for AI Coding Agents
Yamlr includes a native Model Context Protocol server. AI coding assistants (Cursor, Claude Code, GitHub Copilot) use Yamlr as a zero-latency, offline verification compiler before persisting manifests to disk:

```json
{
  "mcpServers": {
    "yamlr": {
      "command": "yamlr",
      "args": ["mcp"]
    }
  }
}
```

### GitOps: Argo CD & Flux
* **Argo CD:** Deploy `yamlr` as a ConfigManagementPlugin (CMP) sidecar to heal manifests dynamically prior to cluster sync.
* **Flux:** Register `yamlr` as a Kustomize post-renderer to catch and repair broken manifests in the continuous reconciliation loop.

---

## Empirical Verification & Benchmark Guarantees

| Metric | Benchmark Guarantee | Verification Status |
|:---|:---|:---|
| **Automated Test Suite** | **844 Automated Tests Passing** (773 Unit + 71 Integration/E2E) | ✅ Passing |
| **Cataloged Production Traps** | **79 Structural, Semantic & Lifecycle Traps** | ✅ Codified |
| **Forensic Healing Rules** | **130 Unique Rule Codes** | ✅ Active |
| **Single-Manifest Resolution Latency** | **<35ms** (34.6ms average across CNCF golden test corpus) | ✅ Benchmarked |
| **Comment & Layout Retention** | **100% Byte-for-Byte Preservation** via Token CST parser | ✅ Invariant Gate |
| **Idempotency Guarantee** | **Mathematical Idempotency:** $h(h(x)) == h(x)$ | ✅ Invariant Gate |

---

## 👥 Authorship & Project Leadership

Yamlr is designed, architected, and maintained by:

* **Nishar A Sunkesala** ([@nisharas](https://github.com/nisharas)) — Creator & Lead Architect  
  Email: [nisharas@yahoo.com](mailto:nisharas@yahoo.com)

---

## 🏢 Enterprise Support & Governance

Yamlr is proprietary commercial software developed and owned by **Yamlr Inc**.
* **Free Community Tier:** Unlimited local offline scanning, formatting, and single-file auto-healing.
* **Enterprise Licensing:** GitOps fleet auto-remediation, custom organizational rule authoring, and air-gapped CI/CD governance.

For commercial inquiries, licensing, and enterprise design partnerships:
* **Website:** [https://yamlr.dev](https://yamlr.dev)
* **Evidence Dossier:** [https://yamlr.dev/evidence](https://yamlr.dev/evidence)
* **Contact:** [contact@yamlr.dev](mailto:contact@yamlr.dev)

---

## Documentation Links

* [CLI Reference Guide](docs/CLI_REFERENCE.md)
* [Configuration Specification](docs/reference/CONFIGURATION.md)
* [Architecture Model & Connective Tissue](docs/ARCHITECTURE_MODEL.md)
* [Healing Rules Catalog](docs/HEALING_RULES.md)
* [Release Playbook](docs/RELEASE_PLAYBOOK.md)
* [Contributing Guide](CONTRIBUTING.md)
* [Security Policy](SECURITY.md)
* [License Terms](LICENSE)
