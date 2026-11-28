#!/usr/bin/env python3
"""Insert the structural blank lines that clang-format does not create.

clang-format preserves a blank line but never invents one. Two layout rules are
therefore checked and applied here:

  * a return statement is set off from the code that computes its value;
  * a control block is set off from the statement before and after it, while a
    break or continue stays with the block it ends.

Usage: add-blank-lines.py [--check] [paths...]

Without paths, the script uses the C and C++ files tracked by the enclosing git
repository, including untracked files that are not ignored. Paths are resolved
from the current working directory.

Exit codes: 0 clean or rewritten, 1 --check found missing blank lines,
2 usage or repository error.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx"}

BLOCK_OPEN = re.compile(r"^(?:if|for|while|switch|do|try)\b")
RETURN = re.compile(r"^(?:co_)?return\b")
CLOSE_ONLY = re.compile(r"^\}$")
# Lines that continue the statement above instead of starting a new one.
CONTINUATION = re.compile(r"^(?:else|catch|while)\b|^[)}\],;.:+*/&|=<>?-]")
LOOP_JUMP = re.compile(r"^(?:break|continue)\s*;")


def run_git(arguments: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *arguments],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as error:
        print(f"git is required to discover project files: {error}", file=sys.stderr)
        raise SystemExit(2) from error
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "git failed"
        print(f"add-blank-lines.py: {message}", file=sys.stderr)
        raise SystemExit(2)
    return result.stdout


def repository_root() -> pathlib.Path:
    return pathlib.Path(run_git(["rev-parse", "--show-toplevel"]).strip())


def project_files(root: pathlib.Path) -> list[pathlib.Path]:
    output = run_git(["-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"])
    files = []
    for name in output.split("\0"):
        if not name:
            continue
        path = root / name
        if path.suffix in SOURCE_SUFFIXES and path.is_file():
            files.append(path)
    return files


def opens_block(text: str) -> bool:
    return text.endswith("{")


def closes_block(text: str) -> bool:
    """True for a closing brace, or a one-line control statement."""
    body = text.strip()
    if CLOSE_ONLY.match(body):
        return True
    return bool(BLOCK_OPEN.match(body)) and not opens_block(body) and body.endswith(";")


def wants_blank(previous: str | None, line: str, previous_closes_block: bool) -> bool:
    body = line.strip()
    if not body or body.startswith("#") or body.startswith("}"):
        return False
    if LOOP_JUMP.match(body):
        return False
    if previous is None:
        return False
    above = previous.strip()
    if not above or opens_block(above) or above.endswith(":"):
        return False
    if BLOCK_OPEN.match(body) or RETURN.match(body):
        return True
    return previous_closes_block and not CONTINUATION.match(body)


def add_blank_lines(text: str, path: pathlib.Path, root: pathlib.Path, report: list[str]) -> tuple[str, bool]:
    lines = text.splitlines(keepends=True)
    newline = "\r\n" if "\r\n" in text else "\n"
    output: list[str] = []
    changed = False
    for number, line in enumerate(lines, start=1):
        last = next((item for item in reversed(output) if item.strip()), None)
        if wants_blank(last, line, bool(last and closes_block(last))):
            above = output[-1].strip() if output else ""
            if above and not opens_block(above) and not above.endswith(":"):
                try:
                    shown = path.resolve().relative_to(root)
                except ValueError:
                    shown = path
                report.append(f"{shown}:{number}: missing blank line before '{line.strip()[:40]}'")
                output.append(newline)
                changed = True
        output.append(line)
    return "".join(output), changed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Insert or check the structural blank lines clang-format does not create."
    )
    parser.add_argument("--check", action="store_true", help="report missing blank lines without writing")
    parser.add_argument("paths", nargs="*", help="C or C++ files; defaults to the enclosing git repository")
    args = parser.parse_args()

    root = repository_root()
    if args.paths:
        targets = [pathlib.Path(item).resolve() for item in args.paths]
    else:
        targets = project_files(root)

    problems: list[str] = []
    rewritten = 0
    for path in targets:
        if path.suffix not in SOURCE_SUFFIXES:
            print(f"skipping non-C++ file: {path}", file=sys.stderr)
            continue
        try:
            with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
                text = handle.read()
        except OSError as error:
            print(f"{path}: {error}", file=sys.stderr)
            return 2
        report: list[str] = []
        updated, changed = add_blank_lines(text, path, root, report)
        if not changed:
            continue
        if args.check:
            problems.extend(report)
        else:
            with path.open("w", encoding="utf-8", newline="") as handle:
                handle.write(updated)
            rewritten += 1

    if problems:
        print("Blank lines are missing:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print("Run format-cpp.sh or add the blank lines by hand.", file=sys.stderr)
        return 1
    if args.check:
        print(f"blank lines clean on {len(targets)} file(s)")
    else:
        print(f"added blank lines in {rewritten} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
