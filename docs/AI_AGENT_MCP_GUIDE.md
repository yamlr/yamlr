# 🔌 Yamlr Model Context Protocol (MCP) Integration Guide
**The Autonomous Safety Compiler for AI Coding Agents (Cursor, Claude Desktop, Windsurf, AGY)**

> [!IMPORTANT]
> **Why AI Agents Need Yamlr:**  
> Large Language Models (LLMs) hallucinate Kubernetes configurations: they invent retired API versions, mangle numeric resource units, strip developer comments, and introduce severe indentation errors.  
> Yamlr provides a sub-5ms, air-gapped, deterministic JSON-RPC MCP server over `stdio` that acts as an in-memory safety gate before AI agents present or commit manifests.

---

## ⚡ 1-Minute Quick Start

### Step 1: Install Yamlr Native Engine
Ensure `yamlr` is installed and available on your system `PATH`:

```bash
# macOS & Linux via Homebrew
brew install yamlr/tap/yamlr

# Or direct native installer (Linux / macOS)
curl -fsSL https://get.yamlr.dev/install.sh | sh

# Windows (PowerShell)
irm https://get.yamlr.dev/install.ps1 | iex
```

Verify installation:
```bash
yamlr --version
# Output: yamlr 0.1.3 (or latest)
```

---

## 🛠️ Client Configuration

### 1. Cursor IDE Setup

#### Option A: Workspace Configuration (Recommended for Teams)
Create `.cursor/mcp.json` in your repository root:
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

#### Option B: Global Cursor Settings
1. Open Cursor **Settings** (`Ctrl+,` or `Cmd+,`).
2. Navigate to **Features** > **MCP**.
3. Click **Add New MCP Server**.
4. Set:
   * **Name:** `yamlr`
   * **Type:** `stdio`
   * **Command:** `yamlr mcp`

---

### 2. Claude Desktop Setup

Open your Claude Desktop configuration file:
* **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
* **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
* **Linux:** `~/.config/Claude/claude_desktop_config.json`

Add the `yamlr` entry to `mcpServers`:

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
Restart Claude Desktop. You will see a hammer icon 🔨 indicating Yamlr tools are active.

---

### 3. Antigravity & Windsurf / Other MCP Clients

Add to your MCP client configuration:
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

To automatically generate and print your exact platform configuration path, run:
```bash
yamlr mcp --install-config
```

---

## 🧰 Tools Exposed to AI Agents

Yamlr exposes two high-performance tools natively over stdio JSON-RPC:

| Tool | Purpose | Arguments | Output |
| :--- | :--- | :--- | :--- |
| `yamlr_scan` | High-speed schema validation and forensic integrity audit. | `manifest` (string, required)<br/>`k8s_version` (string, optional, default `"1.36"`) | JSON containing `status`, `schema_violations`, and `integrity_violations`. |
| `yamlr_heal` | Lossless Concrete Syntax Tree (CST) auto-repair with 100% comment preservation. | `manifest` (string, required) | JSON containing `healed_manifest` and `changed` (boolean). |

---

## 🤖 The "Zero-Hallucination" Cursor & Agent Rule

To force AI agents to automatically validate and heal Kubernetes manifests before showing them to you, add this rule to your repository's `.cursorrules` or `.cursor/rules/k8s-yamlr.mdc`:

```markdown
# Kubernetes Configuration Safety Guardrail

When generating, modifying, or reviewing any Kubernetes YAML manifest:
1. NEVER output unverified Kubernetes YAML directly.
2. ALWAYS invoke the `yamlr_heal` tool on the raw YAML content first to normalize schemas and preserve existing comments.
3. If structural violations remain, invoke `yamlr_scan` to verify against the target Kubernetes OpenAPI version.
4. Only return or save the healed manifest that passes Yamlr verification.
```

---

## 🔒 Security & Privacy Guarantees

* **100% Air-Gapped & Offline:** The Yamlr MCP server executes purely locally in memory. It makes zero outbound network requests and transmits zero bytes of configuration or telemetry.
* **Zero Cluster Access Required:** Executes static and relational schema checks without requiring cluster read or write credentials.
* **Bit-for-Bit CST Preservation:** Untouched syntax nodes, comments, blank lines, and formatting are mathematically preserved.
