# yamlr stats

**Surgical ROI Calculator**

Displays project-wide metrics on healing impact, productivity gains, and technical mastery.

## Usage
```bash
yamlr stats [FLAGS]
```

## Flags
*   `-h, --help`: Show this help message.
*   `--output=json`: Output statistics as structured JSON for reporting.

## Metrics Displayed
*   **Total Scans**: Number of times the project has been audited.
*   **Issues Auto-Fixed**: Cumulative count of manual corrections saved by the engine.
*   **Est. Time Saved**: Total engineering time reclaimed (based on a conservative 2-minute baseline per fix).
*   **Surgical Efficiency**: The average number of fixes applied per healing session.
*   **Project Mastery**: Your rank based on efficiency (Novice, Surgical Lead, Architect, Grandmaster).

## Examples
```bash
# View the ROI dashboard for the current project
yamlr stats

# Export stats for external reporting
yamlr stats --output=json
```

---
*Note: Telemetry is stored locally in `.yamlr/telemetry.json` and is never shared outside your system.*
