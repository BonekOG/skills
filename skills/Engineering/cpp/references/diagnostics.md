# Debugging, Diagnostics, and Production Observability

Read this reference for crashes, hangs, corruption, flaky behavior, production incidents, logging, tracing, or debugger work.

## Evidence ladder

Prefer increasingly invasive tools as needed:

1. Reproducer and failing test.
2. Assertions/invariant checks.
3. Structured logs with correlation/context.
4. Sanitizers/static analysis.
5. Debugger and stack traces.
6. Core/minidump analysis.
7. Thread dumps and lock/wait analysis.
8. Profilers/tracing/perf counters.
9. Targeted instrumentation or record/replay where available.

Gather evidence before editing, form hypotheses from it, and falsify them one at a time. Avoid broad refactors while the failure mechanism is still unknown.

Do not patch symptoms from a stack trace without explaining the invalid state/lifetime/order that produced them.

## Crash workflow

- Preserve the failing build/version, symbols, input, platform, and crash artifact.
- Identify the faulting thread and first trustworthy project frame.
- Inspect ownership/lifetime, bounds, object state, and recent cross-thread activity.
- Reproduce under ASan/UBSan where practical.
- Check whether the visible crash is downstream memory corruption rather than the original write.
- Add a regression test or invariant check after fixing the root cause.

## Hang/deadlock workflow

- Capture all thread stacks.
- Determine whether threads are blocked on mutexes, condition variables, IO, futures, queues, or busy loops.
- Build the wait-for/lock-order relationship.
- Verify shutdown/cancellation paths and callbacks invoked under locks.
- Distinguish deadlock, livelock, starvation, backpressure, and intentionally blocked IO.

TSan may expose races but does not prove absence of deadlock.

## Data corruption

Use watchpoints, bounds instrumentation, ASan, debug allocators, canaries, deterministic seeds, and narrowed reproductions. Inspect iterator/reference invalidation and cross-thread ownership first in C++ code.

## Logging

Log events, not prose dumps. Include stable identifiers, operation/result, relevant sizes/durations, and error context. Avoid secrets and high-cardinality noise. Do not log every retry/loop iteration on hot paths without rate limiting.

## Stack traces and symbols

Keep symbol generation and symbol retention compatible with production debugging. For C++23 projects, `std::stacktrace` may be useful when implementation/toolchain support is adequate; otherwise use repository/platform facilities.

## Metrics and tracing

Instrument boundaries where latency, queue depth, errors, retries, drops, and resource use matter. Tracing is useful for cross-thread/process pipelines; metrics are useful for aggregate health. Avoid instrumentation that changes timing enough to hide the bug without noting the limitation.

## Performance debugging

Use the appropriate profiler: CPU sampling, allocation profiling, lock/contention tracing, IO tracing, cache/perf counters, or flame graphs. Correlate micro-level findings with the product metric before changing architecture.
