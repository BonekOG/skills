# Releasing the skill repository

Versions and publications are deliberately separate:

- Every skill package has its own stable Version in `skills/.../<skill>/meta.json`.
- The repository has its own stable Version in the root `VERSION`.
- GitHub tags and Releases are created only for the repository, named after the
  repository (`skills`) and tagged as `v<MAJOR.MINOR.PATCH>`.
- A repository release contains every skill at its current individual version
  and records those versions in `skills-manifest.json`.

A `v1.0.0` release can therefore contain `grilling` at `0.1.0`, or
any other combination of independently reviewed skill versions. Skill-only
changes do not create GitHub tags or Releases of their own. They are captured
by the next repository release.

`main` is the rolling development branch. Published repository tags and their
GitHub Releases are the reproducible installation points. There are no
per-skill releases, per-skill changelogs, bundle variants, or prerelease
channels in v1.

## Skill versions

Each package-level `meta.json` contains one stable `MAJOR.MINOR.PATCH` value in
its `version` field. Pre-release and build suffixes are not accepted. Existing
skills start at `0.1.0`; a new package starts there unless review justifies
another initial version.

| Change                                                                                                                                                                          | Bump  |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- |
| Rename or remove a skill, break a script interface, require a new mandatory runtime dependency, or deliberately narrow the trigger so previously covered work no longer matches | Major |
| Add a capability, reference, script, or template; widen a trigger; improve behavior compatibly                                                                                  | Minor |
| Fix a typo, link, or explanation without intending a behavior or trigger change                                                                                                 | Patch |

Every skill content change requires a skill version bump in the same pull
request. A metadata-only version change is accepted only when it accompanies a
reviewed package change. Moving a package between categories without changing
its content does not need a version bump because the installed name stays the
same.

A package rename needs a major version bump. Existing installed copies under
the old name are not migrated automatically.

Skill versions appear in the manifest of each repository release. They do not
produce separate Git tags or GitHub Releases.

Each package's `meta.json` is repository metadata and is not installed with the
skill. Changes to dependency metadata are covered by the repository version,
not by a skill version bump.

## Repository version

The root `VERSION` starts at `0.1.0` and follows the same stable Version syntax.
It describes the distribution and tooling around the skills:

| Change                                                                                                                     | Bump  |
| -------------------------------------------------------------------------------------------------------------------------- | ----- |
| Break the installer, release CLI, workflow contract, package layout, or another repository-level interface users depend on | Major |
| Add repository tooling, a workflow capability, a new repository-level validation, or another compatible capability         | Minor |
| Fix repository tooling, workflows, documentation, or packaging without changing the interface                              | Patch |

Changes outside `skills/` require a root `VERSION` bump in the same pull
request. Skill-only changes do not require a repository bump. Bump root
`VERSION` explicitly when you want a new repository snapshot that captures the
current skill versions; a root-version-only change is valid for that purpose.
An unreleased repository version may be corrected to a version above the latest
published tag. Once a version is tagged, later versions must increase.

An intentional baseline reset of skill versions requires a pull request label
`skill-version-reset` and `--allow-skill-version-reset` for local checks. Use it
only while establishing an unreleased baseline; normal changes must keep each
skill version stable or increase it.

## Normal workflow

1. Change one or more skill packages and bump each changed package's `version` in `meta.json`.
   Change repository tooling or docs and bump the root `VERSION` when the
   repository layer changes or when a new snapshot is intended.
2. Run `python3 scripts/check-local.py --base origin/dev` and open a pull
   request into `dev`. Hosted CI does not run for `dev` pull requests.
3. When the changes are ready for release, open a pull request from `dev` into
   `main`. CI runs repository validation, release version checks, and
   installation on Linux, macOS, and Windows for that pull request.
4. Merge into `main` with a merge commit once the `validate` check passes.
5. If release automation is enabled, the Release workflow builds the pending
   repository release, creates `v<version>`, verifies its assets,
   and publishes the GitHub Release.

`check-format.py` validates package structure and metadata. `release.py check
--base` is the history-aware check that rejects changed skill content without
a version bump and validates repository version consistency.

Feature pull requests may be squashed into `dev`. Release pull requests from
`dev` to `main` use merge commits so both long-lived branches keep shared
ancestry and do not accumulate version conflicts.

The release workflow skips an already published repository tag, resumes a
draft Release, and refuses to move the tag or replace assets with different
bytes. If any step fails, rerun the workflow. Do not manually repair a tag in
place.

## Local commands

