# Yamlr Unified Release & Codebase Synchronization Playbook

> **Single Source of Truth:** This document defines the exact checklist, file paths, commands, and architectural rationale for releasing updates across the entire Yamlr ecosystem.
> Whenever code in `native_core` (Rust) or `src/yamlr` (Python) is updated, this playbook guarantees **zero blind spots** and ensures no distribution channel, integration repository, or documentation page is left out of sync.

---

## 🗺️ Ecosystem Architecture & Distribution Topology

```
                                      ┌─────────────────────────────────────────────────────────┐
                                      │              yamlr-core (Private Master)                │
                                      │            Rust native_core + Python SDK                │
                                      └────────────────────────────┬────────────────────────────┘
                                                                   │
           ┌───────────────────────┬───────────────────────────────┼───────────────────────────────┬────────────────────────┐
           ▼                       ▼                               ▼                               ▼                        ▼
 ┌──────────────────┐    ┌──────────────────┐            ┌──────────────────┐            ┌──────────────────┐     ┌──────────────────┐
 │   yamlr/yamlr    │    │  yamlr/releases  │            │yamlr/homebrew-tap│            │  yamlr-website   │     │  PyPI / Registry │
 │  (Public Repo)   │    │  (GitHub Hub)    │            │  (Homebrew Tap)  │            │ (Cloudflare/Web) │     │ (Python Wheels)  │
 ├──────────────────┤    ├──────────────────┤            ├──────────────────┤            ├──────────────────┤     ├──────────────────┤
 │ • Public README  │    │ • vX.Y.Z Release │            │ • Formula/       │            │ • yamlr.dev      │     │ • yamlr-X.Y.Z.whl│
 │ • Dockerfile     │    │ • Binaries (zip/ │            │   yamlr.rb       │            │ • get.yamlr.dev  │     │ • yamlr-X.Y.Z.   │
 │ • GHCR OCI Image │    │   tar.gz)        │            │ • SHA256 Hashes  │            │   (Cloudflare R2)│     │   tar.gz (sdist) │
 │ • Docs Mirror    │    │ • VSIX, Wheels & │            │                  │            │ • Documentation  │     │                  │
 │ • .pre-commit-   │    │   CycloneDX SBOM │            │                  │            │ • WASM Playground│     │                  │
 │   hooks.yaml     │    │ • SLSA Attest    │            │                  │            │                  │     │                  │
 └──────────────────┘    └──────────────────┘            └──────────────────┘            └──────────────────┘     └──────────────────┘
           │                                                                                       │
           ├───────────────────────────────────────────────┐                                       │
           ▼                                               ▼                                       │
 ┌──────────────────┐                            ┌──────────────────┐                              │
 │yamlr/yamlr-action│                            │yamlr/pre-commit- │                              ▼
 │ (GitHub Action)  │                            │      hooks       │                    ┌──────────────────┐
 ├──────────────────┤                            ├──────────────────┤                    │IDE Marketplaces  │
 │ • action.yml     │                            │ • .pre-commit-   │                    │(VS Code & OpenVSX│
 │ • Tags: vX.Y.Z,  │                            │   hooks.yaml     │                    ├──────────────────┤
 │   v1, v1.0.0     │                            │ • Tags: vX.Y.Z   │                    │ • VS Marketplace │
 └──────────────────┘                            └──────────────────┘                    │ • Open VSX Reg.  │
                                                                                         └──────────────────┘
```

---

## 📋 Master Checklist: What, Where, and Why

### 1. Version Bump & Manifests

#### 1A. Core Version Manifests
*Whenever bumping version `X.Y.Z`:*

| File Path | Component | Why It Must Be Updated |
| :--- | :--- | :--- |
| `VERSION` | Engine canonical | Single file read by CLI, CI scripts, and build runners. |
| `native_core/Cargo.toml` | Rust package | Compiles version into native binary (`yamlr --version`). |
| `native_core/Cargo.lock` | Rust lockfile | Deterministic Cargo dependency and version lock. |
| `pyproject.toml` | Python SDK & PyPI | Defines package version for `pip install yamlr` and `maturin`. |
| `src/yamlr/version.py` | Python runtime | `yamlr.__version__` runtime variable for SDK users. |
| `vscode/package.json` | VS Code extension | Extension marketplace version string and VSIX package metadata. |
| `vscode/package-lock.json`| VS Code lockfile | Extension build lockfile version synchronization. |
| `website/package.json` | Web application | Next.js website package version metadata. |

