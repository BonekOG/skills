# Code Style and Conventions

Read this reference when writing or editing C++ source, headers, naming, comments, include structure, or file layout.

## Repository first

Treat checked-in formatters and nearby production code as the visual source of truth. Apply the baseline below only where the repository has no established convention.

## Formatting

- Use English identifiers and documentation.
- Prefer four-space indentation, attached braces, one declaration/member per line, and a practical ~120-column limit.
- Group includes as project, external, then standard-library headers, with blank lines between groups.
- Lay out function bodies in readable phases. Use one blank line where the work changes phase, for example from related local setup to a call sequence, calculation to branching, one independent decision to another, or state mutation to its next operation. Keep tightly related declarations and calls together; do not put a blank line after every statement. Separate a multiline function signature from its first body phase.
- Keep functions cohesive; use guard clauses to keep the happy path visible.
- Extract logic when it separates responsibilities or clarifies an invariant, not to satisfy an arbitrary line-count limit.

## Formatting gates

Formatting is enforced, not negotiated. Inspect the repository for a checked-in `.clang-format`, a format target, a pre-commit hook, or a CI check, and use that configuration. Do not hand-format files and do not reformat code outside the change.

When the repository has no formatter configuration or check, establish the gate as part of the change if the repository owns its C++ sources:

1. Copy `templates/.clang-format` from this skill to the repository root as `.clang-format`. Adjust indentation, column limit, and namespace rules to the documented project convention instead of imposing the template unchanged.
2. Copy `scripts/format-cpp.sh`, `scripts/check-format.sh`, and `scripts/add-blank-lines.py` into the repository's tooling directory, for example `tools/`. Checked-in copies keep the gate runnable for every contributor and in CI without the skill installed.
3. Run `format-cpp.sh` on the affected files, or without arguments for the whole repository when adopting the gate, review the resulting diff, and keep unrelated formatting changes out of the commit.
4. Wire `check-format.sh` into CI and the repository's local check or pre-commit target. Report the command and its result in the change description.

The packaged scripts have these contracts:

| Script | Behavior | Exit codes |
| --- | --- | --- |
| `format-cpp.sh` | Rewrites the given C/C++ files, or all tracked and untracked-unignored files, with `clang-format --style=file`, then inserts structural blank lines | 0 success; 2 missing git worktree, `.clang-format`, `clang-format`, or an invalid path |
| `check-format.sh` | Non-mutating gate for the given files or the whole repository; checks structural blank lines, then runs `clang-format --dry-run --Werror` | 0 clean; 1 formatting differs; 2 missing prerequisite or invalid path |
| `add-blank-lines.py` | Inserts or checks the blank lines clang-format preserves but never creates; `--check` reports only | 0 clean; 1 missing lines; 2 usage or repository error |

Run the shell scripts from anywhere inside the git worktree; they resolve the repository root themselves. They require `git`, Python 3, a `.clang-format` at the root, and `clang-format` with `--dry-run` support. Set `CLANG_FORMAT` to select a versioned binary. On macOS, Homebrew's `clang-format` is usually newer than Apple's command-line tools copy.

`clang-format` keeps a blank line but never inserts one. The companion script therefore enforces the structural part of the layout rule: a blank line before `return` or `co_return`, and a blank line between a control block and the statements around it, while `break` and `continue` stay with their block. Grouping by logical phase inside a function remains a review judgment, not something the script can infer.

A successful formatter run is not a verdict. `check-format.sh` is the gate. Treat a missing formatter as a gap to close, not as permission to skip formatting; treat a failing gate as a failing check.

Naming and selected language checks belong in the project's `clang-tidy` configuration, which needs `compile_commands.json`. Keep that gate separate from formatting, and do not introduce a `clang-tidy` profile that contradicts the repository's style or naming convention. When the project has no such gate and the change warrants it, add one with the same treatment: checked-in configuration, a runnable script, CI wiring, and a documented command.

## Naming

- Use meaningful complete names; use verbs for operations.
- Name booleans with `is`/`has`/`can` forms when natural; an established predicate form such as `showX` is acceptable.
- Use a consistent repository-wide member naming convention rather than introducing a second one.

## Comments

Keep implementation code self-explanatory; do not add comments to C or C++ source files.

## Standard-library namespace convention

- Include the specific standard-library headers that provide the declarations a file uses.
- In implementation files (`.cpp`), import the standard namespace with `using namespace std;` after the include block and do not use qualified standard-library names.
- Keep standard-library names explicitly qualified in headers and public declarations.
- If the toolchain warns about an unqualified standard-library call, adjust the target's warning policy rather than re-qualifying the call.

## Header and implementation layout

- Give every independently named class, struct, or enum its own header and, when it has out-of-line behavior, its own implementation file. Do not accumulate unrelated types in collective headers or monolithic implementation units.
- Keep a module's unavoidable vocabulary (aliases, constants, free functions) in a clearly named limits/queries header rather than hiding it inside an unrelated type header. Deliberate exceptions: C adapter context, alias-only vocabulary, and genuinely header-only helper utilities.
- Keep non-trivial implementation out of headers when doing so improves dependency hygiene, ABI stability, or compile time.

## Splitting an existing module

- Preserve behavior and the public include contract.
- Compute direct includes; use forward declarations only to break a real cycle.
- Update the build graph, then verify the resulting include graph instead of relying on transitive includes.

## Accessor conventions

- Keep non-static data members private in internal types. A directly readable member uses a named accessor; an independently writable member also has a matching write operation (`setX` for a directly assignable value) unless a named invariant-preserving operation or a complete-state factory is the intended write path. Never use public mutable fields as a shortcut.
- Do not add duplicate `getX`/`x` methods or facade methods that merely re-expose a collaborator's accessor.
