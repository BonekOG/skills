# C/AL Semantics

Use this reference when reasoning about C/AL expressions, filters, dates, records, strings, and error behavior. The rules here are the ones that differ from mainstream languages and cause silent defects.

## Boolean evaluation

- C/AL evaluates both operands of `AND` and `OR`. There is no short-circuit.
- A guard does not protect the second operand. In the following condition the right side is evaluated whether or not a record was found:

```cal
IF Rec.FIND('-') AND (Rec."Amount" > 0) THEN
  ...
```

- Use nested `IF` statements when the second test depends on the first, and check the return value before reading fields.
- Side effects on the right of `AND` always happen. Move the call out of the condition.

## Filters and positioning

- `SETRANGE` and `SETFILTER` restrict the next read. They do not position the record and do not load field values.
- Read the record with `GET` or a `FIND` before using its fields. A filter plus an unpositioned record still yields the previous record's values.
- `FINDFIRST` and `FINDLAST` position; `FIND('-')` walks a key in ascending order and `FIND('+')` in descending order. `FIND('=')` locates an exact key value.
- `FINDSET` reads a set and has locking parameters. The first parameter requests update locks; the second controls whether the key is updated. Do not request update locks for a read-only pass.
- `RESET` clears filters; it does not undo a write.
- `FILTERGROUP` separates filter groups, typically for user filters versus code filters. Setting a filter in the wrong group makes it invisible or unremovable.

## Empty dates and times

- `0D` is the undefined date. On SQL Server it is stored as 1753-01-01, not as NULL.
- `0T` is the undefined time, `0DT` the undefined datetime.
- A range such as `01.01.24..31.12.24` excludes blank dates. Include `0D` explicitly when they are valid.
- `TODAY`, `WORKDATE`, and `CALCDATE` are the normal date helpers. `WORKDATE` is user-controlled; do not use it for audit timestamps.
- Adding a duration to `0D` produces surprising results; branch on the blank date first.

## Records and writes

- Assigning a field does not run `OnValidate`. Call `VALIDATE` when the rule must run.
- `MODIFY` does not run the table's `OnModify` trigger. `MODIFY(TRUE)` does. The same distinction applies to `INSERT` and `DELETE`.
- `TRANSFERFIELDS` matches fields by number. Fields with the same number and an incompatible type fail, and validation triggers do not run.
- Temporary record variables behave differently from persisted ones: no database locking, and some operations skip triggers. Do not assume a temporary record proves a persisted one will behave the same.
- `RECORDREF` and `FIELDREF` allow generic access by number. They bypass compile-time checking; validate the field type before writing through them.

## Text and codes

- `Code` values compare ignoring case and trailing spaces. `Text` values do not.
- Text is fixed-length. Assigning a longer value truncates it at the defined length; check the field length before building a value from parts.
- `COPYSTR`, `STRPOS`, `DELSTR`, and `PADSTR` are the string tools. Their positions are one-based.
- `FORMAT` uses the user's regional settings, which makes it unsuitable for machine-readable output. `EVALUATE` parses with the same settings.
- Empty string and blank are not the same as `0D` or zero. Check the type before comparing.

## Numbers and rounding

- `ROUND` takes the value, the precision, and the direction. The default direction is not always the business rule you want; state it.
- Currency and decimal amounts must be compared with tolerance or after rounding, not by exact floating equality.
- Percentages and unit conversions are frequent sources of off-by-one-cent errors. Test with values that land on the rounding boundary.

## Errors and control flow

- `ERROR` aborts the transaction. `MESSAGE` does not. `CONFIRM` returns a Boolean and does not stop the flow by itself.
- There is no TRY/CATCH. `CODEUNIT.RUN` returns a Boolean, and an error inside the called codeunit aborts that run. Check the result; ignoring it turns a failure into silent partial work.
- `TESTFIELD` and `FIELDERROR` are the usual validation guards, but they also abort. Collecting several validation problems requires an explicit list and a single error at the end.
- `COMMIT` ends the transaction. Anything written before it survives a later error.

## Options and legacy choices

- `OPTION` fields store an ordinal, and option strings are separate from the numeric value. Read the option through the defined option string, not by assuming the number.
- `OPTIONSTR` and `EVALUATE` convert between the two. A mismatch between an option and its string is a data defect.
- New choice lists in modern code belong in enums. In C/AL, the equivalent is a well-defined option with a documented mapping, because the language has no enum type.

## Review cues

- A single `IF` with `AND` where the second condition assumes the first succeeded.
- A filter set and fields read without a `GET` or `FIND`.
- A date range that omits `0D`.
- `MODIFY` used where `MODIFY(TRUE)` is required, or the reverse.
- A text concatenation that can exceed the field length.
- `CODEUNIT.RUN` whose Boolean result is ignored.
