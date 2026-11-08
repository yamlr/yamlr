# yamlr upgrade
**Release Upgrade & Offline Token Management**

The `yamlr upgrade` command displays offline release upgrade instructions and guides teams on updating the native binary and offline license entitlements.

> [!NOTE]
> **Kubernetes API Migrations:** To modernize deprecated Kubernetes API versions (e.g., `extensions/v1beta1` -> `apps/v1`, Ingress migrations), use the dedicated [`yamlr migrate`](yamlr_migrate.md) command.

## Usage

```bash
# Display upgrade instructions and release check
yamlr upgrade

# Check active license and upgrade options
yamlr subscribe
```

## Options & Flags

* `-h, --help`: Display help information.

## Upgrading the Standalone Binary

Yamlr is distributed as a single standalone native binary. To upgrade:

### Homebrew (macOS & Linux)
```bash
brew update && brew upgrade yamlr/tap/yamlr
```

### GitHub Releases (Direct Download)
Download the latest pre-compiled archive for your architecture:
* Linux x86_64: `yamlr-linux-x86_64.tar.gz`
* Linux aarch64: `yamlr-linux-aarch64.tar.gz`
* macOS Apple Silicon: `yamlr-macos-aarch64.tar.gz`
* macOS Intel: `yamlr-macos-x86_64.tar.gz`
* Windows x64: `yamlr-windows-x86_64.zip`

Extract and overwrite your existing `yamlr` binary. No system dependencies or runtime packages are required.

## Related Commands

* [`yamlr migrate`](yamlr_migrate.md) — Modernize deprecated Kubernetes API versions.
* [`yamlr auth`](yamlr_auth.md) — Inspect or activate air-gapped signed license tokens.
* [`yamlr version`](yamlr_version.md) — Show current binary version and architecture.
