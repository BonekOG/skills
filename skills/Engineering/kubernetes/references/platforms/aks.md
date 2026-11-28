# Azure Kubernetes Service

Load only when the target is AKS or uses Azure-specific Kubernetes integrations.

## Resolve installed integrations

Capture AKS and Kubernetes versions, node-pool operating systems and architectures, Azure CNI mode, network policy implementation, ingress or Gateway controller, managed add-ons, CSI drivers, autoscaling, and workload identity setup. Do not assume an add-on or legacy identity mechanism from cluster age alone.

## Identity

Prefer Microsoft Entra Workload ID when it is the cluster standard. Verify the Kubernetes ServiceAccount annotation, federated identity credential subject and audience, namespace, managed identity permissions, and application SDK credential chain. Avoid client secrets in manifests and ordinary Kubernetes Secrets.

## Networking and ingress

Distinguish internal and external load balancers, Application Gateway integrations, ingress controllers, Gateway API, private clusters, and Azure CNI variants. Validate annotations and subnet capacity against the deployed controller and network model.

## Storage and nodes

Match Azure Disk, Azure Files, or Blob CSI behavior to workload semantics, access modes, topology, performance, backup, and encryption. Review Windows-specific security and filesystem behavior separately from Linux nodes.

## Sources

- AKS documentation: https://learn.microsoft.com/azure/aks/
- Workload identity: https://learn.microsoft.com/azure/aks/workload-identity-overview
- AKS networking: https://learn.microsoft.com/azure/aks/concepts-network
