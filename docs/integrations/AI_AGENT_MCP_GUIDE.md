# 🔌 Yamlr Model Context Protocol (MCP) Server Guide

**What:** Native Tool endpoints enabling IDEs, developer editors, and automated workflows to audit, heal, and reason over Kubernetes manifests.  
**Why:** Standardized JSON-RPC protocol allowing development environments to inspect and generate valid, comment-preserving Kubernetes infrastructure.

---

## 🔌 Configuration

### 1. IDE Configuration (`mcp.json`)

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

### 2. Standalone MCP Client Configuration

```json
{
  "mcpServers": {
    "yamlr": {
      "command": "python",
      "args": ["-m", "yamlr.mcp_server"]
    }
  }
}
```

---

## 🛠 Available MCP Tools

| Tool Name | Purpose | Input Parameters |
|:---|:---|:---|
| `scan_manifests` | Audits YAML for schema & 42 forensic detectors | `{"path": "path/to/manifest.yaml"}` |
| `heal_manifests` | Automatically remediates violations in-place | `{"path": "path/to/manifest.yaml"}` |
| `get_resource_dependencies` | Queries cross-resource relationship graph | `{"path": ".", "kind": "Deployment", "name": "api"}` |
| `get_openapi_schema` | Returns strict OpenAPI schema property rules | `{"kind": "Ingress", "k8s_version": "1.30"}` |
| `propose_infrastructure_mutation` | Dry-runs proposed patches through Yamlr Engine | `{"path": "...", "mutation_patch": "..."}` |
