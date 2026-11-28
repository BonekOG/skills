# KPIs and quality gates

Metrics are used as **signals**, not substitutes for engineering judgment.

## Tier A — hard gates

Unless the repository explicitly overrides them:

| Gate                                       |     Target |
| ------------------------------------------ | ---------: |
| `cargo fmt --check`                        |  100% pass |
| `cargo check`                              |  100% pass |
| compiler warnings in changed build targets |          0 |
| `cargo clippy ... -D warnings`             | 0 warnings |
| test suite                                 |  100% pass |
| undocumented non-trivial unsafe blocks     |          0 |
| known failing tests introduced by change   |          0 |

## Tier B — policy gates

These may have justified local exceptions.

| Signal                                            | Default policy                                     |
| ------------------------------------------------- | -------------------------------------------------- |
| Production `unwrap` / `expect`                    | 0 on recoverable/input-dependent paths             |
| New unsafe code                                   | requires explicit safety rationale + focused tests |
| New dependency                                    | requires clear need; avoid duplicate capability    |
| Public API change                                 | review semver/MSRV/docs impact                     |
| Lint suppression                                  | narrow scope + reason                              |
| Unbounded queue/task creation from external input | not allowed                                        |
| Blocking call inside async runtime path           | isolate/offload or justify                         |
| `Arc<Mutex<_>>` introduced                        | confirm shared-mutability model is intentional     |

## Tier C — review KPIs / heuristics

These are **review triggers**, not automatic failures.

### Function size

- ~60+ logical LOC: review whether responsibilities should split.
- ~100+ logical LOC: strong signal to inspect cohesion.
- Exception: straightforward parsers/state machines/generated glue may remain clearer as one function.

### Parameter count

- 5–7 parameters: inspect whether a domain/config type improves clarity.
- More than ~7: strong signal for redesign unless the function is low-level/FFI-generated.
- Do not hide unrelated parameters in a meaningless “context” struct.

### Nesting / control-flow complexity

- nesting > 3–4 levels: look for early returns, helpers, or better modeling.
- cyclomatic/cognitive complexity > ~10–15: investigate, but do not refactor mechanically.

### Clone/allocation budget

No universal numeric limit.
Review every newly introduced clone/allocation in:

- loops;
- request hot paths;
- large data structures;
- high-frequency async tasks.
  Classify it as intentional or debt.

### Unsafe surface

Track:

- number of unsafe blocks/functions changed;
- lines of unsafe boundary code;
- safety tests/invariant docs.
  Goal is **small, stable, auditable surface**, not blindly zero unsafe.

### Test quality

Prefer:

- explicit coverage of changed behavior;
- branch/invariant coverage in critical logic;
- property tests for broad input domains.
  Avoid optimizing only for line coverage percentage.

A repository may choose a line coverage floor (for example 80%) as a regression alarm, but this skill does **not** treat any universal coverage percentage as proof of quality.

### Dependency health

Review new crates for:

- maintenance activity;
- security advisories;
- transitive dependency cost;
- feature footprint;
- license compatibility;
- MSRV impact.

### Performance

Use product-specific budgets:

- p50/p95/p99 latency;
- throughput;
- memory;
- allocations;
- binary size;
- startup time.
  Never invent thresholds without system requirements.

## Suggested scorecard for PR review

Use status, not a weighted vanity score:

```text
Correctness          PASS / CONCERN / FAIL
Type modeling        PASS / CONCERN / N/A
Ownership            PASS / CONCERN / FAIL
Errors               PASS / CONCERN / FAIL
Concurrency          PASS / CONCERN / N/A
Unsafe               PASS / CONCERN / N/A
Security             PASS / CONCERN / N/A
Performance          PASS / CONCERN / N/A
Tests                PASS / CONCERN / FAIL
Public API / SemVer  PASS / CONCERN / N/A
Tooling gates        PASS / FAIL
```

A `CONCERN` requires reviewer discussion; it is not automatically a rejection.
