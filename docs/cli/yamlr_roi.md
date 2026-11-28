# yamlr roi

**Manifest Quality & Engineering Impact Analysis**

Displays verified manifest health metrics, defect remediation impact, and reliability statistics computed across Kubernetes workspaces.

## Usage
```bash
yamlr roi [PATH] [FLAGS]
yamlr impact [PATH] [FLAGS]
```

## Description
The `roi` command (aliased to `impact`) provides factual engineering analytics on the reliability value delivered by Yamlr's automated manifest parsing and remediation engine. Rather than using speculative financial models, Yamlr measures direct technical outcomes across syntax, schema, and relational topology.

## Flags
*   `-h, --help`: Show this help message.
*   `--output=json`: Output statistics as machine-readable structured JSON.
*   `--verbose`: Full execution breakdown of analyzed resources.
*   `-q`, `--quiet`: Minimal output mode (exit codes only).

## Metrics Displayed
*   **Manifests Analyzed**: Total Kubernetes manifest files discovered and ingested.
*   **Documents Parsed**: Discrete YAML document streams partitioned and validated.
*   **Outages Prevented**: Critical cross-resource link failures (e.g. dangling Service selectors, orphaned Ingress backends, broken ConfigMap/Secret references) intercepted before cluster deployment.
*   **Violations Remediated**: Schema errors, missing required fields, and policy violations safely fixed.
*   **API Deprecations Upgraded**: Obsolete Kubernetes API versions automatically transitioned to stable counterparts.
*   **Integrity Risk Mitigated**: Cumulative severity-weighted risk reduction score.

## Examples
```bash
# View workspace manifest quality and impact
yamlr roi ./k8s

# Export factual impact metrics for CI reporting or observability
yamlr roi ./k8s --output=json
```

---
*Note: All telemetry is computed hermetically and locally from manifest AST and topological graphs. Zero data egress.*
