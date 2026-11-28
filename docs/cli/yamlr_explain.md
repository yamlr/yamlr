# yamlr explain

**Rule & Remediation Documentation**

Provides detailed explanations for specific Rule IDs or configuration topics.

## Usage
```bash
yamlr explain [RULE_ID]
```

## Description
Yamlr findings include a Rule ID (e.g., `rules/no-latest-tag`). Use `explain` to get a full description, the rationale (Why?), and the remediation steps (How?).

## Examples
```bash
yamlr explain rules/no-latest-tag
yamlr explain config/security
yamlr explain config/discovery   # New: Guide to finding features
```
