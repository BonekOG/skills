# Live diagnostics

Use this reference for unhealthy workloads and cluster symptoms. Keep commands scoped and read-only until a specific mutation is authorized.

## Establish scope

Resolve context, namespace, resource owner, and relevant time window. Prefer named resources over cluster-wide output. Avoid commands that dump configuration or logs broadly when they can expose credentials or personal data.

Useful starting points, adapted to the target:

```bash
kubectl config current-context
kubectl cluster-info
kubectl -n <namespace> get <kind> <name> -o wide
kubectl -n <namespace> describe <kind> <name>
kubectl -n <namespace> get events --sort-by=.metadata.creationTimestamp
kubectl -n <namespace> logs <pod> -c <container> --tail=200
kubectl -n <namespace> logs <pod> -c <container> --previous --tail=200
```

Treat logs as potentially sensitive. Narrow by container, time, and line count; redact before reporting.

## Trace ownership before symptoms

Move from the user-facing resource to its owners and dependencies: ingress or Gateway, Service, EndpointSlice, pod, ReplicaSet or controller, node, configuration references, identity, and backing service. Do not patch a generated child before identifying the reconciling owner.

## Symptom boundaries

- **Pending:** scheduling events, requests, quota, node readiness, taints, affinity, topology, PVC binding, runtime class, and device availability.
- **CrashLoopBackOff:** current and previous termination state, exit code, logs, command, configuration, write paths, probes, and dependency behavior.
- **Image pull failure:** exact image reference, pull-policy behavior, registry reachability, node architecture, and pull-secret metadata without displaying credentials.
- **Traffic failure:** ready endpoints, Service selectors and ports, listener binding, DNS, NetworkPolicy, ingress or Gateway status, and proxy configuration.
- **Storage failure:** PVC and PV phase, StorageClass, topology, access mode, CSI events, mount errors, capacity, and application consistency.
- **Rollout stuck:** workload conditions, unavailable replica reason, new ReplicaSet, pod events, readiness, quota, surge capacity, and admission results.

## Hypothesis discipline

State observations separately from hypotheses. Rank likely causes and choose the next inspection that best separates them. Absence of an event is not proof that a subsystem is healthy, and a recent warning is not necessarily causal.

Stop broadening the investigation when the request is answered or when the next step would cross an authorization boundary.

## Sources

- Application troubleshooting: https://kubernetes.io/docs/tasks/debug/debug-application/
- Service debugging: https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/
- Pod failure reasons: https://kubernetes.io/docs/tasks/debug/debug-application/determine-reason-pod-failure/
