#!/usr/bin/env python3
"""Inspect, merge, and export Business Central XLIFF translation units.

Business Central imports the XLIFF file that the AL toolchain generates for the
app; the unit IDs belong to that file. This script therefore never invents IDs.
It works on the generated file textually and changes only target elements, so
IDs, notes, comments, and formatting survive a merge or import.

Usage:
    python3 translation-tool.py status --lang-file de-DE.xlf [--base-file NEW.xlf] [--source app]
    python3 translation-tool.py merge --base NEW.xlf --previous OLD.xlf --out de-DE.xlf
    python3 translation-tool.py export --lang-file de-DE.xlf --out units.csv
    python3 translation-tool.py import --lang-file de-DE.xlf --csv units.csv --out de-DE.xlf

Exit codes:
    0  clean
    1  findings: empty targets, units missing from the file, lost translations,
       unknown IDs, or a locked label with a translation
    2  usage or file error

The label scan reads .al sources textually. It recognises Label '...' with a
trailing Comment and Locked property in the same statement. It does not parse
AL, so treat its result as a completeness check for humans.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

WORK_STATES = {
    "needs-translation",
    "needs-review-translation",
    "needs-adaptation",
    "needs-l10n",
}

UNIT_START = re.compile(r"<trans-unit\b[^>]*>", re.S)
SOURCE = re.compile(r"<source\b[^>]*>(.*?)</source>", re.S)
NOTE = re.compile(r"<note\b[^>]*>(.*?)</note>", re.S)
TARGET = re.compile(r"<target\b([^>]*?)(/>|>(.*?)</target>)", re.S)
ENTITY = re.compile(r"&(#x[0-9A-Fa-f]+|#[0-9]+|[a-z]+);")

LABEL = re.compile(r"\bLabel\s+'((?:[^']|'')*)'", re.IGNORECASE)
COMMENT = re.compile(r"\bComment\s*=\s*'((?:[^']|'')*)'", re.IGNORECASE)
LOCKED = re.compile(r"\bLocked\s*=\s*true\b", re.IGNORECASE)

NAMED_ENTITIES = {"amp": "&", "lt": "<", "gt": ">", "quot": '"', "apos": "'"}


def fail(message: str, code: int = 2) -> None:
    print(f"translation-tool.py: {message}", file=sys.stderr)
    raise SystemExit(code)


def unescape(text: str) -> str:
    def replace(match: re.Match) -> str:
        body = match.group(1)
        if body[:2].lower() == "#x":
            return chr(int(body[2:], 16))
        if body.startswith("#"):
            return chr(int(body[1:]))
        return NAMED_ENTITIES.get(body, match.group(0))

    return ENTITY.sub(replace, text)


def escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def attribute(tag: str, name: str) -> str:
    match = re.search(rf"\b{name}\s*=\s*(\"([^\"]*)\"|'([^']*)')", tag)
    if not match:
        return ""
    return match.group(2) if match.group(2) is not None else match.group(3)


def load_text(path: Path) -> str:
    if not path.exists():
        fail(f"file not found: {path}")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        fail(f"{path} is not UTF-8; pass the encoding the AL toolchain produced")


def read_units(text: str) -> list[dict]:
    units = []
    index = 0
    position = 0
    while True:
        start = UNIT_START.search(text, position)
        if start is None:
            return units
        end = text.find("</trans-unit>", start.end())
        if end == -1:
            fail(f"unterminated trans-unit near offset {start.start()}")
        end += len("</trans-unit>")
        block = text[start.start() : end]
        source = SOURCE.search(block)
        note = NOTE.search(block)
        target = TARGET.search(block)
        units.append(
            {
                "index": index,
                "start": start.start(),
                "end": end,
                "block": block,
                "id": attribute(start.group(0), "id"),
                "source": unescape(source.group(1)) if source else "",
                "target": unescape(target.group(3) or "") if target else "",
                "state": attribute(target.group(0), "state") if target else "",
                "note": unescape(note.group(1)) if note else "",
            }
        )
        index += 1
        position = end


def with_target(block: str, value: str, state: str) -> str:
    target = TARGET.search(block)
    escaped = escape(value)
    if target is not None:
        attributes = target.group(1)
        if re.search(r"\bstate\s*=", attributes):
            attributes = re.sub(
                r"\bstate\s*=\s*(\"[^\"]*\"|'[^']*')",
                f'state="{state}"',
                attributes,
                count=1,
            )
        else:
            attributes = attributes.rstrip() + f' state="{state}"'
        replacement = f"<target{attributes}>{escaped}</target>"
        return block[: target.start()] + replacement + block[target.end() :]

    sibling = SOURCE.search(block)
    anchor = sibling.start() if sibling else block.rfind("</trans-unit>")
    line_start = block.rfind("\n", 0, anchor) + 1
    indent = block[line_start:anchor]
    if not sibling:
        indent += "  "
    closing = block.rfind("</trans-unit>")
    closing_line = block.rfind("\n", 0, closing) + 1
    element = f'{indent}<target state="{state}">{escaped}</target>\n'
    return block[:closing_line] + element + block[closing_line:]


def apply_targets(text: str, replacements: dict[int, str]) -> str:
    pieces = []
    position = 0
    for unit in read_units(text):
        if unit["index"] not in replacements:
            continue
        pieces.append(text[position : unit["start"]])
        pieces.append(with_target(unit["block"], replacements[unit["index"]], "translated"))
        position = unit["end"]
    pieces.append(text[position:])
    return "".join(pieces)


def scan_labels(paths: list[Path]) -> list[dict]:
    files: list[Path] = []
    for path in paths:
        if not path.exists():
            fail(f"source path not found: {path}")
        files.extend([path] if path.is_file() else sorted(path.rglob("*.al")))

    labels = []
    for path in files:
        if path.suffix.lower() != ".al":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in LABEL.finditer(text):
            statement = text[match.end() : match.end() + 400].split(";", 1)[0]
            comment = COMMENT.search(statement)
            labels.append(
                {
                    "text": match.group(1).replace("''", "'"),
                    "comment": comment.group(1).replace("''", "'") if comment else "",
                    "locked": bool(LOCKED.search(statement)),
                    "path": path,
                    "line": text.count("\n", 0, match.start()) + 1,
                }
            )
    return labels


def pending(units: list[dict]) -> list[dict]:
    return [
        unit
        for unit in units
        if not unit["target"].strip() or unit["state"].lower() in WORK_STATES
    ]


def command_status(args: argparse.Namespace) -> int:
    units = read_units(load_text(args.lang_file))
    findings = 0

    empty = [unit for unit in units if not unit["target"].strip()]
    work = [unit for unit in units if unit["state"].lower() in WORK_STATES]
    print(f"{args.lang_file}: {len(units)} units, {len(units) - len(empty)} translated")
    if empty:
        findings += len(empty)
        print(f"  {len(empty)} units have no target text")
        for unit in empty[:10]:
            print(f"    {unit['id']}  {unit['source'][:70]!r}")
        if len(empty) > 10:
            print(f"    ... and {len(empty) - 10} more")
    if work:
        findings += len(work)
        print(f"  {len(work)} units are marked as needing work")

    if args.base_file:
        base_units = read_units(load_text(args.base_file))
        language_ids = {unit["id"] for unit in units}
        base_ids = {unit["id"] for unit in base_units}
        new = [unit for unit in base_units if unit["id"] not in language_ids]
        stale = [unit for unit in units if unit["id"] not in base_ids]
        if new:
            findings += len(new)
            print(f"  {len(new)} units in {args.base_file} are missing from the language file")
            for unit in new[:10]:
                print(f"    {unit['id']}  {unit['source'][:70]!r}")
        if stale:
            findings += len(stale)
            print(f"  {len(stale)} units no longer exist in {args.base_file}")
            for unit in stale[:10]:
                print(f"    {unit['id']}  {unit['source'][:70]!r}")

    if args.source:
        labels = scan_labels(args.source)
        sources = {unit["source"] for unit in units}
        missing = [label for label in labels if label["text"] not in sources]
        if missing:
            findings += len(missing)
            print(f"  {len(missing)} labels from source are not in the language file")
            for label in missing[:10]:
                print(f"    {label['path']}:{label['line']} {label['text']!r}")
        translated_locked = [
            unit
            for unit in units
            if any(label["locked"] and label["text"] == unit["source"] for label in labels)
            and unit["target"].strip()
            and unit["target"].strip() != unit["source"]
        ]
        if translated_locked:
            findings += len(translated_locked)
            print(f"  {len(translated_locked)} locked labels carry translated text")
            for unit in translated_locked[:10]:
                print(f"    {unit['id']}  {unit['source'][:70]!r}")

    print("  result: clean" if findings == 0 else f"  result: {findings} findings")
    return 0 if findings == 0 else 1


def command_merge(args: argparse.Namespace) -> int:
    base_text = load_text(args.base)
    base_units = read_units(base_text)
    previous_units = read_units(load_text(args.previous))

    by_id = {unit["id"]: unit for unit in previous_units if unit["id"]}
    by_source: dict[tuple[str, str], dict] = {}
    for unit in previous_units:
        if unit["target"].strip():
            by_source.setdefault((unit["source"], unit["note"]), unit)

    replacements: dict[int, str] = {}
    used: set[int] = set()
    from_id = from_source = 0
    for unit in base_units:
        candidate = by_id.get(unit["id"])
        if candidate is not None and candidate["target"].strip():
            from_id += 1
            used.add(id(candidate))
        else:
            candidate = by_source.get((unit["source"], unit["note"]))
            if candidate is None or not candidate["target"].strip():
                continue
            from_source += 1
            used.add(id(candidate))
        replacements[unit["index"]] = candidate["target"]

    lost = [unit for unit in previous_units if unit["target"].strip() and id(unit) not in used]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(apply_targets(base_text, replacements), encoding="utf-8")
    print(
        f"{args.out}: {len(base_units)} units, {from_id} from the same ID, "
        f"{from_source} matched by source text, {len(base_units) - len(replacements)} left empty"
    )
    if lost:
        print(f"  {len(lost)} translated units from {args.previous} had no counterpart:")
        for unit in lost[:10]:
            print(f"    {unit['id']}  {unit['source'][:70]!r}")
        print("  review them before importing the merged file")
        return 1
    return 0


def command_export(args: argparse.Namespace) -> int:
    units = read_units(load_text(args.lang_file))
    selected = units if args.all else pending(units)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["id", "source", "target", "state", "note"])
        for unit in selected:
            writer.writerow(
                [unit["id"], unit["source"], unit["target"], unit["state"], unit["note"]]
            )
    print(f"{args.out}: {len(selected)} units exported")
    return 0


def command_import(args: argparse.Namespace) -> int:
    text = load_text(args.lang_file)
    units = read_units(text)
    by_id = {unit["id"]: unit for unit in units if unit["id"]}

    if not args.csv.exists():
        fail(f"file not found: {args.csv}")
    replacements: dict[int, str] = {}
    unknown: list[str] = []
    with args.csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        if "id" not in fields or "target" not in fields:
            fail(f"{args.csv} needs at least the columns id and target")
        for row in reader:
            unit_id = (row.get("id") or "").strip()
            value = (row.get("target") or "").strip()
            if not value:
                continue
            unit = by_id.get(unit_id)
            if unit is None:
                unknown.append(unit_id)
                continue
            replacements[unit["index"]] = value

    args.out.parent.mkdir(parents=True, exist_ok=True)
    output = apply_targets(text, replacements)
    args.out.write_text(output, encoding="utf-8")
    remaining = len(pending(read_units(output)))
    print(f"{args.out}: {len(replacements)} translations applied, {remaining} units still open")
    if unknown:
        print(f"  {len(unknown)} rows reference IDs that do not exist in {args.lang_file}:")
        for unit_id in unknown[:10]:
            print(f"    {unit_id}")
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="report gaps in a language file")
    status.add_argument("--lang-file", type=Path, required=True)
    status.add_argument("--base-file", type=Path, help="newly generated XLIFF to compare against")
    status.add_argument(
        "--source",
        type=Path,
        nargs="*",
        help="AL source files or directories, to check that every label has a unit",
    )
    status.set_defaults(handler=command_status)

    merge = subparsers.add_parser("merge", help="carry translations into a regenerated file")
    merge.add_argument("--base", type=Path, required=True, help="newly generated XLIFF")
    merge.add_argument("--previous", type=Path, required=True, help="previously translated XLIFF")
    merge.add_argument("--out", type=Path, required=True)
    merge.set_defaults(handler=command_merge)

    export = subparsers.add_parser("export", help="write open units to CSV for translators")
    export.add_argument("--lang-file", type=Path, required=True)
    export.add_argument("--out", type=Path, required=True)
    export.add_argument("--all", action="store_true", help="export every unit, not only open ones")
    export.set_defaults(handler=command_export)

    importer = subparsers.add_parser("import", help="apply translated CSV rows to a language file")
    importer.add_argument("--lang-file", type=Path, required=True)
    importer.add_argument("--csv", type=Path, required=True)
    importer.add_argument("--out", type=Path, required=True)
    importer.set_defaults(handler=command_import)

    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
