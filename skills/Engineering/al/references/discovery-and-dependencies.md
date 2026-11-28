# Discovery and Dependencies

Use this reference to turn a requirement into the right objects, the right extension points, and the right app dependencies before writing code.

## Trace the requirement to the data model

Work in this order and write the trace down; it is the design artifact the implementation follows:

1. **Entity.** Which business object does the requirement concern, and does a base table already represent it? Check the base app symbols, not only the visible pages.
2. **Presentation.** Which page shows it today? Read its `PageType` and `SourceTable`. A requirement about a page is often a requirement about the table behind it.
3. **Structure.** Is it a header with lines? Then the header page has a `Part` control pointing at a lines page, and the lines page has a `SubPageLink`. Adding a line field means touching the line table and both pages.
4. **Existing extension.** Search the app for a table extension, page extension, or enum extension on the same target. Duplicate fields and duplicate controls are the most common defect in extension work.
5. **Extension point.** Find the control you want to anchor to, the event you want to subscribe to, or the enum you want to extend, in the current symbols. Confirm the anchor and the event exist in that version.
6. **Dependency.** Determine which app must be referenced for every type you use. Do not add a dependency because an inventory listed it; add it because a symbol requires it.

## Field and control IDs

- Field IDs for table extensions must fit the range the base table allows and must be unique across all extensions installed together.
- Control IDs in page extensions must be unique within the resulting page. Check the base page's controls and any other extension on the same page.
- When two extensions collide, the second one fails to publish or produces duplicated controls. An inventory of installed extensions is the only reliable check.

## App dependencies

- Declare dependencies in `app.json` with the app `id`, `name`, `publisher`, and a version range. The publisher and name identify the app; the GUID identifies it unambiguously.
- Use `propagateDependencies` only when consumers must receive the same dependency graph. It widens the install requirement and should be deliberate.
- Indirect dependencies are still dependencies at runtime. If a type comes from a transitively referenced app, the reference must be resolvable in the target environment.
- Symbols come from the environment. Use the project's symbol download step and refresh them after a platform update; stale symbols produce code that compiles locally and fails elsewhere.

## Version and platform constraints

- `application`, `platform`, and `runtime` in `app.json` set the minimum environment. Raising them is a deployment decision, not a convenience.
- Some language features and APIs only exist from a specific runtime. Check the docs for the runtime in use rather than assuming the newest syntax is available.
- Conditional compilation (`#if`) is appropriate only when the app genuinely supports several versions. It doubles the test matrix; do not use it to avoid choosing a baseline.

## SaaS and on-premises

- On SaaS, .NET interop, direct file system access, native SQL, custom control add-ins, and some legacy APIs are unavailable. Design integrations through API pages, OData, web services, or events.
- On-premises allows more, but portability and supportability still argue for the SaaS-compatible option unless a requirement forces otherwise.
- `Access = Internal` and permission sets behave differently across deployment models; verify the effective permissions in the target environment.

## Events

- Prefer integration events published by the base app for reactions that must survive platform updates.
- Confirm the event signature in the target symbols; event signatures change between versions.
- Subscribers run inside the publisher's transaction. Do not commit, show UI, or start long operations there.
- If the platform lacks a suitable event, state that explicitly and propose the smallest safe alternative instead of patching a base object conceptually.

## Multi-company and data scope

- `DataPerCompany = false` tables are shared across companies. They need their own key design, their own permissions, and careful handling in upgrade code that runs per company.
- Setup tables and number series are the usual suspects when behavior differs between companies. Check the company context before concluding that code is wrong.

## Discovery output

Before implementation, be able to state: the target table and fields, the pages and controls touched, the extension points used, the apps referenced, the runtime baseline, and the IDs allocated. If any of these is unknown, the design is not finished.
