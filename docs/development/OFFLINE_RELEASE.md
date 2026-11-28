# Provider-independent native release path

Build and verify candidates locally. This path uses Git, Cargo, Python, and
`cryptography`; packaging and verification make no hosted-service calls. It does
not replace platform smoke tests or third-party redistribution review.

## Build and assemble evidence

```sh
cargo test --locked --manifest-path native_core/Cargo.toml
cargo build --locked --release --manifest-path native_core/Cargo.toml --bin yamlr
python scripts/ci/smoke_binary.py native_core/target/release/yamlr
```

On Windows, use `yamlr.exe`. Generate reviewed third-party notices with the
existing cargo-about configuration and a CycloneDX SBOM with the release SBOM
tooling. Supply those real files; the packager checks format/presence, which is
not a legal review or proof that the inventory is complete.

Use a dedicated Ed25519 release-signing key held outside the repository. Do not
reuse the license-signing key. Distribute its public key through an independently
trusted channel; a public key downloaded beside an artifact is not a trust root.
This change does not create or authorize any production signing identity.

```sh
python scripts/ci/offline_release.py package --binary native_core/target/release/yamlr --license-file LICENSE --notices THIRD_PARTY_NOTICES_RUST.txt --sbom release-sbom.cdx.json --signing-key /secure/release-signing.pem --output native_core/target/offline-release --version v0.1.0 --target linux-x86_64 --revision YOUR_EXACT_GIT_REVISION
```

The production CLI requires the current clean Git revision. Existing development
changes must be reviewed and captured first; do not reset them to satisfy this
check. For explicitly labelled development candidates use `--profile debug` and
`--source-dirty` as appropriate. Their verification requires
`--allow-development` and is not production acceptance.

## Verify before installation

Copy the ZIP, its `.manifest.json`, and `.manifest.sig` by any transport. Pin the
expected version and target and supply a separately trusted public key:

```sh
python scripts/ci/offline_release.py verify --archive yamlr-v0.1.0-linux-x86_64.zip --manifest yamlr-v0.1.0-linux-x86_64.manifest.json --signature yamlr-v0.1.0-linux-x86_64.manifest.sig --trusted-key /trusted/yamlr-release-public.pem --version v0.1.0 --target linux-x86_64
```

Verification checks the Ed25519 manifest signature, expected version/target,
archive name/size/SHA-256, and production/development policy. Only after successful
verification extract the ZIP and install the binary. The four archive members
are the root executable, LICENSE, third-party notices, and the SBOM. No GitHub
CLI or hosted identity/billing service is involved.

Archives use fixed member timestamps and permissions. Existing candidates are
never overwritten, and the private-key artifact guard runs before signing.
The signed source/profile fields are producer declarations, not an independent
build attestation; release gate results and platform evidence remain necessary.
Production key custody, rotation, and reviewer approval remain operational work.

Tests use disposable development keys and fixture files. They verify valid
signatures, tampering rejection, wrong keys/version/target, development-policy
rejection, no overwrite, private-key exclusion, and deterministic packaging.
They do not establish that a production release has been built or reviewed.
