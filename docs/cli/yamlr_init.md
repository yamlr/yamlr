# yamlr init

**Project Initialization**

Scaffolds a new `.yamlr.yaml` configuration file in the current directory.

## Usage
```bash
yamlr init
```

## Options
*   `--force`: Overwrite existing `.yamlr.yaml` file.
*   `--output FORMAT`: Report format (text, json).

## Description
*   Detects if a `.yamlr.yaml` already exists.
*   Detects connected Kubernetes cluster version (if `kubectl` is available) and presets `cluster_version`.
*   Writes a commented default configuration file.

## Examples
```bash
cd my-repo
yamlr init
```
