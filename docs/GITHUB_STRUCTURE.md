# 🏗️ Yamlr GitHub Architecture (Visa-Optimized)

This document defines the physical structure of your repositories to satisfy the "Public Impact" (O1 Visa) vs "Private IP" (Commercial Defense) strategy.

---

## 🏗️ 1. The Three Repositories

| Repo Name | Visibility | Goal | Content Summary |
|---|---|---|---|
| **`yamlr/yamlr`** | 🟢 **PUBLIC** | **Visa Evidence (Adoption)** | CLI Wrapper, UI, Specs, Binary Releases. |
| **`yamlr/yamlr-core`** | 🔴 **PRIVATE** | **Original Contribution** | The Engine (Lexer, Pipeline). |
| **`yamlr/yamlr-enterprise`** | � **PRIVATE** | **Commercial Success** | Pro Features (SAML, Multi-Cluster). |

---

## 📂 2. File System Mapping

You will maintain **ONE** local Monorepo (e.g., `yamlr` folder), but push to **TWO** remotes using strict `.gitignore` rules or a deployment script.

### 🟢 Repository: `yamlr/yamlr` (Public)
*Users see this. It looks like a full open source project, but the "Engine" is missing (replaced by binary in releases).*

```text
/
├── README.md               # "Yamlr: The K8s Healer"
├── USER_GUIDE.md           # Full Docs
├── LICENSE                 # Apache 2.0 (for CLI/UI)
├── pyproject.toml          # Deps
├── catalog/                # ✅ Public Schema Definitions
│   └── k8s_v1.30.json
├── src/
│   └── yamlr/
│       ├── __init__.py
│       ├── cli/            # ✅ Public Entry Point
│       ├── ui/             # ✅ Public Rich UI Logic
│       ├── core/           # ❌ EXCLUDED (Private)
│       ├── parsers/        # ❌ EXCLUDED (Private)
│       └── pro/            # ❌ EXCLUDED (Private)
└── hack/
    └── install.sh          # Fetches the `yamlr` binary from GitHub Releases
```

### 🔴 Repository: `yamlr/yamlr-core` (Private)
*The Foundation. Dependencies: None.*

```text
/
├── src/yamlr/core/         # ✅ INCLUDED
├── src/yamlr/parsers/      # ✅ INCLUDED
├── src/yamlr/pro/          # ❌ EXCLUDED (Belongs to Enterprise)
```

### � Repository: `yamlr/yamlr-enterprise` (Private)
*The Revenue Layer. Dependencies: yamlr-core.*

```text
/
├── src/yamlr/pro/          # ✅ INCLUDED
├── src/yamlr/core/         # ✅ INCLUDED (Monorepo view)
```

---

## 🔄 3. Synchronization Workflow (The "Solo Founder" Hack)

Since you are one person, do not maintain two separate folders. Use a **Split Push Script**.

### Step 1: `.gitignore` for Public Repo
Create a special `.gitignore_public` file:
```text
src/yamlr/core/
src/yamlr/parsers/
src/yamlr/pro/
tests/
tools/
```

### Step 2: The Push Script
We will create `hack/push_all.py` that:
1.  Pushes **Everything** to `origin_private` (`yamlr-core`).
2.  Temporarily applies `.gitignore_public`.
3.  Commits specific public folders to a temporary branch.
4.  Pushes that branch to `origin_public` (`yamlr`).

---

## 📝 4. Thought Leadership Repo: `yamlr/k8s-specs`

This is a **Manual Mirror**. You do not push code here. You push **Knowledge**.

*   Extract the logic from `src/yamlr/analyzers/*.py`.
*   Convert it to Markdown:
    *   `specs/E001-ghost-service.md`
    *   `specs/E002-stuck-dash.md`
*   Launch this on HackerNews: *"I documented every way Kubernetes YAML breaks."*

---

## ✅ Action Items

1.  **Rename Local Folder**: `kubecuro` -> `yamlr`.
2.  **Initialize Remotes**:
    *   `git remote add private git@github.com:yamlr/yamlr-enterprise.git`
    *   `git remote add public git@github.com:yamlr/yamlr.git`
3.  **Create Split Script**: I can generate `hack/git_split.py` for you next.
