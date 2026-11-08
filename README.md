<p align="center">
  <img src="https://raw.githubusercontent.com/yamlr/yamlr/main/assets/yamlr-banner.png" alt="Yamlr Banner" width="600" onerror="this.style.display='none'"/>
</p>

# Yamlr

[![Release](https://img.shields.io/github/v/release/yamlr/yamlr?style=flat-square&color=blue)](https://github.com/yamlr/yamlr/releases)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-orange?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey?style=flat-square)]()
[![Documentation](https://img.shields.io/badge/Docs-yamlr.dev-blueviolet?style=flat-square)](https://yamlr.dev/docs)

**Yamlr is the Autonomous Kubernetes YAML Healing & Schema Enforcement Engine.**

Yamlr detects and **actively heals** configuration errors, schema deviations, and cross-resource linkage defects (broken Services, ghost PVCs, mismatched labels/ports) **before** they reach your cluster.

Unlike conventional linters that only print warnings, Yamlr:
- 🩹 **Auto-heals** broken manifests while preserving **comments**, whitespace, and indentation.
- ⚡ Runs **100% offline & local-first** with sub-millisecond native execution (Rust core).
- 🔒 **Zero telemetry or egress**: your infrastructure manifests never leave your machine or CI runner.
- 🤖 Native **Model Context Protocol (MCP)** server built-in for AI coding assistants (Claude Code, Cursor, Windsurf).

---

## 🚀 Quick Install

### macOS / Linux (Official Shell Installer)

`ash
curl -fsSL https://get.yamlr.dev/install.sh | bash
`
*Or download directly from GitHub Releases:*
`ash
YAMLR_REPO="yamlr/yamlr" YAMLR_VERSION="v0.1.0" sh -c "#!/usr/bin/env bash  set -e  REPO="yamlr/yamlr" INSTALL_DIR="/usr/local/bin" BIN_NAME="yamlr"  echo "Downloading latest Yamlr release..."  # Get latest release tag API_URL="https://api.github.com/repos/$REPO/releases/latest" LATEST_TAG=$(curl -sL $API_URL | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')  if [ -z "$LATEST_TAG" ]; then     echo "Error: Could not determine latest release tag."     exit 1 fi  echo "Latest tag: $LATEST_TAG"  # Determine OS and Arch OS=$(uname -s | tr '[:upper:]' '[:lower:]') ARCH=$(uname -m) if [ "$ARCH" = "x86_64" ]; then ARCH="amd64"; fi if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then ARCH="arm64"; fi  # Current Nuitka matrix maps everything to amd64/x86_64 for simplicity, but script handles logic FILE_NAME="yamlr-${LATEST_TAG}-${OS}-amd64.tar.gz" DOWNLOAD_URL="https://github.com/$REPO/releases/download/$LATEST_TAG/$FILE_NAME"  echo "Downloading $DOWNLOAD_URL ..." curl -fsSL -o "/tmp/$FILE_NAME" "$DOWNLOAD_URL"  echo "Extracting telemetry..." tar -xzf "/tmp/$FILE_NAME" -C "/tmp"  echo "Installing to $INSTALL_DIR (requires sudo)..." sudo mv "/tmp/$BIN_NAME" "$INSTALL_DIR/$BIN_NAME" sudo chmod +x "$INSTALL_DIR/$BIN_NAME"  # Cleanup rm -f "/tmp/$FILE_NAME"  echo "" echo "✅ Yamlr Installed Successfully!" echo "Run 'yamlr welcome' to get started.""
`

### Homebrew (macOS / Linux)

`ash
brew install yamlr/tap/yamlr
`

### Windows (PowerShell)

Download yamlr-windows-x86_64.zip directly from the [Releases page](https://github.com/yamlr/yamlr/releases/latest), unpack yamlr.exe, and add to your PATH.

---

## ⚡ 60-Second Quick Start

`ash
# 1. Initialize Yamlr in your Kubernetes repo
yamlr init

# 2. Perform a read-only clinical scan across all manifests
yamlr scan .

# 3. Preview auto-remediation diff (without modifying files)
yamlr heal . --dry-run

# 4. Safely apply deterministic, comment-preserving fixes
yamlr heal . --apply
`

---

## 🤖 AI Agent MCP Integration (Claude Code, Cursor, Windsurf)

Yamlr includes a built-in Model Context Protocol (MCP) server so your AI agent can audit and heal manifests directly in IDE:

`ash
# Register Yamlr MCP server in Claude Desktop / Claude Code
yamlr mcp --install-config
`

---

## 📚 Documentation & Guides

Explore detailed guides in [docs/](docs/):
- **[Getting Started Guide](docs/guides/GETTING_STARTED.md)**
- **[CLI Reference](docs/reference/CLI_REFERENCE.md)**
- **[Pre-Commit Hook Integration](docs/guides/PRE_COMMIT_GUIDE.md)**
- **[GitOps / CI/CD Integration (GitHub Actions, ArgoCD, Flux)](docs/guides/CI_CD_INTEGRATION.md)**
- **[AI Agent MCP Guide](docs/guides/AI_AGENT_MCP_GUIDE.md)**
- **[Configuration Specification](docs/reference/CONFIGURATION.md)**

---

## ⚖️ License

Yamlr CLI is distributed under the Yamlr Software License. The engine is free for individual developers, local evaluation, and open-source workflows. Enterprise teams, multi-node automation, and CI/CD organizational enforcement require an Enterprise License. See [yamlr.dev/pricing](https://yamlr.dev/pricing) for details.
