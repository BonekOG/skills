# Migration and Transactions

Use this reference for batch data changes, one-time migrations, and any code that commits.

## Shape of a migration

A migration is a small program with a lifecycle:

1. **Select.** Read the source rows with explicit filters and a stable key order.
2. **Validate.** Check required values, relations, ranges, and duplicates before writing.
3. **Transform.** Apply the mapping explicitly, including empty dates, option values, and text trimming.
4. **Write.** Insert or modify in batches, with a deliberate trigger decision and a commit boundary.
5. **Log.** Record one row per failure with the source key and the reason.
6. **Reconcile.** Compare counts and control totals between source and target.
7. **Restart.** Make the next run skip completed work.

## Control flow and progress

- A processing-only report or a codeunit with a confirming entry point is the usual shape. The report variant gives the user a request page and progress; the codeunit variant is easier to test.
- Do not start a long migration from a trigger. Run it from a report, a job, or an explicit action.
- Show progress for long runs, and make the run interruptible only if the interruption is handled as a controlled stop rather than a half-written batch.

## Commits

- `COMMIT` ends the transaction. Everything written before it is durable; a later error cannot roll it back.
- Commit per batch, not per record, unless the record count is small. Per-record commits are slow; one commit at the end risks a long lock and a large rollback.
- After a commit, the restart marker must already be durable, or a crash reprocesses records that were already written.
- Never commit inside a loop that also relies on rollback for correctness.

## Restartability and idempotency

- Use a processed flag, a marker table, or a processed range. The marker must be written in the same transaction as the data it describes, or before the commit that makes the data durable.
- Make each record's transformation idempotent where possible: writing the same computed value twice must not duplicate or double-count.
- Test the second run. It must either do nothing or produce the same result. A migration that appends on every run is a defect, even if the first run looked correct.

## Triggers during migration

- `VALIDATE` runs the field's validation trigger. Direct assignment does not.
- `INSERT(TRUE)` and `MODIFY(TRUE)` run table triggers. The non-true forms skip them.
- Skipping triggers is sometimes necessary for a bulk load, but it also skips the invariants those triggers enforce. If you skip them, validate explicitly and document why.
- Validation triggers may themselves write to other tables or set defaults. A bulk load that runs them can be much slower, and can also cascade into flows the migration did not intend.

## Locking and concurrency

- `LOCKTABLE` and update locks in `FINDSET` change how other sessions can read and write. Use them when a read-then-write sequence must be atomic.
- Long transactions hold locks. Batch size, commit frequency, and index usage determine whether the migration blocks users.
- Deadlocks are a symptom of inconsistent access order or long transactions, not a reason to retry blindly. See [sql-interoperability.md](sql-interoperability.md).

## Error handling

- C/AL has no exception handling. A failed record aborts the codeunit run unless you structure the write so failures are detectable.
- Write the failure to a log table with the source key, the field, the value, and the reason, then continue with the next record if the business allows it.
- At the end, report the number of successes, failures, and skipped records. A migration that reports only "done" is not verifiable.
- Do not swallow a failure to keep the batch moving unless the log makes the loss visible and the owner accepts it.

## Reconciliation

- Compare record counts, key ranges, and control totals between source and target.
- Check a sample of transformed records by hand, including edge cases: blank dates, zero amounts, maximum text lengths, and duplicate keys.
- Reconcile after the final commit, not only after the dry run.

## Before running on real data

- Run on a restored copy with realistic volume.
- Measure duration and lock impact, and choose the maintenance window from the measurement.
- Have a tested restore path. "We can restore the backup" is only credible if the restore was rehearsed.
- Record the exact version, company, and date of the run in the change documentation.
