# Performance Engineering and Data-Oriented Design

Read this reference only for performance-sensitive design or measured performance work.

Optimize the actual workload, not the perceived speed of a language or the appearance of source code. C++ is not inherently slower than Rust: with equivalent algorithms, semantics, data layouts, target CPUs, libraries, and optimized builds, either can win depending on the workload. Compare generated code and measured behavior rather than relying on language-wide benchmark rankings.

## Evidence first

Establish:

- target metric: latency percentile (including p95/p99 and jitter where relevant), throughput, CPU cycles, instructions, cache misses, memory, allocations, startup, binary size, compile time, energy, etc.;
- representative workload, input distributions, data size, concurrency, hot/cold-cache conditions, and production-like constraints;
- baseline measurement, correctness invariants, and commit/build identity;
- profiler/benchmark methodology and sufficient repetitions;
- acceptable regression/noise threshold, accuracy tolerance (for floating point), and resource budget;
- hardware/OS, compiler and standard-library versions, build flags, CPU features, and deployment portability requirements.

Use optimized builds with symbols for runtime profiling (for example, Release or RelWithDebInfo with debug symbols); do not mistake debug or sanitizer overhead for production performance. Keep microbenchmarks representative and prevent dead-code elimination, constant folding of fixed inputs, unrealistic cached inputs, and measurement of setup work unless setup is the subject. Separate wall time, on-CPU work, off-CPU waiting, and end-to-end latency. When profiling or reproducible execution is unavailable, mark findings as hypotheses, not measured improvements.

## Optimization order

Prefer this order unless measurements point elsewhere:

1. Algorithmic complexity and amount of work.
2. Data movement and representation.
3. Cache locality/data layout.
4. Allocation frequency and lifetime.
5. Lock/contention/scheduling behavior.
6. IO/syscall/batching behavior.
7. Vectorization/SIMD/compiler optimization.
8. Instruction-level/micro optimizations.

Do not optimize spelling while the algorithm or memory traffic dominates. Identify the dominant bottleneck with profiling before choosing an intervention; changing multiple factors at once obscures causality. Form a falsifiable hypothesis, change one factor, remeasure, and retain only improvements that persist on representative end-to-end workloads. Use Amdahl's law to judge whether a hot-path improvement can materially affect the total.

## Data layout

For hot collections, compare object graphs against contiguous representations.

Consider:

- `std::vector<T>` over individually allocated nodes when stable addresses are not required;
- AoS vs SoA according to which fields are accessed together and which operations vectorize;
- hot/cold field separation and smaller working sets;
- compact IDs/handles instead of pointer-heavy graphs, accounting for indirection and handle validity;
- batching and preallocation when workload shape is known;
- avoiding redundant conversions/copies between pipeline stages;
- access stride, alignment, cache-line utilization, TLB pressure, false sharing, and NUMA effects when supported by profiles;
- reducing unpredictable branches and dependent memory loads where measurements justify it.

Choose layout from access patterns, not fashion. Measure before introducing complex SoA/ECS-style structures. Check the memory footprint, correctness of object lifetime/alignment, and p99 impact alongside average throughput.

## Allocation

Profile allocations before adding pools/arenas/PMR.

When allocation is material:

- reserve known capacities;
- reuse buffers/objects where lifetime is clear;
- batch allocations;
- consider monotonic/arena allocation for bulk same-lifetime objects;
- use `std::pmr` when allocator selection must propagate across standard containers;
- benchmark allocator contention, allocation sizes, peak memory, and reset/destruction costs, not only allocation-call counts.

Do not keep memory indefinitely merely to reduce allocator calls without considering peak usage. Avoid dangling references, lifetime violations, unbounded pools, and hidden changes to ownership or thread safety. Do not replace the global allocator without explicit justification and end-to-end validation.

## Copying and movement

Avoid unnecessary copies, but do not replace readable value semantics with fragile views everywhere. Small values are often cheaper and safer to copy. Measure large-object/cross-boundary copies and redesign data flow when they dominate.

Distinguish copying from moving and from actual memory traffic: `std::move` is only a cast and does not guarantee an inexpensive move; move operations, copy elision, and return-value optimization depend on type and context. Avoid dangling `std::span`/`std::string_view` and measure the cost of serialization, conversions, temporary buffers, and ownership handoffs across stages. Prefer clear lifetime contracts over unverified zero-copy claims.

## Concurrency performance

