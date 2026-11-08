# yamlr install
**Automated CI/CD Workflow & Git Hook Installer**

The `yamlr install` command installs automated Yamlr enforcement integrations directly into your Git workspace.

---

## Synopsis

```bash
yamlr install {hook|action} [flags]
```

---

## Targets

### 1. `hook`
Installs a zero-latency Git pre-commit hook into `.git/hooks/pre-commit`.
```bash
yamlr install hook
```
Every commit will automatically trigger a sub-50ms audit across staged manifests, preventing invalid YAML and schema regressions from entering git history.

### 2. `action`
Generates an official GitHub Actions workflow template at `.github/workflows/yamlr-safety.yml`.
```bash
yamlr install action
```
Automatically audits pull requests, generates SARIF reports for the GitHub Code Scanning tab, and blocks merges on critical defect thresholds.

---

## Examples

```bash
# Protect every local commit with a pre-commit guard
yamlr install hook

# Add Yamlr auditing to your GitHub Actions CI pipeline
yamlr install action
```
