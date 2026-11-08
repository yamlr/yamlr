# yamlr manual

**The Terminal User Guide & Reference**

The `manual` command renders high-fidelity documentation directly in your terminal. This allows for a 100% offline-first experience where you never have to leave the shell to master the engine.

## Usage
```bash
yamlr manual [TOPIC]
```

## Description
*   **The Big Book**: Running `yamlr manual` with no arguments opens the full **Yamlr User Guide**.
*   **Targeted Reference**: Pass a command name (e.g., `scan`, `heal`, `rules`) to view the specific manual for that subcommand.
*   **Specialized Topics**:
    *   `config`: Opens the full **Yamlr Configuration Guide** (`CONFIGURATION.md`).
*   **Rich Rendering**: Uses the engine's internal markdown processor for a premium, formatted reading experience.
*   **Offline-First**: Bundled directly into the binary; no internet connection required.

## Examples

**Open the main User Guide:**
```bash
yamlr manual
```

**View the Scan command manual:**
```bash
yamlr manual scan
```

**View the Configuration Guide:**
```bash
yamlr manual config
```

---
[back to User Guide](../USER_GUIDE.md)
