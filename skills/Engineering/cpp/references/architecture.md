# Architecture and Component Design

Read this reference only when the task changes component boundaries, dependency direction, state ownership, public APIs, or subsystem structure.

## Boundary model

For each non-trivial component, identify:

- Responsibility: what behavior belongs here and what does not.
- State: what persistent state exists.
- Ownership: who creates and destroys the component and its state.
- Mutation: which operations may change state and under what synchronization model.
- Dependencies: which lower-level facilities it needs and why.
- Failure surface: which failures cross the boundary and in what representation.
- Concurrency: thread/executor affinity, reentrancy, and shutdown semantics.
- Deployment/ABI: whether the boundary crosses a shared library, process, plugin, device, or network.

Do not split a cohesive component merely to create controller/service/repository/interface layers. Split when responsibilities, lifetimes, independent variation, testing boundaries, deployment, or performance characteristics justify it.

## Dependency direction

- Keep high-level product/domain behavior independent of transport, persistence, UI, OS, and protocol details when those details vary independently.
- Put adapters at real boundaries rather than wrapping every class in an interface.
- Prevent dependency cycles. If two components require each other, reconsider responsibility or extract the minimal shared contract/data type.
- Avoid service locators and ambient global state. Pass required dependencies explicitly or own them in a higher-level composition root.
- Prefer acyclic target graphs that reflect runtime ownership and deployment boundaries.

## State and invariants

- Keep authoritative mutable state in one clearly owned place whenever practical.
- Prefer operations such as `reserve()`, `commit()`, `advance()`, or domain-specific verbs over exposing mutable members.
- Represent important states explicitly with enums/variants/state types when a collection of booleans can produce illegal combinations.
- Make transitions validate preconditions and preserve invariants.
- Avoid duplicate caches or mirrored state without a clear invalidation/update protocol.

## Abstraction choice

Use the least powerful abstraction that satisfies the requirement:

1. Concrete value type or function.
2. Concrete owned collaborator.
3. Template/concept for compile-time polymorphism when variation is static and generic code is valuable.
4. Type erasure/function object when runtime substitution is needed without inheritance coupling.
5. Abstract base class when identity/runtime polymorphism and stable virtual semantics are genuinely appropriate.
6. Plugin/process boundary when independent deployment, fault isolation, language/compiler isolation, or ABI requirements justify it.

Do not introduce abstraction only because a second implementation might exist someday.

## API design checklist

- Is ownership obvious from the type?
- Is nullability intentional?
- Are units and ranges clear?
- Can callers violate an invariant through exposed representation?
- Is a borrowed argument guaranteed to outlive its use?
- Does the return type communicate absence/failure distinctly from a valid value?
- Is the API synchronous or asynchronous by contract?
- Are thread-safety and reentrancy requirements documented where non-obvious?
- Does exposing a template/STL/container type create unwanted compile-time or ABI coupling?
- Can the API be made smaller without losing necessary capability?

## Common rejection patterns

Reject or simplify designs with:

- one interface per concrete class with no independent runtime variation;
- one CMake library per conceptual layer despite identical lifecycle/deployment;
- shared ownership used to avoid deciding ownership;
- generic repositories/managers/controllers that hide domain operations;
- public setters for every field instead of invariant-preserving operations;
- event buses for local direct collaboration;
- cross-component callbacks with unspecified lifetime/cancellation;
- inheritance used only for code reuse.
