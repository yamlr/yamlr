# yamlr graph
Visualize resource dependencies and analyze the blast radius of potential failures.

## Subcommands
### topo
Displays an ASCII tree of all resource relationships in the current workspace.
```bash
yamlr graph topo
```

### blast-radius
Analyzes the impact of a specific resource. Shows all downstream dependents that would be affected if the root resource fails or is modified.
```bash
yamlr graph blast-radius --resource Deployment/my-app
```

### export
Exports the ResourceGraph in professional diagram formats.
```bash
yamlr graph export --format mermaid
yamlr graph export --format dot
```

## Flags
* `--resource`: The target resource key (e.g., `Service/my-svc` or `Deployment/ns/my-app`).
* `--format`: Export format (`mermaid`, `dot`, `json`). Default: `mermaid`.

### Universal Expert Flags
Available across primary commands:

*   **`--timing`**: [PERFORMANCE] Output surgical execution timing breakdown.
*   **`--timing-file <FILE>`**: [PERFORMANCE] Save performance profiling data to a JSON file.
*   **`--verbose`**: Full audit logs and engine stages.
*   `-q`, `--quiet`: Minimal output mode (exit codes only).
