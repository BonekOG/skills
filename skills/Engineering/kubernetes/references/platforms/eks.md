# Amazon EKS

Load only when the target is EKS or uses AWS-specific Kubernetes integrations.

## Resolve installed components

Capture EKS and Kubernetes versions, managed or self-managed node type, VPC CNI mode, CoreDNS and kube-proxy versions, load-balancer controller, CSI drivers, node provisioning, and identity mechanism. AWS add-ons and controller CRDs are versioned APIs; inspect the deployed versions before generating configuration.

## Identity

Prefer EKS Pod Identity or IAM roles for service accounts according to the cluster's established mechanism. Match Kubernetes ServiceAccount, namespace, trust configuration, IAM role, and SDK credential-chain behavior. Do not introduce static AWS access keys.

## Networking and load balancing

Account for VPC subnet capacity, security groups, target type, source preservation, health checks, and VPC CNI behavior. Treat AWS Load Balancer Controller annotations as controller-version-specific. Verify whether the workload uses ingress, Gateway API, or a LoadBalancer Service.

## Storage and nodes

Match EBS or EFS CSI capabilities to access mode, topology, encryption, and snapshot requirements. For Karpenter or another node autoscaler, inspect NodePool or equivalent constraints, disruption policy, architecture, capacity type, zones, and pod scheduling requirements together.

## Sources

- EKS best practices: https://docs.aws.amazon.com/eks/latest/best-practices/introduction.html
- EKS Pod Identity: https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html
- AWS Load Balancer Controller: https://kubernetes-sigs.github.io/aws-load-balancer-controller/
