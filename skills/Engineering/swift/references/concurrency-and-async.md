# Swift Concurrency

## Default model

Prefer structured concurrency. A task should normally have an owner, a lifetime, and cancellation propagation.

## Isolation

- Treat actor isolation as part of the API contract.
- Keep UI-observable mutable state on the appropriate main-actor boundary.
- Put mutable shared non-UI state behind a coherent actor or other deliberate synchronization primitive.
- Minimize cross-actor chatter; design operations around useful units of work.
- Remember actor methods are reentrant across suspension points. Revalidate assumptions after `await` when state may have changed.

## `Sendable`

- Let the compiler teach you where values cross isolation domains.
- Prefer genuinely `Sendable` value types.
- Avoid `@unchecked Sendable` unless you can prove the synchronization/lifetime invariant and document it.
- Avoid `nonisolated(unsafe)` as a diagnostic silencer.

## Tasks

Prefer:

- child tasks / `async let` for fixed parallel work
- task groups for dynamic parallel work
- `.task` in SwiftUI for view-scoped async work

Use unstructured `Task {}` only when the lifetime/owner is clear. Store/cancel task handles when work must stop before natural completion.

Avoid `Task.detached` unless you deliberately need to drop actor/task context and can explain ownership, priority, task-local, and cancellation consequences.

## Cancellation

- Cancellation is cooperative.
- Propagate `CancellationError` unless intentionally translating it.
- Check cancellation in CPU loops, chunked I/O, retries, and long transformations.
- Cancel superseded work such as searches, image loads, and refreshes.

## Bridging legacy callbacks

When wrapping callbacks with continuations:

- resume exactly once
- preserve cancellation when the underlying API supports cancellation
- preserve actor/isolation expectations
- avoid escaping continuation state into ambiguous lifetimes

## Review checklist

- What isolation domain owns each mutable variable?
- What crosses actor boundaries, and is it `Sendable`?
- Who owns every task?
- What cancels it?
- Could state change while suspended?
- Are callbacks/continuations resumed exactly once?
- Has unsafe annotation been introduced merely to satisfy the compiler?

## Swift 6.2+ approachable concurrency

When the project enables newer Swift 6.x concurrency settings, inspect the build settings before assuming legacy behavior:

- A target can opt into **default MainActor isolation**. In such a target, declarations may inherit main-actor isolation without explicit annotations. Do not scatter redundant `@MainActor` merely from habit; understand the target's default isolation first.
- Newer Swift 6.x modes can keep ordinary `async` functions on the caller's execution context rather than implicitly hopping to a generic concurrent executor. Do not infer parallelism from `async` alone.
- Use explicit concurrent execution (`@concurrent` where supported and appropriate) only when the operation is intentionally safe and useful to run concurrently.
- Migration should remove accidental data-race hazards rather than suppress diagnostics. Treat stricter compiler errors as architectural feedback.
- Library code must be especially careful about changing isolation annotations because actor isolation and `Sendable` requirements are part of source/API behavior.

## Parallelism choices

Use:

- `async let` for a fixed, small number of independent child operations;
- task groups for dynamic fan-out/fan-in;
- actors for serialized mutable state, not for generic "background work";
- bounded concurrency when work size can grow with user/server data;
- `AsyncSequence` when values naturally arrive over time and backpressure/lifecycle matter.

Avoid spawning one task per element of an unbounded collection without a resource budget.

## Actor reentrancy pattern

Any invariant read before an `await` may be stale afterward. Prefer one of:

- capture immutable values needed for the operation;
- move the full atomic state transition inside one isolated synchronous section;
- re-check version/identity/state after suspension before committing results;
- represent in-flight operations explicitly so stale results can be rejected.

## Continuation safety

For `withCheckedContinuation` / `withCheckedThrowingContinuation` bridges:

- resume exactly once on every reachable terminal path;
- define what happens when the caller is cancelled before the callback fires;
- do not retain continuation state indefinitely;
- prefer native async APIs when available instead of wrapping them again.
