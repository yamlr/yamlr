# yamlr mcp

Start the Yamlr Model Context Protocol (MCP) server.

## Why 
MCP is an open protocol for connecting development environments and developer tools to precision language engines. By running Yamlr as an MCP server, you enable editor integrations (such as VS Code, Neovim, JetBrains, or automated dev tools) to perform surgical Kubernetes manifest analysis and healing with 100% deterministic safety.

## Usage
```bash
yamlr mcp [OPTIONS]
```

## Options

### `--transport` (default: `stdio`)
The transport protocol to use for communication.
- `stdio`: standard input/output (recommended for IDE integrations).
- `http`: (Not yet implemented in v1.1).

### `--port` (default: `8000`)
The port to listen on when using HTTP transport.

## MCP Tools Exposed

### 🔍 `scan_manifest`
Performs a deep safety audit of a directory or single manifest.
- **Input**: `path` (string)
- **Output**: A safety report containing:
    - **Rule ID**: Unique identifier for the violation.
    - **Rationale**: An architectural explanation of why the fix is necessary.
    - **Impact Description**: The real-world consequence of ignoring the issue.
    - **Risk Level**: High/Medium/Low assessment.

### 🔧 `heal_manifest`
Applies surgical repairs to Kubernetes manifests.
- **Input**: `path` (string), `rules` (optional list of Rule IDs to filter).
- **Output**: A transaction receipt showing exactly what was changed and a SHA-256 DNA proof of intent preservation.

### ❓ `why`
Provides deep architectural context for any Yamlr Rule ID.
- **Input**: `rule_id` (string)
- **Output**: A comprehensive explanation of the security or operational logic behind the rule.

## IDE Integration Configuration Example

To connect Yamlr to your IDE or MCP client, add the following to your MCP client configuration:

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

## Safety Guardrails
- **Read-Only by Default**: The `scan_manifest` tool never modifies files.
- **DNA Receipts**: Every `heal_manifest` call generates a cryptographic proof that nothing outside the intended fix was altered.
- **Deterministic**: Unlike raw LLM suggestions, Yamlr's MCP tools are strictly deterministic and schema-validated.

### Universal Expert Flags
Available across primary commands:

*   **`--timing`**: [PERFORMANCE] Output surgical execution timing breakdown.
*   **`--timing-file <FILE>`**: [PERFORMANCE] Save performance profiling data to a JSON file.
*   **`--verbose`**: Full audit logs and engine stages.
*   `-q`, `--quiet`: Minimal output mode (exit codes only).
