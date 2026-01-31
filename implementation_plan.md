# Implementation Plan: Prophetic Migration Engine (Deprecation Auto-Fix)

## Goal
Enable Yamlr to automatically upgrade deprecated Kubernetes APIs (e.g., `extensions/v1beta1` Deployment -> `apps/v1`) during the healing process.

## User Review Required
> [!IMPORTANT]
> Auto-migration modifies the `apiVersion` and potentially the schema structure (e.g., adding `selector`). This is a semantic change.
> We must ensure the `DNA Check` in the pipeline alerts the user that "Logic has changed" (which is intentional here).

## Proposed Changes

### Core Logic
#### [MODIFY] [deprecations.py](file:///d:/yamlr/src/yamlr/core/deprecations.py)
*   Update `DeprecationInfo` dataclass to include `migration_strategy` (enum/callable).
*   Define migration strategies for common deprecations (Deployment, Ingress, CronJob).

#### [NEW] [migrator.py](file:///d:/yamlr/src/yamlr/core/migrator.py)
*   `MigrationEngine` class.
*   `migrate(doc: Dict, target_version: str) -> Tuple[Dict, List[str]]`.
*   Logic to apply specific structural patches (e.g., adding selectors).

#### [MODIFY] [pipeline.py](file:///d:/yamlr/src/yamlr/core/pipeline.py)
*   Inject `MigrationEngine` execution after Stage 6 (Structure) and before Stage 6.5 (Content Analysis).
*   Add Stage 6.1 audit logs.

## Verification Plan

### Automated Tests
*   Create `tests/migration_test.py`.
*   Input: `extensions/v1beta1` Deployment (manifest string).
*   Action: Run `engine.heal`.
*   Assert: Output contains `apps/v1` and `spec.selector`.

### Manual Verification
*   Create `legacy_deployment.yaml`.
*   Run `yamlr heal legacy_deployment.yaml`.
*   Verify output is modern.

## Phase 4: Legacy Logic Porting (IMMEDIATE PRIORITIES)
This phase focuses on transferring high-value logic from the legacy monolith (`Synapse`/`Shield`/`Lexer`) to the modular system (`CrossResourceAnalyzer`, `KubeLexer`).

### 4.1 Cross-Resource Enhancements (`analyzers/cross_resource.py`)
-   **Service Port Logic:** Validate `targetPort` exists in the container's `ports`.
-   **Ingress Logic:** Validate backend Services exist and ports match.
-   **Volume Mounts:** Validate ConfigMap/Secret references in `volumes`.

### 4.2 Lexer Enhancements (`parsers/lexer.py`)
-   **Stuck Dash Fix:** Explicitly support `-image: nginx` (Legacy regex handled this).

### 4.3 Test Coverage
-   Created dedicated test cases for Service Port mismatch and Ingress backend validation.
