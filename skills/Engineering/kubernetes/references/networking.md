# Networking

Use this reference for Services, EndpointSlices, DNS, ingress, Gateway API, NetworkPolicy, or service-mesh traffic.

## Trace the traffic contract

Follow the complete path and verify each hop:

1. client name and protocol;
2. external load balancer, ingress, or Gateway listener;
3. route match and backend reference;
4. Service port and target port;
5. ready EndpointSlices and pod labels;
6. container listener address and protocol;
7. NetworkPolicy, mesh policy, and cloud firewall behavior.

An accepted manifest does not prove that selectors or ports connect to a ready endpoint.

## Exposure decisions

Choose ClusterIP, headless Service, NodePort, LoadBalancer, ingress, or Gateway from the platform and protocol requirements. Do not assume ingress exists or supports arbitrary TCP/UDP. Treat annotations as controller APIs and verify their version-specific documentation.

Keep admin, debug, and metrics endpoints private unless exposure is explicitly required. Validate TLS ownership and certificate scope at the component that terminates TLS.

## NetworkPolicy

Confirm that the installed CNI enforces the policy features used. Policies are additive and select pods by labels; a typo can silently select none. When adding default-deny, inventory required DNS, control-plane, identity, telemetry, and dependency traffic first. A policy object alone does not prove isolation.

## DNS and dual stack

Check the actual search path, namespace, Service family policy, and resolver behavior. Avoid hard-coded pod IPs. Use stable service discovery and account for client DNS caching and connection reuse when endpoints change.

## Sources

- Services: https://kubernetes.io/docs/concepts/services-networking/service/
- NetworkPolicy: https://kubernetes.io/docs/concepts/services-networking/network-policies/
- DNS: https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/
- Gateway API: https://gateway-api.sigs.k8s.io/
