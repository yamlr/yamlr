# yamlr evidence
**Export Cryptographic Compliance Audit Evidence Bundle**

The `yamlr evidence` command aggregates cryptographic manifest DNA fingerprints, Write-Ahead Log (WAL) remediation receipts, and engine environment states into a verifiable, auditor-ready evidence bundle archive.

This enterprise feature provides mathematical proof of manifest provenance, tamper-detection, and change tracking for SOC2, HIPAA, and CIS compliance audits.

## Usage

```bash
# Export evidence bundle for current workspace
yamlr evidence .

# Export bundle to custom tarball path
yamlr evidence ./k8s -o compliance-evidence.tar.gz

# Export evidence summary as structured JSON
yamlr evidence ./manifests --json
```

## Options & Flags

### Positional Arguments
* `[PATH]`: Workspace root or directory containing manifests and journals (defaults to `.`).

### Output Controls
* `-o, --output <PATH>`: Destination archive file path. Defaults to `yamlr-evidence.tar.gz`.
* `-j, --json`: Emit evidence summary as structured JSON to stdout instead of packaging an archive.

## Evidence Bundle Contents

The exported bundle (`.tar.gz`) contains:
1. **Remediation WAL Journal**: Immutable event logs of every automated change applied by `yamlr heal`.
2. **Cryptographic DNA Fingerprints**: SHA-256 structural DNA records for before-and-after manifest states.
3. **Audit Results**: Findings from CIS benchmark and schema conformity checks.
4. **Attestation Metadata**: Timestamp, binary version, architecture, and operator identity.

## Exit Codes

* `0` (`EXIT_SUCCESS`): Evidence bundle generated and exported successfully.
* `1` (`EXIT_VIOLATIONS`): Violations or integrity discrepancies encountered during bundle assembly.
* `124` (`EXIT_SYSTEM_ERROR`): File I/O or archive creation failure.

## Related Commands

* [`yamlr dna`](yamlr_dna.md) — Generate structural DNA fingerprints of manifests.
* [`yamlr sign`](yamlr_sign.md) — Cryptographically sign manifests with HMAC-SHA256.
* [`yamlr verify`](yamlr_verify.md) — Forensically verify manifest signatures against tampering.
