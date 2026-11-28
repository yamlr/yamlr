# Native CLI contract

Every routed command is validated with Clap before entitlement renewal, reads,
writes, or service startup. Execution uses the same argument definitions. Run
`yamlr <command> --help` for that command's complete flags, aliases, value types,
and defaults. Help succeeds without activating paid capabilities.

## Rules

- Options may precede or follow the positional argument. Compact short values
  and `--option=value` are accepted for value options.
- `--` ends options. A subsequent path such as `--apply` is a literal path and
  cannot enable writing. Commands that do not accept a path reject it.
- Unknown flags, extra paths, missing values, duplicate aliases, unsupported
  output formats, invalid versions, and invalid ports are usage errors.
- Scan report selectors (`--output`, `--json`, `--sarif`) are mutually exclusive.
  Helm, Kustomize, and local OCI source adapters are mutually exclusive.
- `heal --dry-run --apply` remains a preview: dry run wins and cannot create
  generated stubs. `fix --dry-run` also remains a preview.
- Baseline create/check and rollback list/transaction modes are mutually exclusive.
- Paid execution requires the normal entitlement checks. Help and argument
  validation never bypass execution licensing.

## Command families

| Commands and aliases | Contract |
| --- | --- |
| scan, lint | One target; typed Kubernetes version, severity threshold, text/JSON/SARIF output; source adapter and report selectors; scan help lists additional switches. |
| heal, fix | One target; typed Kubernetes version and text/JSON/SARIF output; preview/apply/dry-run, policy inputs, stubs, metrics, and source adapters. Fix inserts implicit apply before `--`; dry run still wins. |
| check | One target, typed version and severity threshold, quiet output. |
| diff | One target and unified/plain preview options. |
| fmt | One target or stdin `-`; optional explicit write. |
| audit | One target and text/JSON/SARIF output. |
| catalog | Optional nonempty category and JSON switch. |
| baseline | One target, snapshot filename, exclusive create/check modes. |
| schema | ingest, fetch, list, clean subcommands; fetch version/offline options. |
| explain | Optional rule ID. |
| sign, verify | One target, explicit key or signing-key environment fallback; sign optionally writes. Key values after the option terminator are not options. |
| graph, drift | One target; graph optionally accepts a nonempty focus. |
| rollback, restore | Optional transaction, journal path, or exclusive list mode. |
| roi, impact, pulse, metrics, stats | One target; text/JSON output or JSON switch. |
| secure | One target and optional output filename. |
| evidence | One target, output filename, optional JSON switch. |
| idp-export | One target, output filename, explicit backstage/port/prometheus/metrics/otel format. |
| fleet | One target, typed version, branch, explicit apply, JSON, PR, and Git dry-run switches. |
| watch | One target; unknown options cannot start a watch loop. |
| webhook | Typed port from 1 to 65535, optional dry run. Mutation only; TLS must terminate at a trusted proxy. Unsupported TLS/validation flags are rejected. |
| rpc, service, daemon | Typed loopback port and dry-run/test alias. A network listener is not implemented: execution returns an error rather than claiming to serve requests. |
| auth | Default status; status and activate subcommands. Activation requires exactly one positional token or key option. |
| subscribe, upgrade | Subscribe optionally accepts a key; upgrade shows offline instructions and accepts no extra arguments. |
| admin | Required cache-clear, journal-prune, or config-reset subcommand. Extra arguments are rejected before maintenance. |
| vap, export-vap | Default export with name/output; ingest requires an input and rejects export settings. Legacy flag mode uses `--ingest --file <path>`. |
| init | One target and optional force switch. |
| dna | One target, JSON and full-fingerprint switches. |
| doctor, diagnose | Optional verbose switch. |
| install | Instructions by default; explicit git-hook switch. |
| guide | Optional nonempty topic. |
| completion | Exactly one supported shell: bash, zsh, fish, powershell, pwsh. |
| version, --version, -v | Optional JSON switch. |
| help, --help, -h | Top-level reference; no extra arguments. |
| legal, manual, man, migrate, rules, welcome, features, status, demo, lsp, mcp | No command arguments beyond help. Invalid arguments cannot start a stdio daemon. |

## Exit codes and verification

| Code | Meaning |
| --- | --- |
| 0 | Success or help; explicit supported preview/exit-zero behavior applies. |
| 1 | Findings/policy failure or missing entitlement. |
| 2 | Syntax failure where the command distinguishes it. |
| 3 | Invalid command arguments or configuration. |
| 4 | System or input/output failure. |

`tests/test_cli_contract_registration.py` checks that every dispatch name appears
in the parity matrix. `tests/verify_rust_parity.py` compares exact help, stderr,
exit codes, and reports for the standalone binary and isolated Python bridge.
The latest installed-wheel run on 2026-10-02 passed 202 cases across all 62 routed names,
including failure reports for unsupported supplied CRD constraints.
Native tests additionally exercise parser values, option terminators, conflicts,
and no-write behavior. This is implementation evidence; platform release results
and paid executable report acceptance remain separate requirements.
