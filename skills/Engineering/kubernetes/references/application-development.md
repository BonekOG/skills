# Kubernetes-aware application development

Use this reference when changing application or container code, not only deployment YAML.

## Establish the runtime contract

Inspect the language, framework, existing server lifecycle, container build, tests, and deployment manifests. Preserve repository conventions. Determine which behavior is actually required before adding Kubernetes-specific code.

Design the process for replacement at any time:

- keep durable state outside the container filesystem;
- make repeated delivery, retry, and concurrent execution safe where the workload contract requires it;
- avoid relying on pod names, stable local IPs, startup order, or a single replica;
- expose configuration through the repository's established environment or mounted-file mechanism;
- use workload identity or a platform credential provider instead of embedded cloud credentials;
- write normal application logs to standard output or standard error unless the platform contract says otherwise.

## Startup and health

Separate these questions when the application needs health endpoints:

- **startup:** has initialization completed far enough for ordinary health evaluation?
- **liveness:** is local process recovery by restart likely to help?
- **readiness:** should this instance receive new traffic now?

Do not add a liveness endpoint by reflex. A failing dependency in liveness can restart every replica during the same outage. Readiness may include a dependency only when the application truly cannot serve useful traffic without it and removing all replicas from routing is the intended behavior.

Keep health handlers bounded, inexpensive, and free of sensitive data. Test state transitions, not just the HTTP status in a permanently healthy process.

## Termination and draining

Handle the platform's termination signal in the process that runs as container PID 1. On termination:

1. stop accepting new work or become unready when the protocol supports it;
2. allow bounded in-flight work to finish;
3. close listeners, workers, and telemetry exporters;
4. exit before the configured grace period.

Do not assume a shell wrapper forwards signals. Prefer exec-form container entrypoints or explicit forwarding. Use a lifecycle hook only when application-level shutdown cannot express the required coordination; fixed sleeps are a last-resort compatibility measure, not the default design.

## Resources and scaling behavior

Avoid deriving thread, worker, heap, or connection-pool sizes from host capacity when the container can see a smaller cgroup allocation. Confirm the runtime is container-aware and make concurrency configurable when appropriate.

For CPU-based autoscaling, stable CPU requests are part of the scaling contract. For queue or request-based scaling, expose or consume the metric that represents demand. Make background work lease-aware or idempotent if multiple replicas can process the same item.

## Configuration and files

- Fail startup with an actionable message for missing required configuration, but never include secret values.
- Define precedence when flags, environment variables, and files overlap.
- Decide whether mounted configuration is read once or reloaded; do not imply hot reload accidentally.
- Write temporary data only to documented writable paths and bound its growth.
- Treat container image contents as immutable. Persist uploads, databases, and durable queues externally.

## Networking and identity

Bind service listeners to the intended container interface rather than loopback unless a sidecar-only contract requires loopback. Respect forwarded headers only from trusted proxies. Expose separate admin or metrics listeners deliberately and avoid routing them publicly by default.

Use short-lived workload identity credentials where supported. Scope Kubernetes API access to the exact resources and verbs the application uses, and disable service-account token mounting when it does not call the API.

## Validation

Prefer existing unit and integration tests. Add focused tests when behavior changes:

- health transitions during startup, dependency loss, and shutdown;
- signal-driven graceful termination with bounded completion;
- missing and rotated configuration;
- duplicate or concurrent work when retries are possible;
- container execution as the intended non-root user with expected writable paths.

Validate the built container and rendered workload together when feasible; either side can violate the combined contract.

## Authoritative starting points

- Kubernetes application checklist: https://kubernetes.io/docs/concepts/cluster-administration/manage-deployment/
- Container lifecycle hooks: https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/
- Liveness, readiness, and startup probes: https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/
- Configuration best practices: https://kubernetes.io/docs/concepts/configuration/overview/
