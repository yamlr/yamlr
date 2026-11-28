# Yamlr Evidence Report (Sample)

This is a sample evidence report demonstrating the cryptographic DNA-tracing provided by Yamlr Enterprise.

## Audit Summary
- **Target**: `broken_resource.yaml`
- **Timestamp**: 2026-03-04T07:15:00Z
- **Verdict**: ✅ HEALED (Verifiable)
- **Signature Method**: HMAC-SHA256
- **Signature**: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6`

## Verifiable Payload (JSON)
```json
{
  "signature_method": "HMAC-SHA256",
  "signature": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
  "payload": {
    "file_path": "broken_resource.yaml",
    "timestamp": 1741065300.0,
    "original_sha256": "f8e9d0c1b2a3948576d5c4b3a2918273645e5f6d7c8b9a0123",
    "healed_sha256": "0a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y",
    "identities": [
      {
        "kind": "Service",
        "name": "web-service"
      },
      {
        "kind": "Deployment",
        "name": "web-frontend"
      }
    ],
    "remediations": [
      {
        "rule_id": "rule/resource-limits",
        "severity": "WARNING",
        "message": "Container 'nginx' has no resource limits defined"
      },
      {
        "rule_id": "rule/no-latest-tag",
        "severity": "ERROR",
        "message": "Container uses 'nginx:latest'. Do not use ':latest' tag in production."
      }
    ]
  }
}
```

## Compliance Mapping
- **SOC2 CC7.2**: Addressed via `resource-limits` enforcement.
- **CIS 5.7.3**: Addressed via `resource-limits` enforcement.
- **NIST SP 800-190**: Addressed via `no-latest-tag` enforcement.
