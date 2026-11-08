# yamlr sign
**Cryptographic Manifest Signing & DNA Receipt Embedding**

The `yamlr sign` command signs Kubernetes manifests with cryptographic non-repudiation signatures embedded directly into the manifest metadata annotations `[Pro]`.

---

## Synopsis

```bash
yamlr sign [path] [flags]
```

---

## Description

`yamlr sign` guarantees supply-chain provenance. It computes the deterministic Semantic DNA hash of the Kubernetes resource AST, signs the digest using local private keys, and records the signature in `metadata.annotations['yamlr.dev/signature']`.

Downstream CI/CD pipelines, GitOps sync processes, and admission webhooks can verify the signature using `yamlr verify` to ensure zero unauthorized alterations occurred.

---

## Examples

```bash
# Sign all manifests in the current directory
yamlr sign .

# Sign a specific deployment manifest
yamlr sign ./k8s/deployment.yaml
```

---

## Options & Flags

*   **`path`** *(positional, optional)*:  
    Path to manifest file or directory to sign. Defaults to `.`.
*   **`--k8s-version <VERSION>`**:  
    Target Kubernetes schema version context.
*   **`-f, --output-file <PATH>`**:  
    Path to write signature report (JSON).
*   **`--exit-zero`**:  
    Always exit with code `0`.

---

## See Also

*   [`yamlr verify`](yamlr_verify.md) — Cryptographically verify signed manifests.
*   [`yamlr dna`](yamlr_dna.md) — Inspect raw semantic AST fingerprints.
*   [`yamlr evidence`](yamlr_evidence.md) — Package cryptographic audit bundles.
