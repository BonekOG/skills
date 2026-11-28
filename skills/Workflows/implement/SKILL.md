---
name: implement
description: "Use when implementing a piece of work based on a spec or a set of tickets."
compatibility: "Requires git."
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

Account for the specifics of the programming language in play, and use the
matching tools and skills for it.

If the user passes a ticket reference, fetch it from the issue tracker and state its title before starting. If the reference is ambiguous, ask.

Call the Skill tool with "tdd" where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, call the Skill tool with "code-review" to review the work.

Commit your work to the current branch.
