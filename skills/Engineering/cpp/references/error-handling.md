# Error Architecture and Exception Safety

Read this reference when designing or changing failure behavior, exceptions, result types, error codes, transactions, or cleanup.

## Classify failures

Choose behavior based on the kind of failure:

- **Programming error / violated invariant:** assertion, contract mechanism, fail-fast behavior, or explicit defensive error according to project policy. Do not silently continue with corrupted assumptions.
- **Expected recoverable failure:** repository result type, `std::expected<T,E>`, optional only when absence is not an error, or an established error-code model.
- **Exceptional operation failure:** exception when the repository uses exceptions for such failures and stack unwinding is the appropriate propagation mechanism.
- **Process/ABI/foreign-runtime boundary:** convert to an explicit boundary representation; do not leak C++ exceptions across unsupported boundaries, including thread entry points.

Do not mix several error architectures in one subsystem without a boundary reason.

## Result types

When using `expected`/Result-like APIs:

- preserve the underlying successful value instead of manufacturing a generic success;
- propagate every fallible operation unless intentionally translating the error;
- enrich errors with context at meaningful boundaries, not at every stack frame;
- avoid string-only errors when callers need structured handling;
- keep error enums/types stable enough for callers but not over-generalized.

Use `optional` only for absence. If callers must know why there is no value, use an error-bearing result.

## Exceptions

- Catch by `const&` unless ownership/consumption requires otherwise.
- Catch only to recover, translate, add meaningful context, enforce a boundary, or perform logic not already guaranteed by RAII.
- Do not catch-and-ignore broadly.
- Avoid throwing from destructors.
- Mark functions `noexcept` only when the contract can be honored; remember that violating `noexcept` terminates.
- Review move operations and swap when exception guarantees depend on them.

## Exception guarantees

Know which guarantee a mutating operation provides:

- **No-throw:** cannot fail by exception.
- **Strong:** failure leaves observable state unchanged.
- **Basic:** invariants remain valid but state may change.
- **None:** avoid unless unavoidable and clearly contained.

Prefer commit-after-success patterns for multi-step state changes. Build new state in temporaries, validate, then swap/commit where practical.

## Transactional work

For files, databases, state machines, or multiple resources:

1. validate inputs;
2. acquire resources under RAII;
3. stage work without publishing partially valid state;
4. commit once all required operations succeed;
5. let rollback/cleanup occur automatically where possible.

If partial progress is externally visible, define idempotency/retry/compensation explicitly.
