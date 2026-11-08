
# Man Page Installation & Usage

Yamlr includes standard troff man pages for all commands, providing a native documentation experience on Linux and macOS.

## 1. Quick Usage (Without Installation)
You can view a local man page file directly using the `man` command:

```bash
# View the man page for 'yamlr check'
man ./docs/man/man1/yamlr-check.1
```

## 2. Installation (Standard Linux/macOS)
To make the man pages available system-wide (so you can just type `man yamlr-check`), install them to your system's man path.

### Option A: System-Wide (Requires Sudo)
```bash
sudo cp docs/man/man1/*.1 /usr/share/man/man1/
sudo mandb # Update the manual database
```

### Option B: User-Local (No Sudo)
```bash
mkdir -p ~/.local/share/man/man1
cp docs/man/man1/*.1 ~/.local/share/man/man1/
export MANPATH=$HOME/.local/share/man:$MANPATH
```

## 3. End-User Experience
Once installed, users can access documentation natively:

```bash
# General help
man yamlr-scan

# Specific command details
man yamlr-heal
man yamlr-auth
```
