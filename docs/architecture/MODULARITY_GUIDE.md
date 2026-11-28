# Yamlr: Product & Architectural Safety Guide

## 🏁 The Vision
Yamlr is an autonomous engine designed for high-trust environments. Because we are "vibe coding" (AI-led development), we maintain strict architectural boundaries to ensure any engineering auditor or future investor can verify our quality in under 48 hours ($20M Target).

## 🛡 1. Why Modularity Matters to the Product
- **Zero-Failure Trust**: By keeping logic in "Stages," we ensure that a bug in one fix (like a Service port fix) cannot accidentally break another (like a Deployment migration).
- **Fast Evolution**: We can add new "Magic Moments" (like `yamlr demo`) without touching the core healing logic.
- **Acquisition Readiness**: Modularity makes the codebase "Ingestable." A clean, decoupled core is a high-value asset.

## 🧱 2. The Agent Safety Protocol
Our AI development agents follow a strict protocol to prevent "spaghetti code":
- **Small, Focused Modules**: No 1,000-line "God Objects."
- **Stage-Based Growth**: New features are added as discrete "Stages," not by bloating existing files.
- **Safety Integrity**: Every healing logic change is isolated and testable.

## 🔍 3. How to Audit the "Vibes" (For the Visionary)
Even without coding knowledge, you can verify the engineering health:
1.  **Check `src/yamlr/core/engine/`**: This should be a collection of specialized modules (auditor, processor, etc.).
2.  **Check `src/yamlr/parsers/`**: Look for `physicist.py` and `schema_healer.py`. If `structurer.py` is >500 lines, we failed.
4.  **Check `base.py` / `bridge.py`**: These orchestrators should remain small orchestrators, not "God Objects."
5.  **Check `models.py`**: This is the "Source of Truth" for data.

## 🚀 4. Summary for AI Agents
Agents must strictly follow the [.agent/rules/modularity-enforcement.md](../.agent/rules/modularity-enforcement.md) protocol. This ensures the product visionary's goals are met with professional-grade engineering rigor.
