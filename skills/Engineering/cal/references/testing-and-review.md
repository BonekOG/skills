# Testing and Review

Use this reference to verify a C/AL change and to review an object diff against its baseline.

## Test codeunits

- A test codeunit uses `SubType = Test` and the project's test runner. Test functions follow the runner's discovery convention on that NAV version; check the project's existing tests rather than inventing a pattern.
- Arrange, act, assert. Create the records the test needs; do not inherit them from a previous test or from the development company.
- Use the test library codeunits available in the environment for assertions, random values, and sales or purchase setup. Confirm the library version before depending on a function.
- Temporary records keep a test fast and leave no data behind, but they do not exercise storage, locking, or triggers the same way. Use persisted records when the contract is about what lands in the database.
- A test that commits must clean up, or it fails on the second run.

## What to test

- Posting and calculation results: amounts, VAT, dimensions, and status changes.
- Validation rules, including the negative cases and the order in which triggers fire.
- Number series and document flows: create, release, post, reopen.
- Batch jobs and migrations: first run, second run, failure handling, reconciliation totals.
- Permission behavior: a role can do its job and cannot do a forbidden action.
- Reports: filters, totals, and the empty result. Layout is a visual check.

## What not to test

- Platform behavior that Microsoft owns.
- Exact auto-generated document numbers, unless the numbering rule is the contract.
- The wording of a message, unless the wording is contractual.
- Which private function was called.

## Verification sequence for a change

1. Diff the edited object against the baseline export. Read the diff, not only the summary.
2. Confirm the encoding, line endings, and non-ASCII characters match the baseline wherever the change did not intend otherwise.
3. Import into a development database and compile the object.
4. Compile the dependent objects; a changed table or codeunit signature can break callers.
5. Exercise the changed flow with realistic data, including the empty and error cases.
6. Run the project's tests, or state that none exist and describe the manual scenarios.
7. Export the new state and keep it as the next baseline.

## Review checklist

- Encoding and line endings preserved; no new question marks where letters belong.
- Comments only in code bodies, not in field, key, control, variable, or text constant blocks.
- Function and variable IDs unique within the object.
- Object ID and name inside the project's range and naming convention.
- Triggers cover insert, modify, delete, and rename where the behavior requires it.
- `MODIFY(TRUE)`, `INSERT(TRUE)`, and `VALIDATE` used deliberately, not by habit.
- Filters set before reads, and the record positioned before its fields are used.
- Date ranges handle `0D`, and empty dates are not compared as numbers.
- No `AND` or `OR` whose second operand assumes the first succeeded.
- Text assignments cannot exceed the field length.
- Transaction boundaries and commits are deliberate, and a failure cannot leave half-written data.
- Permissions and menu entries exist for anything new that a user must reach.
- No debug messages, commented-out code, or temporary file paths left behind.
- Object metadata (modified flag, version list) updated per project convention, and only where the project requires it.

## Comparing exports

- Compare per object, not as one large file, so the review names the objects that changed.
- Compare the baseline and the new export in the same encoding. A diff tool that decodes differently produces false changes.
- Object order in a combined export is not meaningful; do not treat a reordered file as a change.