#### 1B. Secondary & Governance Manifests
*Must never be overlooked:*

| File Path | Component | Why It Must Be Updated |
| :--- | :--- | :--- |
| `CHANGELOG.md` | Release Governance | Mandatory entry `## [X.Y.Z] - YYYY-MM-DD` documenting features and fixes. |
| `SECURITY.md` | Security Policy | Updates the active supported version statement (`We support version X.Y.Z`). |
| `Formula/yamlr.rb` | Homebrew Formula | Sets `version "X.Y.Z"` and SHA256 hashes for all 4 Unix tarballs. |
| `deploy/charts/yamlr-webhook/Chart.yaml` | Kubernetes Helm Chart | Updates `version` and `appVersion`. |
| `deploy/charts/yamlr-webhook/values.yaml`| Kubernetes Helm Values | Updates container `image.tag: "X.Y.Z"`. |
| `bazel/rules_yamlr/MODULE.bazel` | Bazel Module | Updates toolchain `version = "X.Y.Z"`. |
| `bazel/rules_yamlr/yamlr/repositories.bzl` | Bazel Repositories | Updates `def yamlr_register_toolchains(version = "X.Y.Z")`. |
| `docs/conf.py` | Sphinx Documentation | Updates `release = "X.Y.Z"`. |

---

### 2. Ecosystem & Integration Repositories

#### 2A. GitHub Action (`yamlr/yamlr-action`)
*Location: `d:\yamlr-action` -> `https://github.com/yamlr/yamlr-action`*

| Action Required | Details / Why |
| :--- | :--- |
| **`action.yml`** | Bump `inputs.version.default` to `vX.Y.Z`. |
| **`README.md`** | Update quickstart snippets (`uses: yamlr/yamlr-action@vX.Y.Z`) and release badge. |
| **Git Tags** | Push tag `vX.Y.Z`, and **force-update** floating tags `v1` and `v1.0.0` to point to the new commit. |

#### 2B. Git Pre-Commit Hooks
*Developers consume pre-commit via two valid repository URLs:*

1. **`yamlr/yamlr` (Public Repo Mirror):**
   - **File:** `.pre-commit-hooks.yaml` **must exist at the root of `yamlr/yamlr`**.
   - **Tag:** Tag `vX.Y.Z` on `yamlr/yamlr` must include `.pre-commit-hooks.yaml` so `repos: - repo: https://github.com/yamlr/yamlr, rev: vX.Y.Z` resolves without failure.
2. **`yamlr/pre-commit-hooks` (Dedicated Tap):**
   - **File:** `d:\yamlr-pre-commit\.pre-commit-hooks.yaml` synchronized with root hooks.
   - **`README.md`:** Documents verified hooks (`yamlr-scan`, `yamlr-fmt`, `yamlr-fix`, `yamlr-heal`).
   - **Tag:** Push tag `vX.Y.Z`.

#### 2C. Homebrew Formula (`yamlr/homebrew-tap`)
*Location: `d:\homebrew-tap` -> `https://github.com/yamlr/homebrew-tap`*
- Update `Formula/yamlr.rb`:
  - `version "X.Y.Z"`
  - `sha256` for `macos-aarch64`
  - `sha256` for `macos-x86_64`
  - `sha256` for `linux-aarch64`
  - `sha256` for `linux-x86_64`
- Commit and push to `main`.

---

### 3. WebAssembly (WASM) In-Browser Playground Engine

Yamlr's interactive playground at `yamlr.dev/preview` runs client-side Rust via WebAssembly.
Whenever `native_core` logic, parsers, or heuristics are modified:

| Step | Command | Output Target |
| :--- | :--- | :--- |
| **Build WASM** | `cd native_core && wasm-pack build --target web --out-dir ../website/public/wasm -- --features wasm` | `website/public/wasm/yamlr_native_bg.wasm` & `yamlr_native.js` |
| **CI Workflow**| `.github/workflows/wasm.yml` | Automated build and verification |
| **Deploy** | Included automatically in `website` Next.js SSG build and Cloudflare Pages deployment. |

---

### 4. Installer Scripts
*Installers must point to the new version and verify checksums:*

