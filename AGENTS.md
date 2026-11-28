# Agent Guide

## What this repository is

This repository is a collection of skill packages for Codex and
other agents. Packages live at `skills/<category>/<skill>/`. The `skills/`
directory and the category folders are containers without `SKILL.md`; every
directory below them that contains a `SKILL.md` is one skill package. There is
no application source code and no build system at the repository root.

The category folders group packages by audience:

- `Engineering/` holds language and platform guidance, selected by the
  technology in play: AL and C/AL for Dynamics 365 Business Central and
  Dynamics NAV, C++, Kubernetes, Rust, Swift, and Terraform.
- `Helper/` holds supporting workflows an agent uses during a session: research,
  prototyping, test-first development, code review, bug diagnosis, domain
  modeling, grilling, PR writing, and interactive wizards.
- `Workflows/` holds commands a person invokes deliberately: PR babysitting,
  handoffs, interviews, implementation and ticket workflows, teaching,
  architecture improvement, and wayfinding. Most are manual-only.

Category folders are repository organization only. `scripts/install-skills.py`
flattens the tree, so every package installs as `<CODEX_HOME>/skills/<skill>`
regardless of its category. Moving a package between categories does not change
its installed path.

Read the relevant skill's `SKILL.md` and references when a task concerns that
skill; do not assume every repository task belongs to a skill.

## Repository state and hard rules

`main` is the default release branch, `dev` is the protected integration
branch, and `origin` points to `https://github.com/BonekOG/skills.git`. Verify
the current repository state with `git status`, `git log --oneline -5`, and
`git remote -v`; do not assume a particular worktree or history state.

- Create coherent, scoped commits with descriptive messages as part of normal work.
- Do not force-push, rewrite shared history, or delete remote branches.
- Push when the task is to publish or the user has approved it. Open feature
  pull requests into `dev`; release pull requests go from `dev` to `main`.
- Before any Git operation, inspect `git status` and preserve the existing worktree state.
- Never discard, overwrite, or rewrite uncommitted user work.
- Never commit secrets or generated artifacts such as `__pycache__` or `.DS_Store` files.
- Do not run destructive commands or reformat unrelated files. Keep each change limited to the assigned work item.
- Keep packages inside a category folder and keep category folder names as they are: `Engineering`, `Helper`, and `Workflows`.
- Keep frontmatter `name` equal to the package directory name. Renaming a package means renaming its directory and updating its link in `README.md` and its path in this file.

## Using skills

A skill becomes available to Codex once its package directory sits directly
under `${CODEX_HOME:-$HOME/.codex}/skills`. Categories are flattened on
install, so `skills/Helper/tdd` becomes `~/.codex/skills/tdd`. Codex selects a
skill from the `name` and trigger-style `description` in its `SKILL.md`
frontmatter; `agents/openai.yaml` only adds UI metadata such as a display name,
short description, and default prompt.

Several imported skills are manual-only. They set
`disable-model-invocation: true` in `SKILL.md` and
`policy.allow_implicit_invocation: false` in `agents/openai.yaml`. Keep both
fields when editing such a package. `check-format.py` rejects a one-sided or
conflicting setting when converting a skill to or from manual-only.

After selection, read `SKILL.md` first and load only the references the task
needs. To try local edits in Codex, install the packages from this repository
with `scripts/install-skills.py`. To install selected packages, pass a
comma-separated list to `--skill`:

```sh
python3 scripts/install-skills.py --skill rust,kubernetes
```

Keep the installed package intact. Moving or flattening files inside it breaks
the relative references, scripts, and templates that `SKILL.md` routes to.

## Local installation

Install Git and Python 3.10 or newer. Clone the repository and run the
installer from its root:

```sh
git clone https://github.com/BonekOG/skills.git
cd skills
python3 scripts/install-skills.py
```

On Windows PowerShell, use `py -3 scripts/install-skills.py`. To use a
published snapshot, download the archive from the repository Releases page,
verify its checksum, extract it, and run `scripts/install-skills.py` from the
extracted directory.

