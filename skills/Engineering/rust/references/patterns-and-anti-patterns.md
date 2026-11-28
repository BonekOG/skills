# Rust patterns and anti-patterns

## Prefer Rust-native patterns

Classic OO patterns often collapse into simpler Rust constructs:

- Strategy -> trait/generic/closure.
- State -> enum or typestate.
- Visitor -> trait/enum matching depending openness.
- Builder -> useful for optional/evolving construction.
- RAII -> ownership + `Drop`.
- Newtype -> domain distinction and API control.
- Adapter -> trait impl / wrapper.
- Command -> enum/trait object when operations are data.

Do not mechanically port Java/C++ architecture.

## Strong patterns

### Newtype

Separate domain identities/units and constrain APIs.

### Type state

Compile-time operation ordering when state transitions are stable and safety-critical.

### RAII guards

Tie cleanup/release/reset to scope exit.

### Extension traits

Add cohesive helper behavior without polluting unrelated namespaces.

### Sealed traits

Useful when a public trait must not be implemented externally.

### Parse, then validate/normalize

Convert untrusted/loose representations to strong domain types at boundaries.

## Anti-patterns

### Clone-driven programming

Using cloning to avoid ownership design.

### Stringly typed domain

States/types encoded as arbitrary strings.

### Boolean state explosion

Multiple flags encode a state machine implicitly.

### `Arc<Mutex<_>>` everywhere

Shared mutable state becomes the default architecture.

### God context

A giant application context passed everywhere with unrelated services/config.

### Trait-for-everything

Premature interfaces make code harder to navigate and generic errors harder to understand.

### Mega error enum

Every underlying dependency error is surfaced as a public variant.

### Over-chained iterators

Dense combinator chains that obscure state and errors.

### Unsafe escape hatch

Unsafe introduced because safe ownership design feels inconvenient.

### Premature macro abstraction

Macros hide ordinary duplication before semantics stabilize.

## Pattern selection rule

Choose the least powerful pattern that makes invariants and variation explicit. Clarity beats cleverness: prefer immutable bindings by default, small pure transformations, and explicit state transitions.
