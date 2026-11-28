# Code Style and Object Design

Use this reference when choosing objects, naming them, allocating IDs, shaping pages and codeunits, or reviewing AL style.

## Names and identifiers

- The compiler rejects object names longer than 30 characters (AL0305). Compose the project affix and the descriptive part against that budget before you start, not after the first compile.
- Permission set objects that can be assigned to users are limited to 20 characters. Permission sets generated from a longer name need a deliberately shortened name.
- Follow the app's existing affix and object-number convention. A prefix or suffix, and a block of object IDs per functional area, are project decisions. Do not present one customer's prefix or ranges as a general AL rule.
- Object IDs, field IDs, control IDs, and enum value IDs come from `idRanges` in `app.json` and from the app's allocation record. Never take them from a blog post, a sample repository, or another app's manifest.
- Do not reuse the ID of a deleted object. Upgrade code, report selection entries, permission sets, and external integrations may still reference it.
- Table and field names are developer-facing; captions are user-facing. Give both, and keep the caption in a label so it can be translated.
- Do not rename a published field or object to fix a wording problem. Change the caption; a name change is a compatibility decision.

## Choosing the object type

| Need                                   | Object                                                   |
| -------------------------------------- | -------------------------------------------------------- |
| A new business entity                  | New table, page, and permission entries                  |
| Extra fields or logic on a base entity | `tableextension`, `pageextension`, and event subscribers |
| Extra values on a base enum            | `enumextension`, only when the base enum is extensible   |
| A new choice list owned by the app     | `enum`, not a legacy `Option` field                      |
| Extra columns on an existing report    | `reportextension`                                        |
| A new report                           | `report` with an explicit dataset and layout             |
| Reusable logic without UI              | `codeunit`, preferably with a narrow public surface      |
| A read-only projection for integration | API page or query, depending on the consumer             |

Do not create a parallel table that duplicates a base table because extending it feels complicated. Duplicate entities drift, and reconciliation becomes permanent work.

## Tables and fields

- Every new field needs a `DataClassification`. Pick the value from what the field actually holds; do not default everything to `CustomerContent` without thinking.
- Use `FieldClass = FlowField` for calculated values and `FlowFilter` for the filters that drive them. Do not store what a correct flowfield can compute, unless performance evidence requires a persisted value.
- `NotBlank`, `Editable = false`, and `InitValue` are schema decisions. Adding `NotBlank` to an existing table with blank rows is a data problem, not a property tweak.
- `TableRelation` documents and enforces the lookup. Use `ValidateTableRelation = false` only with a custom validation path that still checks the relation.
- Keep triggers thin. A trigger that formats, validates, posts, and sends mail is a maintenance problem; move behavior into named procedures or codeunits and call it from the trigger.
- `DataPerCompany` changes the data scope. Treat it as an architectural decision, especially for setup and numbering tables.
- Mark objects and procedures `Access = Internal` or `local` when they are not part of the app's contract. A smaller public surface is easier to change later.
- `TableType = Temporary` records behave differently: no database persistence, different locking, and no triggers on some operations. Do not treat a temporary record as a staging table without checking that behavior.

## Pages

- Choose `PageType` from how the page is used: `Card`, `List`, `Document`, `ListPart`, `CardPart`, `Worksheet`, `RoleCenter`, `API`, or a dialog type.
- A document page is a header with line parts. The part needs the right `SubPageLink` and the lines page needs the matching key, or the page loads the wrong lines or all of them.
- Set `ApplicationArea`, `UsageCategory`, `SearchTerms`, and the lookup and drill-down page properties so the page is reachable and behaves like the rest of the application.
- In page extensions, verify that the `addafter` anchor exists in the current symbols. Anchors move between versions and between base apps. Prefer `addlast` when position is not meaningful.
- Use `modify` and move operations sparingly. Every modified base control is a future merge conflict with the platform.
- API pages need explicit fields, a stable `EntityName` and `EntitySetName`, `ODataKeyFields`, and a versioned URL. Treat the field names as an external contract once published.

## Codeunits, procedures, and events

- Use `SubType = Test` for test codeunits, `SubType = Upgrade` for upgrade code, and the default subtype for business logic. Install codeunits and install triggers are legacy; check whether the target version still supports them before relying on them.
- Prefer explicit parameters and return values over global state. A `SingleInstance` codeunit is for genuine shared state, not a bag of globals.
- `[TryFunction]` procedures cannot show UI or commit, and their failures are silent. Use them only where the caller checks the result and reports a meaningful error.
- Publish integration and business events with clear names, a stable signature, and an `IsHandled` parameter only when a subscriber genuinely overrides behavior.
- Subscribers must be defensive: the publisher's record may be partially loaded, filters may be set, and the event may fire inside a loop.
- Keep procedure bodies short enough to read in one screen. Extract the branch that needs a name.

## Readability and style

- Match the surrounding file. If the repository has an `.editorconfig`, an AL formatter configuration, or a consistent indentation in existing objects, follow it instead of introducing a second style.
- AL's editor supplies a document formatter through the AL Language extension. Agree in the project whether formatting is applied on save and enforced in review. There is no authoritative standalone formatter to assume; if a project wants a CI gate, verify the tool first and document the command.
- Qualify record variables with their variable name (for example `CustomerRec."No."`). AL has no `WITH` statement, so the record variable is always written out.
- Prefer early exits and a `case` statement over deeply nested conditions.
- Comments explain why, constraints, and non-obvious platform behavior. They do not restate the next line.
- Use `///` documentation comments on procedures that form the app's internal API.
- Put user-visible text in `Label` values with a `Comment` that tells the translator what the text means. Use `Locked = true` when the text is contractual and must not be reworded.
- Do not reformat unrelated objects while making a change. A diff full of whitespace hides the actual change and makes review unreliable.

## Review cues

- An object name near or over 30 characters, or a permission set name over 20.
- An ID that is not inside `idRanges`, or a field ID copied from an example.
- A base table or base page edited directly instead of extended.
- A new `Option` field where an `enum` belongs, or numeric enum values in code.
- A trigger that contains business logic which no other caller can reuse.
- A page extension anchored to a control that does not exist in the target symbols.
- Hard-coded user-facing text outside a label.
- Formatting changes mixed into a functional change.
