# Resources, scheduling, and disruption

Use this reference for requests, limits, QoS, placement, autoscaling, quotas, and disruption controls.

## Resource decisions

Requests affect scheduling and commonly affect autoscaling calculations. Limits affect runtime enforcement. CPU and memory have different behavior: CPU limits throttle; memory limits can lead to OOM termination. Choose them from observed behavior, SLOs, node policy, and multi-tenancy needs rather than fixed ratios.

Avoid universal rules about CPU limits or memory headroom. When production measurements do not exist, label initial values as estimates and define how they will be tuned. Include every application, init, and sidecar container in the budget.

## Scheduling

Trace unschedulable pods through scheduler events before changing requests. Consider allocatable capacity, quota, taints and tolerations, node affinity, topology constraints, runtime class, PVC topology, extended resources, and priority.

Topology spread and anti-affinity trade resilience for scheduling flexibility. Match them to real node and zone topology. Avoid constraints that require failure domains the cluster does not provide.

## Autoscaling

Confirm that the chosen metric represents demand and that scaling can reduce the bottleneck. CPU utilization targets depend on CPU requests. Check stabilization, rate limits, cold-start time, downstream capacity, and minimum safe replica count. For event-driven work, consider backlog and processing latency rather than CPU alone.

## Disruption budgets

Use a PDB when availability during voluntary eviction matters and the workload can run with a defined number of healthy replicas. Verify selectors and `disruptionsAllowed`. Ensure the budget permits intended maintenance. Do not imply protection from involuntary failures or direct controller changes.

## Sources

- Resource management: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
- Pod QoS: https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/
- Pod disruptions: https://kubernetes.io/docs/concepts/workloads/pods/disruptions/
- Horizontal autoscaling: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
