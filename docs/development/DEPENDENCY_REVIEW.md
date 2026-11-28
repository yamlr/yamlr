# Dependency review preparation

`scripts/ci/prepare_dependency_review.py` consumes offline, locked Cargo metadata
and collects declared license expressions, repository/source identifiers, and
available package license/notice texts with hashes. It writes into a new directory
and rejects escaping notice paths and private-key material.

The local 2026-10-02 inventory contains **274 package records**. **11 have no
collected notice text**. Every entry remains explicitly **unreviewed**. The graph
includes development and target-specific dependencies, so it is not a list of
exactly what is shipped and must not be labelled an artifact SBOM.

Reproduce preparation from the repository root:

```powershell
cargo metadata --locked --offline --format-version 1 --manifest-path native_core/Cargo.toml > native_core/target/dependency-metadata.json
python scripts/ci/prepare_dependency_review.py --metadata native_core/target/dependency-metadata.json --output native_core/target/dependency-review
```

Review must also cover Python/JavaScript distributions, embedded Kubernetes/CRD
schemas, forensic catalogs, vendored material, and artwork/fonts. Existing release
workflows generate SBOMs and dependency notices; their output still needs review
against the actual candidate packages.

`scripts/ci/prepare_product_review.py` also reads a verified all-product source
snapshot and collects npm lockfile declarations, versions, source/integrity
identifiers, and candidate asset hashes. The first local capture produced 447
npm records across project lockfiles and 14 asset records. These records are
unreviewed, include development/optional dependencies, and do not contain
upstream notice texts. Assets have unconfirmed provenance. Inline/adapted code
still needs review beyond this path-based asset selection.

```powershell
python scripts/ci/prepare_product_review.py native_core/target/source-review/all-product-candidate.zip --output native_core/target/source-review/product-review.json
```

The output must be a new file; an existing review record is never overwritten.

For each redistributed component record its exact source/version/hash, license
and notice evidence, distribution obligations, unresolved questions, reviewer,
decision, and date. Resolve missing notices and provenance rather than generating
a passed decision. Item 0.4 remains open until that review is completed.
