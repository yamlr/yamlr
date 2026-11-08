# Argo CD Integration (The Supplier Pivot)

Yamlr integrates natively with Argo CD as a Config Management Plugin (CMP) v2. This enables "Self-Healing GitOps" by automatically repairing manifests during the Argo CD sync process.

## Architecture: The "Supplier of Truth"
In this mode, Yamlr acts as a sidecar to the `argocd-repo-server`. 
1. **Discovery**: Argo CD identifies YAML manifests.
2. **Generation**: Yamlr renders the "Healed DNA" of the manifests.
3. **Application**: Argo CD applies the pristine, valid manifests to the cluster.

## Deployment

### 1. Sidecar Injection
Patch your `argocd-repo-server` deployment using the provided Kustomize patch:

```yaml
# integrations/argocd/sidecar-patch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: argocd-repo-server
spec:
  template:
    spec:
      containers:
      - name: yamlr
        image: yamlr/yamlr:latest
        command: [/var/run/argocd/argocd-cmp-server]
        ...
```

### 2. Plugin Configuration
Mount the `plugin.yaml` as a ConfigMap into the sidecar:

```yaml
# integrations/argocd/plugin.yaml
apiVersion: argoproj.io/v1alpha1
kind: ConfigManagementPlugin
metadata:
  name: yamlr
spec:
  version: v1.0
  generate:
    command: ["yamlr", "heal", ".", "--quiet", "--output", "text", "--yes-all"]
  discover:
    find:
      glob: "**/*.{yaml,yml}"
```

## Clinical Output Precision
Yamlr automatically detects the Argo CD environment (via `ARGOCD_APP_NAME`). When detected, it:
1. **Redirects UI to stderr**: Ensuring `stdout` contains only pure YAML.
2. **Forces Quiet Mode**: Silences banners and headers.
3. **Batch Streaming**: Concatenates multiple documents with `---` boundaries for controller ingestion.
4. **UTF-8 Stability**: Forces UTF-8 encoding on Windows to prevent stream corruption.

## Verification
You can simulate the Argo CD CMP execution locally using the provided verification script:
```bash
python scripts/verify_argo.py
```
