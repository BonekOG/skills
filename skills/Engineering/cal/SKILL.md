---
name: cal
description: Use when maintaining, reviewing, debugging, or modernizing Microsoft Dynamics NAV C/AL objects and classic customizations, especially .txt or .fob object exports, C/AL codeunits, and legacy data migrations.
disable-model-invocation: false
---

# C/AL Engineering

Work safely inside a legacy Dynamics NAV codebase: change objects in place, keep the export format and encoding intact, preserve behavior that the business depends on, and leave a path toward AL. C/AL is version-bound and runs on an older runtime, so the platform's exact behavior matters more than general programming intuition.

The user's request takes precedence over these recommendations. An explicit authorization boundary for importing objects, compiling in a live database, or running a data migration still applies.

## 1. Select the operating mode

| Mode          | Use when                                                                  | Start with                                                                                |
| ------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| **ANALYZE**   | Understanding an object, a posting flow, or an undocumented customization | [object-workflow.md](references/object-workflow.md), then semantics                       |
| **CHANGE**    | Fixing or extending an existing C/AL object                               | Object workflow plus the reference for the touched area                                   |
| **MIGRATE**   | Moving or transforming data, or running a batch update                    | [migration-and-transactions.md](references/migration-and-transactions.md)                 |
| **REVIEW**    | Reviewing a diff, export, or change request                               | [testing-and-review.md](references/testing-and-review.md)                                 |
| **MODERNIZE** | Preparing or executing a move to AL                                       | [project-workflow-and-modernization.md](references/project-workflow-and-modernization.md) |
| **DOCUMENT**  | Capturing what was learned about legacy behavior                          | [knowledge-capture.md](references/knowledge-capture.md)                                   |

Reading objects is not authorization to import them. Importing and compiling against a live database is a separate step.

## 2. Load focused guidance

Read only the references the task needs:

- Object structure, triggers, properties, function numbering, and editing flow: [object-workflow.md](references/object-workflow.md).
- Encoding, line endings, export formats, and verifying an edit: [encoding-and-editing.md](references/encoding-and-editing.md).
- Expression evaluation, filters, dates, records, strings, and legacy types: [cal-semantics.md](references/cal-semantics.md).
- Batch migrations, commits, restartability, locking, and reconciliation: [migration-and-transactions.md](references/migration-and-transactions.md).
- Company prefixes, column names, flowfields, and deadlocks in the SQL layer: [sql-interoperability.md](references/sql-interoperability.md).
- Test codeunits, review checklist, and comparison against a baseline: [testing-and-review.md](references/testing-and-review.md).
- The project method and the modernization path to AL: [project-workflow-and-modernization.md](references/project-workflow-and-modernization.md).
- Recording findings about undocumented behavior without turning guesses into rules: [knowledge-capture.md](references/knowledge-capture.md).

This skill ships no runnable scripts. The splitting and validation scripts found in the source material were tied to one project's folder layout, assumed a particular encoding, and in places deleted directories. If a project needs an object splitter, write a generic one there with explicit input, explicit encoding, a dry run, collision checks, and no recursive deletion.

## 3. Reconnaissance before editing

1. NAV version, build, and cumulative update. Behavior differs between releases, and a fix that works on one build may not exist on another.
2. Export format: a single `.txt` with many objects, per-object files, or a `.fob`. The format decides how a change is applied and how a diff is reviewed.
3. The export encoding and line endings, measured on the baseline file rather than assumed from a tool's default.
4. The database and company the objects belong to, the SQL Server collation, and whether the deployment is on-premises or hosted.
5. Add-ins, automation objects, and file system dependencies, since these constrain any later move to AL.
6. The project's compile gate and object import procedure, and whether a failing compile blocks delivery.
7. Existing conventions: object IDs, prefixes, function numbering, comment style, and how object metadata is maintained.

## 4. Operating invariants

- Export and keep a baseline of every object you touch before editing. A textual diff against that baseline is the only reliable review of a C/AL change.
- Determine the encoding per export and preserve it. Do not normalize the whole file to a different code page or to Unix line endings.
- Comments are allowed inside trigger and procedure bodies, not in `FIELDS`, `CONTROLS`, `KEYS`, `VAR`, or text constant blocks. A comment in the wrong section corrupts the object on import.
- C/AL evaluates both operands of `AND` and `OR`. A guard like "if the record exists and then read it" does not protect the second operand.
- Setting a filter does not position a record. Read it with `GET` or a `FIND` before using field values.
- `0D` is the empty date and is stored as 1753-01-01 on SQL Server. It is not NULL, and date ranges that omit it exclude blank dates.
- Function IDs are allocated per object. Search the object before assigning a new one.
- Object IDs, prefixes, and ranges come from the project's register, never from an example.
- A change to a base object is a permanent fork from the vendor's code. Record why it was necessary.

## 5. Validation before finishing

Compile the changed objects in a development database and compare the result against the baseline export. A clean import proves the object text parses; confirm the behavior the change affects:

- the objects import and compile on the same NAV build as the target environment;
- a textual diff against the baseline shows only the intended changes, with encoding and line endings unchanged;
- the touched triggers and procedures were exercised in a test company with representative data;
- posting, journal, and batch flows that read the changed tables still produce the same results;
- any data change was reconciled by counts or totals before it was applied to a live company.

Report which objects were imported, which build they were compiled on, which company was used, and what was verified manually.

## 6. Reporting

State the objects and functions changed, the encoding and line endings of the export, the compile result, the data impact, and anything unverified. If a needed reference was not available in the source material, say so instead of presenting an assumption as established behavior.
