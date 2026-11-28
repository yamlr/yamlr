# Yamlr Performance Claims and Benchmark Status

**Status:** No independently reproducible performance results are currently published.

Earlier versions of this report included latency, throughput, and competitor comparison figures without a checked-in benchmark result set that substantiates them. Those figures are withdrawn and must not be used as product guarantees or comparative claims.

Yamlr includes a native Rust implementation, but that fact alone does not establish end-to-end latency, throughput, memory use, or performance relative to other tools. Results depend on manifest size and shape, enabled checks, storage, hardware, and build configuration.

## Requirements for publishing benchmark results

Before publishing measured results, retain the benchmark command and source revision, machine and operating-system details, toolchain and build flags, input corpus and corpus hash, warm-up and repetition policy, raw results, and analysis method. Separate parser microbenchmarks from full scan and healing workflows. Compare other tools only when they process equivalent inputs and perform equivalent work.

Report comment and formatting preservation separately from performance. Preservation claims need a defined supported-input boundary and representative regression fixtures; benchmark timings do not prove correctness.

Until those records are available, describe Yamlr as a native Rust implementation and avoid fixed latency, throughput, memory, or comparative performance guarantees.
