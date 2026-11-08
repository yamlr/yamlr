# Flux Integration (Remediation Pivot)

Yamlr integrates with Flux CD to provide "Self-Healing GitOps" via a Post-Renderer pattern for Helm and a specialized remediation pattern for Kustomization.

## Architecture: The "Supplier of Truth"
In this mode, Yamlr acts as a clinical filter for manifests before Flux applies them:
1. **Source**: Flux retrieves manifests from Git or a Helm repo.
2. **Remediation**: Yamlr heals the manifests using its surgical engine.
3. **Application**: Flux applies the healed, valid manifests to the cluster.

## Deployment

### 1. Flux Helm Post-Renderer
Use the `yamlr-post-renderer` script in your `HelmRelease`:

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2beta1
kind: HelmRelease
metadata:
  name: my-app
spec:
  # ...
  postRenderers:
    - kustomize:
        patches:
          - patch: |
              # This triggers the Yamlr remediator sidecar
              apiVersion: apps/v1
              kind: Deployment
              metadata:
                name: my-app
              spec:
                template:
                  metadata:
                    annotations:
                      yamlr.dev/healed: "true"
```

The `post-renderer` sidecar should have the `yamlr` binary and the `post-renderer.sh` script configured.

## Clinical Output Precision
Yamlr automatically detects the Flux environment (via `FLUX_KUSTOMIZATION_NAME` or `FLUX_HELM_RELEASE_NAME`). When detected, it:
1. **Redirects UI to stderr**: Ensuring `stdout` contains only pure YAML.
2. **Forces Quiet Mode**: Silences banners and headers.
3. **Batch Streaming**: Concatenates multiple documents with `---` boundaries.
4. **UTF-8 Stability**: Forces UTF-8 encoding for reliable manifest streams.

## Verification
You can simulate the Flux remediation lifecycle locally:
```bash
python scripts/verify_flux.py
```
