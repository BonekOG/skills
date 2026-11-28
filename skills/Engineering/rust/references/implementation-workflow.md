# Implementation Workflow and Verification

Read this reference when implementing or changing Rust code.

## Workflow

- [ ] Read repository instructions and the closest relevant code.
- [ ] Identify behavior/invariants and acceptance criteria.
- [ ] Decide data model and ownership boundaries.
- [ ] Identify failure modes and error types.
- [ ] Identify concurrency/unsafe/performance implications.
- [ ] Implement the smallest coherent change.
- [ ] Add/update behavior-focused tests.
- [ ] Review for unnecessary clones, allocations, locks, panics, and abstractions.
- [ ] Run the verification gates below.
- [ ] Report what changed, what was verified, and any remaining risk.

## Verification gates

Run the repository's own checks first if present. Otherwise run:

1. `cargo fmt --all -- --check`
2. `cargo check --workspace --all-targets --all-features`
3. `cargo clippy --workspace --all-targets --all-features -- -D warnings`
4. `cargo test --workspace --all-features`
5. `cargo doc --workspace --all-features --no-deps` for public/library API changes

`scripts/check.sh` runs gates 1–5 (opt out of the rustdoc gate with `RUST_SKILL_DOCS=0`). Run targeted tests during iteration and the broad gate before completion when feasible. Never claim a check passed unless it actually ran successfully.

Gate tiers, justified exceptions, and review signals: [quality-gates.md](quality-gates.md).