Measure contention, queueing, wakeups, false sharing, and scheduling before adding threads or lock-free structures. More parallelism can increase tail latency and memory traffic.

Profile both on-CPU and off-CPU time. Examine synchronization frequency, ownership transfer, producer/consumer imbalance, thread oversubscription, affinity/NUMA when relevant, and memory-ordering costs. Batch work or reduce shared mutable state before reaching for lock-free code. Require race-free correctness and throughput **and** latency measurements under representative contention; do not weaken atomic ordering or synchronization based on intuition.

## Compiler-level optimization

Use compiler optimization settings appropriate to the target. Establish and record a reliable optimized baseline before exploring flags: commonly `-O2` or `-O3` on GCC/Clang, with the equivalent supported configuration on MSVC. Compare configurations empirically; `-O3` is not universally faster than `-O2`. Consider LTO/ThinLTO and representative-workload PGO when build/deployment complexity is justified and benchmarked. Preserve debuggability/rollback strategy for production builds.

When compiler evidence points to missed optimizations:

- inspect generated assembly in a release-equivalent configuration and correlate it with sampled hot paths (e.g. `perf`, VTune, Compiler Explorer);
- enable optimization/vectorization diagnostics (e.g. Clang `-Rpass=loop-vectorize -Rpass-missed=loop-vectorize`, GCC `-fopt-info-vec-optimized -fopt-info-vec-missed`) and inspect loop dependencies, alignment, contiguous access, and aliasing;
- compare `-march`/`-mtune` and ISA-specific builds only for compatible deployment targets. `-march=native` is suitable for local experiments or homogeneous known hardware, not generic distributable binaries; use runtime dispatch/multiple builds where portability requires it;
- evaluate auto-vectorization before hand-written intrinsics or architecture-specific assembly; validate numeric equivalence and performance across target CPUs;
- verify aliasing and lifetime guarantees before using compiler-specific `restrict`/`__restrict__` or alignment assumptions. Do not introduce undefined behavior, type-punning violations, data races, or unproven assumptions for speed;
- treat `-ffast-math`/`-Ofast` and unsafe floating-point reassociation as **semantic changes**, not default optimizations. Use only with an explicitly approved numerical contract and error testing;
- account for standard-library choice, link-time optimization, and actual generated code when comparing C++ with Rust; Rust commonly uses LLVM, but toolchains, flags, libraries, and implementation details can dominate observed differences.

`inline`, `constexpr`, templates, and `std::move` are not standalone performance strategies. Never assume source-level terseness guarantees better code generation. Avoid project-wide flag changes, new dependencies, and ABI changes without explicit scope and regression checks. Sanitizers (ASan/UBSan/TSan where supported) validate separate builds; do not benchmark their overhead as production performance.

## Benchmark quality

Record environment and workload assumptions. For microbenchmarks use a framework such as Google Benchmark when already available or appropriate. Validate gains on end-to-end/product workloads before claiming user-visible improvement.

For trustworthy comparisons:

- benchmark the same semantics, algorithms, data representations, numeric precision, error handling, allocation ownership, and I/O behavior; particularly for C++ vs Rust, do not equate different standard-library implementations or defaults with intrinsic language speed;
- use optimized builds and document exact compiler versions, standard libraries, `-O` levels, CPU targets, LTO/PGO status, input seeds, commit hashes, and dependency versions;
- run multiple repetitions, control competing workloads and CPU-frequency/thermal effects as practical, include warmup where appropriate, alternate variant order, and report median plus dispersion (and p95/p99 for latency workloads);
- isolate timed operations from fixture setup unless setup is part of the target; guard against dead-code elimination and overly predictable fixtures;
- use system profilers (`perf`/VTune/Instruments/appropriate platform tools), compiler optimization reports, and hardware counters to explain results; high instruction count, cache misses, or assembly differences are diagnostic evidence, not by themselves proof of an end-to-end gain;
- run functional/regression tests and compatible sanitizer configurations separately; for floating point, check tolerances and special values. Measure resource and latency regressions alongside any throughput gain;
- report baseline → candidate with units, sample count, variability, environment, exact change, correctness outcome, and decision: **keep**, **revert**, **inconclusive**, or **unmeasured proposal**.

Do not claim statistically meaningful speedups inside noise, extrapolate from microbenchmarks to an entire application, or invent benchmark/profiler outputs when tools cannot be run. Stop or revert if correctness, safety, portability, or maintainability costs exceed the measured benefit.
