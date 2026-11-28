---
name: swift
description: Use for implementing, refactoring, reviewing, debugging, testing, architecting, or optimizing Swift/SwiftUI code for Swift and Apple-platform. Keep in mind when handling .swift files.
compatibility: "Requires bash, dirname, git, python3, and swift. The Swift toolchain must include swift format."
---

# Swift Engineering

This file is the **only entry point and source-of-truth router** for Swift engineering work. Do not look for or invoke other Swift skills. All detailed guidance lives under `references/` and is subordinate to this file.

## Mission

Produce Swift code that is correct, idiomatic, understandable at the call site, safe under Swift 6 concurrency, proportionately architected, testable, observable, accessible, secure, performant where measured, and maintainable over time.

## Operating procedure

For every nontrivial task:

1. Inspect the project before changing it: Swift language mode/toolchain, Xcode/SDK, deployment targets, platforms, package/module boundaries, architecture, state ownership, concurrency annotations, persistence/network/security layers, test framework, and CI/tooling.
2. Identify the affected engineering domains from the routing table below.
3. Read the corresponding reference files **before** implementing or reviewing that part of the task.
4. Preserve established project conventions unless they conflict with correctness, safety, the user's explicit requirements, or a rule in this skill.
5. Prefer the smallest design that makes ownership, state, effects, failure behavior, and dependencies explicit.
6. Validate the actual changed behavior with build/type-check, focused tests, and the project's existing lint/format gates when practical.
7. Before finishing, apply `references/review-checklist.md` to the changed domains and state any remaining uncertainty.

## Production defaults

Prefer:

- `let` and value semantics for plain data and immutable snapshots.
- enums and exhaustive `switch` for finite state.
- structs for values; classes for identity/lifetime; actors for shared mutable concurrent state.
- typed domain models over stringly typed state, flag matrices, `[String: Any]`, or weakly modeled tuples.
- clear APIs optimized for the use site.
- `async`/`await`, structured concurrency, explicit task ownership, and cooperative cancellation.
- one clear owner for mutable UI state.
- dependency injection at real side-effect boundaries rather than hidden globals.
- errors that preserve recovery semantics.
- behavior-focused tests at the lowest durable layer, plus a small number of E2E tests for critical product truth.
- measurement before performance optimization.
- accessibility, privacy, migration safety, and deployment availability as correctness concerns.

Avoid by default:

- reachable force unwraps, `try!`, or unexplained `fatalError` in production paths.
- `Any`/`AnyObject` as a substitute for domain modeling.
- hidden singleton/service-locator dependencies.
- `Task.detached`, `@unchecked Sendable`, or `nonisolated(unsafe)` as escape hatches.
- GCD wrappers around APIs that already have correct Swift-concurrency APIs.
- protocols created solely so every concrete type can be mocked.
- giant view models/services/repositories with unrelated responsibilities.
- architecture migrations hidden inside unrelated feature work.
- arbitrary sleeps in asynchronous tests.
- custom crypto or TLS trust logic without an explicit threat model and lifecycle plan.

## Reference routing

Read only the references relevant to the task, but treat them as one coherent rule set:

| Topic / trigger                                                                           | Required reference                        |
| ----------------------------------------------------------------------------------------- | ----------------------------------------- |
| Idiomatic Swift, optionals, generics, protocols, collections, closures, modern syntax     | `references/language-idioms.md`           |
| Naming, argument labels, public APIs, mutating semantics, docs                            | `references/api-design.md`                |
| Struct/class/actor choice, identity, enums, ownership, protocol modeling                  | `references/type-modeling.md`             |
| Throws, typed/domain errors, cancellation, diagnostics                                    | `references/error-handling.md`            |
| async/await, actors, Sendable, tasks, cancellation, AsyncSequence, continuations          | `references/concurrency-and-async.md`     |
| MV/MVVM/MVI/TCA/Clean/Coordinator, state/effect boundaries                                | `references/architecture.md`              |
| Dependency injection, service boundaries, clocks/UUIDs/network/store seams                | `references/dependency-management.md`     |
| Swift packages/modules, access control, dependency direction                              | `references/package-modularity.md`        |
| Swift Testing, XCTest, XCUITest, deterministic tests, E2E strategy                        | `references/testing.md`                   |
| SwiftUI state, Observation, identity, composition, navigation, accessibility, performance | `references/swiftui.md`                   |
| UIKit/AppKit interop, lifecycle, deployment availability, platform boundaries             | `references/apple-platform-boundaries.md` |
| URLSession, HTTP semantics, DTOs, retries, cancellation, auth                             | `references/networking.md`                |
| SwiftData/Core Data/files/defaults, migration, transactions, integrity                    | `references/persistence.md`               |
| Keychain, CryptoKit, LocalAuthentication, Secure Enclave, privacy, TLS                    | `references/security.md`                  |
| CPU/memory/rendering/startup/concurrency performance and profiling                        | `references/performance.md`               |
| Correctness-first PR/diff review methodology                                              | `references/review-workflow.md`           |
| SwiftLint/SwiftFormat/build gates/quality gates                                           | `references/tooling-quality-gates.md`     |
| Smell catalog and patterns to challenge during design/review                              | `references/anti-patterns.md`             |
| Final implementation/API/concurrency/SwiftUI/security/PR checks                           | `references/review-checklist.md`          |

### Packaged tooling

The skill ships reusable Swift formatting gates: `scripts/format-swift.sh` rewrites tracked sources, `scripts/check-format.sh` is the non-mutating gate, `scripts/check-block-separation.py` supplies the structural blank-line rule, and `templates/.swift-format` is the baseline configuration. When a project has no gate, copy them into its tooling directory and wire the check into CI. Usage, prerequisites, exit codes, and the decision to add a gate are documented in [tooling-quality-gates.md](references/tooling-quality-gates.md#formatting-gates).

## Conflict resolution

When rules appear to conflict, use this precedence:

1. Correctness and data integrity.
2. Security and privacy.
3. Explicit user/product requirements.
4. Compiler-enforced Swift semantics and actor isolation.
5. Existing externally visible API/source compatibility.
6. Deployment-target compatibility.
7. Established project architecture and conventions.
8. Simplicity, clarity, testability, and maintainability.
9. Performance only after measurement, unless complexity is obviously pathological.
10. Mechanical style.

Do not preserve a local convention that is demonstrably unsafe merely for consistency; explain the deviation instead.

## Definition of done

Before finishing a meaningful Swift change:

- affected targets build or type-check when practical;
- focused tests for changed behavior run;
- `scripts/check-format.sh` passes, including when the gate had to be added first;
- concurrency code is re-read for isolation, `Sendable`, reentrancy, task lifetime, and cancellation;
- SwiftUI code is re-read for source of truth, identity, lifecycle, navigation, accessibility, and availability;
- persistence changes are re-read for migration and data-loss risk;
- network/security changes are re-read for retry/idempotency, trust, secret handling, and sensitive logging;
- public API changes are checked at real call sites;
- validation performed and remaining risks are summarized.
