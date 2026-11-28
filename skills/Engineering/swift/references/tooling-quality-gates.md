# Swift Tooling and Quality Gates

## Philosophy

Automate mechanical rules. Humans and reviewers should spend attention on semantics, architecture, correctness, accessibility, security, and performance.

## Formatting gates

Formatting is a reproducible gate, not an editor preference. Use one checked-in configuration and run it consistently locally and in CI. Avoid per-developer formatting preferences that create diff noise.

`swift-format` ships with the Swift 6 toolchain as `swift format`, so the gate needs no separate formatter install on current Xcode versions. Projects that pin an older toolchain can use a standalone `swift-format` binary; the scripts accept either.

The skill ships one gate in four files:

| File | Role |
| --- | --- |
| `templates/.swift-format` | Baseline configuration: 4-space indentation, 120-column lines, at most one blank line, ordered imports, trailing commas in multi-element collections, and defect-adjacent rules such as `NeverForceUnwrap` left off by default |
| `scripts/check-format.sh` | Non-mutating gate: runs `swift format lint --strict` and the blank-line rule |
| `scripts/format-swift.sh` | Rewrites sources with the configuration, then fixes blank-line separation |
| `scripts/check-block-separation.py` | Enforces the structural rule: blank lines around control-flow blocks; a declaration stays attached to the statement defining or consuming it, and a guard stays attached to its protected group |

Prerequisites are a Swift 6 toolchain (or `swift-format`) and `python3`. Both shell scripts run from anywhere inside the project's git worktree, check every tracked and untracked-unignored `.swift` file by default, and accept explicit paths instead. They read `.swift-format` from the worktree root and fail with exit 2 when the configuration, the formatter, or Python is missing.

Exit codes: `check-format.sh` returns 0 when clean, 1 when formatting or blank-line separation differs (with the offending locations on stderr), and 2 on missing prerequisites or bad arguments. `format-swift.sh` returns 0 after rewriting and is idempotent, so a second run reports no changes.

To add the gate to a project that has none, copy `templates/.swift-format` to the project root and the three scripts into a tooling directory such as `scripts/`, then call `scripts/check-format.sh` from the fastest CI lane and from a pre-commit hook. When a change touches Swift sources and the project has no gate, add it as part of that change instead of hand-formatting. Keep one large format-only commit separate from a feature change so review stays readable.

A clean `check-format.sh` run proves formatting and blank-line structure only. It does not compile the code, run tests, or enforce SwiftLint rules.

## SwiftLint

Adopt rules incrementally. A useful rule must be:

- correct for the project's Swift/toolchain version
- actionable
- low enough noise that warnings are not ignored

Do not enable every opt-in rule blindly.

## CI order

A practical fast-fail sequence:

1. generated/config validation
2. formatting gate (`check-format.sh`)
3. SwiftLint
4. build/type-check
5. focused unit/component tests
6. broader integration/UI tests
7. release/security checks as applicable

## Warnings

Treat new compiler warnings in changed code as defects unless the project has an explicit exception. Do not blanket-disable diagnostics to make CI green.

## Legacy adoption

For existing large codebases:

- baseline or scope linting to changed files first
- avoid one giant “format everything + feature change” diff
- migrate unsafe concurrency/style debt in bounded changes

## Hard gates for new or changed production code

- **Compiler:** affected targets build without new compiler errors or unexplained warnings.
- **Concurrency:** no new `@unchecked Sendable` / `nonisolated(unsafe)` without a written invariant and review reason.
- **Crash primitives:** no new reachable `try!` or force unwrap of user/network/persistence/external data.
- **Cancellation:** supersedable or lifecycle-bound async work has an explicit cancellation story.
- **Sensitive data:** no credentials, tokens, private payloads, or user-sensitive material in logs, defaults, analytics, fixtures, or source.
- **Persistence:** schema changes have a migration/data-integrity plan and upgrade validation.
- **Deployment:** new Apple APIs respect the minimum OS contract or have explicit availability/fallback behavior.
- **Tests:** changed business behavior has regression coverage at the lowest durable test layer.

## Useful engineering KPIs

Track trends that reveal actual engineering risk:

- escaped ownership/lifetime defects;
- escaped concurrency/data-race defects;
- flaky-test rate;
- time to reproduce production defects;
- unsafe annotation/lint suppression additions vs removals;
- E2E reliability for critical user journeys;
- build/test feedback time for changed modules;
- crash-free and hang/hitch regressions where applicable.

Do not use raw line coverage, number of tests, number of protocols, or number of modules as standalone quality scores.

## Constructs requiring explicit justification

Challenge every new use of:

- `Task.detached`;
- `@unchecked Sendable`;
- `nonisolated(unsafe)`;
- custom cryptography;
- custom TLS trust/pinning;
- destructive persistence reset as migration strategy;
- long-lived global singleton state;
- arbitrary sleeps in tests;
- `Any` dictionaries crossing architectural boundaries.
