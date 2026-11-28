---
name: al
description: Use when designing, implementing, reviewing, upgrading, or testing Microsoft Dynamics 365 Business Central AL extensions and customizations, especially for .al files, app.json manifests, and AL objects.
compatibility: "Requires python3. The bundled permission-set and translation tools use it."
disable-model-invocation: false
---

# AL Engineering

Make Business Central changes that compile against the symbols of the target environment, extend the base application without breaking its data model, and stay correct through schema synchronization and upgrades. Treat object IDs, keys, and upgrade code as production data decisions.

The user's request takes precedence over these recommendations. Treat the guidance as decision support; an explicit authorization boundary for publishing, syncing, upgrading, or restoring an environment still applies.

## 1. Select the operating mode

| Mode        | Use when                                                                                 | Start with                                                                                                         |
| ----------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **DESIGN**  | Choosing objects, extension points, table or page structure, enums, or API surfaces      | [code-style-and-object-design.md](references/code-style-and-object-design.md), then discovery                      |
| **BUILD**   | Creating a new app, object, page, report, or codeunit                                    | Discovery, [code-style-and-object-design.md](references/code-style-and-object-design.md), then the data references |
| **CHANGE**  | Extending or fixing an existing customization                                            | Discovery, then the reference for the touched area                                                                 |
| **UPGRADE** | Adding, removing, or changing fields, keys, enums, or data                               | [upgrades-and-data-migrations.md](references/upgrades-and-data-migrations.md)                                      |
| **REVIEW**  | Reviewing a diff, an app, a pull request, or a design                                    | [code-style-and-object-design.md](references/code-style-and-object-design.md) and the touched references           |
| **DEBUG**   | Investigating wrong values, failed validation, missing data, or broken pages and reports | [records-flowfields-and-enums.md](references/records-flowfields-and-enums.md), plus the touched area               |

Editing an app does not authorize publishing it. Publishing does not authorize installing, syncing, or upgrading data in an environment.

## 2. Load focused guidance

Read only the references the task needs:

- Object selection, naming, IDs, page types, codeunit subtypes, procedures, labels, and formatting: [code-style-and-object-design.md](references/code-style-and-object-design.md).
- Tracing a requirement to the right table, page, field, and extension point; app dependencies and symbol resolution: [discovery-and-dependencies.md](references/discovery-and-dependencies.md).
- Record access, partial records, filters, flowfields, enums, media, and generic record access: [records-flowfields-and-enums.md](references/records-flowfields-and-enums.md).
- Table extensions, keys, table relations, and `TransferFields` semantics: [schema-keys-and-transferfields.md](references/schema-keys-and-transferfields.md).
- Upgrade codeunits, upgrade tags, deprecation, schema sync, and data migration: [upgrades-and-data-migrations.md](references/upgrades-and-data-migrations.md).
- Report datasets, layouts, report extensions, and report selection: [reports-rdlc-and-report-selection.md](references/reports-rdlc-and-report-selection.md).
- Multiple validations, error collection, user-facing messages, and telemetry: [validation-and-error-collection.md](references/validation-and-error-collection.md).
- Test codeunits, test libraries, isolation, and what to test: [testing.md](references/testing.md).
- Translation files, permission set generation, and the tooling that keeps both reproducible: [translations-and-permissions.md](references/translations-and-permissions.md).
- The end-to-end project method and C/AL to AL conversion: [project-workflow-and-conversion.md](references/project-workflow-and-conversion.md).

Two standard-library Python scripts ship with this skill, each independent of a tenant or a file layout:

- `scripts/generate-permissionset.py` renders a permission set from a JSON spec, with sorted and deduplicated entries. `--check` fails when the committed object drifts from the spec. `templates/permissionset.json` is a starting point.
- `scripts/translation-tool.py` carries existing translations into a freshly generated XLIFF, reports missing and untranslated units, and moves work through CSV. It never invents unit IDs.

