# Confirmed product scope

Confirmed by the founder on 2026-10-02: all components listed below are in scope
for remediation and release acceptance. None is deferred by this scope decision.

| Component group | Scope |
| --- | --- |
| Native CLI and Python SDK | Included |
| VS Code extension | Included |
| WASM package | Included |
| GitHub Actions | Included |
| Website | Included |
| Gateway services | Included |
| Billing services | Included |

Each group needs an exact source/build-input inventory, packaging or deployment
definition, dependency/asset provenance, and applicable acceptance evidence.
The default native/SDK snapshot covers only the first group. The optional
`all-product-development-source` snapshot now inventories sources/configuration
across the confirmed groups. Its explicit selection policy still needs review
against actual packages, external inputs, and deployment definitions; inventory
coverage alone does not close baseline acceptance.

This scope confirmation does not authorize publishing code, deploying services,
creating accounts, or changing ownership declarations. Candidate contents and
those external actions must be made concrete before any necessary approval.
