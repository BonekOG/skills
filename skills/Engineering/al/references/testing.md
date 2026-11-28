# Testing

Use this reference to decide what to test in an AL app, how to isolate the tests, and what evidence to report.

## Test structure

- Test codeunits set `SubType = Test` and live in a separate test app that depends on the app under test. Shipping tests in the production app adds dependencies and surface area for no benefit.
- Mark test procedures with `[Test]` and let the project's test runner discover them.
- Arrange, act, assert. Keep the arrangement explicit: create the records the test needs, do not inherit them from a previous test.
- One test codeunit per business area or business case is a workable starting convention. Split it when setup and helpers stop being shared.
- Use `[TransactionModel(TransactionModel::AutoRollback)]` when the test only reads or writes data that should not persist, and verify that the chosen model matches what the test asserts.
- Use the test library codeunits available in the environment, such as the assert library, instead of writing ad-hoc comparison helpers. Confirm the library app is present before depending on it.

## Isolation

- Tests must pass on a clean company and on a company with data. Create what you need, and use unique identifiers so parallel or repeated runs do not collide.
- Temporary records are fast and leave no trace, but they behave differently from persisted records. Use them for logic tests whose contract does not depend on storage.
- A test that commits data must clean up, or it will fail on the second run.
- Do not depend on the development company's numbering series, setup values, or posting groups. Set them in the test, or the test documents an environment rather than a behavior.
- Confirm dialogs, messages, and report requests need handlers. Register them in the test instead of disabling the behavior in production code.

## What deserves a test

- Posting and calculation results: amounts, taxes, dimensions, and status transitions.
- Validation rules that protect data integrity, including the negative cases.
- Number series, document copying, and release/post/reopen flows.
- Permission sets: that a role can perform its intended action and cannot perform a forbidden one.
- Upgrade logic: that a rerun is harmless and that the tag is set.
- Error collection: that all problems are reported in one pass.
- Report dataset behavior: filters, totals, and empty results. Layout correctness is a manual or visual check.

## What not to test

- Platform behavior that the base app owns.
- Exact auto-generated document numbers, unless the numbering rule is the contract.
- Incidental formatting of a message.
- Implementation details such as which private procedure was called.

## UI tests

- `TestPage` and `TestRequestPage` drive pages from code. They are the only way to test some page logic, and they are slow and brittle.
- Use them for page-specific behavior that cannot be reached through a codeunit, and keep them few.
- Prefer testing the codeunit or table logic directly when the page only calls it.

## Running tests

- Report the environment: local container or sandbox, Business Central version, test app version, and the command or page used.
- In a container-based setup, the project's test runner or the container tooling's test command is the evidence. In a managed environment, the pipeline or the test runner page is.
- A test run that was skipped, filtered, or failed to publish is not a passing run. Say which.
- If the project has no automated test setup, state that the change was verified manually and describe the scenarios.

## Test data

- Build fixtures in code so the test states its own preconditions.
- Use realistic values where the rule depends on them: dates around period boundaries, amounts that round, text at the length limit.
- Keep fixtures free of customer names, real identifiers, and personal data.
