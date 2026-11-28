# Swift Language Idioms

## Core rules

- Optimize for semantic clarity, not minimum character count.
- Prefer immutable `let` bindings; use `var` only for actual mutation.
- Prefer value types for independent data values; choose reference types for identity/lifetime semantics.
- Model impossible states out of the type system rather than guarding them repeatedly at runtime.
- Prefer exhaustive `switch` over nested boolean logic for finite domain states.
- Keep optionals meaningful: `nil` should represent one clear absence state.
- Avoid nested optionals and collections of optionals unless each absence has domain meaning.
- Prefer `guard` for early rejection of preconditions and invalid states; keep the success path visually dominant.
- Avoid force unwraps except for invariants that are structurally guaranteed and locally obvious; document why if used.
- Avoid `try!` in production paths.

## `some` and `any`

- Use opaque `some Protocol` when the implementation chooses one hidden concrete type and callers do not need heterogeneity.
- Use existential `any Protocol` when values of multiple conforming concrete types must be stored or passed behind a runtime box.
- Do not erase concrete types prematurely; type erasure has readability, optimization, and capability costs.

## Generics and protocols

- Use generics when preserving concrete type information improves correctness or performance.
- Put constraints where they express the actual operation requirements.
- Prefer protocol composition only when each protocol represents a coherent capability.
- Avoid “protocol for every class” design. A protocol should represent substitutability, a boundary, or a reusable capability.

## Collections

- Choose the data structure for semantics first: ordering, uniqueness, lookup complexity, and mutation pattern.
- Avoid repeated linear scans inside loops when a set/dictionary index makes the intent clearer and complexity bounded.
- Prefer lazy transforms only when they materially avoid work or allocation; do not make simple code harder to read without evidence.
- Keep transformations pure where practical; separate mapping/filtering from side effects.

## Closures

- Capture `self` explicitly when capture semantics matter.
- Do not reflexively use `[weak self]`; choose strong/weak/unowned based on lifetime and cycle analysis.
- `unowned` is only correct when lifetime dominance is guaranteed.
- Avoid long nested closure pyramids; extract named operations or convert callback APIs to async when appropriate.

## Property wrappers and macros

- Treat wrappers/macros as semantic tools, not decoration.
- Understand ownership and generated behavior before adopting them in public or persistent models.
- Avoid stacking wrappers when the resulting storage/update semantics are non-obvious.

## Review prompts

Ask:

- Can the type system eliminate this invalid state?
- Is an optional carrying more than one meaning?
- Is this existential necessary?
- Is this reference type actually about identity?
- Is mutation scoped as tightly as possible?
