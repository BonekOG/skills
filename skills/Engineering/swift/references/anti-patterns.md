# Swift / iOS Anti-Patterns Catalog

Use this as a smell list, not an automatic rejection list.

## Language/modeling

- Boolean flag matrices representing a state machine.
- Stringly typed identifiers/states when a domain type is cheap.
- `Any` dictionaries passed through layers.
- Force unwraps on user/network/persistence-derived data.
- Reference types used where independent value snapshots are intended.

## Architecture

- God ViewModel / God Service.
- One protocol per concrete class with no real substitutability.
- Repository layers that only forward method names.
- Hidden singleton/service-locator dependencies.
- Domain code importing UI/network/database concrete implementation details.

## Concurrency

- `Task.detached` used to escape isolation errors.
- `@unchecked Sendable` added without an explicit synchronization proof.
- Tasks launched without ownership/cancellation.
- Assuming actor state cannot change across `await`.
- Blocking locks/semaphores on async execution paths without careful justification.

## SwiftUI

- Duplicate source of truth.
- Unstable `ForEach` identity.
- Network/database side effects inside rendering logic.
- Expensive filtering/sorting in `body` on every invalidation.
- Blanket `.animation` behavior unrelated to explicit state changes.
- `AnyView` as routine view composition.

## Networking/data

- Decoding before validating HTTP status semantics.
- Blind retries of non-idempotent requests.
- Treating cache and source-of-truth as the same thing without policy.
- Shipping schema changes without migration testing.

## Security

- Tokens in UserDefaults/logs.
- Custom crypto.
- Biometric success boolean treated as a protected secret.
- Custom TLS trust without lifecycle/rotation strategy.

## Testing

- Sleeps for async synchronization.
- Tests coupled to private helpers.
- Massive snapshot/UI suites that duplicate lower-level behavior tests.
- Coverage percentage used as a proxy for test value.
