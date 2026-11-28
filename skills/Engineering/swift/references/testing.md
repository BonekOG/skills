# Swift Testing

## Testing strategy

Prefer the cheapest test that gives reliable confidence in the behavior:

1. pure/domain tests
2. boundary/component tests
3. integration tests
4. focused UI/end-to-end tests for critical product truth

Do not maximize test count or coverage percentage at the expense of signal.

## Swift Testing

For new unit/component tests, prefer Swift Testing where supported by the project. Use expressive test names, parameterized cases where they reduce duplication, and clear preconditions.

Use XCTest/XCUITest where platform/UI automation, legacy infrastructure, performance metrics, or unavailable Swift Testing capabilities require it.

## Behavior over implementation

Test externally meaningful outcomes and invariants. Avoid tests that break solely because a private helper was renamed or code moved between types.

## Determinism

Control:

- time/clocks
- UUID/randomness
- network responses
- persistence state
- scheduler/task completion points when needed
- locale/calendar/time zone for formatting logic

Do not use arbitrary sleeps to make async tests pass.

## Async tests

- Await the actual condition or operation.
- Exercise cancellation when it is part of behavior.
- Test actor-isolated behavior from the correct isolation context.
- Avoid accidentally serializing tests that are intended to prove concurrent safety.

## Fixtures

Keep fixtures small and semantically named. Prefer builders/factories when many tests need valid defaults with one or two overrides.

## UI/E2E

Keep a small set of durable E2E tests for critical user journeys and regression truth. Prefer accessibility identifiers/stable semantics over brittle layout coordinates or timing assumptions.

## Review questions

- What bug would this test catch?
- Could it pass while the feature is broken?
- Could it fail while user-visible behavior is correct?
- Is nondeterminism hidden behind timing/retry hacks?
- Does the test prove the failure/cancellation path too?
