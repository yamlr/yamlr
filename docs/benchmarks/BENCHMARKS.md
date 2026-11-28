# Yamlr development benchmarks

No release performance baseline has been established. Earlier latency, memory,
and competitor comparison tables in this document had no retained measurement
artifacts and have been removed. They must not be used as product claims.

## Local optimized candidate measurements (2026-10-01)

An optimized Windows candidate was built with the locked Cargo dependency graph
from the current working tree. Each workload below had 31 warmed samples and
passed the invalid-Pod fidelity check. These are exploratory measurements on
one development machine, not release regression budgets or platform guarantees.

| ConfigMap files | Warmup ms | Warmed median ms | Warmed nearest-rank p95 ms |
| --- | ---: | ---: | ---: |
| 1 | 68.786 | 55.693 | 60.486 |
| 250 | 3729.741 | 79.261 | 93.630 |
| 1000 | 5584.510 | 146.873 | 205.184 |

Retained raw samples and environment details are in
`docs/development/measurements/release-windows-20261001-{1,250,1000}.json`.
All runs used binary SHA-256
`f958a548841ddee848cb6463c202845266a148dbdeb4356b113fa84ff3904e8d`.
The source is not yet a reviewed clean revision; Git SHA is unavailable in
these records. The binary digest identifies the measured artifact but does not
replace source provenance.

Warmup and warmed latency differ substantially. Cache state was not forcibly
cleared, so warmup must not be advertised as a controlled cold-cache benchmark.
Only ConfigMap directory scans were measured here; CRD, multi-document,
healing, memory, other platforms, and stable-runner budget calibration remain.
Standalone release-profile JSON smoke passed; paid SARIF executable smoke was
explicitly skipped because no test entitlement was available.

## End-to-end native CLI measurement

Build the executable and run the reproducible harness:

```sh
cargo build --locked --release --manifest-path native_core/Cargo.toml --bin yamlr
python scripts/ci/benchmark_cli.py --binary native_core/target/release/yamlr --output performance-results/scan-cli.json --files 250 --samples 7 --build-profile release
```

On Windows, append `.exe` to the binary path. The benchmark includes process
startup, traversal, parsing, schema/integrity validation, and JSON report writing.
It generates a deterministic ConfigMap corpus, requires every file to be scanned,
and rejects an invalid Pod before measurement to prove validation is active.

The JSON artifact records raw latency samples, median, nearest-rank p95, a separate
warmup measurement, binary and corpus SHA-256 hashes, build profile, Kubernetes
version, and environment information. It measures neither peak memory nor p99.
Seven samples are exploratory; they do not establish a dependable tail-latency
budget. Debug runs are harness checks, not release performance evidence.

The performance workflow builds the release CLI and uploads the measurement
artifact. It fails on build, scan, or measurement-integrity errors. It does not
currently enforce a latency regression threshold.

## Establishing a regression budget

Collect repeated release runs on a stable runner with representative small,
large, multi-document, CRD, and healing workloads. Retain exact revisions and
artifacts, quantify run-to-run variation, then choose workload-specific budgets
with a documented tolerance. Validate the budget against deliberately introduced
regressions before enabling it as a release blocker. Competitor measurements
require the same corpus, hardware, configurations, and validation scope.

Criterion microbenchmarks in `native_core/benches` measure selected internal
operations separately; their results must not be described as CLI latency or
proof of universal layout preservation. Review supported repairs and run the
preservation/idempotence tests alongside any performance changes.
