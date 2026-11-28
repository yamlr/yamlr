# Security Architecture & Zero-Data Egress

Yamlr is engineered as a secure, local-first systems binary designed to satisfy the most demanding enterprise security standards, including SOC2 Type II, ISO 27001, PCI-DSS, FedRAMP, and air-gapped defense network constraints.

Unlike SaaS developer tools that require organizations to grant external cloud access to proprietary Git repositories, Yamlr enforces a strict **Zero-Data Egress Guarantee**.

---

## Table of Contents

1. [The Zero-Data Egress Pillar](#1-the-zero-data-egress-pillar)
2. [Hermetic Binary & Catalog Isolation](#2-hermetic-binary--catalog-isolation)
3. [Memory Safety & Crash Resilience (Rust Core)](#3-memory-safety--crash-resilience-rust-core)
4. [Jail-Safe Path Normalization & Symlink Defenses](#4-jail-safe-path-normalization--symlink-defenses)
5. [Offline Air-Gapped Licensing Architecture](#5-offline-air-gapped-licensing-architecture)
6. [Least-Privilege Policy Synthesis (`yamlr secure`)](#6-least-privilege-policy-synthesis-yamlr-secure)
7. [Enterprise Guardrails & Size Limits](#7-enterprise-guardrails--size-limits)

---

## 1. The Zero-Data Egress Pillar

Most enterprise Kubernetes outages originate in private configuration code containing sensitive microservice topologies, database hostnames, internal DNS records, and referenced Secret names.

### Architectural Comparison

| Security Characteristic | Cloud-Hosted SaaS Linters | Yamlr Native Engine |
|:---|:---|:---|
| **Code Exfiltration** | Manifests uploaded to third-party cloud | **0% Byte Egress**. Processes 100% in-memory locally. |
| **Cluster Credentials**| Requires `kubeconfig` or cloud IAM role | **Zero credentials needed**. Operates completely offline. |
| **Network Callbacks** | Phones home for rules, telemetry, license checks | **Zero outbound socket connections** by default. |
| **Supply-Chain Exposure**| Multi-tenant cloud databases, third-party APIs | Single, self-contained, statically linked binary. |
| **Air-Gapped Support**| Broken without internet proxy bypass | Fully operational in dark sites, submarines, and enclaves. |

---

## 2. Hermetic Binary & Catalog Isolation

Yamlr packages 100% of its required operational intelligence directly into the compiled native binary:

1. **Embedded OpenAPI Schemas:** Kubernetes OpenAPI v3 definitions for versions 1.21 through 1.37+ are compressed and embedded into binary data segments at compile time.
2. **Embedded Forensic Catalogs:** 53+ native detectors, the Kubernetes API deprecation database, and CIS Benchmark v1.8.0 mapping tables are bundled statically.
3. **Zero Dynamic Downloads:** Running `yamlr scan`, `yamlr heal`, or `yamlr doctor` never downloads external schema files or rule updates at runtime.

---

## 3. Memory Safety & Crash Resilience (Rust Core)

The Yamlr execution core (`native_core`) is written entirely in modern Rust, eliminating entire categories of common systems vulnerabilities:

* **Zero Buffer Overflows:** Guaranteed by Rust's strict ownership model and borrow checker.
* **Zero Use-After-Free Vulnerabilities:** Memory is safely allocated and deallocated at compile-time boundaries.
* **Deterministic Resource Deallocation:** File handles and AST memory are purged immediately upon completing manifest processing.

---

## 4. Jail-Safe Path Normalization & Symlink Defenses

When executing inside automated CI/CD runners or untrusted developer repositories, Yamlr actively protects against path traversal and malicious symlink attacks:

```rust
// Verified check implemented in remediation_io/journal.rs:
if file_path.contains("..") {
    return Err("Security Violation: Path traversal attempts (..) are strictly forbidden.".to_string());
}

let metadata = fs::symlink_metadata(path).map_err(|e| format!("Metadata Error: {}", e))?;
if !metadata.is_file() {
    return Err("Security Violation: Targeted path is not a regular file (Symlinks forbidden).".to_string());
}
```

* **Path Traversal Defense:** Prevents malicious manifests from using `../` to access files outside the workspace.
* **Symlink Trap Mitigation:** Refuses to follow or mutate symbolic links pointing to sensitive host paths (such as `/etc/passwd` or `/var/run/secrets`).

---

## 5. Offline Air-Gapped Licensing Architecture

Enterprise licensing in Yamlr does not rely on cloud license servers, HTTP heartbeats, or SaaS activation portals:

```bash
# Check current entitlement status
yamlr auth status

# Activate signed offline license token
yamlr auth activate <SIGNED_ED25519_LICENSE_TOKEN>
# or:
yamlr subscribe --key <SIGNED_ED25519_LICENSE_TOKEN>
```

### Cryptographic Verification:
* License grants are digitally signed by Yamlr Inc. using asymmetric **RSA / Ed25519** private keys.
* The native binary verifies the token's cryptographic signature against an embedded public key.
* The engine verifies expiration dates, seat limits, and enabled feature tiers completely in-memory without initiating a single network socket connection.

### Customer-Managed PKI & Enclave Roots:
* Public release binaries enforce the embedded public key as the sole tamper-proof root of trust to prevent self-minted bypasses.
* Organizations requiring customer-owned root CAs or signed PKI delegation are served via dedicated private enterprise builds or signed delegation certificates issued under enterprise agreements.

---

## 6. Least-Privilege Policy Synthesis (`yamlr secure`)

Yamlr includes an autonomous security synthesis command designed to enforce Zero-Trust standards across unhardened workloads:

```bash
yamlr secure ./manifests --apply
```

### What `yamlr secure` Synthesizes:
1. **Default-Deny `NetworkPolicy`:** Generates missing ingress/egress microsegmentation policies for isolated namespaces.
2. **Pod Security Context Hardening:** Enforces `runAsNonRoot: true`, `allowPrivilegeEscalation: false`, and `capabilities: { drop: ["ALL"] }`.
3. **Filesystem Immutability:** Enforces `readOnlyRootFilesystem: true` and automatically mounts `/tmp` scratch volumes.

---

## 7. Enterprise Guardrails & Size Limits

To prevent accidental denial-of-service in multi-tenant environments:

* **10MB Manifest Size Guardrail:** The AST sharder automatically rejects YAML manifests exceeding 10MB (`Security Violation: Manifest size exceeds 10MB limit`).
* **Concurrency File Locks:** When applying mutations, Yamlr acquires atomic file locks (`.lock`) to prevent concurrent process write races.
* **Write-Ahead Logging (WAL):** Every file mutation is journaled before touching disk, guaranteeing that any interrupted operation can be completely rolled back.
