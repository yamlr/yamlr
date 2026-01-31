# Yamlr Enterprise: The "Safe AI" Strategy
## Philosophy: Intelligence without Hallucinations

You are absolutely right to be concerned. **"AI Hallucinations" in infrastructure = Production Outages.**
Yamlr Enterprise is designed on a core principle: **Deterministic Guardrails are authoritative; AI is advisory.**

We call this architecture the **"Safety Sandwich"**.

---

## 1. The Safety Sandwich Architecture
We never let a Large Language Model (LLM) touch your cluster directly. Every AI action is "sandwiched" between deterministic layers.

### 🥪 Layer 1: Context Gathering (Deterministic)
*   **The Global Graph:** We don't just dump text into an LLM. We first build a rigorous dependency graph of your cluster (Service A -> Pod B -> ConfigMap C).
*   **Safety Filter:** We sanitize inputs. Secrets are redacted *before* they leave your premise.

### 🥩 Layer 2: The "AI Surgeon" (Generative)
*   **Role:** The LLM's job is *reasoning* and *explanation*, not execution.
*   **Task:** "Analyze these pod usage metrics (low CPU) and strict resource quotas. Propose a new `resources.requests` configuration."
*   **Output:** The LLM produces a *proposed* YAML manifest.

### 🥪 Layer 3: Simulation & Policy Check (Deterministic)
*   **Syntax Validation:** The proposed YAML is run through the standard Yamlr Linter.
*   **Policy Gate:** "Does this new config violate our 'No Privileged Containers' rule?" (OPA/Kyverno).
*   **Graph Simulation:** "If we apply this change, does it break the Service Selector link?"
*   **Result:** If *any* check fails, the AI proposal is rejected *before* a human ever sees it.

---

## 2. Feature Deep Dive: Capabilities vs. Risks

| Feature | How it works | The Risk (Crash) | The Yamlr Guardrail |
| :--- | :--- | :--- | :--- |
| **Drift Doctor** | Syncs Git with Cluster State. | Deletes a critical live resource that wasn't in Git. | **"Zombie Protection":** We verify active traffic/connections before suggesting deletion. |
| **Smart Limits** | AI analyzes Prometheus metrics to set CPU/Mem. | Sets CPU too low, app throttles and dies. | **"Safe Floors":** We enforce hard minimums based on historical peaks (e.g., "Never below 95th percentile"). |
| **AI Explain** | Explains *why* a policy failed. | Suggests a fix that bypasses security. | **Policy Enforcement:** The *fix* is re-scanned. If it's insecure, it's blocked. |
| **Auto-Refactor** | Slices monoliths into files. | Breaks internal references. | **Graph Integrity:** We verify all `Ref` links (Services, PVCs) resolve effectively after refactoring. |

---

## 3. The "Human-in-the-Loop" Workflow
Yamlr Enterprise is not an "Auto-Pilot" (yet). It is a "Co-Pilot".

1.  **AI Proposes:** "I detected 50% waste in the `frontend` deployment. I recommend resizing."
2.  **Yamlr Verifies:** "Simulation passed. No policies violated."
3.  **Human Approves:** The user gets a **Pull Request**, not a direct cluster apply.
    *   *User sees:* "Drift Doctor wants to merge 3 commits."
    *   *User action:* Click "Merge".
4.  **GitOps Deploys:** ArgoCD/Flux syncs the change.

**Summary:** You don't crash the cluster because the AI *cannot* apply changes. It can only submit PRs that pass your CI/CD pipeline.

---

## 4. Q&A for your Users
**Q: "What if the AI hallucinates a non-existent API version?"**
A: The deterministic Schema Validator (Layer 3) will catch it immediately: `Error: apiVersion 'v2' does not exist`. The proposal is discarded.

**Q: "Will it delete my database?"**
A: No. StatefulSets and PVCs are marked as `Protected Resources` by default. The AI is structurally forbidden from generating `DELETE` operations for these kinds unless you explicitly override a "Break Glass" procedure.
