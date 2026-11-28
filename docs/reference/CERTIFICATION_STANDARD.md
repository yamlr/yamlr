# Yamlr Manifest Verification Standard (v1.0)

**The "Yamlr Verified" badge indicates that a Kubernetes repository meets strict standards of structural integrity, schema validity, and cross-resource safety.**

---

## Technical Criteria

To achieve **Yamlr Verified** status, a project's manifests must satisfy three core requirements:

### 1. Structural Determinism
- **Pass**: 100% schema validation across target Kubernetes releases (v1.21 through v1.32+).
- **Pass**: Zero Critical or Error violations in the validation pipeline.
- **Requirement**: No unknown fields on standard APIs, valid scalar types, and no syntax ambiguities.

### 2. Resource & Image Hygiene
- **Pass**: Explicit resource `limits` and `requests` declared for all containers.
- **Pass**: Immutable image tagging (pinned to specific version tags or SHA-256 digests; no `:latest`).
- **Requirement**: Predictable resource consumption and reproducible rollout behavior.

### 3. Cross-Resource Relational Integrity
- **Pass**: All referenced ConfigMaps, Secrets, and PersistentVolumeClaims exist in the target namespace.
- **Pass**: Service port mappings strictly match underlying container workload ports.
- **Pass**: Ingress rules point to active, valid backend services.

---

## Verification in CI/CD

```yaml
# GitHub Actions check
- name: Verify Manifest Integrity
  run: yamlr scan ./k8s --fail-on error
```

When all checks pass, embed the verified badge in your `README.md`:
```markdown
![Yamlr Verified](https://yamlr.dev/badges/yamlr-verified.svg)
```

**Specification:** Yamlr Manifest Quality Standard  
**Standard ID:** `YAMLR-SPEC-v1`
