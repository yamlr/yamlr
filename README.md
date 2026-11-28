# Yamlr: The Kubernetes Configuration Resolution Plane

> Reconcile and repair Kubernetes configurations before deployment.

[![CI Matrix](https://github.com/yamlr/yamlr/actions/workflows/release-binaries.yml/badge.svg)](https://github.com/yamlr/yamlr/actions)
[![VS Code](https://img.shields.io/badge/VS%20Code-yamlr--k8s-blue?logo=visualstudiocode)](https://marketplace.visualstudio.com/items?itemName=yamlr.yamlr-k8s)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-blue)](https://get.yamlr.dev)
[![License](https://img.shields.io/badge/license-Proprietary-blue.svg)](LICENSE)

Yamlr resolves schema deviations, cross-resource dependencies, and deprecated APIs before manifests reach the cluster. Built with a high-performance native core, it validates configurations offline against official schemas, preserves every human comment and layout detail, and delivers deterministic idempotent repairs.

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

### Pre-Built Binaries
Static binaries are published with every release on [GitHub Releases](https://get.yamlr.dev):
- **Linux:** `x86_64` (glibc / musl), `aarch64` (ARM64)
- **macOS:** Apple Silicon (`aarch64`), Intel (`x86_64`)
- **Windows:** `x86_64` (`yamlr.exe`)

---

## 5-Minute Quickstart

### 1. Audit manifests against embedded Kubernetes schemas
```bash
yamlr scan ./k8s
```
*Validates offline against pre-compiled Kubernetes OpenAPI schemas (`v1.21` through `v1.37`), with forward-compatible baseline fallback and dynamic fetch for `v1.38+`.*

### 2. Preview proposed repairs in unified color diff
```bash
yamlr heal ./k8s --diff
```
*Inspect exact changes before writing anything to disk.*

### 3. Apply repairs in-place (preserves comments and formatting)
```bash
yamlr heal ./k8s --apply
```
*Fixes broken selectors, typo fields, ports, deprecated API versions, and RBAC bindings.*

### 4. Format manifests according to official Kubernetes schema hierarchy
```bash
yamlr fmt -w ./k8s
```

---

## Integrations

### Pre-Commit Hook
Enforce clean, self-healed manifests before every git commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/yamlr/yamlr
    rev: v0.1.3
    hooks:
      # Safe read-only preview (blocks commit and displays diff if repairs needed)
      - id: yamlr-heal
      # To auto-repair manifests in-place instead, use yamlr-heal-apply:
      # - id: yamlr-heal-apply
      - id: yamlr-scan
        args: ["--fail-on", "error"]
```

### GitHub Actions CI
Run schema audits and upload native SARIF reports to GitHub Code Scanning:

```yaml
name: Manifest Gate
on: [push, pull_request]

jobs:
  yamlr:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Audit Manifests
        uses: yamlr/yamlr-action@v0.1.3
        with:
          path: ./manifests
          output-file: results.sarif
      - name: Upload SARIF to GitHub Code Scanning
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
```

### VS Code Extension
Real-time keystroke diagnostics, schema hover tooltips, and one-click quick-fixes via the embedded Language Server:
1. Search for `Yamlr` in the VS Code Marketplace or install [`yamlr.vsix`](https://get.yamlr.dev).
2. The extension automatically invokes the native `yamlr lsp` background daemon.

### GitOps: ArgoCD & Flux
- **ArgoCD CMP:** Deploy `yamlr-cmp.yaml` as a ConfigManagementPlugin sidecar to heal manifests prior to sync.
- **Flux:** Add `yamlr` as a Kustomize post-renderer to catch and repair broken manifests in the reconciliation loop.

---

## Empirical Fleet Proof

We test Yamlr against real-world production Kubernetes manifests across top CNCF projects. Every manifest must pass 5 strict invariant gates without exception:

1. **Zero Dropped Comments:** Runtime pre-write gate strictly enforces zero comment loss (`healed_comments >= orig_comments`).
2. **Kubernetes OpenAPI v3 Schema Validity:** All healed files validate against official Kubernetes OpenAPI schemas.
3. **Mathematical Idempotency:** Applying healing twice produces zero diff: `h(h(x)) == h(x)`.
4. **Headless `kubectl dry-run` Validation:** Clean pass through client dry-run verification.
5. **Keyword Collision Immunity:** Field names matching reserved keywords (such as `type`, `status`, `port`) are parsed with correct contextual scope.

### Fleet Validation & Invariant Testing (Category A: CNCF Ecosystem)
| Metric | Result |
| :--- | :--- |
| **CNCF Ecosystem Corpus Manifests** | **Evaluated across CNCF Golden Test Corpus** |
| **Automated Regression Suite** | **821 Automated Tests Passing (757 Unit + 64 Integration)** |
| **Production Architecture Traps Cataloged** | **79** |
| **Zero Spurious Mutations** | **100.0% Byte-for-Byte Unchanged on Fully Compliant Manifests** |
| **Single Document Healing Latency** | **Sub-50 ms typical (warm cache)** |

---

## The 79 Production Traps Handled by Yamlr

Yamlr isolates and automatically repairs 79 structural, semantic, and cross-resource production traps, including:

- **Cross-Resource Misalignment:** Mismatched `spec.selector.matchLabels` and `spec.template.metadata.labels`, broken Service `targetPort` names, orphaned ConfigMap/Secret volume mounts.
- **RBAC & Security Constraints:** Missing `ServiceAccount` declarations, malformed `RoleBinding` subjects, CIS Benchmark container security context defaults.
- **API Version Deprecations:** Automatic migration of retired Kubernetes APIs (`extensions/v1beta1`, `networking.k8s.io/v1beta1`) to active stable equivalents.
- **Syntax & Schema Traps:** Unquoted YAML octal numeric strings (e.g. `0777`), tab-polluted indentation, boolean scalar truncation (`yes`/`no`/`on`/`off`), and multiline block scalar formatting (`|`, `>`).
- **Resource Limits & Units:** Correction of legacy or invalid memory units (e.g. `1000M` vs `1000Mi`), probe timing conflicts (`periodSeconds` < `timeoutSeconds`), and PDB availability constraints.

---

## Model Context Protocol (MCP) Server

Yamlr includes a built-in Model Context Protocol server. AI coding agents and LLM orchestration frameworks can connect to Yamlr via standard I/O:

```bash
yamlr mcp
```

Agents use Yamlr as a deterministic, offline compiler to audit and heal generated Kubernetes infrastructure before submitting pull requests or applying manifests to clusters.

---

## Documentation

- [CLI Reference Guide](docs/CLI_REFERENCE.md)
- [Configuration Documentation](docs/CONFIGURATION.md)
- [Architecture Model](docs/ARCHITECTURE_MODEL.md)
- [Positioning & Architecture Strategy](docs/Yamlr_Positioning_Strategy.md)

---

## License

Yamlr is proprietary software owned by Timonel Labs. See [LICENSE](LICENSE) for commercial and evaluation terms.
