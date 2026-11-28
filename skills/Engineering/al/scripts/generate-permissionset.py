#!/usr/bin/env python3
"""Generate or verify a Business Central permission set object from a JSON spec.

Hand-assembled permission sets drift: entries are duplicated, rights differ
between environments, and the order changes with whoever typed last. This
script renders the object reproducibly from a spec that can be reviewed like
code and checked in CI.

Usage:
    python3 generate-permissionset.py SPEC.json
    python3 generate-permissionset.py SPEC.json --out "My Set.al"
    python3 generate-permissionset.py SPEC.json --check "My Set.al"

Exit codes:
    0  generated output on stdout, wrote --out, or the checked file matches
    1  the checked file differs from the spec
    2  usage error or invalid specification

Specification:

    {
      "id": 50100,
      "name": "APP ADMIN",
      "caption": "App Admin",
      "assignable": true,
      "permissions": [
        {"type": "tabledata", "name": "Customer", "rights": "RIMD"},
        {"type": "page", "name": "Customer Card", "rights": "X"},
        {"type": "codeunit", "name": "Customer Mgt.", "rights": "X"}
      ]
    }

Rights are canonicalized to RIMDX order with their case preserved: uppercase
letters are direct permissions and lowercase letters are indirect permissions,
so the case is part of the meaning. Duplicate (type, name) entries with the
same rights collapse; a duplicate with different rights is an error, because
merging the two would silently change what the set grants. Entries are sorted
by type and then by name, so the same spec always produces the same object.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TYPE_ORDER = ("tabledata", "table", "page", "report", "codeunit", "query", "xmlport")
RIGHTS_ORDER = "RIMDX"
IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def fail(message: str, code: int = 2) -> None:
    print(f"generate-permissionset.py: {message}", file=sys.stderr)
    raise SystemExit(code)


def al_identifier(name: str) -> str:
    return name if IDENTIFIER.match(name) else f'"{name}"'


def al_string(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def require_text(value: object, field: str, limit: int | None = None) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"'{field}' must be a non-empty string")
    text = value.strip()
    if any(ch in text for ch in '"\n\r\t'):
        fail(f"'{field}' must not contain quotes, tabs, or line breaks: {text!r}")
    if limit is not None and len(text) > limit:
        fail(f"'{field}' is {len(text)} characters; the limit is {limit}: {text!r}")
    return text


def canonical_rights(value: object, field: str) -> str:
    text = require_text(value, field)
    unknown = sorted({ch for ch in text if ch.upper() not in RIGHTS_ORDER})
    if unknown:
        fail(
            f"{field} contains {''.join(unknown)!r}; allowed letters are "
            "R, I, M, D, X and their lowercase forms"
        )
    return "".join(
        ch for base in RIGHTS_ORDER for ch in (base, base.lower()) if ch in text
    )


def load_spec(path: Path) -> dict:
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"spec file not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"spec is not valid JSON: {exc}")
    if not isinstance(spec, dict):
        fail("spec must be a JSON object")
    return spec


def normalize(spec: dict) -> tuple[dict, list[tuple[str, str, str]]]:
    object_id = spec.get("id")
    if not isinstance(object_id, int) or isinstance(object_id, bool) or object_id <= 0:
        fail("'id' must be a positive integer")

    assignable = spec.get("assignable", True)
    if not isinstance(assignable, bool):
        fail("'assignable' must be true or false")

    name_limit = 20 if assignable else 30
    name = require_text(spec.get("name"), "name", name_limit)
    caption = spec.get("caption")
    if caption is not None:
        caption = require_text(caption, "caption")

    raw = spec.get("permissions")
    if not isinstance(raw, list) or not raw:
        fail("'permissions' must be a non-empty list")

    merged: dict[tuple[str, str], str] = {}
    for index, entry in enumerate(raw):
        if not isinstance(entry, dict):
            fail(f"permissions[{index}] must be an object")
        kind = require_text(entry.get("type"), f"permissions[{index}].type").lower()
        if kind not in TYPE_ORDER:
            fail(
                f"permissions[{index}].type is {kind!r}; expected one of "
                + ", ".join(TYPE_ORDER)
            )
        object_name = require_text(entry.get("name"), f"permissions[{index}].name")
        rights = canonical_rights(entry.get("rights"), f"permissions[{index}].rights")
        current = merged.get((kind, object_name))
        if current is None:
            merged[(kind, object_name)] = rights
        elif current != rights:
            fail(
                f"permissions[{index}] repeats {kind} {object_name!r} with different "
                f"rights ({current!r} and {rights!r}); consolidate the entries in the spec"
            )

    entries = [
        (kind, object_name, rights)
        for (kind, object_name), rights in merged.items()
    ]
    entries.sort(key=lambda entry: (TYPE_ORDER.index(entry[0]), entry[1].casefold(), entry[1]))

    normalized = {
        "id": object_id,
        "name": name,
        "caption": caption,
        "assignable": assignable,
    }
    return normalized, entries


def render(spec: dict, entries: list[tuple[str, str, str]]) -> str:
    lines = [f'permissionset {spec["id"]} {al_identifier(spec["name"])}', "{"]
    if spec["caption"] is not None:
        lines.append(f"    Caption = {al_string(spec['caption'])};")
    if spec["assignable"] is not None:
        lines.append(f"    Assignable = {'true' if spec['assignable'] else 'false'};")

    head = "    Permissions = "
    continuation = " " * len(head)
    rendered = [f"{kind} {al_identifier(name)} = {rights}" for kind, name, rights in entries]
    for index, entry in enumerate(rendered):
        prefix = head if index == 0 else continuation
        suffix = "," if index < len(rendered) - 1 else ";"
        lines.append(prefix + entry + suffix)
    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("spec", type=Path, help="JSON specification")
    parser.add_argument("--out", type=Path, help="write the generated object here")
    parser.add_argument("--check", type=Path, help="fail when this file differs from the spec")
    args = parser.parse_args()

    if args.out and args.check:
        fail("--out and --check cannot be combined")

    spec, entries = normalize(load_spec(args.spec))
    output = render(spec, entries)

    if args.check:
        try:
            existing = args.check.read_text(encoding="utf-8").replace("\r\n", "\n")
        except FileNotFoundError:
            fail(f"file to check not found: {args.check}", 1)
        if existing != output:
            print(f"{args.check}: differs from {args.spec}", file=sys.stderr)
            expected = output.splitlines()
            actual = existing.splitlines()
            for number, (want, have) in enumerate(zip(expected, actual), start=1):
                if want != have:
                    print(f"  first difference at line {number}", file=sys.stderr)
                    print(f"  expected: {want}", file=sys.stderr)
                    print(f"  actual:   {have}", file=sys.stderr)
                    break
            else:
                print(
                    f"  expected {len(expected)} lines, found {len(actual)}",
                    file=sys.stderr,
                )
            return 1
        print(f"{args.check}: matches {args.spec}")
        return 0

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
        print(f"wrote {args.out} ({len(entries)} permission entries)")
        return 0

    sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
