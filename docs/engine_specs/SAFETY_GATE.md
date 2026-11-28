# Safety Gate — Feature Acceptance Criteria

> **Applies to:** All new features in Yamlr (Free and Pro)
> **Last Updated:** 2026-02-28

## Purpose

Every new feature must strengthen cluster-level safety intelligence.
This gate prevents feature creep that dilutes Yamlr's identity as a
**Kubernetes Configuration Safety Engine**.

## Acceptance Criteria

Every new feature **MUST** answer YES to at least one:

| # | Question | Weight |
|:--|:---------|:-------|
| 1 | Does this strengthen **cluster-level safety intelligence**? | Required |
| 2 | Does this deepen **cross-resource dependency awareness**? | Tier 0 |
| 3 | Does this improve **version compatibility detection**? | Tier 0 |
| 4 | Does this enhance **deterministic remediation trust**? | Tier 0 |
| 5 | Does this create a **developer workflow habit** (CI/CD, pre-commit, IDE)? | Tier 0 |

If a feature answers NO to all five, it is **rejected** unless explicitly
approved by the product owner.

## Mandatory Gates (Per `.agent/rules/yamlr-cli.md`)

| Gate | Rule | Enforcement |
|:-----|:-----|:------------|
| 🔒 Trust | Default must be safe + explainable. Aggressive fixes are opt-in. | S1 preview for semantic changes |
| 🔒 Comments | Default healing preserves comments and formatting. | Opt-in for destructive formatting |
| 🧊 Determinism | Same input + same version + same config = identical output. | Automated test requirement |
| ⚡ Speed | Hook <2s, CI <15s/1000 files, IDE <500ms | Benchmark requirement |

## Anti-Patterns (Automatic Rejection)

- ❌ Features that only work on individual files (no system-level value)
- ❌ Features that require cluster connectivity for basic operation
- ❌ Features that add non-deterministic behavior (ML, LLM, random)
- ❌ Features that compete with existing ecosystem tools (OPA, Kyverno, Checkov)
- ❌ Features from Tier 2+ (Drift Doctor, AI Surgeon, Dashboards, SOC2, SSO)

## Complement Strategy Test

Before building ANY new detection or fix:

1. **Does an existing tool already do this?** → If yes, build a complement integration, not a competitor
2. **Can we import their output?** → If yes, implement `yamlr import <tool-report>`
3. **Can they consume our output?** → If yes, enhance SARIF/JSON export with graph context
