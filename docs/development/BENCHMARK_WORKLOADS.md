# Representative development benchmarks

Run `scripts/ci/benchmark_workloads.py` with a freshly built executable. It
creates its inputs in a temporary directory and retains JSON measurements at
the requested output path. Telemetry is disabled for child commands.

| Workload | Acceptance before recording timings |
| --- | --- |
| Multi-document ConfigMaps | Complete clean report, input unchanged, invalid final Pod rejected. |
| Custom resources | Supplied CRD used, nested wrong type rejected, invalid final document rejected, clean valid stream. |
| Clean healing | Exact byte preservation, including the owner comment and CRLF endings; second apply unchanged. |
| Deprecated Deployment repair | API version changes to apps/v1, valid DNA seal added, other YAML values and owner comment preserved; second apply unchanged. |

Each workload has one separately recorded warmup and raw measured samples.
Reports include corpus/CRD/executable hashes, build profile, host information,
median, and nearest-rank p95. Resetting each input before each sample prevents
measuring only the already healed file. Idempotence verification runs outside
the timed first healing invocation. A changing executable invalidates the run.

Example from the repository root, after building an optimized CLI:

```powershell
python scripts/ci/benchmark_workloads.py --binary native_core/target/release/yamlr.exe --output native_core/target/workloads.json --documents 250 --samples 31 --build-profile release
```

The performance workflow runs this acceptance suite and retains raw JSON.
These are synthetic development workloads on a particular executable and host.
They do not establish broad comment/anchor preservation, complete CRD constraint
support, peak memory limits, production performance, or competitor comparisons.
Set regression budgets only after observing variance on a controlled runner;
hosted-runner timing fluctuations must not become invented product guarantees.
