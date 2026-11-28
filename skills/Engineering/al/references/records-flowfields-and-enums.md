# Records, FlowFields, and Enums

Use this reference for record access, filtering, partial records, calculated fields, enums, media, and generic record handling.

## Finding records

- `Get` retrieves by primary key and throws when the record does not exist. `GetBySystemId` does the same by system ID.
- `FindFirst`, `FindLast`, and `FindSet` position a record set. `FindSet` reads the whole set lazily; the filters and key determine what "the set" means.
- `IsEmpty` is the cheap existence check when you do not need the record contents.
- `Reset` clears filters and resets the key; it is not a rollback. Decide deliberately whether the next operation should inherit filters.
- `SetCurrentKey` and `SetAscending` change iteration order, not the filter. Sorting on a non-indexed field can be expensive on large tables.

## Filters

- Filters are applied when the record is read, not when they are set. Setting a filter does not position the record; you still need `Get` or a find call.
- `SetRange` sets a value range, `SetFilter` sets a filter expression. Both accept an empty value to clear that field's filter.
- Date filters interact with the empty date `0D`. A range like `01/01/24..31/12/24` excludes records with no date; include `0D` explicitly when blank dates are legitimate.
- FlowFilters are set like normal fields but only affect `CalcFields` and flowfield reads. Reset them when they should not leak into the next calculation.

## Partial records

- `SetLoadFields` limits which fields are read. Call it before the read operation, and include every field the code later reads or writes.
- A field that was not loaded does not load on access; it returns its default value. This is the main source of "the field is suddenly empty" defects.
- `AddLoadFields` adds fields to an existing selection without discarding it. `SetBaseLoadFields` covers base-table fields when the load set was declared in an extension context; confirm its exact effect in the docs for your runtime before relying on it.
- Do not use partial records for inserts, deletes, renames, `TransferFields`, or copies into temporary records. Those operations need the full record.
- `Modify` on a partial record writes the loaded fields; fields outside the load set keep their stored values. Confirm this against the runtime documentation before using partial records in a write path, and test the resulting row.
- There is no universal "fewer than five records" rule. Load fields when the read pattern and the measured cost justify it, and keep the load set correct.

## FlowFields

- A flowfield is calculated from its `CalcFormula` (sum, count, exist, lookup, min, max, average). Reading it without calculating returns the last calculated value, often zero.
- `CalcFields` computes the named flowfield for the current record. Call it after the filters and FlowFilters are set.
- Calculating a flowfield over a large set runs a query per record. Filter first, calculate only what is displayed, and prefer a set-based query when a total is all that is needed.
- A SIFT-maintained total is a performance tool for sums over indexed fields, not a substitute for a correctly defined flowfield.
- Flowfields are read-only. Do not try to assign one; change the underlying data or the formula.

## Enums

- Define new choice lists as `enum` objects, with an explicit value ID for each member. The ID is stable; the caption is translatable.
- Extend an enum only when it is marked extensible, and add values through an `enumextension`. Adding values to a non-extensible enum is not an option.
- Reference values by name, for example `Enum::"My Enum"::"My Value"`. Never write the numeric value, and never copy numeric values from a legacy `Option` field.
- Table fields typed as an enum store the enum value, not an arbitrary integer. Do not compare a field against a raw number.
- When converting a legacy `Option` field, map each option explicitly to an enum value and verify the persisted data, because the ordinal mapping is not guaranteed to match.

## Records, references, and media

- `RecordRef` and `FieldRef` enable generic code over table and field numbers. Use them when the table is genuinely dynamic; otherwise a typed record is safer and faster.
- `FieldRef.Value` and `FieldRef.Validate` bypass compile-time typing. Confirm the field type and range before writing through them.
- `Media` and `MediaSet` hold images; `Blob` holds arbitrary binary data. Use streams and `TempBlob` for processing instead of loading whole blobs into memory.
- `InStream` and `OutStream` are single-use in the direction they were created; do not reuse one for a second read without rewinding.

## Validation and writes

- Assigning a field does not run its validation trigger. Call `Validate` when the business rule must run.
- `TestField` throws when the value is empty or does not match; it is a guard, not a user-facing validation flow.
- `Insert(true)` and `Modify(true)` run the table triggers. `Insert(false)` and `Modify(false)` skip them; use the skipping form only when you can justify why the triggers must not run.
- `Init` sets defaults; it does not clear an existing record's data unless the platform says so for that operation.
- `LockTable` changes concurrency behavior and is not a general substitute for a correct transaction design. Use it deliberately, and check its behavior on the deployment model.
