# SQL Interoperability

Use this reference when a C/AL problem crosses into SQL Server: naming, diagnostics, deadlocks, or direct queries.

## What the SQL layer looks like

- Each company's tables are stored with the company name as a prefix, separated by a dollar sign. A table named `Customer` in company "CRONUS" is `CRONUS$Customer`. Company names with spaces or special characters need quoting or bracketing.
- Field names become column names with characters that SQL does not accept replaced. Dots and percent signs, for example, are normalized in the column name. Do not assume the SQL column name equals the C/AL field name.
- Flowfields are not columns. They are computed from the flowfield definition at read time, so they never appear in a table's column list.
- SIFT totals are maintained in separate index structures. A query against the base table does not see them.
- The empty date is stored as 1753-01-01, the empty time as midnight. A SQL query that filters on NULL for a blank date finds nothing.

## Reading the database

- Read-only diagnostics are useful: row counts, orphan checks, duplicate keys, values that violate a business rule.
- Treat SQL as an observation tool. The application's triggers, validation, and derived data are not applied to a direct write.
- A direct update bypasses triggers, skips SIFT maintenance, and can leave references inconsistent. Even a "simple" correction can corrupt a flowfield total or a dimension.
- If a direct write is unavoidable, scope it to the exact rows, record the before and after values, and have the application owner confirm the repair.

## Indexes and keys

- Keys belong in the object definition. An index created only in SQL Server disappears on a schema synchronization or a table rebuild, and it is invisible to the application's own key selection.
- Adding a key to a large table takes time and locks. Plan it like a migration.
- Clustered index choices affect every query on the table. On an existing installation, changing clustering is a database-level decision.

## Deadlocks

- A deadlock means two sessions acquired locks in opposite order, or one session held locks long enough for the other to time out.
- Diagnose with the lock resources, the statements involved, and the access order. A retry loop hides the problem and makes the log noisy.
- Fixes that work: consistent key order across code paths, shorter transactions, committing between batches, and filtering on indexed fields.
- Fixes that do not work: raising the timeout, retrying indefinitely, or adding a global lock.

## Query behavior

- Collation decides case and accent sensitivity. A comparison that works in the development database can behave differently after a restore into another collation.
- `WITH (NOLOCK)` reads uncommitted data. It is acceptable for a diagnostic count, not for a value that drives a correction.
- Parameterized ad-hoc queries from an external tool are fine for analysis. Embedding SQL in application code couples the solution to the database layout and blocks a later move to a managed service.

## Company copies and restores

- Restoring a company or a database carries its collation, its object metadata, and its encryption keys. A restore into a different environment is not the same as a migration.
- Compare row counts and control totals after a copy before drawing conclusions from a test run.
- A company copy used for migration rehearsal must include the same customizations and the same data volume class as production, or the timing evidence is misleading.

## Review cues

- A SQL fix proposed as the solution to an application defect.
- An index added in SQL to make one query faster.
- `WITH (NOLOCK)` used in logic that decides what to correct.
- A deadlock handled only by retrying.
- A query that assumes a blank date is NULL.
