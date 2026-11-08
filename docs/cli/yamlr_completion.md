# yamlr completion

**Shell Autocomplete Generator**

Generates shell completion scripts for Bash, Zsh, Fish, and PowerShell.

## Usage
```bash
yamlr completion [SHELL] [--install]
```

## Options
*   `--install`: Automatically install the completion script to your shell profile (e.g., `.bashrc`, `.zshrc`).
*   `--word TEXT`: (Internal) The current word being completed.
*   `--position INT`: (Internal) The cursor position in the line.

## Description
Outputs the completion script to stdout. You should source this script in your shell profile.

## Examples

**Bash:**
```bash
source <(yamlr completion bash)
```

**Zsh:**
```bash
source <(yamlr completion zsh)
```

**PowerShell:**
```powershell
yamlr completion powershell | Out-String | Invoke-Expression
```
