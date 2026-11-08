# yamlr rules

**Rule Catalog Dashboard**

Displays a comprehensive table of all active semantic rules, checkers, and healers available in the current version.

## Usage
```bash
yamlr rules [FLAGS]
```

## Flags
*   `-v, --verbose`: Show full rationale for every rule in an extra column.
*   `--output=json`: Export rule database as structured JSON.

## Columns
*   **ID**: The unique Rule ID (e.g., `rules/no-latest-tag`).
*   **Name**: Human-readable name.
*   **Severity**: ERROR, WARNING, or INFO.
*   **Description**: Brief summary of what the rule detects.

## Examples
```bash
yamlr rules
# Lists all 50+ active rules
```
