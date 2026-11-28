# Identity, RBAC, and secrets

Use this reference for ServiceAccounts, RBAC, cloud workload identity, Secret consumption, or credential exposure.

## Identity first

Identify which component needs to act, against which API, in which namespace or external account. Prefer a dedicated workload identity with short-lived credentials. Disable automatic ServiceAccount token mounting when the pod does not call the Kubernetes API.

For cloud APIs, use the managed platform's workload identity mechanism when available. Do not store long-lived cloud access keys in images, manifests, Helm values, ConfigMaps, or ordinary Kubernetes Secrets.

## RBAC

Build permissions from observed API calls or an explicit contract:

- prefer namespaced Role and RoleBinding when cluster scope is unnecessary;
- list concrete API groups, resources, subresources, and verbs;
- use `resourceNames` only when its verb and API semantics actually support that restriction;
- separate application runtime, deployment automation, and human break-glass identities;
- inspect aggregation labels and inherited bindings before concluding a subject is least-privileged.

Avoid wildcard resources or verbs unless the controller must discover an open-ended API surface and the risk is explicitly accepted.

## Secret handling

Kubernetes Secret objects are an API transport and storage mechanism, not proof of encryption or safe delivery. Determine encryption-at-rest, RBAC, audit, backup, Git, and node-access implications.

Do not display secret values during inspection. Compare metadata, key names, object versions, references, and rollout checksums. Prefer an established external-secret, sealed-secret, or platform secret workflow when the repository already uses one.

Environment variables are simple but are captured at process start and can leak through diagnostics. Mounted projected volumes support file-based consumption and rotation semantics, but the application must reopen or watch files deliberately.

## Sources

- RBAC good practices: https://kubernetes.io/docs/concepts/security/rbac-good-practices/
- ServiceAccounts: https://kubernetes.io/docs/concepts/security/service-accounts/
- Secrets good practices: https://kubernetes.io/docs/concepts/security/secrets-good-practices/
