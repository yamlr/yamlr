# Security Policy

The Yamlr team takes the security and integrity of Kubernetes infrastructure configurations seriously.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

If you discover a potential security vulnerability in Yamlr, please **do NOT report it via public GitHub issues**.

Instead, please send a responsible disclosure report to:
- **Email**: security@yamlr.dev

Please include:
1. Description of the vulnerability and potential attack vector / blast radius.
2. Steps to reproduce or proof-of-concept manifest.
3. Affected Yamlr CLI version and operating system.

### Response Timeline
- **Initial acknowledgment**: Within 24 hours.
- **Triage & severity assessment**: Within 48 hours.
- **Fix & advisory release**: Coordinated disclosure within 14 days of verification.

## Local-First Security Guarantee
Yamlr is designed from the ground up to be **local-first and air-gapped compliant**:
- No manifest content, filenames, metadata, or PII is ever transmitted over the network.
- The binary requires zero network access to scan, heal, diff, format, or sign manifests.
