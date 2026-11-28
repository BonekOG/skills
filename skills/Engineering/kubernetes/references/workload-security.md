# Workload security

Use this reference for pod security contexts, admission posture, host access, or container hardening.

## Separate standards from additional hardening

First identify the enforced Pod Security Admission profile and version, or the relevant external policy engine. The Kubernetes Restricted profile constrains fields such as privilege escalation, root execution, seccomp, capabilities, host namespaces, and volume types. A read-only root filesystem is useful additional hardening but is not itself a Restricted-profile requirement.

Apply controls to every applicable container class: regular, init, and ephemeral containers. Account for Windows-specific behavior and user namespaces instead of emitting Linux-only fields blindly.

## Review decisions

- non-root execution and image compatibility;
- privilege escalation and Linux capability set;
- seccomp and, where used, AppArmor or SELinux policy;
- privileged mode, host namespaces, host ports, devices, and hostPath mounts;
- writable filesystem paths and volume ownership;
- service-account token mounting;
- image source, immutability, signatures, and provenance as required by repository policy.

Do not invent numeric user or group IDs without checking the image. Do not add `fsGroup` automatically; it can change volume permissions and startup cost. Do not set `hostUsers: false` without confirming user-namespace support and filesystem/runtime limitations.

## Exceptions

System agents, CNIs, storage plugins, hardware plugins, and some operators may require host or privileged access. Minimize the exact capability and scope, document why it exists, and validate the surrounding admission policy. Do not force an application baseline onto infrastructure pods when it breaks their intended function.

## Validation

Use the exact policy version and operating system. Server-side dry run validates admission but does not prove runtime compatibility. Combine schema and policy checks with a container smoke test under the intended UID, filesystem, and capability constraints.

## Sources

- Pod Security Standards: https://kubernetes.io/docs/concepts/security/pod-security-standards/
- Security contexts: https://kubernetes.io/docs/tasks/configure-pod-container/security-context/
- Linux security constraints: https://kubernetes.io/docs/concepts/security/linux-kernel-security-constraints/
- User namespaces: https://kubernetes.io/docs/concepts/workloads/pods/user-namespaces/
