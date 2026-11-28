# Swift Code Review

## Review goal

Find concrete reachable defects and regression risks. Do not manufacture style comments to look thorough.

## Establish context first

Determine:

- Swift version/language mode
- SDK and minimum deployment target
- affected targets/modules
- concurrency mode/strictness
- relevant dependencies
- test/build coverage

## Trace changed behavior

Read beyond the diff when needed:

- callers and call sites
- data/state owners
- task creation/cancellation
- observer/delegate registration and teardown
- persistence schema/migrations
- navigation/identity sources
- network/auth side effects

## High-priority review invariants

### Ownership and lifetime

- retained cycles
- premature weak references
- observers/tasks/resources outliving owners
- callbacks after teardown

### Concurrency

- actor-isolation violations
- non-Sendable values crossing domains
- reentrancy assumptions across `await`
- lost cancellation
- detached/unowned tasks
- unsafe annotations masking races

### Identity and representation

- unstable SwiftUI list identity
- entity/value identity confusion
- lossy mapping between transport/persistence/domain models
- locale/timezone/unit assumptions

### Error and side effects

- swallowed failures
- duplicate writes/requests
- non-idempotent retries
- partial updates without transaction semantics
- logging sensitive data

### Compatibility

- unavailable API for deployment target
- source/API compatibility regressions
- migration/data loss risks

## Findings format

For each finding provide:

1. severity based on user/data/correctness impact
2. exact location
3. reachable failure scenario
4. why current tests/guards do not prevent it
5. smallest robust fix direction

If no concrete defect is found, say so and list coverage gaps or assumptions instead of inventing issues.
