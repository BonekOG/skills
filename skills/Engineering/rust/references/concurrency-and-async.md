# Async and concurrency

## First question: do you need concurrency?

Use concurrency to satisfy throughput/latency/responsiveness requirements, not as an architectural default.

## Async rules

- Never block an async executor thread with long blocking IO/CPU work; use blocking pools/dedicated threads as appropriate.
- Do not hold a synchronous mutex guard across `.await`.
- Hold async locks across `.await` only when the protected invariant genuinely spans the await.
- Keep cancellation behavior explicit.
- Propagate deadlines/timeouts at boundaries where hanging work is unacceptable.
- Bound concurrency; do not spawn unbounded work from unbounded input.

## Task ownership

Every spawned task should have an ownership/lifecycle story:

- who cancels it?
- who awaits/joins it?
- what happens on error?
- can it outlive the request/component?
- is detached execution intentional?

Avoid fire-and-forget unless loss and shutdown semantics are deliberate.

## Channels

Choose based on semantics:

- one-shot for a single response;
- bounded MPSC for backpressure;
- broadcast/watch for state/event fanout when their loss/replay behavior matches requirements.

Prefer bounded channels when producers can outpace consumers.

## Shared state

Prefer message passing/ownership transfer when it simplifies invariants.
Use locks when shared mutable state is genuinely the simplest model.
Keep lock scope minimal and document lock-order rules if multiple locks exist.

## Atomics

Use atomics only with a clear memory model.
Defaulting every ordering to `SeqCst` may be safe but can obscure design; weakening orderings without expertise can be unsound.
Document non-trivial ordering rationale.

## `Send` / `Sync`

Do not paper over missing `Send`/`Sync` with unsafe impls.
Understand which field prevents auto-traits and whether cross-thread use is semantically safe.
