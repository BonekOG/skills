# Testing, Analysis, and Fuzzing

Read this reference when adding tests, validating a change, or investigating correctness and safety risks with tests and analysis tools.

For untrusted input, trust boundaries, secrets, and resource limits, read [security.md](security.md) alongside this reference.

## Test strategy

Test at the highest level that proves the important behavior reliably, then add lower-level tests where they improve diagnosis or cover combinatorial logic.

- **Behavior/E2E:** externally visible product workflows and critical invariants.
- **Integration:** component boundaries, filesystem, database, network, serialization, process interaction.
- **Unit:** algorithms, state machines, edge-heavy pure logic, focused invariants.
- **Property-based:** parsers, transformations, math, round trips, state-machine invariants.
- **Fuzzing:** untrusted parsers/protocol/file-format boundaries and complex decoders.

Do not mock implementation details merely to make a unit test possible. Prefer concrete collaborators, fakes at real boundaries, or integration tests when they better represent product truth.

Tests should be deterministic, independent, and explicit about fixtures/state. Give failures enough information to diagnose the violated invariant.

## Regression tests

For a bug fix, add coverage that fails for the original failure mode whenever practical. Place the test at the boundary where the regression is most meaningfully prevented, not necessarily at the exact line that was broken.

## Sanitizers

Use the repository-supported sanitizer builds:

- **ASan:** out-of-bounds, use-after-free and related memory errors.
- **UBSan:** many undefined-behavior classes such as invalid shifts, misalignment, overflow checks configured by the project.
- **TSan:** data races in threaded code.
- **MSan:** uninitialized reads where the supported toolchain/dependency environment makes it practical.

Do not run incompatible sanitizers together unless the toolchain supports that combination. Treat sanitizer reports as defects until disproven with evidence.

## Static analysis

Use compiler warnings plus configured analyzers such as clang-tidy and Clang Static Analyzer. Prefer repository-configured checks. High-value classes include correctness, lifetime, concurrency, performance, portability, CERT/security, and modernize checks that do not create churn without benefit.

When available and appropriate, use lifetime/buffer-safety analysis to find dangling views and unsafe pointer arithmetic.

## Fuzzing

Fuzz boundaries that accept attacker-controlled or structurally complex input:

- file formats and importers;
- protocol/network frames;
- parsers/deserializers;
- image/audio/media decoders;
- compression/archive readers;
- custom binary formats.

A fuzz target should be deterministic, fast, side-effect-contained, and sanitizer-enabled. Seed it with valid minimal corpus samples and preserve interesting regressions as normal tests where useful.
