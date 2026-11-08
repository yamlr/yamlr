# Canonical CLI Reference

Yamlr is architected as an ultra-high performance native systems binary compiled in Rust (`yamlr v0.1.0`). It operates directly on raw YAML ASTs and the Kubernetes OpenAPI resolution plane to audit, format, and autonomously heal Kubernetes manifests with deterministic layout and comment preservation.

This reference provides a complete, 100% code-verified specification of all commands, flags, arguments, exit codes, and operational failure modes supported by the native engine.

---

## Table of Contents

1. [Global Conventions & Exit Codes](#global-conventions--exit-codes)
2. [Core Resolution & Remediation](#core-resolution--remediation)
   - [`yamlr scan`](#yamlr-scan)
   - [`yamlr heal`](#yamlr-heal)
   - [`yamlr diff`](#yamlr-diff)
   - [`yamlr fmt`](#yamlr-fmt)
   - [`yamlr fix`](#yamlr-fix)
   - [`yamlr migrate`](#yamlr-migrate)
   - [`yamlr check`](#yamlr-check)
   - [`yamlr lint`](#yamlr-lint)
3. [Forensic Diagnostics & Inspection](#forensic-diagnostics--inspection)
   - [`yamlr doctor` / `yamlr diagnose`](#yamlr-doctor--yamlr-diagnose)
   - [`yamlr explain`](#yamlr-explain)
   - [`yamlr catalog`](#yamlr-catalog)
   - [`yamlr rules`](#yamlr-rules)
   - [`yamlr evidence`](#yamlr-evidence)
   - [`yamlr stats` / `yamlr status`](#yamlr-stats--yamlr-status)
4. [Topology, Graphing & Contract Drift](#topology-graphing--contract-drift)
   - [`yamlr graph`](#yamlr-graph)
   - [`yamlr drift`](#yamlr-drift)
   - [`yamlr dna`](#yamlr-dna)
   - [`yamlr roi` / `yamlr pulse` / `yamlr impact`](#yamlr-roi--yamlr-pulse--yamlr-impact)
5. [Transactional WAL & Governance](#transactional-wal--governance)
   - [`yamlr rollback` / `yamlr restore`](#yamlr-rollback--yamlr-restore)
   - [`yamlr sign` & `yamlr verify`](#yamlr-sign--yamlr-verify)
   - [`yamlr secure`](#yamlr-secure)
   - [`yamlr baseline`](#yamlr-baseline)
   - [`yamlr audit`](#yamlr-audit)
   - [`yamlr fleet`](#yamlr-fleet)
   - [`yamlr schema`](#yamlr-schema)
6. [Daemons & Ecosystem Integration](#daemons--ecosystem-integration)
   - [`yamlr lsp`](#yamlr-lsp)
   - [`yamlr mcp`](#yamlr-mcp)
   - [`yamlr rpc` / `yamlr daemon`](#yamlr-rpc--yamlr-daemon)
   - [`yamlr watch`](#yamlr-watch)
   - [`yamlr webhook`](#yamlr-webhook)
   - [`yamlr vap` / `yamlr export-vap`](#yamlr-vap--yamlr-export-vap)
   - [`yamlr idp-export`](#yamlr-idp-export)
7. [System Administration & Setup](#system-administration--setup)
   - [`yamlr init`](#yamlr-init)
   - [`yamlr guide`](#yamlr-guide)
   - [`yamlr features`](#yamlr-features)
   - [`yamlr admin`](#yamlr-admin)
   - [`yamlr auth` & `yamlr subscribe`](#yamlr-auth--yamlr-subscribe)
   - [`yamlr upgrade`](#yamlr-upgrade)
   - [`yamlr completion`](#yamlr-completion)
   - [`yamlr install`](#yamlr-install)
   - [`yamlr manual` / `yamlr man`](#yamlr-manual--yamlr-man)
   - [`yamlr welcome` & `yamlr demo`](#yamlr-welcome--yamlr-demo)

---

## Global Conventions & Exit Codes

### POSIX Process Exit Codes
Every Yamlr command conforms strictly to POSIX process exit contracts, making it deterministic in CI/CD runners, Git pre-commit hooks, and IDE extensions:

| Exit Code | Constant | Meaning | Typical Trigger |
|:---|:---|:---|:---|
| `0` | `EXIT_SUCCESS` | Clean / Succeeded | No violations found, diff cleanly previewed, or healing applied successfully. |
| `1` | `EXIT_VIOLATIONS` | Lint / Policy Violations | Violations detected in `scan` or `check` exceeding `--fail-on` threshold, or dry-run pending fixes. |
| `2` | `EXIT_USAGE` | Invalid CLI Arguments | Missing required positional parameter, unrecognized flag, or unknown subcommand. |
| `4` | `EXIT_SYNTAX_ERROR` | Unfixable Syntax Error | Unparseable YAML, malformed documents, or broken syntax that auto-healing cannot safely resolve. |
| `124` | `EXIT_SYSTEM_ERROR` | System / I/O Fault | File unreadable, permission denied, or engine write failure during rollback/healing. |

### Global Flags
These flags are supported across all scanning and healing entry points:

- `--k8s-version <VERSION>`, `-k <VERSION>` (Alias: `--kube-version`): Target specific Kubernetes OpenAPI release schema (e.g., `1.28`, `1.30`, `1.36`). Defaults to `1.36`.
- `--output <FORMAT>`, `-o <FORMAT>`: Standard output formatter. Values: `text`, `json`, `sarif` (case-insensitive).
- `--quiet`, `-q`: Suppress informational headers, ASCII banners, and progress updates. Emits only errors or structured output.
- `--exit-zero`: Enforce exit code `0` even when policy violations or syntax errors are detected (useful for non-blocking telemetry runs in CI).
- `--no-telemetry` (Aliases: `--disable-telemetry`): Disable anonymous operational metrics reporting.
- `--otel` (Alias: `--export-metrics`): Export OpenTelemetry compliant spans and metrics for enterprise observability.

---

## Core Resolution & Remediation

### `yamlr scan`
Audits YAML files, Helm templates, Kustomize overlays, or directory trees for schema errors, API deprecations, security misconfigurations, and cross-resource topological integrity faults.

```bash
yamlr scan [PATH] [OPTIONS]
```

#### Arguments & Flags
- `[PATH]`: Target file or directory to scan. Defaults to `.` (current working directory).
- `-k, --k8s-version <VERSION>`: Target Kubernetes version (e.g., `1.25`, `1.28`, `1.30`, `1.31`).
- `-o, --output <FORMAT>`: Output format (`text`, `json`, `sarif`).
- `-f, --output-file <PATH>`: Write output directly to a destination file path.
- `-j, --json`: Shorthand for `--output json`.
- `--sarif`: Shorthand for `--output sarif` (SARIF v2.1.0 schema for GitHub Code Scanning).
- `--fail-on <SEVERITY>`: Minimum violation severity that triggers exit code `1`. Options: `info`, `low`, `medium`, `high`, `critical`, `error`.
- `--workspace <DIR>`: Explicit workspace root directory for cross-resource identity indexing (Alias: `--workspace-dir`).
- `--crd <PATH>`: Path to custom CRD definitions file or directory to dynamically extend schema validation.
- `--helm`: Render Helm charts into flat manifests in-memory before scanning.
- `--kustomize`: Execute Kustomize overlays before scanning.
- `--oci-layer <PATH>`: Scan Kubernetes manifests extracted from an OCI container layer.
- `-w, --watch`: Enter continuous file-watch mode, rescanning on save.
- `--exit-zero`: Always exit with code `0`.

#### Practical Examples
```bash
# Standard directory scan
yamlr scan ./manifests

# CI check failing only on HIGH or CRITICAL violations
yamlr scan ./k8s --fail-on high

# Export SARIF directly for GitHub Actions Security tab
yamlr scan ./deploy -o sarif -f results.sarif

# Audit manifests against upcoming Kubernetes 1.31 deprecations
yamlr scan ./base -k 1.31
```

---

### `yamlr heal`
The flagship autonomous remediation engine. Analyzes Kubernetes resources and safely repairs schema regressions, deprecated `apiVersions`, selector mismatches, and security policies while strictly preserving comments, inline documentation, key ordering, and whitespace.

```bash
yamlr heal [PATH] [OPTIONS]
```

#### Arguments & Flags
- `[PATH]`: File or directory to heal. Defaults to `.`.
- `-d, --dry-run`: Preview remediations in memory without writing any changes to disk (exits `1` if changes needed).
- `--diff`: Display a unified, colorized diff comparing original file content with proposed fixes.
- `-a, --apply`: Atomically commit healed changes to disk and record a Write-Ahead Log (WAL) transaction journal.
- `-k, --k8s-version <VERSION>`: Target Kubernetes schema version for upgrades (e.g. `1.30`).
- `-o, --output <FORMAT>`: Output format (`text`, `json`, `sarif`).
- `--generate-stubs` (Alias: `--create-stubs`): Automatically synthesize missing referenced objects (e.g., stubbing a missing `Secret` or `ConfigMap` required by a `Deployment`).
- `--ingest-opa <PATH>`: Ingest an external JSON policy constraint report file and automatically synthesize remediation rules.
- `--ingest-kyverno <PATH>`: Ingest an admission policy report YAML and synthesize matching auto-heals.
- `--workspace <DIR>`: Explicit workspace root directory for cross-resource identity indexing (Alias: `--workspace-dir`).
- `--verify-kubectl`: Pipe healed manifests through local `kubectl --dry-run=client` to provide secondary kernel validation.
- `--explain-gate`: Print detailed diagnostic explanations if a pre-write safety gate blocks an in-place write.
- `--summary`: Output a condensed remediation count table instead of individual diffs.

#### Practical Examples
```bash
# Preview what would be healed in a unified diff (safe inspection)
yamlr heal ./k8s --diff

# Apply all safe remediations in-place with automatic WAL snapshot creation
yamlr heal ./k8s --apply

# Upgrade all manifests to Kubernetes 1.30 and synthesize missing ConfigMap stubs
yamlr heal ./manifests --apply -k 1.30 --generate-stubs
```

#### Pre-Write Invariant Verification Gates
Before touching the filesystem in `--apply` mode, Yamlr enforces 6 mandatory in-memory pre-write safety gates:
1. **YAML Syntax Validation:** Bounded YAML document deserialization ensures healed output parses cleanly without infinite loops or memory leaks.
2. **Non-Empty AST Verification:** Aborts write if healed output produces an empty shard tree, preventing accidental file truncation.
3. **Comment Preservation Invariant:** Verifies zero comment loss; write aborts if `healed_comments < orig_comments`.
4. **ConfigMap & Secret Payload Immutability:** Guarantees that configuration data, environment payloads, and scripts inside `ConfigMap` and `Secret` resources are 100% byte-for-byte immutable. Only consumer keyRefs in workloads may be aligned.
5. **In-Memory Double-Pass Idempotency:** Runs a secondary in-memory healing cycle and aborts if pass 2 yields further mutations, guaranteeing mathematical stability (`heal(heal(M)) == heal(M)`).
6. **Filesystem Concurrency Guard:** Checks that the file was not modified on disk by another process (editor, CI step, git) between the initial read and write back.

#### SRE Production Reliability Annotations
Yamlr enforces Google SRE best practices with zero unsolicited mutations. Advanced production safeguards operate as non-mutating Advisories by default, and can be activated via declarative manifest annotations:
- yamlr.dev/safe-probes: Injects a dedicated startupProbe cloning livenessProbe to protect slow container initializations from CrashLoops (PRB-007).
- yamlr.dev/drain-hook: Injects a /bin/sleep 15 lifecycle.preStop hook to eliminate traffic drops during pod termination while iptables/ipvs update (REL-015).
- yamlr.dev/topology-routing: Injects service.kubernetes.io/topology-mode: auto to restrict traffic within AZs and eliminate cross-zone egress charges (NET-021).
- yamlr.dev/safe-storage: Injects safe sizeLimit: 1Gi to unbounded mptyDir volumes to protect host root filesystems from eviction (STO-009).

#### Cross-Resource Reference Alignment (REF-006 & NET-020)
By default, mismatched ConfigMap/Secret keys (`configMapKeyRef.key`) and Ingress backend service port names emit explainable **S0 Advisories** without mutating files. To authorize autonomous S2 in-place alignment for unambiguous distance-1 typos, enable `allow-reference-alignment: true` in `.yamlr.yaml` or set the manifest annotation `yamlr.dev/allow-reference-alignment: "true"`.

---

### `yamlr diff`
Shorthand alias for `yamlr heal <PATH> --diff --dry-run`. Emits a colorized POSIX-compliant unified diff of all proposed remediations.

```bash
yamlr diff ./deploy/production.yaml
```

---

### `yamlr fmt`
Canonical Kubernetes manifest formatter and layout normalizer. Reorders keys deterministically to the official Kubernetes OpenAPI hierarchy (`apiVersion` -> `kind` -> `metadata` -> `spec` -> `data` -> `status`), preserves all comments and blank lines, and guarantees Windows (`\r\n`) and Unix (`\n`) newline invariance across single and multi-document streams. In-place writes (`-w`) are protected by an atomic file-replacement write mechanism and an OpenAPI pre-write schema gate.

```bash
yamlr fmt [PATH] [OPTIONS]
```

#### Flags
- `-w, --write`: Overwrite files in-place with formatted content, backed by atomic file-swap backups and OpenAPI schema validation.
- Target `-`: Stream manifest from stdin and emit formatted result to stdout (e.g., `helm template . | yamlr fmt -`).

---

### `yamlr fix`
Rapid non-destructive auto-repair alias for `yamlr heal --apply`. Resolves trivial schema syntax errors, trailing spaces, indent errors, and deprecated API versions.

```bash
yamlr fix ./manifests
```

---

### `yamlr migrate`
Dedicated Kubernetes API version modernization engine. Surgically upgrades deprecated and retired Kubernetes APIs (`extensions/v1beta1`, `networking.k8s.io/v1beta1`, `policy/v1beta1`, `autoscaling/v2beta1`, `batch/v1beta1`, etc.) to modern stable APIs across single manifests, multi-document streams (`---`), or deep directory hierarchies. Enforces a strict zero-side-effect contract: never alters container commands, resource quotas, or non-deprecated specs.

```bash
# Preview proposed migrations in color unified diff
yamlr migrate ./k8s --to 1.30 --diff

# Apply migrations in-place with safety backups
yamlr migrate ./k8s --to 1.30 --apply

# Apply migrations in CI without generating .bak backup files
yamlr migrate ./k8s --to 1.30 --apply --no-backup
```

#### Arguments & Flags
- `[PATH]`: Target file or directory to migrate. Defaults to `.`.
- `--to <VERSION>`, `--k8s-version <VERSION>`: Target Kubernetes version (e.g., `1.30`, `1.32`).
- `-a, --apply`: Apply migrations in-place to disk with pre-write schema gate verification and atomic backups.
- `-d, --diff`: Display colored unified diff showing exact proposed line changes.
- `--dry-run`: Preview proposed migrations without modifying files on disk (default).
- `--no-backup`: Disable `.bak` safety backup creation in clean CI/CD or Git worktrees.
- `-q, --quiet`: Suppress banners and progress; print only migrated file records.

---

### `yamlr check`
Strict non-healing linter for CI/CD gates. Traverses manifests, evaluates schema conformance and CIS hardening invariants, and exits with non-zero status if violations exist.

```bash
yamlr check ./k8s --fail-on error
```

---

### `yamlr lint`
Alias for `yamlr check`. Executes workspace linting with configured diagnostic thresholds.

```bash
yamlr lint ./k8s
```

---

## Forensic Diagnostics & Inspection

### `yamlr doctor` / `yamlr diagnose`
Executes an end-to-end self-test of the Yamlr execution environment. Verifies embedded schemas (v1.21 through v1.37+), checks forensic rule catalogs, detects `helm` and `kustomize` binaries on the system `$PATH`, checks `.yamlr.yaml` integrity, and validates WAL disk write permissions.

```bash
yamlr doctor
yamlr doctor --verbose
# or alias:
yamlr diagnose
```

---

### `yamlr explain`
Interactive rule explainer. Provides detailed rationale, CIS Kubernetes Benchmark citations, security severity, and remediation guidance for any rule ID, detector code, or deprecated API.

```bash
yamlr explain <RULE_ID>
```

#### Examples
```bash
# Explain pod security context cap-drop rule
yamlr explain SEC-001

# Explain CIS Kubernetes benchmark rule
yamlr explain CIS-4.2.1

# Explain Ingress API deprecation and migration path
yamlr explain DEP-INGRESS
```

---

### `yamlr catalog`
Displays the complete directory of built-in forensic detectors, deprecation tables, and autonomous healers compiled into the native engine.

```bash
yamlr catalog
```

---

### `yamlr rules`
Audits custom user-defined validation policies, ValidatingAdmissionPolicies (CEL), and external admission policy integrations loaded in the current workspace.

```bash
yamlr rules
```

---

### `yamlr evidence`
Generates a structured compliance evidence report for SOC2, ISO 27001, and CIS Kubernetes Benchmark audits.

```bash
yamlr evidence [PATH] --output json
```

---

### `yamlr stats` / `yamlr status`
Displays workspace health metrics, total healed violations, active license tier, and WAL journal snapshot counts.

```bash
yamlr stats
yamlr status
```

---

## Topology, Graphing & Contract Drift

### `yamlr graph`
Renders an architectural dependency and relationship graph of the manifests in the workspace. Maps cross-resource bindings such as `Service` -> `Deployment` (via selector matching), `ServiceAccount` -> `RoleBinding` -> `ClusterRole`, and `PersistentVolumeClaim` -> `PersistentVolume`.

```bash
yamlr graph [PATH] [OPTIONS]
```

#### Options
- `--format <dot|svg|mermaid|json>`: Output format (defaults to ASCII terminal view).
- `--output-file <PATH>`: Write graph directly to file.

---

### `yamlr drift`
Analyzes drift between declared GitOps manifests and live cluster configurations or historical baselines.

```bash
yamlr drift [PATH]
```

---

### `yamlr dna`
Calculates a cryptographic semantic fingerprint (DNA) of the resource topology. Detects functional changes while ignoring harmless cosmetic edits (such as whitespace or comment adjustments).

```bash
yamlr dna ./manifests
```

---

### `yamlr roi` / `yamlr pulse` / `yamlr impact`
Calculates engineering ROI, time saved through automated remediation, and estimated outage prevention impact across your codebase.

```bash
yamlr roi
yamlr pulse
```

---

## Transactional WAL & Governance

### `yamlr rollback` / `yamlr restore`
Restores modified manifests to their exact byte-for-byte pre-healed state using the atomic Write-Ahead Log (WAL) stored in `.yamlr/wal/` (or current directory journal files).

```bash
yamlr rollback [PATH]
yamlr restore [PATH]
```

---

### `yamlr sign` & `yamlr verify`
Cryptographically signs verified Kubernetes manifests using SHA-256 and Ed25519 signatures, and verifies manifest integrity during GitOps deployment pipelines.

```bash
# Sign manifest batch
yamlr sign ./manifests --key <PRIVATE_KEY_PATH>

# Verify cryptographic provenance in CI
yamlr verify ./manifests --public-key <PUBLIC_KEY_PATH>
```

---

### `yamlr secure`
Synthesizes missing least-privilege `NetworkPolicy` objects and restrictive `PodSecurityStandards` for unhardened deployments.

```bash
yamlr secure ./manifests --apply
```

---

### `yamlr baseline`
Creates a baseline snapshot of current manifest states or evaluates current manifests against an established baseline.

```bash
# Capture snapshot
yamlr baseline snapshot --out baseline.json

# Check for regressions
yamlr baseline verify baseline.json
```

---

### `yamlr audit`
Executes an in-depth security and CIS compliance audit across all workloads.

```bash
yamlr audit ./manifests
```

---

### `yamlr fleet`
Discovers, audits, and applies autonomous remediations across multiple GitOps repositories simultaneously. Supports automated Git branch creation and pull request scaffolding.

```bash
yamlr fleet <DIRECTORY> [OPTIONS]
```

#### Flags
- `-a, --apply`: Commit verified remediations across discovered repositories.
- `-k, --k8s-version <VERSION>`: Target Kubernetes version (defaults to `1.36`).
- `--branch <NAME>`: Custom branch name for automated commits.
- `--create-pr`: Prepare automated pull requests for each healed repository.
- `--dry-run-git`: Preview Git operations without creating real branches or commits.
- `-j, --json`: Emit fleet execution summaries as JSON.

#### Example
```bash
# Preview fleet-wide upgrade to Kubernetes 1.30 across all repos in /gitops
yamlr fleet /gitops -k 1.30

# Apply remediations and create PR branches across all repos
yamlr fleet /gitops -k 1.30 --apply --create-pr
```

---

### `yamlr schema`
Manages offline OpenAPI schemas and workspace CustomResourceDefinition (CRD) distillation caches.

```bash
yamlr schema <SUBCOMMAND>
```

#### Subcommands
- `ingest <PATH>`: Distills and caches custom CRD schemas from the target directory into `.yamlr/schemas/`.
- `fetch <VERSION> [--offline]`: Retrieves and caches the official Kubernetes OpenAPI schema bundle for a specific version.
- `list`: Lists all cached native and custom schemas in the workspace.
- `clean`: Purges `.yamlr/schemas/` to reclaim disk space.

```bash
# Ingest CRDs from a local chart
yamlr schema ingest ./crds

# List cached schemas
yamlr schema list
```

---

## Daemons & Ecosystem Integration

### `yamlr lsp`
Starts the native Language Server Protocol (LSP) daemon over standard I/O (`stdio`). Provides real-time in-editor diagnostics, autocomplete, hover explanations, and instant code actions for VS Code, Neovim, and JetBrains IDEs.

```bash
yamlr lsp
```

---

### `yamlr mcp`
Launches the Model Context Protocol (MCP) server over `stdio`. Exposes Yamlr's healing and scanning tools directly to AI coding assistants (such as Antigravity, Claude Desktop, and Cursor).

```bash
yamlr mcp
```

---

### `yamlr rpc` / `yamlr daemon`
Starts the native high-throughput `ManifestService` RPC daemon over TCP. Allows external orchestrators, CI runners, and local developer daemons to submit document chunks and receive healed manifests with sub-millisecond latency.

```bash
yamlr rpc [OPTIONS]
```

#### Flags
- `--serve`: Starts the TCP RPC listener.
- `--port <PORT>`: Port number to bind (defaults to `50051`).
- `--dry-run`: Validates daemon configuration without binding network sockets.

```bash
# Start RPC daemon on port 50051
yamlr rpc --serve --port 50051
```

---

### `yamlr watch`
Monitors manifest directories using OS-native filesystem notifications (`inotify` on Linux, `kqueue` on macOS, ReadDirectoryChanges on Windows) and triggers rapid sub-millisecond healing previews on save.

```bash
yamlr watch ./k8s
```

---

### `yamlr webhook`
Runs an ultra-lightweight HTTP admission webhook daemon to validate and mutate Kubernetes manifests in-flight before admission to the cluster.

```bash
yamlr webhook --port 8443 --tls-cert cert.pem --tls-key key.pem
```

---

### `yamlr vap` / `yamlr export-vap`
Compiles Yamlr's built-in forensic rules into native Kubernetes `ValidatingAdmissionPolicy` (CEL) definitions for direct cluster-level enforcement.

```bash
yamlr vap --out ./admission-policies/
```

---

### `yamlr idp-export`
Exports manifest health scores and metadata into Internal Developer Portal formats such as Spotify Backstage or Port.

```bash
yamlr idp-export --format backstage
```

---

## System Administration & Setup

### `yamlr init`
Scaffolds a `.yamlr.yaml` configuration file in the root of the repository with sensible defaults, target schema versions, and rule toggles.

```bash
yamlr init
```

---

### `yamlr guide`
Interactive terminal tour of Yamlr's forensic rules, zero-comment-loss healing architecture, and GitOps workflows.

```bash
yamlr guide [TOPIC]
```

#### Supported Topics
- `security` (or `sec`): Deep dive into container hardening and CIS Benchmark rules.
- `network` (or `net`): Ingress routing contracts, Gateway API, and service selectors.
- `gitops`: Sync-wave ordering and atomic WAL rollback journals.
- `rules` (or `catalog`): Overview of all 53+ built-in forensic rules across 6 core pillars.

```bash
# Explore container security best practices in terminal
yamlr guide security
```

---

### `yamlr features`
Outputs the complete registry of all 21 autonomous healing stages, their security tiers (`S0` safe, `S1` preview, `S2` apply), and safety defaults.

```bash
yamlr features
```

---

### `yamlr admin`
Administrative subcommands for engine maintenance and CI runner hygiene.

```bash
yamlr admin <SUBCOMMAND>
```

#### Subcommands
- `cache-clear`: Purges the local cached external CRD schemas and temporary AST tables.
- `journal-prune`: Prunes stale `.yamlr_journal_*.wal` rollback snapshot files.
- `config-reset`: Safely resets workspace `.yamlr.yaml` configuration file to default state.

#### Examples
```bash
# Clean cached schemas on a long-running CI runner
yamlr admin cache-clear

# Clean old rollback journals
yamlr admin journal-prune
```

---

### `yamlr auth` & `yamlr subscribe`
Manages commercial Team and Enterprise license activations. Designed to operate completely offline in air-gapped enclaves without external network callbacks.

```bash
# Check current entitlement status
yamlr auth status
yamlr subscribe

# Activate offline signed license token
yamlr auth activate <SIGNED_LICENSE_TOKEN>
yamlr subscribe --key <SIGNED_LICENSE_TOKEN>
```

---

### `yamlr upgrade`
Checks current binary version and prints verified offline download and release verification guidance.

```bash
yamlr upgrade
```

---

### `yamlr completion`
Generates native shell completion scripts for all major shells.

```bash
yamlr completion <bash | zsh | fish | powershell>
```

#### Installation Instructions
```bash
# Bash (Linux/macOS)
yamlr completion bash > /etc/bash_completion.d/yamlr

# Zsh
yamlr completion zsh > ~/.zsh/completion/_yamlr

# Fish
yamlr completion fish > ~/.config/fish/completions/yamlr.fish

# PowerShell (Windows / pwsh)
yamlr completion powershell | Out-String | Invoke-Expression
```

---

### `yamlr install`
Displays hermetic installation instructions or automatically installs a native Git pre-commit hook into the current repository.

```bash
# Install automatic zero-dependency pre-commit hook in .git/hooks/pre-commit
yamlr install --git-hook

# Display installation guide
yamlr install
```

---

### `yamlr manual` / `yamlr man`
Renders the built-in Unix man page (`man 1 yamlr`) directly in your terminal.

```bash
yamlr manual
yamlr man
```

---

### `yamlr welcome` & `yamlr demo`
Interactive onboarding commands for new developers and instant live demonstrations of comment-preserving remediation.

```bash
yamlr welcome
yamlr demo
```
