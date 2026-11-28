# yamlr version

Display the version information for the Yamlr CLI and Core Engine.

## Usage
```bash
yamlr version
# OR
yamlr --version
```

## Description
The `version` command provides detailed information about the current installation, including:
- **CLI Version**: The version of the command-line interface.
- **Engine Version**: The version of the underlying healing engine.
- **Build Hash**: The Git commit hash or build identifier.
- **Native Target**: The platform architectures (e.g., windows-amd64).

## Examples
```bash
$ yamlr version
Yamlr v1.1.0-hardened
Core Engine: v1.0.4
Build: 20260213.1
Target: windows-amd64 (Native)
```
