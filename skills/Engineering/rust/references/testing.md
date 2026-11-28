# Testing

## Test behavior and invariants

Prefer tests that prove externally meaningful behavior over tests coupled to private helper structure.

Testing pyramid is contextual, but use the cheapest level that can reliably prove the contract:

- unit tests for local logic/invariants;
- integration tests for crate/component boundaries;
- property tests for broad input spaces/invariants;
- end-to-end tests for critical user/system flows.

## Regression tests

For a bug fix:

1. reproduce with a failing test when feasible;
2. fix;
3. keep the test focused on the behavior that regressed.

## Table-driven tests

Use data-driven cases when many inputs share one behavioral rule.
Keep names/cases readable.

## Property-based testing

Good candidates:

- parsers/serializers;
- round trips;
- arithmetic/domain invariants;
- state-machine transitions;
- collection transformations.

Properties are stronger than enumerating a few lucky examples.

## Snapshot tests

Use when structured output is intentionally reviewed as a whole.
Avoid snapshots for highly volatile or irrelevant formatting.
Review snapshot changes as code changes, not automatic updates.

## Concurrency tests

Avoid sleep-based timing assumptions when synchronization can prove readiness.
Test cancellation/shutdown/error propagation.

## Coverage

Coverage is diagnostic, not a target to game.
Suggested policy:

- changed critical behavior must be covered;
- security/safety invariants need explicit tests;
- uncovered branches in core logic trigger review;
- repository-wide percentage may be monitored, but a universal numeric threshold is not sufficient evidence of quality.

## Mutation testing

For high-risk pure logic, mutation testing can expose weak assertions.
Treat mutation score as an optional quality signal, not a universal gate.