| File Path | Command Target | Why It Must Be Updated |
| :--- | :--- | :--- |
| `install.sh` | Linux / macOS curl | Default `VERSION="X.Y.Z"` fallback in `curl -fsSL https://get.yamlr.dev/install.sh \| bash`. |
| `install.ps1` | Windows PowerShell | Default `$Version = "X.Y.Z"` fallback in `irm https://get.yamlr.dev/install.ps1 \| iex`. |
| `scripts/install.sh` | Local script mirror | Mirror of `install.sh` used for testing and dev workflows. |
| `website/public/install.sh` | Live CDN endpoint | Served directly by Cloudflare Pages/R2 at `https://yamlr.dev/install.sh` and `get.yamlr.dev`. |
| `website/public/install.ps1` | Live CDN endpoint | Served directly by Cloudflare Pages/R2 at `https://yamlr.dev/install.ps1` and `get.yamlr.dev`. |

---

### 5. Website, UI & Documentation Pages
*All user-facing surfaces must reflect the latest version and download links:*

| File Path | Location / Element | Why It Must Be Updated |
| :--- | :--- | :--- |
| `website/src/components/Footer.tsx` | Footer Badge & Link | Shows `Release vX.Y.Z` badge and links to `Release Downloads (vX.Y.Z)`. |
| `website/src/components/SmartInstall.tsx` | Modal Downloads & Snippets | Direct download links AND verification output (`yamlr X.Y.Z (x86_64, CST engine v1.31)`). |
| `website/src/app/page.tsx` | Hero / Quickstart | Direct version references in pre-commit and install snippets. |
| `website/src/app/preview/page.tsx` | Sandbox Banner | Engine version displayed in playground environment. |
| `website/src/app/docs/[slug]/page.tsx` | Docs Route Generator | Must include `downloads` and `pre-commit-guide` in `DOC_PAGES` to prevent 404s. |
| `website/docs/*` | All Markdown Docs | `GETTING_STARTED.md`, `CLI_REFERENCE.md`, `DOWNLOADS.md`, `CI_CD_INTEGRATION.md`. |

---

### 6. Multi-Platform Compilations & Compliance Assets

The complete set of release packages placed in `dist/vX.Y.Z/`:

| Artifact Name | Purpose | Generator / Runner |
| :--- | :--- | :--- |
| `yamlr-windows-x86_64.zip` | Windows x86_64 binary | `cargo build --release --bin yamlr` |
| `yamlr-linux-x86_64.tar.gz` | Linux x86_64 static musl | `cross build --release --target x86_64-unknown-linux-musl` |
| `yamlr-linux-aarch64.tar.gz` | Linux ARM64 static musl | `cross build --release --target aarch64-unknown-linux-musl` |
| `yamlr-macos-x86_64.tar.gz` | macOS Intel (x86_64) | GitHub Actions `macos-15-intel` runner |
| `yamlr-macos-aarch64.tar.gz` | macOS Apple Silicon (arm64) | GitHub Actions `macos-latest` (M-series) runner |
| `yamlr-k8s-X.Y.Z.vsix` | VS Code Extension Package | `cd vscode && npx @vscode/vsce package` |
| `THIRD_PARTY_NOTICES_RUST.txt` | Rust License Attribution | `cargo about generate --locked --fail about.hbs` |
| `yamlr-sbom-*.cdx.json` (x5) | CycloneDX SBOMs | `anchore/sbom-action` for all 5 targets |
| `SHA256SUMS.txt` / `checksums.txt` | Checksum Manifests | `sha256sum *` |
| SLSA Provenance Attestation | Supply chain integrity | `actions/attest@v4.2.1` |

---

### 7. External Distribution Channels Checklist

#### Channel A: GitHub Releases (`yamlr/releases`, `yamlr/yamlr`, `yamlr/yamlr-core`)
- Create release tag `vX.Y.Z` across all three repositories.
- Upload all 6 binary assets + `checksums.txt` + `SHA256SUMS.txt` + SBOMs.
- Upload Python `.whl` and `.tar.gz` sdist.

#### Channel B: Homebrew Tap (`yamlr/homebrew-tap`)
- Update `Formula/yamlr.rb` with version and 4 SHA256 hashes. Commit and push.

