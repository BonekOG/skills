# API design

## Public API principles

Public APIs should be:

- unsurprising;
- difficult to misuse;
- explicit about ownership and failure;
- minimal in surface area;
- semver-conscious.

## Naming

Follow Rust conventions:

- types/traits: `UpperCamelCase`;
- functions/modules/variables: `snake_case`;
- constructors commonly `new`;
- conversions use standard trait conventions when applicable;
- predicates read naturally (`is_empty`, `contains`, `has_*` when appropriate).

Names should describe domain intent rather than implementation mechanism.

## Input flexibility

Prefer borrowed canonical inputs (`&str`, `&Path`, `&[T]`) when ownership is not required.
Use generic conversion bounds only when they materially improve ergonomics without harming errors/inference.

## Builders

Builders are useful when:

- many optional parameters exist;
- construction needs readable call sites;
- configuration evolves over time.

Do not use a builder for a two-field object with obvious construction.

## Return concrete vs `impl Trait`

Use concrete types when they are meaningful/stable API.
Use `impl Trait` to hide implementation details where caller behavior does not depend on the concrete type.
Use boxed/dynamic traits when runtime polymorphism is required.

## Re-exports

Treat re-exported third-party types as part of your public dependency contract.
Do not casually leak dependency types through public fields, errors, or method signatures.

## Semver checklist

Before changing a public API, check:

- removed/renamed items;
- new trait requirements;
- changed generic bounds;
- changed error variants if consumers match exhaustively;
- changed feature defaults;
- MSRV changes;
- serde/wire-format changes;
- changed auto-trait behavior (`Send`/`Sync`).
