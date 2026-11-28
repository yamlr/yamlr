# yamlr diff

Preview the changes the native healer would make to YAML manifests. The command does not modify files.

## Usage

```text
yamlr diff [PATH] [-u|--unified]
```

`PATH` may be a YAML file or a directory. It defaults to the current directory. Directories are traversed recursively for `.yaml` and `.yml` files.

## Options

- `-u`, `--unified`: Render changes in unified diff form. Without this option, show an inline word diff.

The target path and `-u` may appear in either order. Other options are currently unsupported and return a usage error; this command does not accept `--output-file`, `--exit-zero`, `--helm`, `--kustomize`, `--crd`, or Kubernetes-version flags.

## Examples

```bash
yamlr diff
yamlr diff ./manifests
yamlr diff ./deployment.yaml --unified
yamlr diff --unified ./manifests
```

## Exit status

- `0`: The preview completed and no changes were proposed.
- `1`: At least one file has proposed changes.
- `3`: The target path does not exist.
- `4`: A manifest could not be read or directory traversal failed.
- `3`: An unsupported option or extra target path was supplied.
