# Swift Package and Module Design

## Module when it buys something

Create a package/target boundary for at least one strong reason:

- ownership/team boundary
- independent reuse
- compile-time dependency enforcement
- expensive build isolation
- distinct platform support
- stable domain capability
- security/sensitive implementation boundary

Do not split every folder into a module.

## Dependency direction

- High-level domain behavior should not depend on low-level UI/transport/storage implementation details.
- Keep dependency graphs acyclic.
- Avoid “shared” dumping grounds; give shared code a coherent domain purpose.
- Keep feature-to-feature dependencies explicit and narrow.

## Access control

Default to the narrowest visibility that supports the intended use. Public APIs are long-term compatibility obligations; do not make types public merely to reach them from tests if a better test architecture exists.

## Package hygiene

- Pin/version external dependencies according to the project's release policy.
- Minimize transitive dependency exposure.
- Isolate wrappers around volatile third-party SDKs.
- Prefer package resources and generated code workflows that are deterministic in CI.
- Keep macros/plugins/build tools security-reviewed because they execute during builds.
