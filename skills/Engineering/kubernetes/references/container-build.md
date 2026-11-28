# Container builds for Kubernetes

Use this reference when changing a Dockerfile, build pipeline, entrypoint, or image contract for a Kubernetes workload.

## Build the runtime artifact deliberately

Use the repository's established build system and base-image policy. Prefer reproducible multi-stage builds that leave compilers, package managers, credentials, and source-only dependencies out of the runtime image. Pin dependencies and base images according to the team's update strategy; digest pinning improves reproducibility but also requires an explicit refresh process.

Never pass registry tokens, package credentials, SSH keys, or cloud credentials through image layers, build arguments, committed files, or logs. Use the build system's secret-mount mechanism when private dependencies require credentials.

## Runtime contract

- run the application as a non-root identity when compatible with the application and target policy;
- use exec-form entrypoints so the process receives signals;
- avoid a shell or supervisor unless it has a concrete lifecycle role and forwards signals correctly;
- bind intended service ports and document writable paths;
- keep mutable state outside the image and durable state outside the container filesystem;
- include only health-check tooling the actual probe mechanism requires;
- support every target node architecture or constrain scheduling accordingly.

Do not add a Dockerfile `HEALTHCHECK` as a substitute for Kubernetes probes without confirming how the runtime and platform use it.

## Image identity and provenance

Use an image reference that supports the repository's release and rollback model. Produce architecture, source revision, build time, and package provenance through the established labels, attestations, or SBOM workflow. Do not claim an image is secure solely because it is small or uses a distroless base.

## Validation

Build the exact target stage, inspect its configured user and entrypoint, run the existing tests, start it with representative configuration, send a termination signal, and verify expected writable paths. Use the repository's vulnerability, signature, and policy checks when present; report unavailable checks rather than inventing a clean result.

## Sources

- Images: https://kubernetes.io/docs/concepts/containers/images/
- Container lifecycle: https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/
- Kubernetes image security checklist: https://kubernetes.io/docs/concepts/security/security-checklist/
