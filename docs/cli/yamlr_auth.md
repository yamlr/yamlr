# yamlr auth

**Enterprise Authentication**

Manages authentication for Yamlr Enterprise features (Pro).

## Usage
```bash
yamlr auth [COMMAND]
```

## Commands
*   `login`: Initiates a Device Flow login to Yamlr Cloud. Unlocks Pro features like OPA integration and Remote Bundles on this machine.
*   `logout`: Clears local credentials.
*   `status` / `whoami`: Checks current authentication state.

## Examples
```bash
yamlr auth login
# Follow the prompts to authenticate via browser
```
