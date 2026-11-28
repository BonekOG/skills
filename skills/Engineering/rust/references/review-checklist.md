# Rust code review checklist

## Correctness

- [ ] Behavior matches requirement.
- [ ] Edge cases / error paths are handled.
- [ ] State invariants are explicit.
- [ ] Integer conversions/overflow assumptions are safe.
- [ ] Cancellation/shutdown semantics are sound where applicable.

## Ownership

- [ ] No clone was added merely to appease the borrow checker.
- [ ] Borrowed inputs use appropriate view types.
- [ ] Shared ownership is intentional.
- [ ] Mutable borrow/lock scopes are minimal.

## Modeling

- [ ] No contradictory boolean/optional states.
- [ ] Domain IDs/units cannot be accidentally mixed.
- [ ] Validation occurs at a clear boundary.

## Errors

- [ ] No recoverable failure is hidden behind panic/unwrap.
- [ ] Errors preserve useful context/source information.
- [ ] Public errors do not leak accidental implementation coupling.

## API

- [ ] Public surface is minimal and idiomatic.
- [ ] Naming/conversions follow Rust conventions.
- [ ] Semver implications considered.
- [ ] Docs updated for public behavior.

## Concurrency

- [ ] No blocking work on async executor threads.
- [ ] Locks are not held across await without necessity.
- [ ] Spawned tasks have lifecycle/error ownership.
- [ ] Queues/concurrency are bounded where input can be unbounded.

## Unsafe / security

- [ ] Unsafe is necessary and locally justified.
- [ ] SAFETY invariant is documented.
- [ ] Untrusted input is bounded/validated.
- [ ] Secrets are not logged.

## Performance

- [ ] Algorithm is appropriate.
- [ ] No obvious hot-path allocation/clone regression.
- [ ] Complexity added for performance is backed by evidence.

## Testing

- [ ] Changed behavior has tests.
- [ ] Bug fixes have regression coverage when feasible.
- [ ] Tests assert meaningful outcomes, not private implementation.
- [ ] Relevant quality gate commands pass.
