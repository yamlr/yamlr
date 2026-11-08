# yamlr restore
**Restore Manifests via Atomic WAL Remediation Journal**

The `yamlr restore` command (canonical alias for `yamlr rollback`) restores Kubernetes manifests to their exact pre-remediation state using the Write-Ahead Log (WAL) forensic journal.

Whenever `yamlr heal --apply` modifies files on disk, Yamlr captures an atomic pre-mutation snapshot and logs a transaction record in the remediation journal (`.yamlr/journal.jsonl`). `yamlr restore` lets you list past transactions and roll back any change deterministically.

## Usage

```bash
# List all recorded remediation transactions
yamlr restore --list

# Roll back a specific transaction by its ID
yamlr restore <TRANSACTION_ID>

# Specify a custom journal file path
yamlr restore --journal /path/to/journal.jsonl --list
```

## Options & Flags

### Positional Arguments
* `[TRANSACTION]`: The unique transaction ID (UUID) to roll back. If omitted and `--list` is not specified, Yamlr lists recent transactions and provides rollback guidance.

### Journal Controls
* `-l, --list`: List recent remediation transactions recorded in the journal.
* `-j, --journal <PATH>`: Custom path to the remediation journal file. Defaults to `.yamlr/journal.jsonl`.

## How It Works

1. **Transactional WAL Journal**: Before modifying any manifest on disk, Yamlr writes a journal record containing the file path, timestamp, and pre-remediation byte contents.
2. **Deterministic Reversion**: Passing `<TRANSACTION_ID>` reads the journal entry and atomically restores the original file content with bit-for-bit fidelity, preserving original timestamps and permissions.
3. **Audit Trail**: Rolled-back transactions are marked as `ROLLED_BACK` in the journal for forensic compliance tracking.

## Exit Codes

* `0` (`EXIT_SUCCESS`): Transaction listed or manifest successfully restored.
* `2` (`EXIT_USAGE`): Invalid arguments passed.
* `3` (`EXIT_CONFIG_ERROR`): Specified transaction ID not found in journal.
* `124` (`EXIT_SYSTEM_ERROR`): Journal unreadable or filesystem write error.

## Related Commands

* [`yamlr rollback`](yamlr_rollback.md) — Canonical rollback command.
* [`yamlr heal`](yamlr_heal.md) — Autonomous remediation engine.
* [`yamlr evidence`](yamlr_evidence.md) — Export compliance audit evidence bundle.
