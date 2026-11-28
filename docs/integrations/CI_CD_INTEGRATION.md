# CI/CD Integration & Automated Gating

Yamlr is architected as an ultra-fast, zero-overhead gatekeeper for continuous integration and continuous deployment pipelines. Compiled in native Rust, Yamlr scans thousands of manifests in milliseconds with zero JVM/Node startup latency, requires zero network connectivity, and adheres strictly to POSIX exit codes and SARIF 2.1.0 reporting standards.

---

## Table of Contents

1. [POSIX Process Exit Codes](#1-posix-process-exit-codes)
2. [Gating Options & Thresholds](#2-gating-options--thresholds)
3. [Native Git Pre-Commit Hook (`yamlr install --git-hook`)](#3-native-git-pre-commit-hook-yamlr-install---git-hook)
4. [GitHub Actions Workflow](#4-github-actions-workflow)
5. [GitLab CI Pipeline](#5-gitlab-ci-pipeline)
6. [SARIF 2.1.0 & GitHub Code Scanning Integration](#6-sarif-210--github-code-scanning-integration)
7. [Enterprise OpenTelemetry Export (`--otel`)](#7-enterprise-opentelemetry-export---otel)

---

## 1. POSIX Process Exit Codes

Yamlr's exit codes are deterministic, making it simple to write reliable CI scripts:

| Exit Code | Meaning | CI Behavior |
|:---|:---|:---|
| **`0`** | Clean / Succeeded | Pipeline passes. No violations found, or healing applied successfully. |
| **`1`** | Violations Detected | Pipeline fails. Violations meet or exceed `--fail-on` threshold, or dry-run has pending repairs. |
| **`2`** | CLI Usage Error | Pipeline fails. Invalid arguments, missing required paths, or unrecognized flags. |
| **`124`**| System / I/O Fault | Pipeline fails. Permission denied, disk full, or corrupted input stream. |

---

## 2. Gating Options & Thresholds

### Control Minimum Failure Severity: `--fail-on`
By default, `yamlr scan` exits with code `1` only on `error` and `critical` violations:

```bash
# Block builds on critical and error violations (default)
yamlr scan ./manifests --fail-on error

# Strict mode: fail builds even on warnings (e.g. missing resource limits, soft deprecations)
yamlr scan ./manifests --fail-on warning

# Hyper-strict mode: fail on informational hygiene issues
yamlr scan ./manifests --fail-on info
```

### Non-Blocking Telemetry Runs: `--exit-zero`
To run Yamlr in informational mode (e.g., during initial repository onboarding without blocking PR merges):

```bash
yamlr scan ./manifests --exit-zero --output sarif > report.sarif
```

---

## 3. Native Git Pre-Commit Hook (`yamlr install --git-hook`)

Yamlr can install a zero-dependency, native Git pre-commit hook directly into your local `.git/hooks/` directory:

```bash
yamlr install --git-hook
```

Output:
```text
[OK] Installed native Git pre-commit hook at '.git/hooks/pre-commit'.
Staged Kubernetes YAML manifests will now be automatically healed before every commit.
```

### How the Native Hook Works:
* Intercepts `git commit`.
* Filters only staged `.yaml` and `.yml` files (`git diff --cached`).
* Runs `yamlr heal --apply` on the staged files.
* Automatically stages the healed files (`git add`).
* Includes a cross-platform `.bat` companion for Windows developers.

### Integration with `pre-commit` Framework
If your team uses the Python-based `pre-commit` framework, add this to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/yamlr/yamlr
    rev: v0.1.0
    hooks:
      - id: yamlr-scan
        args: ["--fail-on", "error"]
      - id: yamlr-fmt
        args: ["--write"]
```

---

## 4. GitHub Actions Workflow

Add this workflow file to `.github/workflows/yamlr-gate.yml`:

```yaml
name: Kubernetes Configuration Resolution Gate

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  yamlr-audit:
    name: Audit & Verify K8s Manifests
    runs-on: ubuntu-latest
    permissions:
      security-events: write # Required for SARIF upload
      contents: read

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Install Yamlr Native Binary
        run: |
          curl -fsSL https://get.yamlr.dev/install.sh | bash
          yamlr version

      - name: Audit Manifests (SARIF Export)
        run: |
          yamlr scan . \
            --k8s-version 1.30 \
            --fail-on error \
            -o sarif \
            -f yamlr-results.sarif

      - name: Upload SARIF to GitHub Security Tab
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: yamlr-results.sarif
          category: yamlr-k8s-resolution
```

---

## 5. GitLab CI Pipeline

Add this job to `.gitlab-ci.yml`:

```yaml
stages:
  - test

yamlr-manifest-gate:
  stage: test
  image: ghcr.io/yamlr-dev/yamlr:latest
  script:
    - yamlr doctor
    - yamlr scan ./manifests --fail-on error --output text
  artifacts:
    reports:
      codequality: yamlr-results.sarif
    when: always
```

---

## 6. SARIF 2.1.0 & GitHub Code Scanning Integration

Yamlr's native SARIF exporter (`yamlr scan -o sarif`) produces standard OASIS SARIF v2.1.0 documents.

When uploaded to GitHub:
1. Every violation appears directly in the **Security → Code scanning** tab.
2. In Pull Requests, line-level annotations highlight the exact key causing the issue.
3. Every finding provides the canonical Rule ID (e.g., `NET-001`, `SEC-001`), official CIS Benchmark citation, and the single-command fix (`yamlr heal <file> --apply`).

---

## 7. Enterprise OpenTelemetry Export (`--otel`)

For enterprise platform teams using centralized observability (Datadog, Grafana, Dynatrace), Yamlr can emit OpenTelemetry-compliant metrics directly during CI executions:

```bash
yamlr scan ./manifests --otel --export-metrics
```

Metrics Emitted:
* `yamlr.scans.total`: Total manifest files inspected.
* `yamlr.heals.total`: Total auto-remediations applied.
* `yamlr.outages.prevented`: Quantified outage-risk mitigation count.
* `yamlr.duration_ms`: Execution duration in milliseconds.
