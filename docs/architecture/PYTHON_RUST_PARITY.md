# Python and Rust CLI parity

The supported Python command line is a bridge to the native Rust CLI. It first
uses a bundled or installed `yamlr` binary and otherwise calls the Rust CLI
through `yamlr_native.native_cli_run`. The public Python API also calls native
Rust functions for scanning and healing.

| Interface | Implementation | Parity expectation |
| --- | --- | --- |
| Standalone `yamlr` executable | Rust CLI dispatcher | Reference behavior |
| `python -m yamlr` with a bundled/installed binary | Rust CLI dispatcher | Same exit codes and reports as the executable |
| `python -m yamlr` through the extension fallback | Rust CLI dispatcher via PyO3 | Same command contract as the executable |
| `yamlr.scan_yaml` and `yamlr.heal_yaml` | Rust engine via PyO3 | Same underlying scan/heal engine; Python return types are API-specific |
| `YAMLR_FORCE_PYTHON=1` source compatibility path | Archived Python CLI | Not packaged or part of the supported parity contract |

The CI parity runner compares the standalone binary with the Python CLI's
extension fallback for 202 shared cases: JSON scan/version output, compact scan
options, option terminators, help for all 62 routed command names and aliases, missing values,
unknown options, duplicate aliases, invalid versions/formats/thresholds, and
incomplete input reports despite exit-zero, unsupported supplied CRD constraints,
nested type violations, and process
exit codes. Scan JSON reports are checked against the repository report
schema. Audit, catalog, baseline, fmt, and fix now participate in help and
unknown-option checks. Conflicting baseline modes, duplicate write/apply flags,
compact catalog categories, and formatter preview preservation are also checked.
Timing fields are excluded because they vary between runs. This suite
checks every dispatch name; a regression check rejects a new routed command
without corresponding parity cases. Supported Python CLI behavior is delegated
to the same dispatcher, rather than maintained as a separate Python parser.

The clean-wheel CI job builds a reference executable and runs the same matrix
with the temporary environment's Python interpreter. Every extension-bridge
process uses isolated mode (`-I`); package import checks require both `yamlr`
and `yamlr_native` to resolve inside the temporary environment. The source
checkout and user site packages cannot supply the implementation under test.
The Windows candidate built on 2026-10-02 passed this installed-wheel matrix
and CLI/API smoke. Other host results are required by platform acceptance (5.1).
Paid signing was compared at entitlement denial because no test entitlement was
available; paid executable report coverage remains in 3.7. This does not claim
every licensed execution path was exercised. The complete supported grammar is
documented in [CLI_CONTRACT.md](cli/CLI_CONTRACT.md) and native command help.

The native extension is packaged inside `yamlr_native`, whose compatibility
initializer retains the public `import yamlr_native` API. Both build manifests
explicitly include `yamlr` and `yamlr_native`. This follows the
[Maturin mixed-project layout](https://www.maturin.rs/project_layout.html).
Wheel inspection rejects missing wrapper/native files and archived legacy
modules before installation.
