# yamlr secure
**Synthesize Least-Privilege Network Policies**

The `yamlr secure` command analyzes Service definitions, workload selectors, and active ingress topologies to automatically synthesize least-privilege Kubernetes `NetworkPolicy` manifests, establishing zero-trust network boundaries across namespaces.

## Usage

```bash
# Analyze services in current directory and generate network policies
yamlr secure .

# Generate policies for specific directory and save to file
yamlr secure ./k8s -o ./k8s/network-policies.yaml
```

## Options & Flags

### Positional Arguments
* `[PATH]`: Manifest directory or file containing Kubernetes Services and workloads (defaults to `.`).

### Output Controls
* `-o, --output <PATH>`: File path where generated `NetworkPolicy` manifests should be written. If omitted, generated policies are printed to stdout.

## Security Architecture

1. **Service Topology Discovery**: Discovers all `Service` resources, their target ports, protocols (TCP/UDP), and selector labels.
2. **Namespace Isolation**: Scopes policies to workload namespaces to restrict lateral cluster movement.
3. **Least-Privilege Ingress**: Generates ingress rules permitting only explicit traffic matching defined Service endpoints.

## Exit Codes

* `0` (`EXIT_SUCCESS`): Policies synthesized successfully.
* `1` (`EXIT_VIOLATIONS`): Specified target path does not exist.
* `124` (`EXIT_SYSTEM_ERROR`): Manifest discovery or file read failure.

## Related Commands

* [`yamlr audit`](yamlr_audit.md) — CIS benchmark and compliance audit.
* [`yamlr graph`](yamlr_graph.md) — Inspect relational topology dependency graph.
