# Reports, Layouts, and Report Selection

Use this reference when creating, copying, extending, or diagnosing a report.

## The dataset is a contract

- A report's dataset defines the columns and their types. The layout consumes those names. Renaming a column without updating the layout breaks the report at runtime, not at compile time.
- Keep column names stable once a layout or an external consumer depends on them. Change the caption when only the label should change.
- Filters belong in the data items, not in code that loads everything and discards rows. A report that reads the whole table is a performance incident waiting for volume.
- `DataItemLink` and `DataItemLinkReference` define the header-to-line relation. A wrong link produces plausible but incorrect totals, which is worse than an error.
- Request filter fields determine what the user can filter on the request page. They also shape the query; include the fields users actually filter by.

## Creating a report

- Allocate the report ID from `idRanges`. Do not copy an ID from an example.
- Name the report within the 30-character limit and write a caption that matches what the report is for.
- Decide the rendering path: RDLC, Word, or Excel layout, or no layout for a processing-only report. A processing-only report must not pretend to have a printable layout.
- Set `UseRequestPage` deliberately. A report that needs parameters but skips the request page fails in batch.
- Add the report to a permission set. A report that users cannot run is not delivered.

## Copying a base report

Copying is the usual starting point for a customized printout. Do the whole set of changes together:

1. New object ID and a new name within the length limit.
2. New caption and description that state the difference from the base report.
3. Layout file copied under a new name, with the report's layout property pointing at the new file.
4. Every reference to the old report ID updated: report selection entries, menus, navigation, code that runs the report, and tests.
5. Permission sets extended for the new report.
6. The copied layout checked for hard-coded company names, logos, and old captions.

Removing the base report from report selection is a separate decision. Leaving both active creates two ways to print the same document with different results.

## Report extensions

- A report extension adds columns or triggers to an existing report. It cannot ship its own layout, so the base layout must be able to consume the added column, or the print output ignores it.
- Keep extension column names distinct from base columns.
- Do not use a report extension to change the meaning of an existing column; add a column and let the layout choose.

## Report selection

- Report selection decides which report runs for a standard usage, such as printing a sales invoice. Add entries only when the requirement is genuinely "this document should print with this report by default".
- Report selection is per company. A customization that works in the development company may not be active in the next one.
- The usage values are version-specific enums. Read them from the symbols or the page; do not copy numeric values or names from an older example.
- Check for an existing entry before adding one. Duplicate or conflicting entries produce unpredictable output.
- Removing a report selection entry changes what users print. Treat it as a functional change and tell the users.

## Layouts

- The layout file path is part of the report definition. Moving or renaming the file without updating the property breaks publishing or runtime.
- RDLC layouts are not generated from the dataset. Every added or renamed column needs a layout change in the designer.
- Test with realistic text lengths and translated captions. Layouts that fit English labels often clip German ones.
- Check page breaks, totals, and the empty-result case. A report with no rows must still render a usable page.

## Diagnosing a broken report

1. Does it compile? A dataset error is caught at build time.
2. Does it run with the request page, and with the filters the user used?
3. Are the totals wrong or missing? Check the data item links and the filters before the layout.
4. Does it render? Check the layout path, the layout name inside the file, and whether the layout references a column that no longer exists.
5. Is it slow? Inspect the generated query, the keys used, and whether the report calculates flowfields per row.

## Review cues

- A copied report that still points at the original layout file, or a layout that still carries the old report name.
- A dataset change without a layout change.
- Report selection added with values copied from another version.
- A processing-only report with a layout, or a printable report that skips the request page.
- Missing permission entries for the new report.
