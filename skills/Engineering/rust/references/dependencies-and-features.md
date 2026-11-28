# Dependencies, features, and MSRV

## Dependency policy

Before adding a crate:

- check whether std/existing dependencies already solve it;
- evaluate maintenance, API maturity, license, security posture, and dependency tree;
- avoid adding a large framework for a tiny helper.

## Feature flags

Features are API surface.

- prefer additive features;
- avoid mutually exclusive feature combinations when possible;
- document feature interactions;
- test important combinations;
- do not casually enable dependency `default-features`.

Beware feature unification in Cargo workspaces/dependency graphs.

## Optional dependencies

Use optional dependencies to isolate heavyweight integrations or platform capabilities when it improves consumers' control.

## MSRV

If the project declares a minimum supported Rust version:

- do not use newer features accidentally;
- test MSRV in CI if support is promised;
- treat an MSRV bump as a compatibility decision.

## Lockfiles

Applications generally commit `Cargo.lock`.
Library policy depends on repository goals, but CI/security tooling may still use lockfiles.
Follow repository convention.

## Build scripts / proc macros

Treat build scripts and proc macros as high-trust code with supply-chain/build-time impact.
Keep them minimal and deterministic where practical.
