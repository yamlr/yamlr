# yamlr catalog

Yamlr validates your manifests against official Kubernetes JSON schemas. These schemas are distilled for performance and cached locally in `~/.Yamlr/catalogs`.

The `yamlr catalog` command allows you to manage this local cache.

## Usage

```bash
# Check status of local catalog
yamlr catalog
```

### Update Catalog
Download the latest schemas from the upstream repository.
```bash
yamlr catalog update
```

### List Versions
See which Kubernetes versions are currently available in your local cache.
```bash
yamlr catalog list
```

## Options
*   **`--kube-version V`**: Target version for catalog operations (alias: **`--k8s-version`**).

## Lazy Fetching
As of Yamlr v1.0, you rarely need to run `yamlr catalog update` manually.

If you run `yamlr upgrade --to 1.32` and the v1.32 schema is missing, Yamlr will **automatically download it** for you in the background.
