# 💎 Yamlr Pro: Verified Feature Matrix

This document defines the official functional boundaries between Yamlr Free (OSS) and Yamlr Pro/Enterprise editions, verified against the latest production codebase.

## 📊 Feature Comparison Matrix

| Capability | Yamlr Free | Yamlr Pro | Code Reference |
| :--- | :---: | :---: | :-- |
| **Core Healing Engine** | ✅ | ✅ | `YamlrEngine` |
| CLI `scan` + `heal` | ✅ | ✅ | `cli/main.py` |
| Non-Destructive Parsing | ✅ | ✅ | `ruamel.yaml` |
| **Healing Quota** | **5 files/day** | **Unlimited** | `core/license_manager.py` |
| **Structural Repairs** | | | |
| Schema-Aware Structuring | ✅ | ✅ | `YamlrStructurer` |
| Type Alignment (Map-as-List) | — | ✅ | `pro/surgery.py` |
| Canonical Export (Auto-Sort) | — | ✅ | `pro/exporter.py` |
| **Security & Hardening** | | | |
| Standard Linter Detection | ✅ | ✅ | `analyzers/` |
| `--harden` (CIS/SOC2 Fixes) | Detect Only | ✅ Auto-Fix | `healers/security.py` |
| Shadow Risk Detection | — | ✅ | `pro/shield.py` |
| Image Tag Pinning (`--fix-tags`) | Detect Only | ✅ Auto-Fix | `healers/image_tag.py` |
| **Compliance & Trust** | | | |
| Semantic DNA Calculation | — | ✅ | `pro/shield.py` |
| Cryptographic DNA Receipts | — | ✅ | `core/entrypoints/heal.py` |
| Evidence Reporting (`evidence`) | — | ✅ | `cli/commands/evidence.py` |
| **Ecosystem Integration** | | | |
| OPA (Open Policy Agent) | — | ✅ | `pro/opa_adapter.py` |
| Kyverno Report Ingestion | — | ✅ | `pro/kyverno_adapter.py` |
| Automated Remediation (`--from-report`) | — | ✅ | `HealConfig.from_report` |

---

## Pro feature Deep Dive (Verified)

### 1. The Healing Quota Guardrail
Yamlr Free allows unlimited `scan` (audit) operations. However, actual `heal` (remediation) is limited to **5 distinct files per 24-hour period**. This is enforced locally in `~/.yamlr/quota.json`.
- **Pro users** have unlimited healing across all workspaces.

### 2. Type-Safe Auto-Repair
Pro users gain access to "Type Alignment" algorithms. These fix common Kubernetes configuration "mismatches" where maps are incorrectly used as lists (or vice-versa), such as:
```yaml
# From this (Invalid):
env:
  DEBUG: "true"
# To this (Fixed):
env:
  - name: DEBUG
    value: "true"
```
This is gated in `SchemaHealer.clean_value` and requires a Pro license.

### 3. Canonical Export & Native Acceleration
- **Canonical Export**: Pro users see their YAML files automatically sorted according to Kubernetes conventions (e.g., `apiVersion` and `kind` always at the top).
- **Native Acceleration**: Uses the Rust extension (`--fast`) for supported operations. Processing time depends on workload, cache state, and platform; no fixed latency is guaranteed.

### 4. Semantic DNA & Receipts
Yamlr Pro calculates a **Semantic DNA hash** for every manifest. This hash represents the "meaning" of the file, ignoring whitespace and comments. Pro users can generate **Compliance Receipts** (`--receipt`) that prove a manifest has been validated and hardened by the Yamlr engine, suitable for SOC2/ISO audits.

---

> [!TIP]
> **Pro Preview Mode**: You can test all Pro features for free using the `--pro-preview` flag. This will simulate all Pro healing logic in your terminal (using `--dry-run` and `--diff`) so you can see the value before upgrading.
