# Encoding and Editing

Use this reference before any edit that rewrites an object export. Encoding damage is silent until import, and then it is a corrupted caption or a failed object.

## Why this matters

C/AL object files are single-byte text using a legacy Windows code page. The same corpus can contain exports in different code pages, because different tools, machines, and script defaults produced them. One real corpus contained both CP850 and Windows-1252 exports; two scripts in it each assumed a different one.

If a file is decoded with the wrong code page and written back, characters such as umlauts, section signs, and currency symbols become question marks or different characters. The object still imports, and the captions are wrong from then on.

## Determine the encoding from the file

1. Pick a line with a known non-ASCII character, typically a German or Danish caption.
2. Inspect its bytes: `hexdump -C file.txt | grep -m1 -A1 ...` or a short Python read of the raw bytes.
3. Compare the byte values with candidate code pages. CP850 and Windows-1252 agree on ASCII and differ on accented letters.
4. Confirm with a second character, and with a full decode that does not produce replacement characters.

Never infer the encoding from the tool that is supposed to have produced the export, and never infer it from the file extension. Measure it.

## Rules for editing

- Preserve the code page. Editing in UTF-8 and writing back UTF-8 changes the bytes of every non-ASCII character unless the import path explicitly supports it.
- Preserve CRLF line endings and the trailing newline. Converting to LF produces a diff on every line and may break tooling that expects Windows text.
- Do not add a byte-order mark.
- Do not reflow or re-align whole blocks to fix one line. Column alignment in field and control blocks is cosmetic; a full re-alignment hides the real change.
- Do not run a bulk encoding conversion "to be safe". It is the most common way to lose characters.
- Make a byte-identical backup before any transformation.

## Verifying an edit

- Count non-ASCII bytes before and after. They should change only where the edit intended.
- Check the specific characters you touched by decoding the same byte range with the chosen code page.
- Count question marks before and after. A new question mark where a letter used to be is a decoding failure, not a typo.
- Diff with a tool that does not normalize encodings, and review line endings in the diff.
- Confirm that the object still imports and compiles before trusting the text.

## Tool traps

- Windows PowerShell 5.1 writes UTF-16 by default with some cmdlets. Writing a C/AL object through such a cmdlet silently doubles every ASCII character.
- Editors that auto-detect UTF-8 and save as UTF-8 will corrupt a CP850 file on the first save.
- `sed` and `awk` operate on bytes in the C locale and on characters in a UTF-8 locale. A locale mismatch can change multibyte handling even when the file is single-byte.
- Git can normalize line endings through `.gitattributes`. Check the attribute for `*.txt` before committing object exports.
- A script that reports "encoding: Windows-1252" may only be reporting its own default. Verify the bytes.

## When the encoding cannot be established

Treat the export as read-only for the purpose of the change: edit in a scratch copy, verify the characters against the original, and have the owner confirm the import result. Do not normalize the file as a side effect of an unrelated change.
