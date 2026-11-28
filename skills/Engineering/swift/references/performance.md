# Swift Performance

## Rule zero: measure

Do not optimize from intuition alone. Establish a reproducible symptom and baseline using relevant profiling/instrumentation.

## Diagnose the bottleneck class

- CPU / algorithmic complexity
- allocation / ARC churn
- memory growth/leaks/retention
- I/O / network latency
- main-thread blocking
- lock/actor contention
- SwiftUI invalidation/layout/rendering
- image decode/resizing
- startup/static initialization

## Common Swift costs

Watch for:

- accidental copy-on-write triggered by mutation of shared buffers
- repeated collection scans in nested loops
- excessive existential/type-erasure churn in hot paths
- bridging Foundation/Objective-C types repeatedly
- autorelease-heavy Objective-C APIs in tight loops
- large temporary allocations from chained transforms
- contention created by one overly broad actor/lock

Do not replace expressive collection code with manual loops unless measurement shows it matters.

## SwiftUI

Investigate stable identity and dependency breadth before micro-optimizing view structs. Reduce expensive repeated computation and oversized observable invalidation domains.

## Concurrency

More tasks are not automatically faster. Bound parallelism for CPU, I/O, service limits, memory, and fairness. Avoid spawning one task per tiny element for large collections without measurement.

## Performance change requirements

For a performance-focused patch, record:

- workload/scenario
- before measurement
- change
- after measurement
- regression test/benchmark when sustainable
