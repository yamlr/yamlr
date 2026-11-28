# yamlr verify
**Cryptographic Manifest Signature Verification**

The `yamlr verify` command verifies the cryptographic non-repudiation signature and Semantic DNA integrity of signed Kubernetes manifests `[Pro]`.

---

## Synopsis

```bash
yamlr verify [path] [flags]
```

---

## Description

The `verify` command provides a supply-chain trust anchor for GitOps and regulated enterprise environments (SOC2, HIPAA, PCI-DSS).

Yamlr embeds a cryptographic signature directly into `metadata.annotations['yamlr.dev/signature']`. When `yamlr verify` is run:
1. It canonicalizes the manifest AST on disk.
2. Extracts and verifies the cryptographic signature against the embedded or local public key.
3. Mathematically proves that the manifest has not been modified or tampered with since it was signed.

---

## Examples

```bash
# Verify all signed manifests in the current directory
yamlr verify .

# Verify a specific signed manifest
yamlr verify deployment.yaml

# Verify in CI/CD pipeline gate (blocks merge on tampering)
yamlr verify ./manifests/prod/
```

---

## Options & Flags

*   **`path`** *(positional, optional)*:  
    Path to manifest file or directory of manifests. Defaults to `.`.
*   **`--k8s-version <VERSION>`**:  
    Target Kubernetes schema version context.
*   **`-f, --output-file <PATH>`**:  
    Path to write verification report (JSON).
*   **`--exit-zero`**:  
    Exit with code `0` even if verification fails.

---

## Exit Codes

*   **`0`** (`EXIT_SUCCESS`): Manifest signatures are cryptographically valid.
*   **`1`** (`EXIT_VIOLATIONS`): Signature mismatch, manifest tampered, or unsigned.
*   **`4`** (`EXIT_SYSTEM_ERROR`): File I/O failure or missing manifest.

---

## See Also

*   [`yamlr sign`](yamlr_sign.md) — Cryptographically sign manifests with DNA receipts.
*   [`yamlr dna`](yamlr_dna.md) — Inspect raw semantic AST fingerprints.
*   [`yamlr evidence`](yamlr_evidence.md) — Package cryptographic audit bundles.

