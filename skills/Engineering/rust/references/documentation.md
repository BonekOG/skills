# Documentation

## Public API docs

Document public APIs with:

- what it does;
- important invariants;
- errors (`# Errors`) when non-obvious;
- panics (`# Panics`) when possible;
- safety contract (`# Safety`) for unsafe APIs;
- examples for non-trivial usage.

Examples should compile when practical (doctests).

## Comments

Write comments for:

- why a surprising choice exists;
- protocol/algorithm constraints;
- concurrency invariants;
- safety invariants;
- performance tradeoffs;
- external compatibility requirements.

Do not narrate obvious syntax.

## Internal docs

Architecture docs should capture decisions that cannot be inferred easily from code:

- ownership of responsibilities;
- dependency direction;
- state machines;
- failure/cancellation model;
- compatibility constraints.

## TODOs

A TODO should identify the missing work/condition, not merely state that code is imperfect.
If the repository uses issue references, follow that convention.
