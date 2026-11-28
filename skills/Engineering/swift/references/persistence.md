# Swift Persistence

## Choose storage by semantics

- UserDefaults: small user preferences/settings, not secrets or primary domain databases.
- Files: documents/blobs/exportable content with explicit file ownership.
- SwiftData/Core Data: relational/object persistence, queries, migrations, offline state.
- Keychain: credentials/secrets, not general app data.

## Boundaries

Do not let persistence framework model details leak through every feature unless the app deliberately uses an active-record style. For larger domains, map persisted representations to stable domain types where it reduces coupling.

## Migrations

Treat schema changes as production data migrations, not compile-only changes.

Before shipping:

- determine whether existing stores can migrate
- test upgrade from representative old schemas/data
- define rollback/recovery expectations
- avoid destructive reset as a default production strategy

## Concurrency

Respect the persistence framework's context/model isolation rules. Do not pass non-Sendable managed objects across isolation domains casually. Pass identifiers or immutable snapshots where appropriate.

## Transactions and integrity

Group changes that must succeed/fail together. Define uniqueness/conflict behavior explicitly. Validate invariants at the domain boundary, not only in UI forms.

## Caching

A cache is not automatically a source of truth. Define expiration, invalidation, corruption behavior, and whether stale data is acceptable.
