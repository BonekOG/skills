# Project Workflow and Modernization

Use this reference for the shape of a C/AL project and for planning a move to AL.

## The working method

1. **Baseline.** Export the objects in scope, record the encoding and line endings, hash the exports, and record the build and compile status. Without this, you cannot tell your error from a pre-existing one.
2. **Scope and object map.** List the objects, their callers, the tables they write, and the reports and forms that present them. Identify the business behavior that must not change.
3. **Design.** Decide what is modified in place and what is new. C/AL has no extension model, so every change to a base object is a fork; record why the fork is necessary and what it touches.
4. **Implement.** Change one coherent area at a time, keep the diff reviewable, and allocate function and variable IDs inside the object.
5. **Compile and compare.** Compile the object and its callers, then diff against the baseline.
6. **Migrate data if needed.** Follow [migration-and-transactions.md](migration-and-transactions.md); run it on a copy first.
7. **Test and accept.** Run tests, exercise the flow with realistic data, and get the business to confirm the behavior.
8. **Deliver.** Package the objects, update permissions and menu entries, write the release note, and state the rollback path.

## Working with an existing codebase

- Prefer reading the actual object over trusting a specification. Legacy documentation describes intent; the object describes behavior.
- Trace from the entry point the user sees: menu or page, form or report, codeunit, table triggers. Write the trace down; it becomes the onboarding material.
- Assume other customizations exist on the same tables. Check every table field ID in use before adding one.
- Keep vendor objects as close to the vendor version as possible. An isolated function called from one place is easier to carry forward than a rewritten trigger.

## Modernization to AL

- The C/AL to AL conversion tool (Txt2Al) shipped with Business Central 14 and is not present in later releases. A conversion project needs that environment or a different approach; do not plan on the tool being available in the target release.
- The supported pipeline is a technical upgrade to a release that can convert, exporting objects in the new syntax and comparing them with the baseline before conversion, then converting and fixing the result.
- What does not carry over: dataports, menu suites, codeunit 1 triggers, and .NET interop on a managed service. Each needs a designed replacement, not a mechanical rewrite.
- Forms become pages. Option fields become enums or enum-backed fields, and the mapping must be checked field by field. Report layouts are rebuilt and tested.
- Record the behavior baseline before converting: key scenarios with expected outputs. Conversion is only successful if the behavior survives, not if the code compiles.

## Choosing between conversion and replacement

- Convert when the customization is mostly data logic and the UI maps cleanly to pages.
- Rewrite when the feature is dominated by forms, dataports, interop, or a workflow that no longer fits the standard application.
- Consider a staged move: keep the legacy solution running, build the replacement capability in AL, migrate data, then retire the legacy objects after acceptance.

## Automation

- Any script that rewrites objects must state its input, output, and encoding explicitly, support a dry run, refuse to delete recursively, and log what it changed.
- Do not copy a project-bound script into another project because it exists. Read what it assumes first.

## Definition of done

- The objects compile on the recorded build, and the callers compile.
- The export is in the original encoding and line endings, and the diff is reviewed.
- Data migrations are reconciliation-checked and restartable.
- Permissions, menu entries, and reports are updated.
- Tests or documented manual scenarios cover the change, including the failure paths.
- The rollback path is written down and credible.
