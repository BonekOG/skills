# Schema, Keys, and TransferFields

Use this reference before changing a table's structure, adding keys, or copying field values between records.

## Keys

- The primary key is the identity of a row. Do not change it. A new primary key changes storage order, every existing relation, and the meaning of every stored reference.
- Secondary keys support lookups, sorting, and range filters. Adding one changes write cost and storage; on a busy table it is a performance decision, not a formality.
- Unique keys enforce a business rule at the database level. Adding one to a table that already contains duplicates fails, and the failure appears during synchronization or at the next write.
- `Clustered` keys only matter on SQL-backed deployments, but they affect every query on that table. Treat a clustering change as a DBA-level decision.
- Keys declared in a table extension may only contain fields the extension defines on older runtimes. Keys that combine base-table and extension fields are only allowed from Business Central 2026 release wave 2 with runtime 18 and later. Check the target version before designing such a key.
- `SumIndexFields` maintain a SIFT index for sums. They speed up specific totals and cost on every write. Add them from a measured need, not by habit.

## Field properties that change behavior

- `DataClassification` is mandatory on new fields and is part of privacy review. Classify by content, not by convenience.
- `FieldClass` decides whether a field is stored, calculated (`FlowField`), or a filter (`FlowFilter`). A field cannot be both stored and calculated.
- `Editable = false` prevents user edits, not code writes. It is not a validation rule and it does not protect the value from flowfields or integrations.
- `NotBlank` is enforced on insert and on validation. Adding it to an existing table requires a data cleanup plan.
- `TableRelation` drives the lookup and, with `ValidateTableRelation = true`, validates the entered value. A relation with a filter expression must match the lookup the users expect.
- `InitValue` only applies when a record is initialized. It does not backfill existing rows.

## CalcFormula

A flowfield needs a formula, for example a sum over a related table filtered by the current record:

```al
field(90; "Open Amount"; Decimal)
{
    FieldClass = FlowField;
    CalcFormula = sum("Cust. Ledger Entry".Amount where("Customer No." = field("No."), Open = const(true)));
}
```

- The filter inside the formula defines what is summed or counted. Get the relation right before worrying about performance.
- `CalcFields` computes one flowfield; a page that shows five flowfields needs all five calculated or they display stale values.
- FlowFilters referenced by the formula must be set before the calculation and reset afterwards when they should not persist.

## TransferFields

`TransferFields` copies matching fields from a source record into a target record.

- Fields are matched by field number, not by position or caption. Two fields with the same number but incompatible types fail at runtime.
- The operation does not run `OnValidate` triggers. Any derived value that a validation trigger would set must be recalculated explicitly.
- Flowfields and fields outside the shared field set are not transferred.
- The second parameter controls whether the target's primary key is initialized from the source. Copying a document usually keeps the target's own number, so choose deliberately.
- Copying a document with `TransferFields` is a starting point, not a complete implementation: line records, totals, dimensions, and status transitions still need explicit handling.
- When only a few fields should move, assign them explicitly. A blanket transfer silently picks up new fields added later by the platform.

## Schema changes and synchronization

- Adding a field is usually safe. Removing one, changing its type, or making it required is a migration.
- Rename a field by name only when the stored data should follow it; the field number is the storage identity. If the rename is cosmetic, change the caption instead.
- Deprecate before deleting: mark the object or field obsolete with a reason and tag, keep it for the agreed period, and only then remove it in a later release.
- `ForceSync` is a parameter of synchronization operations, not an `app.json` setting. It forces a full schema synchronization, can be slow, and can fail on data that violates new constraints. It is not a fix for a schema error and needs explicit authorization on a live environment.
- After a schema change, verify existing rows, not only new ones: defaults, required values, and key uniqueness all surface on existing data first.

## Review cues

- A changed primary key, or a new key that duplicates an existing one.
- A unique key added without checking for duplicate rows.
- A key mixing base and extension fields on a runtime that does not allow it.
- A new field without `DataClassification`, or with the wrong one.
- A `TransferFields` call that assumes validation triggers ran.
- A flowfield added to a list page without a filter or a calculation plan.
- A schema fix proposed as "run a full sync".
