# yamlr status

**Health Dashboard**

Displays an SRE-focused dashboard of the current workspace and system health.

## Usage
```bash
yamlr status [FLAGS]
```

## Flags
*   `--kube-version`: Force a specific Kubernetes version (e.g., `1.31`).
*   `--output=json`: Output dashboard as structured JSON.

## Output
*   **Configuration**: Path to `.yamlr.yaml`, active rules count.
*   **Catalog**: Active Kubernetes schema version and path.
*   **Backups**: Disk usage and file count in `.yamlr/backups`.
*   **Scientific HAS**: Health-as-a-Service scores (Lexical, Schema, Semantic).
*   **System Vitality Index**: Enterprise-grade trust aggregation (Shield Engine).
*   **Onboarding Checklist**: Dynamic status of project setup and completion.
*   **Authentication**: Current User/Pro identity and license status.

## Examples
```bash
yamlr status
```
