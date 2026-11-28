# Google Kubernetes Engine

Load only when the target is GKE or uses Google Cloud-specific Kubernetes integrations.

## Resolve the cluster mode

Capture GKE release channel and versions, Standard or Autopilot mode, node architecture, Dataplane V2 or other networking mode, ingress or Gateway controller, CSI drivers, Config Sync, and workload identity configuration. Autopilot admission and resource defaults can materially change rendered workloads.

## Identity

Use Workload Identity Federation for GKE when it is the cluster standard. Verify the Kubernetes ServiceAccount, IAM principal mapping, namespace, target Google service account where applicable, and application credential-chain behavior. Do not mount long-lived service-account key files.

## Networking and exposure

Distinguish GKE Ingress, Gateway API, internal and external load balancers, and NetworkPolicy implementation. Controller annotations and health-check inference depend on the selected product and version; validate them against the target controller.

## Storage and scheduling

Match Persistent Disk or Filestore CSI features to access mode, topology, expansion, snapshot, and backup needs. In Autopilot, validate privileged features, host access, resource ranges, and workload separation against current admission behavior rather than Standard-cluster assumptions.

## Sources

- GKE documentation: https://cloud.google.com/kubernetes-engine/docs
- Workload Identity Federation: https://cloud.google.com/kubernetes-engine/docs/concepts/workload-identity
- GKE networking: https://cloud.google.com/kubernetes-engine/docs/concepts/network-overview
