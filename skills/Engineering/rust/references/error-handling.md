# Error handling

## Error taxonomy

### Recoverable domain/IO/protocol failure

Return `Result<T, E>`.

### Absence that is not failure

Return `Option<T>`.

### Programmer error / impossible invariant

`panic!`, `debug_assert!`, or `unreachable!` may be appropriate when the invariant is locally proven and violation indicates a bug.

### User/application context

At application boundaries, add context that explains the attempted operation.

## Library vs application

Libraries:

- prefer typed errors;
- preserve source errors where useful;
- expose stable categories rather than dependency internals when possible;
- avoid `anyhow::Error` in public library APIs unless the API intentionally embraces type erasure.

Applications:

- `anyhow` or equivalent contextual aggregation can be appropriate;
- retain structured errors when callers need branching/retry decisions.

## `unwrap` / `expect`

Production code policy:

- avoid on normal runtime inputs;
- allowed for statically guaranteed invariants or initialization where failure is impossible/terminal and the message explains why;
- `expect` is preferable to `unwrap` when the invariant is non-obvious;
- tests may use them freely when failure should fail the test.

Do not hide recoverable failure behind panics.

## Error context

Good context answers:

- what operation failed?
- which high-level resource/action was involved?
- what should a maintainer/user infer?

Do not duplicate the source error string manually if error chaining already preserves it.

## Error enums

Use variants that represent actionable categories, not every low-level detail.
Avoid leaking third-party error types into a long-lived public API unless coupling is intentional.

## Retrying

Retry only when:

- the failure is plausibly transient;
- the operation is idempotent or has an idempotency strategy;
- backoff/jitter and termination are explicit;
- cancellation/deadlines are respected.

Never loop indefinitely on broad `Err(_)`.
