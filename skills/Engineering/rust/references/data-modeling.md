# Data modeling

## Make invalid states unrepresentable

Prefer:

```rust
enum ConnectionState {
    Disconnected,
    Connecting { started_at: Instant },
    Connected { session: Session },
}
```

over:

```rust
struct Connection {
    connected: bool,
    connecting: bool,
    session: Option<Session>,
}
```

where contradictory states can coexist.

## Newtypes

Use newtypes for:

- IDs from different domains;
- units (`Meters`, `Milliseconds`);
- validated strings;
- money/currency values;
- security-sensitive tokens;
- opaque handles.

Benefits:

- prevents accidental mixing;
- centralizes validation;
- improves API intent;
- enables domain-specific trait implementations.

## Constructors and validation

- If construction can fail, return `Result<Self, E>`.
- If a type can only exist when valid, keep fields private and validate in constructors.
- Use smart constructors for validated invariants.
- Avoid public fields on invariant-heavy types.
- Consider `NonZero*`, bounded wrappers, or enums when they encode constraints naturally.

## Booleans

Boolean parameters are often a smell when the call site loses meaning:

```rust
render(data, true, false)
```

Prefer an enum/options type:

```rust
render(data, RenderMode::Compact, CachePolicy::Bypass)
```

Booleans remain fine for obvious local state or predicates.

## Typestate

Use typestate when:

- invalid operation ordering is a significant source of bugs;
- states are few and transitions are stable;
- compile-time enforcement materially improves safety.

Avoid typestate when:

- state is highly dynamic;
- it explodes generic complexity;
- callers need runtime state inspection more than compile-time sequencing.

## Derives

Derive traits intentionally:

- `Debug`: usually yes for internal/domain types.
- `Clone`: only if semantic duplication is valid.
- `Copy`: only for small, trivially copyable value types where implicit duplication is unsurprising.
- `Eq`/`Hash`: only when equality/hash semantics are stable and meaningful.
- `Default`: only when a genuine unsurprising default exists.

Do not derive traits merely because they are convenient.
