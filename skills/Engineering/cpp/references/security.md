# Security and Trust Boundaries

Read this reference when C++ code accepts external or untrusted input, crosses a process or network boundary, handles credentials, or needs a security review of resource limits and failure behavior.

Security work starts at the trust boundary. Identify what is attacker-controlled, which component validates it, and what invariant the validated representation carries. Validation must happen before allocation, indexing, path resolution, command construction, or any other operation that turns untrusted data into authority.

## Boundary checklist

For external or untrusted input:

- validate lengths, counts, offsets, nesting depth, and resource limits before allocation or use;
- guard integer arithmetic used for allocation and indexing;
- reject malformed or ambiguous encodings according to a defined policy;
- constrain filesystem paths and prevent traversal where a sandbox or root is intended;
- avoid shell command construction from untrusted strings;
- use secure temporary-file APIs and avoid TOCTOU patterns;
- use established cryptographic libraries; do not implement cryptographic primitives casually;
- keep secrets out of logs, exception text, crash dumps, and source control;
- define timeouts, queue limits, decompression limits, and other denial-of-service controls where relevant.

Fix the trust boundary and the root cause, not only one observed payload. Preserve the validation when data is copied, serialized, or converted between representations, and add a regression test at the boundary that should have rejected the input.

Use [testing.md](testing.md) for test strategy, sanitizers, static analysis, and fuzzing setup.