Run from the repository root. Python 3.10 or newer and Git are required; the
commands run on Windows and macOS. The examples use `python3`; on Windows, use
`py -3`. The check, plan, and build commands need no network access. Publishing
also requires an authenticated `gh` CLI with permission to push tags and write
Releases.

```sh
python3 scripts/check-local.py --base origin/dev
python3 scripts/check-format.py
python3 scripts/check-dependencies.py
python3 scripts/release.py check --base origin/main
python3 scripts/release.py plan --output release-plan.json
python3 scripts/release.py build \
  --plan release-plan.json \
  --output-dir dist
```

`check-dependencies.py` reports missing runtime commands for the current
machine. It is a capability report, not a release gate.

`plan` reports the pending `v<version>` release. Add
`--include-tagged` when investigating a draft Release whose tag already exists.
The build creates:

- `skills-<version>.tar.gz` and `.sha256`;
- `skills-manifest.json`, listing every included skill and version;
- `repository-<version>.md` under `dist/notes/`.

The repository archive has `skills-<version>/` as its top-level
directory and contains `.github/`, `scripts/`, documentation, every skill, the
root `VERSION`, and the generated `skills-manifest.json`. Archives use stable
timestamps and omit `.DS_Store`,
`__pycache__`, `.pyc`, `dist`, and `.pyo` files.

The release commands return 0 on success and 1 for a failed invariant or
external operation. Invalid command-line usage returns 2.

For a local publication, run `check`, `plan --include-tagged`, `build`, then:

```sh
GH_TOKEN="$(gh auth token)" python3 scripts/release.py publish \
  --plan release-plan.json \
  --dist dist
```

In Windows PowerShell, set the token and run the same Python command:

```powershell
$env:GH_TOKEN = gh auth token
py -3 scripts/release.py publish --plan release-plan.json --dist dist
```

Publishing creates an annotated `v<version>` tag, a draft Release,
uploads the archive, checksum, and manifest, downloads the archive again for
checksum verification, and publishes only after verification succeeds. This is
the same command used by GitHub Actions.

## GitHub automation

The Release workflow has two entry points:

- `workflow_dispatch` with the `publish` switch.
- Pushes to `main`, enabled only while the repository variable
  `RELEASE_AUTOMATION_ENABLED` is `true`.

It releases `v<version>` when the root `VERSION` is untagged. Before
enabling automatic publication, merge the workflow with the variable unset. Run
a dry run from Actions with `publish=false`, inspect the
`release-candidate-*` artifact, then publish the initial repository release
with `publish=true`. Set the switch only after that pilot:

```sh
gh variable set RELEASE_AUTOMATION_ENABLED --body true
```

Clear the switch to pause publishes:

```sh
gh variable delete RELEASE_AUTOMATION_ENABLED
```

The workflow uses `GITHUB_TOKEN` with job-scoped `contents: write`. It never
writes to `main`, never force-pushes, and runs with a non-cancelling
`repository-release-main` concurrency group. `main` requires a pull request and
the CI `validate` check. Repository release tags are protected against update
and deletion.

## Installing a release

Download the complete repository snapshot, verify its checksum, and extract it:

```sh
tag='v0.1.0'
version='0.1.0'
download_dir="$(mktemp -d)"
gh release download "$tag" \
  --pattern "skills-$version.tar.gz*" \
  --pattern 'skills-manifest.json' \
  --dir "$download_dir"
cd "$download_dir"
shasum -a 256 -c "skills-$version.tar.gz.sha256"
tar -xzf "skills-$version.tar.gz"
cd "skills-$version"
python3 scripts/install-skills.py --dry-run
```

In Windows PowerShell:

```powershell
$tag = 'v0.1.0'
$version = '0.1.0'
$downloadDir = Join-Path $env:TEMP "skills-$version"
gh release download $tag `
  --pattern "skills-$version.tar.gz*" `
  --pattern 'skills-manifest.json' `
  --dir $downloadDir
Push-Location $downloadDir
$expected = (Get-Content "skills-$version.tar.gz.sha256").Split()[0].ToLower()
$actual = (Get-FileHash "skills-$version.tar.gz" -Algorithm SHA256).Hash.ToLower()
if ($actual -ne $expected) { throw 'Checksum mismatch' }
tar -xzf "skills-$version.tar.gz"
Set-Location "skills-$version"
py -3 scripts/install-skills.py --dry-run
Pop-Location
```

Remove `--dry-run` to install the included skills. On Linux, replace
`shasum -a 256 -c` with `sha256sum -c`. GitHub's global "Latest release" label
is not the version contract for a monorepo; use the desired `v<version>` tag
or commit.
