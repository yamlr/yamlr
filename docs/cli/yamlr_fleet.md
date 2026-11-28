# yamlr fleet
**[PRO] Fleet Intelligence & Multi-Repo GitOps PR Batching**

The `yamlr fleet` command orchestrates manifest audits and automated remediation Pull Requests across fleets of Git repositories.

---

## Synopsis

```bash
yamlr fleet [status|pr-batch] [flags]
```

---

## Description

In enterprise GitOps environments, platform engineering teams manage hundreds of Kubernetes service repositories.

`yamlr fleet` enables platform teams to:
1. Audit defect posture across multiple Git repositories simultaneously.
2. Apply automated schema upgrades and relational repairs across entire fleets.
3. Automatically branch, commit, push, and open Pull Requests via `gh` or `glab` CLI with audit reports attached.

---

## Subcommands

*   **`status`** *(default)*:  
    Inspect the fleet health and defect score across configured repositories.
*   **`pr-batch`**:  
    Execute fleet remediation and batch-generate Pull Requests across target repositories.

---

## Options & Flags

*   **`--repos <PATH>`**:  
    Path to repository manifest file (JSON/YAML listing repos), a single repository path, or a directory containing cloned repositories.
*   **`--branch <BRANCH>`**:  
    Target git branch name for fleet PRs. Defaults to `yamlr/fleet-upgrade`.
*   **`--title <STRING>`**:  
    PR title and commit message. Defaults to `fix(k8s): automated fleet manifest remediation`.
*   **`--apply`**:  
    Apply fixes directly to repositories on disk.
*   **`--dry-run`**:  
    Simulate fleet upgrades without modifying files or committing.
*   **`--create-pr`**:  
    Automatically push branches and open Pull Requests via GitHub CLI (`gh`) or GitLab CLI (`glab`).
*   **`--report <FILE>`**:  
    Path to write markdown fleet audit summary. Defaults to `fleet-report.md`.

---

## Examples

```bash
# Check status across all repositories listed in repos.yaml
yamlr fleet status --repos ./repos.yaml

# Simulate fleet upgrades across multiple repositories (dry-run)
yamlr fleet pr-batch --repos ./repos/ --dry-run

# Apply upgrades and automatically open Pull Requests on GitHub
yamlr fleet pr-batch --repos ./repos.yaml --apply --create-pr --branch "fix/k8s-1.31-upgrade"
```

