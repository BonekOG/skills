# Workload design

Use this reference to select or review the controller that owns pods.

## Choose by lifecycle

- **Deployment:** interchangeable long-running replicas and rolling replacement.
- **StatefulSet:** stable identity, ordered behavior, or per-replica persistent claims are part of the contract.
- **Job:** bounded work that completes; define retry, completion, and duplicate-execution behavior.
- **CronJob:** scheduled Job creation; define concurrency, missed-run, time-zone, and history behavior.
- **DaemonSet:** one or more pods per eligible node for node-local functionality.
- **Operator-managed resource:** use when an installed controller owns domain lifecycle; do not manage generated children independently.

Do not select StatefulSet only because an application uses storage, or Deployment only because an application serves HTTP. Match the controller to identity and lifecycle semantics.

## Cross-resource invariants

Verify together:

- controller selector and pod-template labels;
- Service selector and target ports;
- ingress or Gateway backend and Service contract;
- PDB and NetworkPolicy selectors;
- HPA target and workload scale support;
- ServiceAccount, ConfigMap, Secret, PVC, and policy references;
- immutable fields that would turn an update into resource replacement.

## Availability is contextual

Replica count, topology spread, anti-affinity, PDB, surge, and unavailable capacity must follow the actual availability objective and cluster topology. A second replica on the same failure domain is not full redundancy, while strict spreading can make a small cluster unschedulable.

PDBs limit some voluntary evictions; they do not protect against node failure, direct deletion, controller rollout, or every autoscaling action. Jobs often should not use a PDB. Confirm that a budget still permits maintenance.

## Controller-specific checks

For StatefulSets, understand PVC retention, update partitioning, identity, quorum, and application-level replication before changing order or scale.

For Jobs and CronJobs, set behavior intentionally for backoff, active deadlines, parallelism, completion mode, TTL, concurrency policy, and missed schedules. Assume a task can start more than once unless its broader system proves otherwise.

For DaemonSets, inspect tolerations, update strategy, host access, priority, and node selectors. Privileged or host-mounted access requires a component-specific justification.

For operators, identify the custom resource as the owning source and inspect reconciliation conditions. Editing generated Deployments or StatefulSets usually creates drift that the operator will revert.

## Sources

- Workload resources: https://kubernetes.io/docs/concepts/workloads/controllers/
- Deployments: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- StatefulSets: https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/
- Jobs: https://kubernetes.io/docs/concepts/workloads/controllers/job/
- CronJobs: https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/
