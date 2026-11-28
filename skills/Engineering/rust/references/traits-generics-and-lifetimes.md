# Traits, generics, and lifetimes

## Traits should model capabilities

Create a trait when:

- multiple implementations exist or are realistically required now;
- consumers need polymorphism at a boundary;
- the trait expresses a domain capability;
- testing needs a stable boundary and the trait is not purely invented for mocking.

Avoid speculative one-implementation traits.

## Static vs dynamic dispatch

Prefer generics/static dispatch when:

- implementation types are known at compile time;
- performance/inlining matters;
- API complexity remains manageable.

Prefer `dyn Trait` when:

- heterogeneous runtime implementations are required;
- compile times/code size matter more than monomorphization;
- a stable object-safe plugin/boundary model is desired.

Do not choose based on ideology.

## Trait bounds

- Put bounds where they are needed.
- Avoid giant “god traits”.
- Prefer standard traits (`AsRef`, `Borrow`, `IntoIterator`, `From`, `TryFrom`) when their semantics fit.
- Do not use `Deref` merely to simulate inheritance or forward arbitrary methods.
- Keep public generic bounds minimal; every bound restricts callers.

## Conversions

Prefer:

- `From` for infallible conversions;
- `TryFrom` for fallible conversions;
- `AsRef` for cheap borrowed conversion/view;
- explicit named methods when semantics are domain-specific or lossy.

Avoid ambiguous generic conversion soup that harms inference and diagnostics.

## Associated types

Use associated types when a trait implementation has one natural corresponding type.
Use generic parameters when the implementation should support multiple values of that type parameter.

## Lifetimes in public APIs

Expose only relationships that callers need to understand.
Excessive lifetime coupling can make otherwise simple APIs difficult to compose.
