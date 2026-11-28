# Upgrades and Data Migrations

Use this reference when a change adds, removes, or alters stored data, when an app version must be upgraded in place, or when data must be migrated into a new structure.

## Upgrade codeunits

- An upgrade codeunit sets `SubType = Upgrade` and implements the upgrade triggers. The per-company triggers run once per company; the per-database triggers run once for the database.
- Upgrade code runs in the context of the upgrade, not in a normal user session. Do not expect UI, user interaction, or a particular company to be current unless the trigger says so.
- The order in which several upgrade codeunits run is not guaranteed. Each codeunit must be correct on its own; combining everything into one large codeunit is a style choice, not a requirement.
- Guard each step with an upgrade tag so a rerun skips completed work. Without a tag, a partially completed upgrade either repeats side effects or stops halfway with no record of where it got to.
- Preconditions belong in the check triggers. Failing a precondition gives a clear reason instead of a half-applied upgrade.

## Companies and scope

- Per-company upgrade code does not run for a company created after the upgrade. New companies need initialization through installation code or the company-initialization path, and that path needs its own test on a fresh company.
- Shared tables (`DataPerCompany = false`) are not per-company data. A per-company trigger that writes shared data runs once per company and multiplies the effect.
- Company-specific setup, number series, and dimension defaults often differ. A migration that hard-codes values from the development company fails in the next one.

## When upgrade code does not run

- Data restored from a backup, migrated by database tools, or imported outside the application runtime never executes upgrade codeunits. Those paths need a separate migration procedure with its own verification.
- Reinstalling an app or removing and re-adding it is not an upgrade. Check what the operation actually does before assuming tags or versions were handled.

## Schema changes as migrations

- Adding a nullable field is cheap. Adding a required field, changing a type, or removing a field requires data preparation and a rollback plan.
- Type changes need an explicit conversion: create the new field, migrate values, validate, switch readers, then deprecate the old field.
- Key changes require duplicate checks and an estimate of the lock time on large tables.
- After the structure changes, existing rows must satisfy the new constraints. Test against a copy of realistic data, not an empty company.

## Data migration patterns

A migration is a small program with a lifecycle, not a one-off script.

1. **Stage.** Copy source data into a staging table, or read it with a documented query. Keep the source untouched until reconciliation passes.
2. **Validate.** Check required values, relations, ranges, and duplicates before writing into the target.
3. **Transform.** Apply mapping rules explicitly: enum mapping, unit conversion, date normalization, text trimming.
4. **Write.** Insert or update in batches with a defined commit boundary.
5. **Log.** Record one row per failed source record with the reason and the source key.
6. **Reconcile.** Compare counts and control totals between source and target.
7. **Rerun.** Make the procedure restartable: a marker table, an upgrade tag, or a processed flag.

- A dry-run mode that reports what would change is worth the extra parameter. Run it before the real pass.
- Batch size and commit frequency trade throughput against restart cost and lock duration. Choose them from the data volume and the maintenance window.
- Never silently skip a failed record. Either fail the migration with a summary or log it and report the count and the cause.
- Test the migration twice in a row. The second run must either do nothing or produce the same result.

## Deprecation

- Mark objects and fields obsolete with a reason and a tag, and state which release removes them. Consumers need a migration window.
- Remove obsolete artifacts only after the window and after confirming that no installed extension or integration still reads them.
- Keep the old name available while external consumers may still reference it; a breaking rename is a new contract.

## Rollback

- Extension upgrades are not automatically reversible. Before an upgrade, capture the current app version, the data backup, and the steps to reinstall the previous version.
- Data migrations that overwrite values need a backup of the affected columns or a reversible mapping. "We can restore the database" is only credible if the restore was tested.

## Review cues

- An upgrade step without a tag or a restart marker.
- A per-company trigger writing to a shared table.
- A required field or type change with no data preparation.
- A migration without reconciliation totals.
- A rerun that duplicates records.
- An upgrade plan that assumes fresh companies were covered.
