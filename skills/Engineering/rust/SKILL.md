---
name: rust
description: Use this skill when producing, reviewing, refactoring, debugging, and architecting Rust code. Keep in mind when handling .rs files.
compatibility: "Requires bash and cargo. The Rust toolchain must include rustfmt, Clippy, and rustdoc."
allowed-tools: Read Write Edit Glob Grep Bash
---

# Rust Engineering

Write Rust that is correct, idiomatic, maintainable, reviewable, and efficient — not merely Rust that compiles.

`SKILL.md` routes the work; the references carry the rules. Load only the references the current task needs.

## Repository precedence

Apply this precedence order:

1. Explicit user requirements.
2. Repository architecture, toolchain and MSRV, public contracts, checked-in configuration, and nearby production code.
3. This skill's engineering defaults.
4. Personal stylistic preference never overrides the above.

Preserve established architecture and conventions unless the requested change requires altering them. When repository practice is unsafe or demonstrably incorrect, fix or isolate it when the task permits; do not blindly copy a bug for consistency.

## Universal invariants

These apply in every mode, even when no reference is loaded.

- Soundness first: no undefined behavior, no unsound `unsafe`, no data races. Keep the unsafe surface minimal and give every non-trivial unsafe block a `SAFETY:` argument. Details: [unsafe-and-ffi.md](references/unsafe-and-ffi.md).
- Make invalid states unrepresentable: enums for mutually exclusive states, newtypes for domain meaning and incompatible identities. Details: [data-modeling.md](references/data-modeling.md).
- Ownership is a design decision: borrow when access suffices, move on transfer intent, clone only for semantic reasons — never to silence the borrow checker. Details: [ownership-and-borrowing.md](references/ownership-and-borrowing.md).
- Failure is typed: `Result` for recoverable failure, `Option` for absence, panic only for programmer errors and violated invariants. Details: [error-handling.md](references/error-handling.md).
- Public types, trait bounds, error enums, features, and re-exports are semver surface; keep the public API minimal and unsurprising. Details: [api-design.md](references/api-design.md).
- Performance changes require evidence; do not add complexity for speculative optimization. Details: [performance.md](references/performance.md).

## Routing table

Load only the references relevant to the task.

| Task / signal                                             | Read                                          |
| --------------------------------------------------------- | --------------------------------------------- |
| Any substantial Rust change                               | `references/operating-model.md`               |
| Implementing or changing Rust code (workflow, done gates) | `references/implementation-workflow.md`       |
| Borrow checker, moves, clones, lifetimes                  | `references/ownership-and-borrowing.md`       |
| Domain types, states, newtypes                            | `references/data-modeling.md`                 |
| `Result`, `Option`, panic, error crates                   | `references/error-handling.md`                |
| Traits, generics, dispatch, lifetimes                     | `references/traits-generics-and-lifetimes.md` |
| Collections, iterator design, allocation                  | `references/collections-and-iterators.md`     |
| Public/library API                                        | `references/api-design.md`                    |
| Modules, crates, workspaces, architecture                 | `references/architecture.md`                  |
| Tokio, async, tasks, channels, locks                      | `references/concurrency-and-async.md`         |
| Latency, throughput, allocation, profiling                | `references/performance.md`                   |
| `unsafe`, raw pointers, FFI                               | `references/unsafe-and-ffi.md`                |
| Unit/integration/property/E2E tests                       | `references/testing.md`                       |
| rustdoc, examples, comments                               | `references/documentation.md`                 |
| Input validation, secrets, deserialization, supply chain  | `references/security.md`                      |
| Design patterns / anti-patterns                           | `references/patterns-and-anti-patterns.md`    |
| logs, tracing, metrics                                    | `references/observability.md`                 |
| dependencies, features, MSRV                              | `references/dependencies-and-features.md`     |
| code review                                               | `references/review-checklist.md`              |
| metrics, thresholds, quality gates                        | `references/quality-gates.md`                 |

## Bundled tooling

The package ships gates a project can adopt when it has none. `scripts/check.sh` runs rustfmt, `cargo check`, Clippy with `-D warnings`, the test suite, and rustdoc; run it from the workspace root and set `RUST_SKILL_DOCS=0` to skip the documentation gate. `templates/cargo-lints.toml` holds the workspace lint baseline, `templates/clippy.toml` the threshold configuration, and `templates/rust-ci.yml` a CI workflow that applies the same gates. Gate definitions and thresholds are documented in [quality-gates.md](references/quality-gates.md); the workflow around them is in [implementation-workflow.md](references/implementation-workflow.md).

## External authority

When a task requires current language, tooling, or platform behavior that may have changed, verify against primary sources before relying on memory: the standard library documentation, the Rust Reference, the Rustonomicon for unsafe semantics, the Cargo Book for build/feature/MSRV behavior, and clippy documentation for lint behavior. Repository-pinned toolchain and dependency documentation wins for version-specific behavior.
