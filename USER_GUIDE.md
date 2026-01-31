# Yamlr / yamlr User Guide

**Yamlr** is a high-fidelity Kubernetes manifest healer and diagnostics tool.  
It identifies logical errors, deprecated APIs, and security risks—then fixes them automatically.

## 🚀 Installation

### 1. Build & Install (Recommended)
This method installs the binary to `~/.local/bin` (or `/usr/local/bin` if run with sudo) so you can run `yamlr` from anywhere.

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Build & Auto-Install
python3 build.py
```
*Note: Ensure `~/.local/bin` is in your `$PATH`.*

### 2. Autocompletion Setup
Enable tab-completion for commands and flags:

**Bash / Zsh:**
```bash
# Add to ~/.bashrc or ~/.zshrc
source <(yamlr completion bash)
```

**PowerShell:**
```powershell
yamlr completion powershell | Out-String | Invoke-Expression
```

---

## 🎭 Dual Identity
This tool has two modes depending on how you call it:

| Command | Identity | Description |
| :--- | :--- | :--- |
| **`yamlr`** | **OSS Mode** | Free for life. Infinite scans. Best-effort healing. |
| **`yamlr`** | **Pro Mode** | Requires license. Unlocks security hardening & compliance reports. |

*Note: Both commands are aliases for the same underlying engine.*

---

## 🛠️ Core Commands

### 1. Scan (Read-Only)
Audit your manifests without making changes.
*   **Default Behavior:** Returns `Exit Code 1` if issues are found.
*   **Multi-Target:** Can scan specific files, directories, or a mix of both.

```bash
# Scan current directory (Implicit recursive)
yamlr scan .

# Scan specific files
yamlr scan deployment.yaml service.yaml

# Mixed mode (Files & Dirs) - Batch Reporting
yamlr scan ./prod-manifests/ ./new-service.yaml

# Scan from stdin (CI/CD pipeline)
cat deployment.yaml | yamlr scan -

# Preview fixes (Dry Run)
yamlr scan . --dry-run
# Alias: yamlr scan . --diff
```

**Report Modes:**
*   **Detailed View:** Automatically shown when scanning a single file.
*   **Summary Table:** Automatically shown when scanning multiple targets.

### 2. Heal (Fix Issues)
Automatically repair syntax, logic, and style issues.

```bash
# Interactive Mode (Single File) - Shows diff & asks for confirmation
yamlr heal deployment.yaml

# Batch Mode (Multi-Target) - Global Confirmation
yamlr heal ./manifests/ file1.yaml file2.yaml

# Dry Run (Preview changes without writing)
yamlr heal . --dry-run
# Alias: yamlr heal . --diff

# Auto-Approve (CI/CD)
yamlr heal broken.yaml -y
yamlr heal ./manifests --yes-all
```

**Safety Interlocks:**
*   **Interactive Mode:** Used when healing a single file. Shows visual diff. Defaults to "No".
*   **Batch Mode:** Used when healing multiple files or directories. Shows summary table. Requires typing `CONFIRM`.

### 3. Initialize Project
Create a default configuration file (`.yamlr.yaml`):
```bash
yamlr init
```

### 4. Explain Rules
Get detailed documentation for any violation ID.
```bash
yamlr explain rules/no-latest-tag
```

---

## ⚙️ Configuration (`.yamlr.yaml`)
Customize behavior globally or per-project.

```yaml
rules:
  threshold: 80         # fail if health score < 80
  
ignore:
  files:
    - "vendor/**"       # Ignore third-party charts
    - "tests/*.yaml"
```

## 🆘 Troubleshooting

**Q: "Missing Required Argument: path"**
A: `yamlr scan` and `yamlr heal` are strict. You must specify a target (e.g., `yamlr scan .`).

**Q: My CI pipeline passes even when files are broken?**
A: Ensure you are using `yamlr scan`, which returns Exit Code 1 on failure.

**Q: How do I upgrade to Pro?**
A: Run `yamlr auth --login <LICENSE_KEY>` to activate yamlr Enterprise features.