`scripts/install-skills.py` walks `skills/` recursively and treats every
directory that contains a `SKILL.md` as one skill package. It copies each
package's installable contents, including `references/`, `scripts/`, `templates/`,
`agents/`, and any other subdirectories, into
`${CODEX_HOME:-$HOME/.codex}/skills`, replacing an installed skill that has the
same directory name. It rejects two packages that share a directory name,
stages all copies before changing the target, and skips `.DS_Store`,
`__pycache__`, and compiled Python files while copying. Unrelated skills in the
target directory stay untouched.

Before copying, the installer calls `scripts/check-dependencies.py` for the
selected packages. Invalid or missing `meta.json` files abort
installation before the target is changed. Missing runtime commands are
reported as warnings because the skills still install without their optional
language toolchains. `meta.json` is repository metadata and is not
copied into the installed package.

Use it to try local changes in Codex. `--dry-run` reports planned installations
and replacements without changing anything; `--target DIR` installs somewhere
else, which is useful when checking the script itself. The installer and all
repository checks use Python 3.10 or newer and run on Windows and macOS. Keep
this repository tooling in `scripts/`; do not copy it into individual skills.

## Skill format contract

- Put YAML frontmatter at the start of every `SKILL.md`, with non-empty `name` and `description` fields.
- Set `name` to the skill directory name, using lowercase kebab-case.
- Keep a stable `version` in the package's `meta.json`, for example `0.1.0`. Only a package content change requires a new version; moving the package between categories does not. The release contract is in [`RELEASING.md`](RELEASING.md).
- Keep the independent repository version in the root `VERSION`. Changes outside `skills/` require a repository version bump; a repository-version-only bump is allowed to publish a snapshot of the current skill set.
- Declare runtime executable requirements in the optional `compatibility` string, which the Agent
  Skills specification defines for environment requirements and limits to 500 characters. Skills
  without specific executable requirements omit the field. Do not use `metadata.requires` or
  `metadata.version`; those are not portable Agent Skills fields. Harness support for interpreting
  `compatibility` varies, so the repository's dependency checker is the local enforcement point.
- Keep each skill's version and runtime command requirements in its `meta.json`. Update that file when
  development adds or removes a runtime command. `check-format.py` rejects a missing or invalid
  metadata file, stale `metadata.requires` or `metadata.version`, and any `compatibility` value that
  differs from the canonical text generated from `meta.json`. The file uses `schemaVersion: 1`, a
  stable `version`, a sorted unique `requires` list, and an optional `detail` string. Dependency
  changes without package content changes are covered by the repository version, not by bumping
  every skill version.
- Never add `SKILL.md` to `skills/`, `skills/Engineering/`, `skills/Helper/`, or `skills/Workflows/`; those are containers, not packages.
- When adding or revising a `description`, write it in third person and begin with a use trigger such as `Use when` or `Use for`; `check-format.py` rejects any other opening. Name relevant file extensions when they help agents recognize when to invoke the skill.
- Treat `SKILL.md` as the entry point and router. Keep its routing concise and point to the appropriate references.
- Put detailed guidance in `references/` and load those files only when relevant to the task. Some imported packages keep topic files at the package root instead, such as `LOGIC.md`, `UI.md`, `tests.md`, or `ADR-FORMAT.md`; route to each of them from `SKILL.md` and keep the package's existing pattern. Use `references/` for new packages and substantial rewrites.
- Do not duplicate reference content in `SKILL.md`; update the router and the reference that owns the guidance instead.
- Optional `agents/openai.yaml` metadata may define `interface.display_name`,
  `interface.short_description`, `interface.default_prompt`, and
  `policy.allow_implicit_invocation`. When the file exists, `interface.display_name` and
  `interface.short_description` must be non-empty; `interface.default_prompt` is optional. If
  either `policy.allow_implicit_invocation` or frontmatter `disable-model-invocation` is present,
  both are required and must be inverse.
- Keep each skill's runnable tooling with that skill. Optional `scripts/` and `templates/` must be runnable or directly usable, documented, and portable, and every file in them must be named in the package's `SKILL.md`; `check-format.py` rejects an unreferenced file. Document runnable tooling's expected working directory, prerequisites, exit codes, and whether a clean run is a verdict.
- Keep Markdown tables well-formed and every relative Markdown link pointed at a real repository path.

## Working on an existing skill

