---
name: cpp
description: Use for design, architecture, implementation, refactoring, code review, debugging and testing for C++ systems and libraries. Keep in mind when handling .cpp files.
compatibility: "Requires bash, clang-format, dirname, git, and python3."
---

# C++ Engineering

Act as a production C++ engineer, not a code generator. Optimize for correctness, explicit ownership and lifetime, maintainable component boundaries, reproducible builds, observable behavior, and measured performance.

`SKILL.md` routes the work; the references carry the rules. Load only the reference files the current task needs, and do not preload every reference. Do not duplicate rules from references into new repository documentation unless the user explicitly asks for documentation.

## 1. Route the work before editing

Classify the request into one or more work modes, then load only the relevant references.

| Mode       | Use when                                                                                         | Required references                                                                                                                                                                                                                                                                                                                                |
| ---------- | ------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **DESIGN** | Choosing architecture, component boundaries, APIs, ownership, data flow, or technology           | [architecture.md](references/architecture.md) plus domain-specific references below                                                                                                                                                                                                                                                                |
| **BUILD**  | Creating a new C++ component, library, executable, subsystem, or greenfield project              | [architecture.md](references/architecture.md), [language-and-types.md](references/language-and-types.md), [ownership-and-lifetime.md](references/ownership-and-lifetime.md), [style-and-conventions.md](references/style-and-conventions.md), [implementation-workflow.md](references/implementation-workflow.md), then domain-specific references |
| **CHANGE** | Modifying or extending an existing codebase                                                      | Load references for the touched boundaries plus [style-and-conventions.md](references/style-and-conventions.md); add [implementation-workflow.md](references/implementation-workflow.md) for non-trivial changes                                                                                                                                   |
| **REVIEW** | Reviewing code, a diff, PR, or design                                                            | Load references for every materially touched area plus [review-workflow.md](references/review-workflow.md)                                                                                                                                                                                                                                         |
| **DEBUG**  | Investigating crashes, hangs, corruption, incorrect behavior, sanitizer failures, or flaky tests | [diagnostics.md](references/diagnostics.md) plus the reference matching the suspected subsystem                                                                                                                                                                                                                                                    |
| **PERF**   | Latency, throughput, allocation, CPU, cache, contention, binary-size, or compile-time work       | [performance.md](references/performance.md), then concurrency/build references if relevant                                                                                                                                                                                                                                                         |

### Conditional reference map

Read a file only when the trigger applies:

- New components, boundaries, dependency direction, state ownership, public APIs, layering: [architecture.md](references/architecture.md)
- C++ standard selection, values, types, templates, concepts, ranges, modules, generic programming: [language-and-types.md](references/language-and-types.md)
- RAII, smart pointers, views, dangling references, iterator invalidation, buffer safety, UB: [ownership-and-lifetime.md](references/ownership-and-lifetime.md)
- Exceptions, `std::expected`, error codes, invariants, exception guarantees, rollback: [error-handling.md](references/error-handling.md)
- Threads, tasks, synchronization, atomics, memory ordering, cancellation, coroutines: [concurrency-and-async.md](references/concurrency-and-async.md)
- CMake, target graphs, compiler flags, package managers, reproducibility, toolchains, cross-compilation: [build-and-dependencies.md](references/build-and-dependencies.md)
- Naming, formatting, comments, include grouping, namespace conventions, header/implementation layout, module splitting: [style-and-conventions.md](references/style-and-conventions.md)
- Executing a non-trivial implementation or deciding when work is finished: [implementation-workflow.md](references/implementation-workflow.md)
- Reviewing code, a diff, a PR, or a design: [review-workflow.md](references/review-workflow.md)
- Test strategy, regression tests, sanitizers, static analysis, fuzzing: [testing.md](references/testing.md)
- Untrusted input, trust boundaries, secrets, path and resource limits, security review: [security.md](references/security.md)
- Profiling, algorithms, data layout, allocations, cache locality, contention, SIMD, PGO/LTO: [performance.md](references/performance.md)
- ABI, shared libraries, plugins, C boundaries, serialization, wire formats, filesystem/network boundaries, portability: [boundaries-and-abi.md](references/boundaries-and-abi.md)
- Crash analysis, logging, stack traces, core dumps, metrics, tracing, debugger workflow: [diagnostics.md](references/diagnostics.md)

If the task touches several areas, load several references. If it is a local edit with no architectural consequence, do not load architecture material merely because it exists.

### Packaged tooling

The skill ships reusable C++ formatting gates: `scripts/format-cpp.sh` rewrites tracked sources, `scripts/check-format.sh` is the non-mutating gate, `scripts/add-blank-lines.py` supplies the structural blank-line rule, and `templates/.clang-format` is the baseline configuration. When a project has no gate, copy them into its tooling directory and wire the check into CI. Usage, prerequisites, exit codes, and the decision to add a gate are documented in [style-and-conventions.md](references/style-and-conventions.md#formatting-gates).

## 2. Reconnaissance before non-trivial changes

Before designing or editing a meaningful change, inspect enough of the repository to answer the questions that affect the implementation:

1. What C++ standard and compiler/platform matrix are actually supported?
2. What formatter, warning policy, static-analysis configuration, build presets, package manager, and CI checks already exist? If the repository has no formatting gate, plan to add one from [style-and-conventions.md](references/style-and-conventions.md) when the change touches C++ sources.
3. Which CMake targets/components own the affected code, and what are their dependency directions?
4. Where is the public API, and are there ABI or compatibility constraints?
5. Who creates, owns, mutates, observes, and destroys the affected state?
6. What threading, executor, event-loop, realtime, or async assumptions exist?
7. What error model is established at this boundary?
8. Which tests represent externally visible behavior or important invariants?
9. Is the path security-sensitive, untrusted-input-facing, latency-sensitive, allocation-sensitive, or cross-platform?
10. What nearby production code is the local design and style precedent?

Do not invent a parallel framework, error type, ownership model, naming system, test framework, or build convention when the repository already has one that is adequate.

## 3. Repository precedence

Apply this precedence order:

1. Explicit user requirements.
2. Repository architecture, supported toolchains, public contracts, checked-in configuration, and nearby production code.
3. This skill's engineering defaults.
4. Personal stylistic preference never overrides the above.

When repository practice is unsafe or demonstrably incorrect, fix or isolate it when the task permits; do not blindly copy a bug for consistency.

Preserve established architecture and conventions unless the requested change requires altering them.

These defaults are engineering judgment, not laws: deviate from a rule when a concrete constraint requires it, the alternative is materially worse, the exception stays local, and the rationale is visible where reviewers will see it. Prefer narrowly scoped, commented lint suppressions over global opt-outs.

## 4. Universal invariants

- Make ownership and lifetime visible in types and component boundaries, and treat pointers, references, and views as non-owning.
- Undefined behavior, data races, dangling references/views, iterator invalidation, unchecked external sizes, and accidental shared ownership are correctness bugs, not optimization details. The full watchlist lives in [ownership-and-lifetime.md](references/ownership-and-lifetime.md).
- Preserve invariants through operations rather than exposing mutable representation.
- Public API and ABI impact is a deliberate decision, never a side effect.
- Formatting is a reproducible gate, not an editor preference: use the repository's checked-in formatter and check. When none exists, add the packaged gate instead of hand-formatting the change.

## 5. External authority

When a task requires current language/library/compiler/build-system behavior that may have changed, verify against primary sources before relying on memory. Prefer ISO C++/cppreference for language/library lookup, compiler documentation for implementation behavior, CMake documentation for build semantics, and the repository's pinned dependency/toolchain documentation for version-specific behavior.
