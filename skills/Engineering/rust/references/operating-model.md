# Operating model

## 1. Understand the change

Before editing, answer:

- What behavior must change?
- What behavior must remain unchanged?
- What invariants already exist?
- Which crate/module owns the concept?
- Is the code library code, application code, infrastructure, proc-macro, embedded, async, FFI, or performance-sensitive?
- Which tests currently prove the behavior?
- Which feature flags / target cfgs affect it?

Search for:

- analogous code paths,
- constructors/builders,
- existing error types,
- internal helper traits,
- tests and fixtures,
- dependency conventions.

## 2. Design in this order

1. Data/invariants.
2. Ownership/lifetime.
3. Error semantics.
4. API boundary.
5. Concurrency model.
6. Implementation.
7. Tests.
8. Performance tuning if evidence requires it.

This order prevents implementation details from dictating the public model.

## 3. Keep change scope controlled

Prefer:

- modifying the narrowest owning module;
- extending an existing abstraction;
- separate mechanical refactors from behavior changes where practical;
- preserving unrelated formatting and experiments;
- small reviewable commits/patches.

Avoid:

- opportunistic architecture rewrites;
- drive-by renames unrelated to the task;
- new framework layers introduced for hypothetical future needs.

## 4. Decide when to abstract

Extract an abstraction when at least one is true:

- the domain has a real concept deserving a name;
- multiple callers need the same behavior with stable variation points;
- duplication is creating inconsistency risk;
- isolation materially improves testing or safety.

Do not create an abstraction only because two code blocks currently look similar.

## 5. Review the diff as a reviewer

Ask:

- Is every changed line necessary?
- Did complexity move or actually decrease?
- Can invalid states now occur?
- Did a private implementation detail become public?
- Did any new allocation/clone/lock become habitual rather than necessary?
- Are failure paths explicit?
- Is the behavior independently testable?

## Exception policy

These are engineering defaults, not religious laws. A rule may be broken when:

1. a concrete constraint requires it,
2. the alternative is materially worse,
3. the exception is local,
4. the rationale is documented where a reviewer can see it.

Prefer narrow `#[allow(...)]` with a reason over workspace-wide suppression.
