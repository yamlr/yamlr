# Source baseline preparation

`scripts/ci/source_snapshot.py` captures an explicit native CLI/Python SDK source
scope, or an expanded all-product development scope, into a deterministic ZIP.
Its manifest lists every included file, byte
size, and SHA-256, plus a digest of the complete ordered inventory.

The source scope includes native source, embedded schemas/catalogs, native tests
and benches, SDK package files, Cargo manifests/lockfile, report schemas, and CI
utilities. `--scope all-product-development-source` adds editor sources and build
metadata, website sources/assets/configuration, infrastructure and billing,
Actions/workflows, wrapper metadata, installers, and selected root build inputs.
This is an explicit candidate policy, not proof that every external build input
or intended distribution file has been captured. Generated executables,
dependency directories, archived Python modules,
and local signing keys are excluded. Named license test fixtures are retained
because Rust tests include them; this source snapshot is not a shipped package.

Capture and verify from the repository root:

```powershell
python scripts/ci/source_snapshot.py capture --output native_core/target/source-review/candidate.zip
python scripts/ci/source_snapshot.py verify native_core/target/source-review/candidate.zip
python scripts/ci/source_snapshot.py capture --scope all-product-development-source --output native_core/target/source-review/all-product-candidate.zip
```

Unpacking requires a new destination directory and validates the entire inventory
first. It refuses traversal, duplicate entries, symlink entries, unexpected files,
missing required inputs/trees, embedded private keys, and mismatched hashes.
Source traversal prunes generated/dependency directories and rejects directory
symlinks. `.env` files and generated website WASM outputs are excluded.
It never cleans the working tree
or overwrites an existing destination.

Two captures of the same candidate produced identical ZIP hashes. An extracted
304-file candidate passed `cargo check --locked --offline` using a separate target
directory and the host dependency cache. This proves that candidate's native build
inputs were sufficient; it is not a clean install or proof of all platform builds.

For release acceptance, review the complete product scope, retain the accepted
inventory, capture a clean source revision, and build/verify the exact artifacts.
The existing dirty checkout remains intact. Snapshot availability does not certify
ownership, dependency redistribution clearance, or release approval.
