# Knowledge Capture

Use this reference when investigating undocumented behavior, when the available material is incomplete, or when a finding must survive the next person.

## Why this is part of the skill

C/AL knowledge often exists only in old objects, in a wiki that was never finished, or in the memory of one person. A knowledge base that names a topic is not evidence that the topic is covered: one corpus of C/AL material indexed 32 topics and contained 11 files. Missing entries read like coverage if nobody checks.

## Distinguish three kinds of statement

- **Documented behavior**: stated by Microsoft documentation for a specific version. Cite the page and the version.
- **Observed behavior**: what happened in a specific environment, build, and data set. Record the reproduction.
- **Convention**: what this project or customer decided. Record the decision and its owner.

Never promote an observed behavior to a rule without a reproduction, and never present a convention as a platform property.

## Record format

For each finding, capture:

- the object, function, and trigger involved;
- the NAV version, build, and cumulative update;
- the deployment model and database collation if relevant;
- the input, the observed result, and how it was verified;
- the date and who verified it;
- whether it is documented, observed, or a project convention.

A finding without a version is not reusable. Behavior changes between cumulative updates.

## Handling gaps

- When a source is missing, say which topic is missing and what was assumed. Do not fill the gap with plausible-sounding guidance.
- When two sources contradict each other, record both and the conditions under which each applies. Do not silently pick one.
- When a question can be answered by reading the object or running a test, do that before writing a rule.

## Keeping the record useful

- Keep findings next to the project they describe, or in the project's documentation, not only in a chat.
- Prefer a short entry that names the object and the version over a long narrative without evidence.
- Update an entry when a later build changes the behavior; do not delete the history of the change.
- Mark open questions explicitly so the next person knows what is still unknown.
