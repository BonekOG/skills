# Concurrency and Asynchronous Design

Read this reference when work crosses threads, tasks, executors, event loops, atomics, callbacks, futures, or coroutines.

## Design before primitives

Define first:

- which thread/task/executor owns mutable state;
- whether callers may invoke operations concurrently;
- whether callbacks are serialized;
- shutdown order;
- cancellation propagation;
- lifetime of queued work and captured objects;
- backpressure/queue limits;
- error propagation across asynchronous boundaries.

Prefer thread confinement, immutable messages, ownership transfer, or actor/task-queue patterns before shared mutable state.

## Threads and synchronization

- Prefer `std::jthread` over `std::thread` when automatic joining and stop-token integration fit the repository.
- Keep critical sections small but preserve invariants; do not split a logically atomic update merely to shorten lock duration.
- Use RAII locking (`lock_guard`, `unique_lock`, `scoped_lock`).
- Establish and document lock ordering when multiple locks can be acquired together.
- Use condition variables with a predicate in a loop/wait overload; account for spurious wakeups.
- Never call unknown/user callbacks while holding an internal mutex unless the reentrancy contract explicitly permits it.
- Consider false sharing and contention only after measuring a relevant hot path.

## Atomics and memory ordering

Atomics prevent data races only for the atomic object; they do not automatically make a larger invariant thread-safe.

- Use `memory_order_seq_cst` or stronger/simple defaults unless a demonstrated need justifies weaker ordering.
- If using acquire/release/relaxed ordering, document the synchronization relationship and what data it protects.
- Do not assume `atomic<T>` is lock-free; query or constrain it if lock-freedom is a requirement.
- Avoid custom lock-free data structures unless the performance requirement is measured and the algorithm can be reasoned about rigorously, including reclamation/ABA issues.

## Task-based concurrency

Prefer tasks/executors/thread pools when work units, not long-lived dedicated threads, are the architectural unit. Reuse the repository's scheduler/runtime; do not add another thread pool casually.

Treat `std::async` carefully: launch policy and future destruction can have surprising behavior. Use it only when its exact semantics satisfy the design.

## Cancellation and shutdown

Cancellation is part of the API, not an afterthought.

- Decide whether cancellation is cooperative and where it is observed.
- Ensure shutdown does not leave tasks holding references to destroyed owners.
- Drain, cancel, or reject queued work according to an explicit policy.
- Make repeated shutdown/destruction safe when practical.

## Coroutines

A coroutine is suspension machinery, not an executor.

Before adding coroutines, define:

- coroutine return/task type;
- scheduler/executor and resumption thread;
- lifetime of coroutine frames and referenced state;
- cancellation/stop-token model;
- exception/error propagation;
- structured ownership of child operations;
- behavior during shutdown.

Avoid detached fire-and-forget coroutines unless the runtime has explicit ownership, error reporting, and shutdown handling for them.
