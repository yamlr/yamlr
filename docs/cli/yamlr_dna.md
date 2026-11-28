# yamlr dna

Calculate or verify the **Semantic SHA-256 DNA** of a Kubernetes manifest `[Pro]`.

## Usage
```bash
yamlr dna <path> [flags]
```

## Description
The `dna` command is a core component of Yamlr's **Zero-Failure Trust Pillar**. It calculates a cryptographic hash that is invariant to formatting, comments, and field ordering. This allows you to mathematically prove that the *meaning* of a manifest has not changed, even if the file structure has been reformatted or healed.

### Why use Semantic DNA?
- **Drift Detection**: Verify that a manifest in Git matches the intent in your cluster, even if whitespace differs.
- **Healing Integrity**: Prove that `yamlr heal` preserved your original intent while fixing syntax or security issues.
- **CI/CD Gates**: Fail builds if the Semantic DNA changes unexpectedly during a pipeline run.

## Arguments
- `path`: The path to the manifest file (required).

## Flags
- `--hash <SHA-256>`: Expected hash for verification. If the calculated DNA does not match this hash, the command exits with code 1.
- `--output <format>`: Output format. Options: `text` (default), `json`.
- `-h, --help`: Show help for the `dna` command.

## Examples

### Generate Semantic DNA
```bash
yamlr dna deployment.yaml
```

### Verify Integrity in CI/CD
```bash
# This will fail if the semantic meaning of deployment.yaml changes
yamlr dna deployment.yaml --hash 250f0af28fe5f1bc89f88eeb0ac086aa70d6028a955fee7d500336b
```

### Get DNA as JSON
```bash
yamlr dna pod.yaml --output json
```

## See Also
- [yamlr status](yamlr_status.md) - View project-wide health and HAS metrics.
- [yamlr heal](yamlr_heal.md) - Repair manifesting while preserving DNA integrity.
