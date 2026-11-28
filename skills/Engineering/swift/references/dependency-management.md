# Swift Dependency Management

## What counts as a dependency boundary

Examples: network client, database/store, filesystem, clock, UUID/randomness source, keychain, analytics, notifications, location, purchase system, external SDK.

## Preferred techniques

Use the simplest representation that preserves semantics:

- concrete value/type parameter when variation is unnecessary
- closure for one small operation
- generic parameter when static substitution is beneficial
- protocol for a coherent multi-operation capability with real substitutability
- environment/dependency container when many feature dependencies must be assembled consistently

## Rules

- Inject dependencies at composition roots rather than reading hidden globals deep in code.
- Keep app-global state explicit even if its lifetime is global.
- Separate configuration from mutable state.
- Avoid service locators that allow arbitrary runtime lookup from anywhere.
- Prefer immutable dependency containers where possible.
- Scope dependencies to the feature/module that needs them.
- Do not expose third-party SDK types past the boundary unless coupling is intentional.

## Test seams

A test seam should let you control behavior that would otherwise be nondeterministic, slow, destructive, private, or externally coupled. Do not abstract pure deterministic code merely to mock it.
