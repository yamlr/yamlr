# yamlr admin

**System & Engine Diagnostics**

The `admin` command provides local operational diagnostics, runtime verification, and machine identity inspection for the Yamlr engine.

## Usage
```bash
yamlr admin [health|stats|users]
```

## Description
Performs local diagnostic inspections of the Yamlr execution environment, verifying native core bindings, local schema caches, and machine fingerprint identification.

## Actions
*   **`health`**: Verify local telemetry gateway connectivity, native engine core linkage, and active schema engine coverage.
*   **`stats`**: Display local workspace defect metrics, supported Kubernetes schema versions, and zero-egress validation state.
*   **`users`**: Display local host machine fingerprint and active licensing tier.

## Examples

**Run engine health diagnostic:**
```bash
yamlr admin health
```

**View workspace engine stats:**
```bash
yamlr admin stats
```

**Inspect local machine identity:**
```bash
yamlr admin users
```

---
*Note: All admin commands operate 100% locally on the host machine with zero external modification capabilities.*
