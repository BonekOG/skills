# Implementation Workflow and Definition of Done

Read this reference when implementing or changing C++ code (BUILD and CHANGE work).

## Workflow

1. Identify affected behavior and invariants.
2. Trace the current call/data/ownership path before adding abstractions.
3. Choose the smallest coherent design that satisfies current requirements.
4. Decide API shape, ownership, failure semantics, and concurrency semantics before implementation when they cross a boundary.
5. Update the build graph only when a real target/dependency boundary changes.
6. For structural refactors, follow the module-splitting and include rules in [style-and-conventions.md](style-and-conventions.md) before compiling.
7. Implement in small cohesive steps and reuse established repository facilities.
8. Add or update tests at the highest useful behavioral level; add lower-level tests for complex algorithms, edge cases, or isolated invariants.
9. Run the repository's formatting gate before compiling when one exists. If the repository has no formatting gate, add one from [style-and-conventions.md](style-and-conventions.md) rather than leaving the change unformatted.
10. Re-read the diff and verify it against the definition of done below, running the verification gates it lists; for performance-sensitive work, produce baseline-compared evidence.

## Definition of done

A C++ change is not complete merely because it compiles. Before finishing, verify the applicable items:

- Required behavior and edge cases are covered.
- Ownership/lifetime and failure paths are explicit and correct.
- None of the correctness hazards named in the `Universal invariants` section of SKILL.md are introduced.
- Public API/ABI impact is intentional.
- CMake target relationships and dependency visibility are correct.
- Tests pass at the relevant behavioral/integration/unit level.
- Formatter, compiler warnings, static analysis, and applicable sanitizers pass or known limitations are stated.
- The formatting gate is reproducible from the repository, not dependent on an editor setting or a hand-formatted diff; when the gate did not exist, the change adds and wires it.
- Performance-sensitive work has evidence rather than intuition.
- Cross-platform code does not assume platform details that the supported matrix contradicts.
- The implementation is no more abstract or complex than the current requirements justify.
