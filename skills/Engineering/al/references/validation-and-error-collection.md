# Validation and Error Collection

Use this reference when a change adds validation, reports multiple problems to the user, or sends diagnostics.

## Error messages

- Say what failed, which value caused it, and what the user can do. "Invalid entry" is not an error message; "The customer number 4711 does not exist in this company" is.
- Put the text in a label with a comment and, when it is contractual, `Locked = true`.
- Do not expose stack traces, table names, or internal identifiers in a user-facing message. Put technical detail in a diagnostic message or telemetry.
- Use `ErrorInfo` when the error needs structure: a message, a detailed message, a stable code, and custom dimensions.

## Structured errors

```al
var
    PostingDateError: ErrorInfo;
begin
    PostingDateError.Message := 'The posting date is outside the allowed period.';
    PostingDateError.DetailedMessage := 'Change the document date or contact accounting.';
    PostingDateError.Code := 'POSTING-DATE-PERIOD';
    PostingDateError.Collectible := true;
    Error(PostingDateError);
end;
```

- The stable code identifies the condition across releases and translations. Do not use the translated text as the identifier.
- Use `Verbosity` for warnings and diagnostic messages; reserve the error level for conditions that stop the operation.
- Keep custom dimensions free of personal data.

## Collecting several problems

- A validation pass over many rows should report all problems, not only the first. Use `ErrorBehavior::Collect` when running the validation codeunit, and mark the individual errors as collectible.
- `HasCollectedErrors`, `GetCollectedErrors`, and `ClearCollectedErrors` inspect and clear the collected set. Clearing the list does not undo data changes.
- Validate everything first, check whether anything was collected, and only then write. A write followed by "and here are the errors" leaves inconsistent data.
- Confirm rollback behavior against the documentation for the runtime in use. Do not assume a collected error left the database untouched.
- `TestField` and `FieldError` throw immediately. They are useful for a single hard precondition, not for a batch that should list every problem.

## Where validation belongs

- Table triggers enforce invariants that must hold regardless of the entry point: imports, APIs, jobs, and pages.
- Page triggers handle what only makes sense while a user is entering data: lookups, defaults, and immediate feedback.
- Codeunits own multi-step business rules and should be callable from a page, a job, or a test.
- Do not duplicate the same rule in three places. Choose the lowest layer that every caller goes through, and call the shared procedure from the others.

## Transactions and commits

- `Commit` ends the current transaction. Everything written before the commit survives a later error; everything after it does not.
- In SaaS, commits are restricted to specific contexts such as upgrade code. Committing inside a normal business transaction is rarely correct and should be justified.
- Validation should not require a commit to work. If it does, the design is hiding a transaction problem.

## Confirmations and warnings

- `Confirm` returns a Boolean and is suitable for "continue despite this warning". It is not a validation mechanism; a user who clicks yes defeats it.
- `Message` is for information, not for reporting failures.
- Do not use dialogs in code that may run in a job, an API call, or an upgrade. Check the execution context first.

## Telemetry

- `Session.LogMessage` emits a structured event. Use a stable event ID, a meaningful message, and dimensions that make the event queryable.
- Follow the project's ID allocation for telemetry. Do not invent an ID that collides with another component.
- Log outcomes that operations need: failures, retries, and volume. Do not log every row.
- Never log personal data, credentials, or full record payloads.

## Review cues

- A loop that throws on the first bad row, so the user fixes them one at a time.
- Collected errors followed by writes before checking the collection.
- An error message assembled from concatenated text instead of a label.
- A stable error code that is actually the translated message.
- A commit inside a validation pass.
- Telemetry containing personal data or an unstable event ID.
