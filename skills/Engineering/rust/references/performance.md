# Performance

## Optimization order

1. Correct algorithm/data structure.
2. Avoid obvious unnecessary work.
3. Measure.
4. Identify bottleneck.
5. Optimize the bottleneck.
6. Measure again.
7. Keep the simpler version if gain is not material.

## Watch items

Review hot paths for:

- repeated allocation;
- repeated parsing/conversion;
- large clones;
- lock contention;
- serialization copies;
- N+1 IO;
- accidental quadratic loops;
- excessive dynamic dispatch where proven costly;
- oversized buffers or cache-unfriendly layouts.

## Benchmarks

Use representative workloads.
Separate:

- throughput,
- p50/p95/p99 latency,
- allocations/bytes,
- memory footprint,
- CPU time.

Microbenchmarks do not automatically predict system performance.

## Copy vs borrow tradeoff

Do not create elaborate lifetime structures to avoid tiny copies unless measured or semantically required.
Conversely, do not clone large buffers/trees for convenience in hot paths.

## Inline / unsafe / SIMD

Use only with evidence.
Compiler-directed attributes are not substitutes for profiling.
Unsafe performance optimizations require correctness tests and a documented safety argument.

## KPI policy

Performance targets belong to the product/system domain (e.g. p99 < X ms), not generic Rust style.
This skill does not invent a latency target without requirements.
