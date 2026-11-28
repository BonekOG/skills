# Swift Type Modeling

## Prefer types over conventions

Use dedicated types when values have different meaning even if their storage is identical: identifiers, money, units, validated strings, timestamps, ranges, permissions, states.

## Struct vs class vs actor

Choose `struct` when:

- values should copy independently
- equality/snapshot semantics make sense
- there is no shared mutable identity

Choose `class` when:

- identity matters across references
- object lifetime/deinitialization is meaningful
- framework inheritance/reference semantics require it

Choose `actor` when:

- shared mutable state crosses concurrent callers
- serialization/isolation is part of the abstraction

Do not choose actor merely because a type has async methods.

## Enums

Prefer enums for finite state machines and mutually exclusive states.

Good:

```swift
enum LoadState<Value> {
    case idle
    case loading
    case loaded(Value)
    case failed(AppError)
}
```

Avoid multiple booleans such as `isLoading`, `hasLoaded`, `didFail`, `isEmpty` when combinations can contradict one another.

## Identity

- Make identifiers stable across rendering/persistence boundaries.
- Do not use changing display data as list identity.
- Distinguish entity identity from current value equality.

## Ownership

For every retained reference, be able to answer:

- who owns it?
- who may outlive whom?
- who tears down observers/tasks/resources?
- is a cycle possible?

Use weak references only to encode actual non-ownership.

## Protocols

Create protocols for:

- meaningful substitutable capabilities
- stable boundaries to external systems
- cross-module contracts
- behavior with multiple real implementations

Do not create a protocol just to make every concrete type mockable. Often a closure, value, generic, or small boundary interface is simpler.
