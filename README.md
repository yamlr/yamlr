# Yamlr

**Configuration errors that break production.**

Yamlr is the Autonomous Manifest Control Plane. It provides semantic safety nets for Kubernetes by detecting and actively healing structural and relational errors before they reach your cluster.

## Features

- **Schema-Grounded Remediation**: Not just a linter. Yamlr actively heals non-compliant manifests.
- **Cross-Resource Graph Validation**: Detect ghost services, broken volumes, and port mismatches across your entire repository.
- **Signed Binary Distribution**: Zero dependencies. C-compiled for speed and security.
- **Local-First Execution**: Zero data egress. Your IP never leaves your machine or your CI runner.

## Quick Install (macOS / Linux)

```bash
curl -fsSL https://yamlr.dev/install.sh | bash
```

## Windows Installation

Download the latest standalone executable from the [Releases page](https://github.com/yamlr/yamlr/releases). Add the folder to your `PATH` for global CLI access.

## Getting Started

Initialize the engine in your repository:
```bash
yamlr init
```

Scan for production failures:
```bash
yamlr scan .
```

Auto-heal safe configuration errors:
```bash
yamlr heal .
```

## Documentation

Read the full architecture and technical guide at [yamlr.dev/docs](https://yamlr.dev/docs).

## License

Yamlr is a commercial product. The core CLI is available for free individual use under the terms of the Yamlr End User License Agreement (EULA), available inside the binary. Enterprise use and CI/CD organizational enforcement require a Pro license. See [yamlr.dev/pricing](https://yamlr.dev/pricing) for details.
