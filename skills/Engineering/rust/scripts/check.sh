#!/usr/bin/env bash
set -euo pipefail

echo "==> rustfmt"
cargo fmt --all -- --check

echo "==> cargo check"
cargo check --workspace --all-targets --all-features

echo "==> clippy"
cargo clippy --workspace --all-targets --all-features -- -D warnings

echo "==> tests"
cargo test --workspace --all-features

if [[ "${RUST_SKILL_DOCS:-1}" == "1" ]]; then
  echo "==> rustdoc"
  RUSTDOCFLAGS="${RUSTDOCFLAGS:-} -D warnings" \
    cargo doc --workspace --all-features --no-deps
fi

echo "==> all Rust engineering gates passed"
