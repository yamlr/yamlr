# yamlr demo

**Interactive Demo Generator**

Scaffolds a `yamlr-demo/` directory containing intentionally broken manifests. This is designed for first-time users to safely test `yamlr scan` and `yamlr heal` without risking their own files.

## Usage
```bash
yamlr demo
```

## Description
Creates:
*   `yamlr-demo/broken-deployment.yaml`: Syntax errors, missing selectors.
*   `yamlr-demo/legacy-ingress.yaml`: Deprecated APIs.
*   `yamlr-demo/.yamlr.yaml`: Sample config.

## Examples
```bash
yamlr demo
cd yamlr-demo
yamlr scan .
yamlr heal .
```