1. Read that skill's `SKILL.md` first.
2. Follow its routing table and read only references relevant to the requested change.
3. Preserve the routing-table structure and existing column names when editing it.
4. If a reference is added, renamed, or removed, update the routing table and any other references to it in the same change.
5. Keep link text, referenced filenames, and actual paths in sync.
6. Keep prose in English, make the smallest scoped change, and preserve unrelated user work.
7. Bump `version` in the package `meta.json` according to [`RELEASING.md`](RELEASING.md) when the package content changes. A category move keeps the existing version and install name. Bump the root `VERSION` when repository tooling, workflows, or documentation change.
8. When a package moves to a different category, update its link in `README.md`, its path in this file, and any repository documentation that names it. Its directory name and frontmatter `name` stay the same.
9. When a package changes its installed name, bump the package's major version and update every name reference.
10. Update `meta.json` and the corresponding `compatibility` frontmatter when runtime command
    requirements change.

## Adding a new skill

1. Choose the category that matches the package's audience and create `skills/<category>/<name>/` with a lowercase kebab-case name.
2. Add `SKILL.md` with valid frontmatter; make `name` match the directory and write a trigger-led description.
3. Add `meta.json` with `schemaVersion: 1`, a `version` of `0.1.0` unless review justifies another
   initial version, and the exact `requires` list for the skill.
4. Make `SKILL.md` the concise entry point and router. Include an instruction to load only what the task needs.
5. Add `references/` only when detailed guidance needs separate files. Name each reference by topic and route to it from `SKILL.md`.
6. Add `agents/openai.yaml`, scripts, or templates only when useful; follow the format contract above.
7. Create or update the skill's row in the matching table in `README.md` and update the layout section in this `AGENTS.md`.
8. Run the release-aware validation commands below and report exactly what you checked.

## Validation before finishing

Run commands from the repository root. On Windows, replace `python3` with
`py -3` in the examples below. Start by checking the worktree:

```sh
git status --short
```

The CI workflow runs only for pull requests targeting `main`. Before opening a
pull request into `dev`, run the CI checks locally on the implementation
machine's operating system:

```sh
python3 scripts/check-local.py --base origin/dev
```

For a release pull request from `dev` to `main`, run the same command with
`--base origin/main`. The script runs the repository format check, the
history-aware release check, and an installation smoke test in a temporary
directory. A clean run is the local CI verdict for that operating system.

An intentional skill-version baseline reset additionally needs
`--allow-skill-version-reset`; hosted CI grants that exception only when the
pull request carries the `skill-version-reset` label.

To run the underlying format check directly:

```sh
python3 scripts/check-format.py
```

It discovers every `SKILL.md` under `skills/`, so category depth does not
matter. It verifies frontmatter, names, trigger-led descriptions, stable versions
in `meta.json` and the root `VERSION`, metadata completeness, canonical
`compatibility` values, agent metadata fields, invocation-policy consistency,
relative Markdown links in the repository, and that every file in a
`references/`, `scripts/`, or `templates/` directory is mentioned in its
`SKILL.md`. It locates the repository root from its own path, so it runs from
any directory. The history-aware version check is `release.py check --base`.

Compare the branch against its target branch when running the underlying checks
directly:

```sh
python3 scripts/release.py check --base origin/dev
```

`release.py` exit code 0 means the release invariants passed; 1 means a
validation, Git, build, or GitHub operation failed; argparse uses 2 for invalid
invocation. The runtime dependency check remains a machine-specific report and
is not a release gate.

Run the runtime dependency check separately to verify the current machine:

```sh
python3 scripts/check-dependencies.py
```

Exit code 0 means every required command is present, 1 means required commands
are missing, and 2 means a metadata file or invocation is invalid.

When a change affects what is installed locally, run
`python3 scripts/install-skills.py --dry-run` to list the packages that would
be added or replaced.

Build a local release candidate when changing release tooling:

```sh
python3 scripts/release.py plan --output release-plan.json
python3 scripts/release.py build \
  --plan release-plan.json \
  --output-dir dist
```

Publishing is reserved for the GitHub release workflow or an explicitly
authorized maintainer run. See [`RELEASING.md`](RELEASING.md) for the full
contract, rollout, recovery, and release installation procedure.

## Reporting

Summarize the files changed, the validation commands run and their results, and
any remaining risks or unverified facts. Be specific; do not claim checks that
were not run.
