# Swift Error Handling

## Model failures by recovery semantics

An error type should help the caller decide what to do: retry, reauthenticate, ask for input, fall back, report corruption, or stop.

Avoid a single generic error string as the domain contract.

## Rules

- Throw for exceptional failure paths where the caller can react.
- Use optionals for ordinary absence when absence is not an error.
- Use `Result` mainly when failure must be stored, passed synchronously, or composed as a value; prefer `async throws` for asynchronous functions.
- Preserve underlying errors when they carry diagnostic value, but do not leak implementation-specific failures through stable public domain APIs without intent.
- Never swallow cancellation as a generic failure.
- Check `Task.isCancelled`/`Task.checkCancellation()` in meaningful long-running work.
- Avoid broad `catch { return nil }` patterns that erase the distinction between missing data, transport failure, decoding failure, and cancellation.

## User messages vs diagnostics

Keep user-facing messages separate from internal diagnostics. Do not display raw server/database/crypto errors to users. Do not log secrets, tokens, PII, or sensitive payloads while diagnosing failures.

## Invariants

`precondition`, `assert`, and `fatalError` are not substitutes for recoverable error handling. Use them only for programmer errors or truly unrecoverable invariants consistent with the product's failure policy.
