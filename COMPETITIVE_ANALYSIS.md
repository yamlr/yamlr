# yamlr Competitive Landscape & Feature Matrix

## 1. Overview
This document provides a detailed breakdown of how yamlr (OSS) and Emplatix (Enterprise) compare against the current market leaders in Kubernetes validation. 

**The Core Differentiator:** While competitors focus on *Reporting* (finding issues), yamlr focuses on *Healing* (fixing issues).

## 2. Feature Comparison Matrix

| Feature Category | Feature | **Kubeval** / **Kubeconform** | **Polaris** | **Pluto** | **yamlr OSS** | **yamlr Enterprise** |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Foundational** | **Schema Validation** | ✅ | ✅ | ❌ | **✅ (Strict)** | **✅ (Deep)** |
| | **Automatic Repairs** | ❌ | ❌ | ❌ | **✅ (Syntax/Indent)** | **✅ (AI Enhanced)** |
| **Best Practices** | **Policy Checks (Linter)** | ❌ | ✅ | ❌ | **✅ (Built-in)** | **✅ (Custom Rego)** |
| | **Security Baseline** | ❌ | ✅ | ❌ | ✅ | ✅ |
| **Lifecycle** | **Deprecation Detection** | ❌ | ❌ | ✅ | ✅ | ✅ |
| | **Auto-Migration (Fix)** | ❌ | ❌ | ❌ | **✅ (Prophetic Engine)** | **✅** |
| **Context** | **Global Graph (Cross-File)** | ❌ | ❌ | ❌ | **✅ (Ghost Services)** | **✅ (Cluster Graph)** |
| | **Port Consistency** | ❌ | ❌ | ❌ | **✅ (Service <-> Pod)** | **✅** |
| | **Ingress Validity** | ❌ | ❌ | ❌ | **✅ (Backend Check)** | **✅** |
| | **Live Cluster Drift** | ❌ | ❌ | ❌ | ❌ | **✅ (Drift Doctor)** |
| **Operations** | **GitOps Integration** | ❌ | ⚠ (Manual) | ❌ | ✅ (CLI) | **✅ (Native Agent)** |
| | **Central Dashboard** | ❌ | ✅ | ❌ | ❌ | **✅ (Multi-Team)** |
| | **AI Explanation** | ❌ | ❌ | ❌ | ❌ | **✅ (AI Surgeon)** |

## 3. Detailed Breakdown by Tier

### A. Competitors (The "Old Guard")
*   **Kubeval / Kubeconform:** Excellent for fast schema validation. "Is this valid YAML?"
    *   *Weakness:* No context. Doesn't know if a Service points to a valid Deployment. Doesn't fix anything.
*   **Polaris:** Excellent dashboard for best practices. "Is this configuration secure?"
    *   *Weakness:* Read-only. Requires setting up a dashboard.
*   **Pluto:** Focused solely on deprecated APIs. "Are you using old versions?"
    *   *Weakness:* Tells you the problem but forces you to manually edit 100 files.

### B. yamlr OSS (The "Local Fixer")
*   **Target:** The Individual Developer & DevOps Engineer.
*   **Philosophy:** "runs on my machine".
*   **Key Capabilities:**
    *   **The Healer:** Input bad YAML -> Output clean YAML. (e.g., Fixes "stuck dashes" like `-name: nginx`)
    *   **The Graph:** Knows that `Service A` needs `Deployment B` (and verifies Ports!).
    *   **The Migrator:** Automatically upgrades `v1beta1` to `v1`.
    *   **Zero Config:** Works out of the box with standard K8s catalog.

### C. yamlr Enterprise (The "Platform Control Plane")
*   **Target:** Platform Teams & SRE Managers.
*   **Philosophy:** "runs on the cluster".
*   **Key Capabilities:**
    *   **Drift Doctor:** "Git says X, Cluster says Y." Reconciles state.
    *   **Policy Guard:** Enforce "No LoadBalancers in Dev" across 50 repos.
    *   **AI Surgeon:** "Explain why this change is needed" for non-expert developers.
    *   **Audit Trail:** Compliance logging for regulated industries.
