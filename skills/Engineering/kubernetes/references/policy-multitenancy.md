# Policy and multi-tenancy

Use this reference for admission controls, namespace tenancy, quotas, Pod Security Admission, Kyverno, Gatekeeper, or organizational Kubernetes policy.

## Define the trust boundary

Identify whether tenants are teams, applications, customers, or mutually untrusted parties. Namespaces provide a policy and naming boundary but are not by themselves strong isolation. Establish cluster sharing, node sharing, control-plane trust, data sensitivity, and platform ownership before prescribing controls.

## Layer controls intentionally

Consider the controls that address the identified boundary:

- namespace lifecycle and ownership;
- ResourceQuota and LimitRange based on real capacity and workload requirements;
- namespaced RBAC and separate automation identities;
- Pod Security Admission profile and version;
- NetworkPolicy supported by the installed CNI;
- node isolation, runtime classes, sandboxing, or separate clusters for stronger boundaries;
- secret, audit, and observability access;
- API priority, object-count limits, and policy-engine capacity.

Do not assume every ResourceQuota requires every pod to declare both CPU and memory; that depends on the quota resources configured. Do not deploy default-deny networking before mapping required platform and dependency traffic.

## Admission policy

For Kyverno, Gatekeeper, ValidatingAdmissionPolicy, or another engine:

1. verify installed engine and API versions;
2. define the exact object and operation scope;
3. handle background scans and existing objects deliberately;
4. exclude platform namespaces and break-glass identities narrowly;
5. test mutation ordering, defaults, generated resources, and failure policy;
6. introduce blocking enforcement only after evaluating current violations and admission availability.

Admission controls sit on a critical write path. Analyze webhook timeout, availability, match conditions, reinvocation, dry-run behavior, and failure policy before changing enforcement.

## Validation

Test representative allowed and denied objects, updates as well as creates, subresources where relevant, Windows and infrastructure exceptions, and behavior when the policy engine is unavailable. Report policy coverage without calling it complete isolation or compliance.

## Sources

- Multi-tenancy: https://kubernetes.io/docs/concepts/security/multi-tenancy/
- ResourceQuota: https://kubernetes.io/docs/concepts/policy/resource-quotas/
- Admission webhooks: https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/
- Validating admission policy: https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/
