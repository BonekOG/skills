# OpenShift

Load only when the target is OpenShift, OKD, ROSA, or ARO.

## Respect platform APIs and ownership

Capture OpenShift and Kubernetes versions, installed Operators, namespace policy, SecurityContextConstraints, Routes or ingress/Gateway usage, cluster monitoring, image registry, and GitOps controllers. Prefer the owning Operator custom resource over editing generated children.

## Workload security

Design application images to run with an arbitrary non-root UID unless a documented SCC requires otherwise. Do not hard-code a UID merely to satisfy generic Kubernetes advice. Ensure writable paths support the assigned identity. Do not edit built-in SCCs; create or bind a narrowly scoped custom SCC only when the platform-supported profiles cannot satisfy a justified workload.

Pod Security Admission and SCC evaluation can both matter. Inspect actual admission errors and effective SCC instead of treating upstream Restricted PSS as the complete OpenShift policy.

## Routing and build ecosystem

Choose Route, ingress, Gateway API, or Service exposure according to installed controllers and repository convention. Validate TLS termination mode and backend protocol together. Account for OpenShift Builds, ImageStreams, internal registry references, and deployment triggers only when the repository uses them.

## Validation

Use `oc explain`, server-side dry run, rendered manifests, and Operator status against the target cluster. Generic upstream examples often assume fixed UIDs, unrestricted volume ownership, or controllers not present on OpenShift.

## Sources

- OpenShift documentation: https://docs.redhat.com/en/documentation/openshift_container_platform/
- SecurityContextConstraints: https://docs.openshift.com/container-platform/latest/authentication/managing-security-context-constraints.html
- Routes: https://docs.openshift.com/container-platform/latest/networking/routes/route-configuration.html
