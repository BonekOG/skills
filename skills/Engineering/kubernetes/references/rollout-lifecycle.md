# Rollout and lifecycle behavior

Use this reference for probes, image identity, update strategy, shutdown, or rollout failures.

## Health semantics

- A startup probe protects slow initialization from ordinary liveness evaluation.
- A readiness probe controls whether an endpoint should receive new traffic.
- A liveness probe should fail only when restarting this container is a useful recovery action.

Probe timing and thresholds must follow measured startup and recovery behavior. Avoid synchronized dependency checks that make every replica unready or restart together. Probe endpoints must be bounded and should not expose internals or credentials.

## Images and process lifecycle

Use an immutable image identity when reproducible rollout and rollback matter. A human-readable tag plus digest can preserve both traceability and immutability where tooling supports it.

Ensure the application process receives termination signals, drains bounded in-flight work, and exits within the grace period. Coordinate readiness, endpoint propagation, load balancer behavior, protocol draining, preStop hooks, and application shutdown from evidence; do not default to an arbitrary sleep.

## Update strategy

Choose surge and unavailable capacity from replica count, scheduling headroom, startup time, dependency capacity, and availability objectives. `maxUnavailable: 0` still needs spare capacity for surge pods. Stateful and node-local workloads require controller-specific ordering and data-safety analysis.

Readiness only proves the configured condition at a point in time. Observe application error rate, latency, saturation, and business health when those signals exist.

## Recovery

A controller rollback changes pod template history; it does not undo database migrations, external side effects, configuration schema changes, or state written by the new version. Identify compatibility direction before presenting rollback as safe.

On failure, capture workload conditions, ReplicaSet or revision state, pod termination reasons, events, logs, and health telemetry before another mutation.

## Sources

- Probes: https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
- Deployment updates: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- Container lifecycle hooks: https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/
