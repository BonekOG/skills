# Object Workflow

Use this reference to read, edit, and import C/AL objects without corrupting the export.

## Export formats

- **Object text (.txt)** is the reviewable form: a sequence of `OBJECT` blocks with properties, fields, keys, controls, and code. It diffs line by line, which makes it the right format for changes under version control.
- **.fob** is a binary container. It imports reliably and reviews poorly. Do not use it as the only artifact of a change.
- **Split files** (one object per file) make review easier but lose the original file boundaries. If the project splits exports, keep the split rule explicit and reproducible.

## Object text anatomy

```text
OBJECT Table 50000 "Example Entry"
{
  OBJECT-PROPERTIES
  {
    Date=...;
    Time=...;
    Modified=Yes;
    Version List=...;
  }
  PROPERTIES
  {
    CaptionML=DEU=Beispiel;
  }
  FIELDS
  {
    { 1   ;   ;No.       ;Code20                             }
  }
  KEYS
  {
    {    ;No.                                             }
  }
  CODE
  {
    BEGIN
    END.
  }
}
```

- `OBJECT` line: type, ID, name. The type and ID identify the object on import; the name is metadata.
- `OBJECT-PROPERTIES`: dates, modified flag, version list. Update these according to the project's convention; do not invent a convention and apply it to every object.
- `PROPERTIES`: object properties, usually including multilingual captions.
- `FIELDS`, `KEYS`, `CONTROLS`: fixed-column blocks. Alignment is for humans; the import is driven by the separators.
- `CODE`: global variables and the object's triggers and procedures.

## Comments and sections

- Comments are allowed in trigger and procedure bodies. `//` for a line, `{ ... }` for a block. Curly braces are also the block delimiters of the object structure, so a stray comment delimiter breaks the file.
- Do not put comments in `FIELDS`, `CONTROLS`, `KEYS`, `VAR`, or `TEXT000` blocks. Put the explanation in the code that uses the field or in the project's documentation.
- Text constants are declared as `TEXT000@...` in the code section. They are the translation surface for messages; keep them stable when the text is contractual.

## Triggers

- Table: `OnInsert`, `OnModify`, `OnDelete`, `OnRename`, and field-level `OnValidate`, `OnLookup`, `OnDrillDown`, `OnAssistEdit`.
- Form: `OnInit`, `OnOpenForm`, `OnCloseForm`, `OnActivateForm`, `OnDeactivateForm`, and the record triggers.
- Report: `OnInitReport`, `OnPreReport`, `OnPostReport`, and data item triggers `OnPreDataItem` and `OnAfterGetRecord`.
- Codeunit: `OnRun`, plus `OnRun` for the object and triggers added by newer releases. Confirm the trigger exists on the target build before using it.

Keep triggers thin. A trigger that validates, posts, prints, and sends mail is untestable; move the behavior into a named function and call it.

## Procedures, functions, and variables

- Global functions are declared with an ID: `PROCEDURE Name@1(...)`. The ID must be unique within the object. Search the object before assigning a new one; deleted functions leave gaps that must not be reused blindly.
- `LOCAL PROCEDURE` limits visibility to the object. Prefer it for helpers.
- Variable IDs are also per object. The numbers are usually large; preserve them and add new ones in the same style as the file.
- Parameters are passed by value unless declared `VAR`. `VAR` parameters are the C/AL equivalent of by-reference.
- There is no structured exception handling. `CODEUNIT.RUN` returns a Boolean, and an error inside the called codeunit aborts it. Design around return values and validation, not around catch blocks.

## Object IDs and naming

- Object IDs come from the project's allocation, usually inside a customer range. Never copy an ID from a sample, a blog post, or another customer's export.
- Prefixes and suffixes follow the project's convention. Check neighboring objects before inventing a prefix.
- Object names, captions, and version lists are visible to users and support. Keep them meaningful.
- Adding a table field means checking the field IDs already used by every extension of that table in the database, not only in this export.

## Editing flow

1. Export the current object (or the current full set) and keep it as the baseline.
2. Edit a copy, in the export's encoding and line endings.
3. Diff the result against the baseline before importing anything. The diff is the review.
4. Import with the intended import action: overwrite an existing object of the same type and ID, or add a new one. Read the action before running it; an overwrite of the wrong ID destroys the original.
5. Compile, then exercise the changed behavior.
6. Export again and keep the new state as the baseline for the next change.

## Legacy surface

- Forms still exist in NAV 2018 and older, and are still imported. New development normally belongs in pages; changing a form is justified when the requirement is about that form.
- MenuSuites define navigation and do not exist in AL. Any modernization plan needs an explicit replacement.
- `DotNet` and `Automation` variables tie the solution to Windows, a specific runtime, and usually on-premises hosting. Record every one you touch; they are migration blockers.
- Dataports are not supported by the AL conversion path and need a designed replacement.

## Review cues

- A comment in a field or key block.
- A reused function or variable ID.
- A trigger that grew into a business process.
- An object edited directly in the designer with no export baseline.
- A version list or modified flag changed on unrelated objects.
- A `DotNet` or `Automation` dependency added without a modernization note.