#### Channel C: Cloudflare R2 Bucket (`yamlr-releases` -> `get.yamlr.dev`)
- Upload binaries to `yamlr-releases/vX.Y.Z/<file>`:
  ```bash
  cd website
  npx wrangler r2 object put yamlr-releases/vX.Y.Z/<file> --file dist/vX.Y.Z/<file> --remote
  ```
- Upload root install scripts:
  ```bash
  npx wrangler r2 object put yamlr-releases/install.sh --file ../install.sh --remote
  npx wrangler r2 object put yamlr-releases/install.ps1 --file ../install.ps1 --remote
  ```

#### Channel D: Cloudflare Pages (`yamlr-website` -> `yamlr.dev`)
- Build static export and deploy:
  ```bash
  cd website
  npm run build
  npx wrangler pages deploy out --project-name yamlr-website
  ```

#### Channel E: PyPI Registry (`pypi.org/project/yamlr`)
- Build wheels & sdist:
  - Windows: `maturin build --release --manifest-path native_core/Cargo.toml`
  - Linux: build via manylinux container / Linux VM
  - macOS: build on macOS runner
  - Source distribution: `maturin sdist` (must contain `LICENSE` at root per PEP 639)
- Upload to PyPI:
  ```bash
  python -m twine upload dist/vX.Y.Z/yamlr-X.Y.Z* -u __token__ -p <PYPI_TOKEN>
  ```

#### Channel F: GitHub Container Registry (`ghcr.io/yamlr/yamlr`)
- Verify `Dockerfile` has `ARG YAMLR_VERSION=X.Y.Z`.
- Trigger `.github/workflows/docker-publish.yml` in `yamlr/yamlr`.
- Verify multi-arch images (`linux/amd64` and `linux/arm64`) under:
  - `ghcr.io/yamlr/yamlr:latest`
  - `ghcr.io/yamlr/yamlr:X.Y.Z`
  - `ghcr.io/yamlr/yamlr:vX.Y.Z`

#### Channel G: VS Code Marketplace & Open VSX Registry
- Publish to Visual Studio Marketplace:
  ```bash
  cd vscode
  npx @vscode/vsce publish --packagePath yamlr.vsix -p <VSCE_PAT>
  ```
- Publish to Open VSX Registry (Cursor, Gitpod, VSCodium):
  ```bash
  npx ovsx publish yamlr.vsix -p <OVSX_PAT>
  ```

---

## ⚡ Canonical Order of Operations (Runbook)

1. **Implement & Test:** Write code, pass all unit & integration tests (`cargo test --lib`).
2. **Version Bump:** Update 8 core manifest files (`VERSION`, `Cargo.toml`, `pyproject.toml`, etc.).
3. **Governance Files:** Update `CHANGELOG.md`, `SECURITY.md`, `Chart.yaml`, and `Formula/yamlr.rb`.
4. **WASM Build:** Rebuild WebAssembly binary for browser playground (`wasm-pack build`).
5. **Website & Docs:** Update `SmartInstall.tsx`, `Footer.tsx`, and Markdown guides.
6. **Compile Binaries & SBOMs:** Build all 5 native binaries, CycloneDX SBOMs, and VS Code `.vsix`.
7. **Attestation & Checksums:** Produce `SHA256SUMS.txt`, `checksums.txt`, and sign with `actions/attest`.
8. **Package PyPI:** Build wheels and sdist, upload to PyPI via `twine`.
9. **Publish GitHub Releases:** Push `vX.Y.Z` tag to `yamlr/releases`, `yamlr/yamlr`, and `yamlr/yamlr-core`; attach assets.
10. **Sync Integrations:**
    - Update `yamlr/yamlr-action` (`action.yml`, tags `vX.Y.Z`, `v1`).
    - Update `yamlr/pre-commit-hooks` and ensure root `.pre-commit-hooks.yaml` exists in `yamlr/yamlr`.
    - Push updated formula to `yamlr/homebrew-tap`.
11. **Upload R2 CDN:** Upload archives and install scripts to `yamlr-releases` on Cloudflare R2.
12. **Deploy Website:** Run `npm run build && wrangler pages deploy out` for `yamlr.dev`.
13. **Publish Docker:** Trigger `docker-publish.yml` for `ghcr.io/yamlr/yamlr:latest`.
14. **Publish Extensions:** Publish VSIX to VS Code Marketplace and Open VSX.
