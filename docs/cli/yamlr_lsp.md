# yamlr lsp
**Language Server Protocol (LSP) Engine (PRO)**

The `yamlr lsp` command starts the LSP Server. This allows IDEs (like VS Code) to leverage Yamlr's forensic analysis and interactive healing directly in the editor.

## Usage

```bash
# Start the LSP server (Stdio mode)
yamlr lsp
```

## IDE Integration

The LSP server is the "Language Server Proxy" that powers the **Yamlr VS Code Extension**. It provides real-time feedback for:
- **Schema Violations**: Instant squiggles for invalid K8s types.
- **Surgical Healing**: Quick-fixes for missing probes, limits, and resource gaps.
- **Forensic Highlighting**: Specialized syntax highlighting for broken manifest shards.

## Protocols

### 1. Stdio Transport
By default, the LSP server communicates via Standard I/O, which is the standard for extension-to-binary communication.

### 2. Forensic Mode
When connected to an IDE, the engine operates in an incremental mode, analyzing only the active buffer to maintain sub-500ms latency.

---

> [!NOTE]
> The LSP server is intended to be started automatically by the Yamlr VS Code Extension. Manual execution is primarily used for debugging and CI integration tests.

> [!IMPORTANT]
> Real-time IDE forensics require a [PRO] license.
