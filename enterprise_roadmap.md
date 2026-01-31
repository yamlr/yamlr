# Yamlr Strategic Roadmap: From "Linter" to "Platform"

## 1. Executive Summary
Yamlr distinguishes itself from the crowded market of Kubernetes validators (Kubeval, Polaris, Trivy) by one core value proposition: **"We Fix It."**
While others simply report errors, Yamlr creates a seamless "Find & Fix" loop for developers. 

This roadmap delineates the path to maximizing this differentiator in OSS while building a compelling Enterprise "Control Plane".

## 2. Competitive Gap Analysis

| Feature | Kubeval / Kubeconform | Polaris | Trivy | **Yamlr OSS** | **Yamlr Enterprise** |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Schema Validation** | ✅ | ✅ | ✅ | ✅ (Strict) | ✅ (Deep) |
| **Policy Checks** | ❌ | ✅ | ✅ | ✅ (Best Practice) | ✅ (Custom Rego) |
| **Deprecation Checks** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Auto-Healing (Fixes)** | ❌ | ❌ | ❌ | **✅ (Core DNA)** | **✅ (AI Enhanced)** |
| **Context Awareness** | ❌ | ❌ | ❌ | **✅ (Global Graph)** | **✅ (Cluster Graph)** |
| **Drift Detection** | ❌ | ❌ | ❌ | ❌ | **✅ (Drift Doctor)** |
| **GitOps Integration** | ❌ | ⚠ (DIY) | ✅ | ✅ (CLI) | **✅ (Native App)** |

**Key Insight:** Yamlr OSS wins on the **Developer Inner Loop** (Local -> Fix). Enterprise wins on the **Operator Outer Loop** (Cluster -> Sync).

## 3. OSS Roadmap: " The Perfect Local Loop"

The goal of OSS is to make `yamlr scan .` the default first step for any K8s developer.

### ✅ Phase 1: The Global Semantic Graph (COMPLETED)
*   **Gap Closed:** Context Awareness.
*   **Capabilities:**
    -   Detect "Ghost Services" (Service matching no Pods).
    -   Detect "Orphan Configs" (Unused ConfigMaps/Secrets).
    -   Suggest fixes based on fuzzy matching across files.

### 🚧 Phase 2: Prophetic Migration (The "Pluto" Killer)
*   **Gap:** Tools like Pluto detect deprecated APIs but don't fix them.
*   **Capabilities:**
    -   **Auto-Migration:** `yamlr heal` automatically upgrades `apps/v1beta1` to `apps/v1`.
    -   **Schema Backfilling:** Automatically injects required fields (e.g., `selector`) during migration.
    -   **Removal Prevention:** Blocks CI if "Removed" APIs are detected.

### 🔮 Phase 3: Local Policy Engine
*   **Gap:** Developers ignore policies until CI fails.
*   **Capabilities:**
    -   Built-in "Security Baseline" (Pod Security Standards).
    -   Resource Quota advisories.

## 4. Enterprise Roadmap: "The Control Plane"

The goal of Enterprise (Yamlr Enterprise) is to give Platform Teams control over `yamlr` usage and cluster state.

### 🚀 Phase 1: The Drift Doctor (Smart Limits & Autoscaling)
*   **Objective:** Reconcile Git State with Cluster State.
*   **Status:** 🚧 Planned (Phase 1)
*   **Features:**
    -   **Drift Analysis:** "Git says X, Cluster says Y."
    -   **Smart Resource Limits (Ported from Legacy Healer):**
        -   **Sidecar Detection:** Auto-detects `istio-proxy`/`envoy` -> Suggests `100m/128Mi`.
        -   **App Detection:** Auto-detects Java/Go apps -> Suggests `500m/256Mi`.
        -   **Dummy Detection:** Auto-detects `pause` containers -> Suggests `10m/32Mi`.
    -   **Inverse Healing:** Generate a PR to update Git to match Cluster.
    -   **Zombie Detection:** Find resources running in Cluster but deleted from Git.

### 🛡️ Phase 2: GitOps Guard (Security & Policy Baseline)
*   **Objective:** Centralized Policy Enforcement.
*   **Status:** 🚧 Planned (Phase 2)
*   **Features:**
    -   **Policy Baseline (Ported from Legacy CLI):**
        -   `yamlr baseline` command to snapshot current "accepted" issues.
        -   CI/CD only fails on *new* violations (Regression Testing).
    -   **Security Analyzer (Ported from Legacy Shield):**
        -   **RBAC Auditing:** Detects wildcard `*` permissions.
        -   **Privilege Escalation:** Flags `privileged: true`.
        -   **Ingress Security:** Validates TLS and IngressClass.
    -   **Web UI:** Visualize health across all repos.
    -   **Audit History:** "Who healed what and when?"

### 🤖 Phase 3: The AI Surgeon
*   **Objective:** Complex Refactoring & Explanation.
*   **Features:**
    -   **Explainability:** "Why did Yamlr change this?" (LLM generated PR descriptions).
    -   **Complex Refactoring:** "Split this giant Manifest into Microservices."
    -   **Security Hardening:** "Rewrite this Role to be least-privilege based on actual usage logs."

## 5. Immediate Technical Action Plan
1.  **Merge Global Graph:** Ensure the recent OSS "Brain Wiring" is stable.
2.  **Scaffold Migration Engine:** Begin work on `deprecations.py` to support *mutation* logic, not just detection.
3.  **Design "Drift Doctor":** Create the interface for `yamlr doctor`.
