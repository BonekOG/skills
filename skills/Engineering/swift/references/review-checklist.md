# Swift Production Review Checklists

Use the relevant sections before declaring work complete. These lists are gates and prompts, not a substitute for reasoning.

## Implementation

- [ ] Project Swift/Xcode/deployment target inspected.
- [ ] Behavior, invariants, and failure semantics are clear.
- [ ] Invalid states are modeled out where reasonable.
- [ ] Ownership and lifetime are explicit.
- [ ] Dependencies and side effects have clear boundaries.
- [ ] Errors preserve recovery semantics.
- [ ] Cancellation is handled where async work can be superseded or torn down.
- [ ] No force unwrap, `try!`, or unsafe concurrency annotation was added without a proven invariant.
- [ ] UI state has one source of truth.
- [ ] New APIs respect deployment availability.
- [ ] Sensitive data is not logged or stored insecurely.
- [ ] Relevant tests were added/updated.
- [ ] Build/test/lint validation was performed where available.

## API design

- [ ] Primary call sites are clear without explanatory comments.
- [ ] Names follow Swift terminology and avoid repeating obvious type information.
- [ ] Argument labels improve meaning.
- [ ] Defaults represent genuinely optional behavior.
- [ ] Invalid parameter combinations are prevented by types where practical.
- [ ] Mutation is visible in semantics/naming.
- [ ] Public surface is minimal.
- [ ] Transport/storage/UI implementation details do not leak accidentally.
- [ ] Error, cancellation, and isolation behavior are part of the contract.
- [ ] Complexity is documented when an apparently cheap property is not O(1).

## Concurrency

- [ ] Every mutable shared value has an isolation strategy.
- [ ] Target default actor-isolation settings are understood.
- [ ] `Sendable` crossings are understood.
- [ ] No unsafe annotations were used just to silence the compiler.
- [ ] Every unstructured task has a clear owner.
- [ ] Long-lived/superseded work can be cancelled.
- [ ] Cancellation is not swallowed as a generic error.
- [ ] State is revalidated after suspension points when reentrancy matters.
- [ ] Continuations resume exactly once.
- [ ] Main-actor scope is no broader than UI semantics require.
- [ ] Parallelism is bounded where workload size can grow.

## SwiftUI

- [ ] Each mutable state value has exactly one owner.
- [ ] Bindings do not create a second source of truth.
- [ ] Observation wrappers match actual ownership/lifetime.
- [ ] Observable dependencies are scoped appropriately.
- [ ] `ForEach`/list identity is stable domain identity.
- [ ] Identity changes are not unintentionally resetting state.
- [ ] Async work follows view lifetime or has another explicit owner.
- [ ] Navigation/presentation states cannot contradict each other.
- [ ] Expensive transformations are not repeated unnecessarily in `body`.
- [ ] Dynamic Type, accessibility semantics/focus, contrast, and reduced motion are considered.
- [ ] New APIs respect minimum OS with fallbacks as required.
- [ ] UIKit/AppKit bridges have correct update/teardown behavior.

## Security and privacy

- [ ] Asset/threat boundary is understood.
- [ ] Secrets are not in UserDefaults/source/logs/analytics.
- [ ] Keychain accessibility/sync policy matches lifecycle needs.
- [ ] Crypto uses platform primitives correctly; nonces/keys are managed safely.
- [ ] Authentication UI is not mistaken for secure storage or cryptographic authorization.
- [ ] TLS trust customization is justified and rotation/failure behavior is defined.
- [ ] Sensitive deep links/WebView bridges validate untrusted inputs.
- [ ] Sensitive files use appropriate protection/sharing policy.
- [ ] Privacy-sensitive data collection/retention is minimized.

## Persistence

- [ ] Schema changes have an explicit migration path.
- [ ] Upgrade from representative previous data was tested where relevant.
- [ ] Destructive reset is not the default recovery strategy.
- [ ] Transactions preserve invariants across partial failure.
- [ ] Framework-managed objects do not cross isolation boundaries unsafely.
- [ ] Cache invalidation/staleness semantics are explicit.

## Networking

- [ ] HTTP status semantics are validated independently of decoding.
- [ ] Retry policy respects idempotency and failure class.
- [ ] Timeouts are deliberate.
- [ ] Cancellation reaches the underlying request.
- [ ] Authentication refresh cannot produce retry loops or duplicate side effects.
- [ ] Secrets/sensitive payloads are redacted from logs.
- [ ] Transport DTOs do not accidentally become the entire domain model when schemas should evolve independently.

## Pull request / final review

### Correctness

- [ ] User-visible behavior matches requirements.
- [ ] Failure/cancellation/empty states are covered.
- [ ] No reachable crash path was added.

### Swift semantics

- [ ] Ownership/lifetime are sound.
- [ ] Concurrency isolation and `Sendable` crossings are sound.
- [ ] State/identity modeling is explicit.

### Platform

- [ ] Deployment-target compatibility is preserved.
- [ ] SwiftUI accessibility/state/navigation are reviewed where applicable.
- [ ] Persistence migrations/data integrity are reviewed where applicable.
- [ ] Security/privacy effects are reviewed where applicable.

### Validation

- [ ] Relevant tests pass.
- [ ] Affected targets build/type-check.
- [ ] Lint/format checks pass if configured.
- [ ] Remaining risks/coverage gaps are stated.
