# API and validation

Use this reference for Kubernetes version compatibility, CRDs, generated YAML, admission, or deprecated fields.

## Resolve the real API surface

Do not select an API version from a static table alone. Establish the target server version and discover resources when cluster access is available:

```bash
kubectl api-resources
kubectl explain <resource> --api-version=<group/version>
kubectl get --raw /openapi/v3
```

For offline work, use the repository's supported Kubernetes range and version-matched schemas. State the assumed floor and ceiling.

## Validation layers

Use the layers that are available and relevant:

1. render Helm or Kustomize to concrete objects;
2. parse YAML and reject duplicate or ambiguous fields where tooling permits;
3. validate built-in APIs against a target-version schema;
4. provide CRD schemas for custom resources rather than treating them as unknown;
5. run policy checks matching the target admission configuration;
6. use server-side dry run for discovery, defaulting, conversion, and admission behavior;
7. inspect diff for ownership changes, deletion, replacement, and defaulted fields.

Client schema success does not prove admission or controller behavior. Server-side dry run can invoke admission webhooks and requires cluster access; use it only against the resolved target and understand webhook dry-run support.

## CRDs and field ownership

Confirm the installed CRD version, served/storage versions, structural schema, conversion path, and owning controller version. A CRD may accept fields that its controller ignores. When server-side apply is used, inspect managed fields conflicts rather than forcing ownership by default.

## Sources

- API deprecation policy: https://kubernetes.io/docs/reference/using-api/deprecation-policy/
- API overview: https://kubernetes.io/docs/reference/using-api/
- Server-side apply: https://kubernetes.io/docs/reference/using-api/server-side-apply/
- Custom resources: https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/
