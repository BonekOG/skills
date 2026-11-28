# Review Workflow

Read this reference when reviewing C++ code, a diff, a pull request, or a design.

Review in this order; do not lead with formatting when correctness risks exist:

1. Behavioral correctness and missing requirements.
2. Ownership/lifetime, UB, iterator/view invalidation, bounds and integer-size safety.
3. Error propagation and exception guarantees.
4. Thread safety, ordering, shutdown, cancellation, deadlocks, races.
5. API compatibility and ABI implications.
6. Architecture/dependency direction and unnecessary abstraction.
7. Security and hostile-input handling.
8. Test quality and regression coverage.
9. Performance claims and measurable hot-path regressions.
10. Build portability, warnings, packaging, and style.

Report concrete findings with file/line references when available. Explain the failure mode and the smallest robust correction. Do not manufacture issues to fill categories.

When useful for the discussion, summarize per-area status (for example PASS/CONCERN/FAIL for correctness, ownership, errors, concurrency, security, tests, API). A CONCERN invites discussion; it is not automatically a rejection.
