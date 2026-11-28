# Project architecture

## Crate boundaries

Create a crate boundary when it provides a real benefit:

- independent reuse/versioning;
- compile-time isolation;
- clear ownership/domain boundary;
- optional dependency isolation;
- platform separation;
- proc-macro requirement.

Avoid “one crate per folder” architecture.

## Module boundaries

Modules should group cohesive concepts, not arbitrary file sizes.
Keep implementation details private by default.
Expose the smallest surface needed by parent/public modules.

## Dependency direction

Prefer stable domain/core layers not depending on transport/UI/storage details.
Use adapters at boundaries where substitutability is actually useful.
Avoid circular conceptual dependencies hidden through utility crates.

## Utility modules

A growing `utils` module is a warning sign.
Move helpers toward the domain concept that owns them.
Use generic utility crates/modules only for genuinely cross-cutting primitives.

## Workspaces

Centralize shared dependency versions/workspace lints where practical.
Keep feature propagation understandable.
Avoid enabling every dependency feature by default.

## Configuration

Parse and validate configuration near startup.
Convert loose external config into validated domain configuration before passing it deeper.
Avoid repeated environment-variable reads throughout business logic.
