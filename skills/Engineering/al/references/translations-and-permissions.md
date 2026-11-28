# Translations and permission sets

Translations and permission sets are deliverables with their own review gate. Both are easy to produce by hand once and then impossible to keep correct: a permission set drifts as objects are added, and a language file silently loses translations when it is regenerated or copied. Use the project's tooling, and when the project has none, add it before handing over the change.

## Check what the project already has

Look before you build:

- translation files under `Translations/`, usually one `<language>.xlf` per language, and the command that generates them;
- a permission set object per role, and anything that produces it: a build task, a `tools/` script, a generator configuration, or a CI job;
- the app's `features` array, where `TranslationFile` enables XLIFF generation;
- task definitions in `.vscode/tasks.json` and the pipeline that publishes the app.

When the project has a generator or a check, run it and follow its layout. Do not hand-edit an object that is generated, and do not replace the project's naming or ID convention with the one below. A generated file that is committed is regenerated from its input, not edited.

## Permission sets

A permission set should be reproducible. The same input must produce the same object, so a review sees only real permission changes.

This skill ships `scripts/generate-permissionset.py` and a starting spec in `templates/permissionset.json`:

```sh
python3 scripts/generate-permissionset.py "tools/myapp-admin.json" --out "Permissions/MyApp Admin.al"
python3 scripts/generate-permissionset.py "tools/myapp-admin.json" --check "Permissions/MyApp Admin.al"
```

The script collapses duplicate object entries that carry identical rights, orders rights as `RIMDX` with their case intact, groups entries by object type, and sorts by name. It rejects a duplicate entry with different rights instead of merging them, because merging would silently change what the set grants. `--check` exits 1 when the committed object differs from the spec, which is the CI gate.

The spec carries the decisions the script must not guess:

- `id` is the permission set's object ID, taken from the app's `idRanges`;
- `name` is limited to 20 characters when the set is assignable, because that is the Business Central limit;
- `assignable` tells whether users can be assigned the set directly;
- `permissions` lists `type`, object `name`, and `rights` for each entry. Accepted types are `tabledata`, `table`, `page`, `report`, `codeunit`, `query`, and `xmlport`. Table data carries R, I, M, and D; the other object types carry X.
- `rights` uses R, I, M, D, and X. Lowercase letters are indirect permissions and mean something different from uppercase ones, so write them as intended and expect the generator to keep the case.

Keep the executable permission entries that a codeunit needs, not just the tables and pages the user opens. Test the result by signing in as the intended role: an administrator account proves nothing about a permission set.

If the project has no generator, copy the script into the project's tooling directory, commit the spec and the generated object, and run `--check` in CI. A permission set that exists only as a hand-sorted object has no source of truth.

## Translations

Business Central imports only the XLIFF file that the AL toolchain generates for the app. Unit IDs belong to that file, so generating them by hand produces a file the platform ignores or rejects. The workflow is therefore always: generate, carry forward, translate, verify.

This skill ships `scripts/translation-tool.py` for the steps around the generated file:

```sh
# carry translations into a freshly generated file
python3 scripts/translation-tool.py merge \
    --base "Translations/de-DE.generated.xlf" \
    --previous "Translations/de-DE.xlf" \
    --out "Translations/de-DE.xlf"

# hand open units to a translator and take them back
python3 scripts/translation-tool.py export --lang-file "Translations/de-DE.xlf" --out units.csv
python3 scripts/translation-tool.py import --lang-file "Translations/de-DE.xlf" \
    --csv units.csv --out "Translations/de-DE.xlf"

# gate: empty targets, missing units, stale units, translated locked labels
python3 scripts/translation-tool.py status --lang-file "Translations/de-DE.xlf" \
    --base-file "Translations/de-DE.generated.xlf" --source src
```

`merge` matches by unit ID first and by source text and note second, so a label that moved to another object keeps its translation. It reports translated units that have no counterpart in the new file and exits 1, because that is where translations are lost. Review those before importing.

`status` exits 1 when the file has empty targets, units the regenerated file no longer contains, labels that never made it into the file, or a `Locked = true` label whose target differs from its source. A clean run is the release gate for a language the app claims to support.

Never fill translations by editing SQL data or by renaming labels until the English text matches. Both break the link between the label and its translation unit.

## Labels

- Put a `Comment` on every label a translator cannot infer from the text alone, such as an abbreviation or a single word with several meanings.
- Use `Locked = true` for product names, legal text, and codes that must not be translated. The target then stays identical to the source.
- Change a label's text only when the meaning changes. Rewording for style invalidates every existing translation of it.
- When a caption is built from a label, expose the label rather than assembling user-facing text from concatenated strings.

## Exit codes

Both scripts follow the same convention: 0 clean or written, 1 findings or drift, 2 usage or input error. Treat 0 as a verdict only for the checks the command covers, and report which languages and permission sets were actually exercised.
