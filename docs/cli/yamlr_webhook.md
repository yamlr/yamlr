# `yamlr webhook`

The webhook accepts Kubernetes `admission.k8s.io/v1` `AdmissionReview` requests using HTTP `POST` with a `Content-Length` header and a body of at most 2 MiB. It preserves the request API version, kind, and UID in its response. When healing changes the object, the response contains a base64-encoded RFC 6902 JSONPatch that replaces the object root; unchanged objects receive no patch.

Malformed requests and processing errors return HTTP 400 with a JSON error body. Kubernetes decides how webhook call failures affect admission according to the `failurePolicy` in the cluster's `MutatingWebhookConfiguration`: `Fail` fails closed, while `Ignore` fails open. Choose and review that policy in the cluster configuration.

The built-in listener speaks HTTP only. Terminate TLS with a trusted proxy or sidecar before exposing it to the Kubernetes API server. The listener rejects `--tls-cert`, `--tls-key`, and `--validate-only` because it does not implement TLS termination or validation-only behavior. It also rejects unknown options and invalid port values.
