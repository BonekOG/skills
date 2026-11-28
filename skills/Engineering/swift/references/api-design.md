# Swift API Design

Use Swift.org's API Design Guidelines as the normative naming baseline.

## Principles

1. **Clarity at the point of use is the primary goal.** Judge the call site, not just the declaration.
2. Prefer clarity over brevity.
3. Omit needless words, but keep words that disambiguate semantics.
4. Use terminology consistently with established Swift/domain precedent.
5. Avoid obscure abbreviations unless they are standard terms of art.

## Naming

- Types/protocols: `UpperCamelCase`.
- Functions/properties/variables/cases: `lowerCamelCase`.
- Name operations by effect and domain meaning, not implementation mechanism.
- Boolean names should read naturally at the use site (`isEmpty`, `canRetry`, `shouldPersist`).
- Name protocols for capabilities/roles, not by appending `Protocol` mechanically unless the codebase deliberately uses that convention.

## Argument labels

- Use labels to make the call read as a phrase where that improves clarity.
- Omit a first label when the argument is the direct object and the call remains unambiguous.
- Do not repeat type information already obvious from the static context.
- Prefer defaults for genuinely optional behavior, usually later in the parameter list.

## Mutating / nonmutating pairs

- Make mutation visible in the name and type semantics.
- Favor established Swift conventions: an operation returning a transformed value should read differently from one mutating `self`.

## Public API discipline

- Keep public surface area minimal.
- Prefer domain types over primitive parameter clusters.
- Avoid leaking transport/database/UI implementation types across module boundaries.
- Consider source compatibility before changing names, generic constraints, actor isolation, error types, or `Sendable` conformance.
- For non-O(1) computed properties that look cheap, document complexity.

## Documentation

Document public/internal-shared APIs when intent, invariants, ownership, complexity, threading/isolation, failure modes, or units are not obvious from the signature.

## API review checklist

- Does the primary use site read clearly without comments?
- Can invalid combinations be represented?
- Are labels doing useful semantic work?
- Is the return type more informative than a tuple/boolean/status code?
- Does the API expose implementation details it should hide?
- Are errors/cancellation part of the contract?
