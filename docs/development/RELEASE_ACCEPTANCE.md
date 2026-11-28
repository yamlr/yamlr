# Development release acceptance

This checklist defines required evidence for a specific candidate revision.
Development progress and release acceptance are separate statuses. Keep evidence
with its source/artifact hashes; never convert missing records into passed checks.

The founder confirmed all seven component groups in `RELEASE_SCOPE.md` on
2026-10-02. An expanded all-product source candidate is now available alongside
the native/SDK snapshot; its selection policy and actual package coverage still
need review.
Founder statements and unresolved ownership questions are recorded in
`OWNERSHIP_STATUS.md`; they do not yet close ownership acceptance.

## Engineering evidence

| Area | Required evidence |
| --- | --- |
| Source baseline | Reviewed file inventory and revision; hashes of uncommitted inputs where applicable; no blanket reset. |
| CLI contract | All advertised commands, flags, aliases, help, option terminators, error codes, and no-mutation behavior documented and checked. |
| Validation | Regression corpus for malformed types, required fields, CRDs, multi-document YAML, flow collections, quoting, cache isolation, and failure reports. Document unsupported schema features. |
| Reports | JSON schema validation and SARIF schema validation; stdout remains a single report with metrics enabled; incomplete input never produces success. |
| Parity/packages | Fresh standalone binary and installed wheel use the same command behavior; no reliance on source-only archived code. |
| Independent core | Local scan/check/heal run with telemetry disabled and without hosted identity or billing credentials. |
| Integration boundaries | Versioned requests/responses, provider adapter tests, and a working alternate integration. |
| Distribution | Build, package, secret-check, verify, and smoke-test locally; transport-independent artifact verification; every advertised target has collected results. |
| Performance | Deterministic corpus, raw samples, revision/build/corpus hashes and environment. Measure variance before setting regression thresholds. |
| Healing | Parsing, idempotence, source-layout and no-write checks for supported repairs; unsupported guarantees omitted from product claims. |

## Records not yet available

The owner confirmed on 2026-10-01 that development currently has the codebase,
with no contributor/contractor agreements, external redistribution review, or
pilot evidence. Those three acceptance areas remain unresolved. They do not
prevent development, but must not be marked complete for a production release.

| Record | Minimum content |
| --- | --- |
| Ownership | Contributor/contractor, contribution or asset, provenance, agreement reference, rights holder, review date. Record uncertainty rather than inventing ownership. |
| Third-party redistribution | Exact release dependency/asset inventory, source/version/hash, license and notices, distribution obligations, reviewer and decision. Include schemas and vendored assets. |
| Pilot validation | Dataset and environment, consent/scope, expected findings, observed findings, false positives/misses, proposed/applied repairs, recovery results, reviewer and date. |

A development signing key is not a production release key. Paid report smoke
tests need an isolated non-production entitlement; keep secrets in configured
secret storage and record only test outcomes. An absent entitlement is a visible
coverage gap, not a reason to bypass license enforcement.

## Current evidence sources

- `docs/REMEDIATION_STATUS.md`: remaining plan items and measured scope.
- `schemas/scan-report.schema.json`: scan JSON contract.
- `tests/verify_rust_parity.py`: executable/extension parity matrix.
- `scripts/ci/smoke_binary.py`: real executable scan/output failure checks.
- `scripts/ci/benchmark_cli.py`: reproducible development measurements.
- `scripts/ci/benchmark_workloads.py`: CRD, multi-document, and healing acceptance
  with raw latency measurements; scope in `docs/development/BENCHMARK_WORKLOADS.md`.
- `.github/workflows/ci.yml` and release workflows: automated gates; retain their
  successful results for the candidate rather than relying on configuration alone.
