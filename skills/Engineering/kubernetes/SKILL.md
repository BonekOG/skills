---
name: kubernetes
description: Use when designing and adapting application code for Kubernetes, creating or reviewing manifests and delivery configuration, diagnosing workloads, and safely operating live clusters.
compatibility: "Requires kubectl."
disable-model-invocation: false
---

# Kubernetes Operations

## Purpose

Make application code and Kubernetes delivery artifacts reliable for the actual repository and target environment. Diagnose from evidence, preserve repository-specific deployment conventions, and keep live-cluster mutations behind explicit authorization.

The user's request takes precedence over this skill's recommendations. Treat the guidance as decision support unless a rule protects credentials, live infrastructure, or an explicit authorization boundary.

## Select the operating mode

Use only the modes required by the request:

1. **Application development** — change or review application code so it starts, serves, scales, shuts down, reports health, and consumes configuration correctly in Kubernetes.
2. **Declarative delivery** — create or review YAML, Helm, Kustomize, GitOps, policies, and CI validation.
3. **Live diagnosis** — inspect a cluster without changing desired or runtime state.
4. **Live mutation** — apply, delete, restart, scale, drain, rollback, or otherwise change a cluster after exact authorization.

Editing repository code or declarative configuration does not authorize applying it to a cluster.

## Discover context proportionally

Inspect repository instructions, deployment tooling, existing manifests, tests, and operational documentation before introducing a new pattern. Capture only context that can change the result:

- target Kubernetes version or supported version range;
- distribution or managed platform and workload operating system;
- environment criticality, namespace, workload owner, and delivery method;
- admission policies, CNI, ingress or Gateway controller, storage, autoscaling, service mesh, GitOps, and observability components;
- application runtime, startup behavior, traffic contract, state, dependencies, and availability expectations.

For offline code or manifest work, continue with explicit assumptions when cluster access is unavailable. Before live commands, resolve the current kubeconfig context, cluster identity, namespace, and exact resources. Verify APIs with discovery, `kubectl explain`, server-side dry run, and the target version rather than a memorized version table.

## Load focused guidance

Read only the references relevant to the selected mode and observed risks:

- Application code or container behavior: [application-development.md](references/application-development.md).
- Container image, Dockerfile, entrypoint, or image supply chain: [container-build.md](references/container-build.md).
- Deployment, StatefulSet, Job, CronJob, DaemonSet, or operator choice: [workload-design.md](references/workload-design.md).
- Live incident or unhealthy workload: [diagnostics.md](references/diagnostics.md).
- Security context or admission posture: [workload-security.md](references/workload-security.md).
- Requests, limits, scheduling, autoscaling, or disruption: [resources-scheduling.md](references/resources-scheduling.md).
- Service, DNS, ingress, Gateway API, or NetworkPolicy: [networking.md](references/networking.md).
- RBAC, ServiceAccounts, workload identity, or Secrets: [identity-secrets.md](references/identity-secrets.md).
- Probes, shutdown, rollout, or image identity: [rollout-lifecycle.md](references/rollout-lifecycle.md).
- API compatibility, CRDs, or schema validation: [api-validation.md](references/api-validation.md).
- Persistent data, PVCs, snapshots, or migrations: [storage-data.md](references/storage-data.md).
- Admission policy, namespace tenancy, quotas, or policy engines: [policy-multitenancy.md](references/policy-multitenancy.md).
- Helm, Kustomize, GitOps, or delivery CI: [delivery-tooling.md](references/delivery-tooling.md).
- Metrics, logs, traces, alerts, or debugging telemetry: [observability.md](references/observability.md).
- Managed platform: read only the matching [EKS](references/platforms/eks.md), [GKE](references/platforms/gke.md), [AKS](references/platforms/aks.md), or [OpenShift](references/platforms/openshift.md) reference.

Do not load multiple platform references unless the task genuinely compares or spans platforms.

## Operating invariants

1. Start live work with the narrowest useful read-only inspection.
2. Treat production, control-plane components, nodes, cluster-scoped resources, admission policy, storage, and identity as high risk regardless of context naming.
3. Do not run a state-changing cluster command without explicit authorization for the exact action and target. This includes `apply`, `delete`, `patch`, `edit`, `replace`, `rollout restart`, `rollout undo`, `scale`, `cordon`, `uncordon`, `drain`, Helm upgrade or rollback, and GitOps sync or suspend operations.
4. Do not print Secret data, tokens, kubeconfig contents, environment dumps, or credentials from logs. Prefer metadata, key names, checksums, status, and narrowly filtered output.
5. Prefer a reviewed change to the owning declarative source over an imperative live fix when GitOps or repository ownership exists.
6. Distinguish Kubernetes requirements, platform constraints, team policy, and optional hardening. Do not turn recommendations such as PDBs, liveness probes, CPU limits, read-only root filesystems, multiple replicas, or default-deny networking into universal requirements.
7. Preserve intentional exceptions for system components, Windows workloads, operators, Jobs, DaemonSets, stateful systems, and specialized hardware. Explain the tradeoff instead of silently normalizing the workload.
8. Before a mutation, state expected effect, blast radius, success signal, failure signal, and recovery path. A rollback is not safe when it can reverse data or schema changes; call that out.

## Work method

1. Identify the owning source and selected operating mode.
2. Inspect the smallest evidence set that can confirm or reject the leading explanation.
3. Select applicable failure domains: application lifecycle, workload security, resources and scheduling, networking, identity and secrets, rollout behavior, API compatibility, storage, or delivery reconciliation.
4. Make the smallest coherent code or configuration change. Keep cross-resource contracts aligned: selectors, labels, ports, health paths, identities, references, storage, and controller ownership.
5. Validate at the closest reliable boundary available. Examples include repository tests, container execution, rendered chart inspection, Kustomize build, schema validation, policy checks, `kubectl diff`, and server-side dry run.
6. For an authorized live change, observe rollout state, events, health, traffic indicators, and application telemetry. Stop and diagnose on unexpected behavior; do not chain additional mutations speculatively.

## Output

Report the result in the shape most useful to the request. Include:

- target and material assumptions;
- evidence or changed artifacts;
- selected risks and tradeoffs;
- validation performed and remaining gaps;
- live impact and recovery notes when applicable.

Separate direct evidence from inference. If missing information prevents a safe live operation, stop before the mutation and ask for that exact information.
