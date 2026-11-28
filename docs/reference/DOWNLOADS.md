# Download Yamlr

## ⬇️ Download Binaries

Standalone binaries are available for Windows, Linux, and macOS. These are the **only** supported way to run Yamlr Pro and ensure 100% compatibility with our security engine.

### Package Managers (Official)
We are currently rolling out to official repositories:
*   **macOS/Linux:** `brew install yamlr/tap/yamlr`
*   **Windows:** `choco install yamlr`

### Manual Download
Download the latest executable for your platform. No Python required.

| Platform | Arch | Distribution Asset |
| :--- | :--- | :--- |
| **Windows** | `x86_64` | [yamlr-windows-x86_64.zip](https://github.com/yamlr/yamlr/releases/latest/download/yamlr-windows-x86_64.zip) |
| **Linux** | `x86_64` (musl) | [yamlr-linux-x86_64.tar.gz](https://github.com/yamlr/yamlr/releases/latest/download/yamlr-linux-x86_64.tar.gz) |
| **Linux** | `aarch64` (musl) | [yamlr-linux-aarch64.tar.gz](https://github.com/yamlr/yamlr/releases/latest/download/yamlr-linux-aarch64.tar.gz) |
| **macOS** | `aarch64` (Apple Silicon) | [yamlr-macos-aarch64.tar.gz](https://github.com/yamlr/yamlr/releases/latest/download/yamlr-macos-aarch64.tar.gz) |
| **macOS** | `x86_64` (Intel) | [yamlr-macos-x86_64.tar.gz](https://github.com/yamlr/yamlr/releases/latest/download/yamlr-macos-x86_64.tar.gz) |

### ⚡ Quick Start (Windows)
1.  Download `yamlr.exe`.
2.  Move it to a folder (e.g., `C:\Program Files\Yamlr`).
3.  **Add that folder to your PATH environment variable.**
4.  Open a new terminal and type:
    ```powershell
    yamlr scan .
    ```

```bash
docker pull ghcr.io/yamlr/yamlr:latest
```
