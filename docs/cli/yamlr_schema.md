# yamlr schema
**Custom Resource Definition (CRD) Schema Management**

The `yamlr schema` command manages and compiles custom Kubernetes schemas and CRD definitions into Yamlr's offline validation cache.

---

## Synopsis

```bash
yamlr schema [ingest|list|clean] [flags]
```

---

## Subcommands

### 1. `ingest`
Compiles and registers CRD YAML manifests into the local schema cache.
```bash
yamlr schema ingest <path> [--out <dir>]
```
*   **`path`** *(required)*: Path to a CRD YAML manifest file or directory of CRDs.
*   **`--out, -o <DIR>`**: Output directory for compiled schema cache. Defaults to `.yamlr/schemas`.

### 2. `list`
Lists all active custom schemas compiled in the schema cache.
```bash
yamlr schema list [--dir <dir>]
```
*   **`--dir <DIR>`**: Schema cache directory to inspect. Defaults to `.yamlr/schemas`.

### 3. `clean`
Clears the local CRD schema cache.
```bash
yamlr schema clean [--dir <dir>]
```
*   **`--dir <DIR>`**: Schema cache directory to purge. Defaults to `.yamlr/schemas`.

---

## Examples

```bash
# Ingest Cert-Manager CRDs into workspace schema cache
yamlr schema ingest ./crds/cert-manager.yaml

# Ingest all CRDs from a directory into .yamlr/schemas
yamlr schema ingest ./manifests/crds/

# List all ingested custom CRD schemas
yamlr schema list

# Clear local CRD schema cache
yamlr schema clean
```