When the project already has tooling for permission sets or translation files, use it and follow its naming, layout, and check. The scripts here are the fallback for a project that has none: copy them into the project's tooling directory, add the spec and the generated objects to version control, and wire the checks into the build.

Usage, exit codes, and the workflow for both are in [translations-and-permissions.md](references/translations-and-permissions.md). The splitting and conversion scripts from the original project material stay out: they were bound to one folder layout and one encoding.

## 3. Reconnaissance before editing

Read the app manifest and the surrounding app before changing an object:

1. `app.json`: `id`, `name`, `publisher`, `version`, `platform`, `application`, `runtime`, `idRanges`, `dependencies`, `propagateDependencies`, `features`, and resource exposure.
2. Target environment: Business Central version, runtime version, SaaS or on-premises, and the symbols actually available in `.alpackages` or the configured symbol path.
3. Existing extensions that already touch the same tables, pages, enums, or reports; duplicate controls and conflicting field IDs are common.
4. Existing conventions in the app: prefixes, suffixes, object ID ranges, codeunit organization, label style, test layout, permission sets, translation files, and the command or CI job that produces the last two.
5. The project's compile and test gate, and whether a failing build is part of normal workflow or a release blocker.
6. Which company, data set, and tenant the change will be exercised against, and whether that environment is production.

Do not allocate object IDs, field IDs, or enum values from blog posts, samples, or another app's manifest. They come from the app's `idRanges`, from symbols, and from the project's own allocation record.

## 4. Operating invariants

- Object names are limited to 30 characters, and the compiler enforces it (AL0305). Permission set names that can be assigned to users are limited to 20 characters. Check the limit before inventing a long name.
- IDs come from `idRanges` in `app.json`. Prefixes and per-area ID blocks are project decisions; never present one project's ranges as an AL rule.
- Never change a table's primary key, and never assume secondary or unique keys are free to alter. A key change is a schema and data decision with locking, performance, and upgrade consequences.
- Base tables and base pages are extended, not edited. Use table extensions, page extensions, enums and enum extensions, and event subscribers.
- Prefer documented extension points and integration events over duplicating base behavior.
- Enum values are typed and taken from symbols or the enum definition. Never write numeric enum values copied from an example or from a legacy `Option`.
- Text that a user sees belongs in a `Label` with a comment, not in a string literal. Keep labels short enough for the UI and stable when the text is contractual.
- Permission sets are generated from a reviewed spec with the project's tooling, or with `scripts/generate-permissionset.py` when the project has none. Hand-sorted entries and rights that differ between environments are drift.
- Translations live in the XLIFF the AL toolchain generates for each language. Carry them forward with the project's tooling or `scripts/translation-tool.py`; never translate by editing table data or by rewording labels until they match.
- Anything that changes stored data, keys, or permissions needs an explicit plan for existing companies, new companies, and environments that will never run the upgrade code.
- A compile is evidence. An editor without errors is not.

## 5. Validation before finishing

Compile the app against the symbols of the target environment. An editor without errors is not a build, and a successful compile is not a successful publish. Confirm what the change actually needs:

- the app compiles for the target platform and runtime version;
- the changed objects publish and synchronize in a non-production company before production;
- upgrade codeunits ran against a copy with representative data whenever the schema changed;
- the affected pages, reports, and API endpoints were opened or exercised with real data;
- permission sets were regenerated from their spec and the project's check, or `--check`, reports no drift;
- every supported language file was regenerated and merged, and its status check is clean or the open units are reported as such;
- new objects, fields, and captions are covered by permission sets and translation files.

Report which app was compiled, against which symbols and version, and which tests or manual scenarios were exercised. If no environment was available, say which checks were skipped instead of implying a successful deployment.

## 6. Reporting

State what changed, why, and which objects and fields were touched. Include the compile result, the data or schema impact for existing companies, the permission and translation impact, and anything that remains unverified, such as behavior in a tenant that was not available.
