# Project Workflow and Conversion

Use this reference for the shape of an AL project and for converting a C/AL solution to AL. It is the transferable procedure; the concrete scripts and tenant-specific steps belong to the project that needs them.

## The working method

1. **Baseline.** Record the app version, `app.json`, runtime, symbol source, build status, and current test status. Export or tag the state you are changing from. Without a baseline you cannot tell an introduced error from a pre-existing one.
2. **Analyze.** List the objects in scope, their dependencies, the extension points they touch, and the ID ranges available. Identify the business behavior the change must preserve.
3. **Design.** Trace each requirement to table, fields, pages, and extension points. Decide what is extended, what is new, and what is left alone. Record the decision where the next person will find it.
4. **Implement.** Make the smallest coherent change. Keep unrelated formatting and renames out of the diff.
5. **Compile and diagnose.** Build against the target symbols. Group diagnostics by code and message, fix the root cause, then rebuild. Cascading errors usually disappear with the first real fix.
6. **Review the delta.** Compare against the baseline. Confirm that generated files, IDs, permissions, and translations moved with the change.
7. **Test and smoke.** Run the automated tests that exist, then exercise the changed flow in an environment with realistic data, including the empty and error cases.
8. **Deliver.** Update permission sets, translations, documentation, and the release notes. State what was verified and what was not.

## Conversion from C/AL

- The Txt2Al conversion tool shipped with Business Central 14 and is not included in later versions. A conversion project needs that environment or a different migration approach; do not assume the tool is available in the current release.
- A workable legacy pipeline is: export the objects in the new syntax from the old environment, compare the exported objects with the previous baseline, then run Txt2Al with explicit source target and rename options.
- Supported object types include codeunits, tables, pages, reports, queries, and XMLports. Dataports are not converted; they need a replacement design. MenuSuites become pages and page extensions. The old codeunit 1 triggers do not exist in AL.
- .NET interop does not exist on SaaS. Automation, OCX, and direct file access need replacements before the code can run there.
- Option fields become enums or enum-backed fields, and the numeric mapping must be checked per field. Address formatting and other platform-supplied helpers may have different signatures.
- If the app is translated, carry the legacy translation information through the conversion so existing translations are not discarded, and review the result rather than trusting the import.

## Conversion sequence

1. Convert the objects with no dependencies first, then their consumers. Compile after each slice.
2. Keep an error inventory per slice: count, code, message, and the object that caused it. Track the count down; do not declare progress from a diff size.
3. Separate cascade errors from independent errors. Fix one root cause, rebuild, and re-measure.
4. Replace removed platform behavior deliberately: codeunit 1 triggers, menu suites, dataports, and interop each need a designed replacement.
5. Rebuild report layouts by hand where the conversion cannot carry them, and test the output.
6. Recreate permissions and report selection, then verify them as a user, not as an administrator.
7. Remove the legacy objects only after the new app covers the behavior and the users have accepted it.

## Automation and fix scripts

- Any script that rewrites source must have an explicit input, an explicit output, and a dry-run mode.
- Make fixes idempotent: running twice must not double-apply.
- Log every change with the object, the old value, and the new value so the result is auditable.
- Never delete recursively or clean a directory the caller did not name explicitly.
- Keep the script with the project that needs it, documented with prerequisites, exit codes, and whether a clean run is a verdict.

## Definition of done

- The app compiles against the target symbols and version.
- New objects and fields have IDs from the allocated ranges and the required classifications.
- Permission sets, translations, and report selection cover the new surface.
- Existing companies, new companies, and environments that will never run upgrade code are each addressed.
- Tests or documented manual scenarios cover the changed behavior, including failure paths.
- The change is reversible, or the rollback limits are stated.
