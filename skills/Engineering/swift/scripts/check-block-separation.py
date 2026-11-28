#!/usr/bin/env python3
"""Enforce blank-line block separation in Swift sources.

Rule: a blank line separates a block-opening statement (if, for, while,
repeat, switch, do, return) and a control-flow block closing brace from
independent statements before and after it at the same indentation level.
Grouped code stays together without internal blank lines: a declaration
and the statements immediately defining or consuming it, and a guard
clause with its protected group.

Blank lines inside string literals or comments are never touched.

Usage: check-block-separation.py [--fix] FILE [FILE ...]

Exit codes: 0 clean or fixed, 1 violations in check mode, 2 usage error.
"""

import argparse
import re
import sys
from pathlib import Path

BLOCK_START = re.compile(r"^(if|for|while|repeat|switch|do|return)\b")
DECLARATION_START = re.compile(r"^(let|var)\b")
DECLARATION_NAME = re.compile(r"^(let|var)\s+([A-Za-z_][A-Za-z0-9_]*)")
MEMBER_DECLARATION = re.compile(r"^(func|deinit|subscript)\b")
RETURN_START = re.compile(r"^return\b")
LAST_WORD = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*$")
CONTROL_OPENERS = {"if", "for", "while", "repeat", "switch", "do"}
STAY_ATTACHED = ("else", "catch", "case", "default", "}", "@", ".")


def code_part(line, state):
    """Return the executable-code prefix of a line, updating parser state.

    state is a dict with keys "block_comment" and "multiline_string".
    """
    if state["block_comment"]:
        end = line.find("*/")
        if end == -1:
            return ""
        state["block_comment"] = False
        line = line[end + 2:]
    if state["multiline_string"]:
        end = line.find('"""')
        if end == -1:
            return ""
        state["multiline_string"] = False
        line = line[end + 3:]

    code = []
    index = 0
    length = len(line)
    while index < length:
        char = line[index]
        two = line[index:index + 2]
        three = line[index:index + 3]
        if two == "//":
            break
        if two == "/*":
            end = line.find("*/", index + 2)
            if end == -1:
                state["block_comment"] = True
                break
            index = end + 2
            continue
        if three == '"""':
            state["multiline_string"] = True
            break
        if char == '"':
            index += 1
            escaped = False
            while index < length:
                inner = line[index]
                if escaped:
                    escaped = False
                elif inner == "\\":
                    escaped = True
                elif inner == '"':
                    index += 1
                    break
                index += 1
            code.append('""')
            continue
        code.append(char)
        index += 1
    return "".join(code)


def opener_kind(code_before_brace: str, previous_kind: str) -> str:
    """Classify the block a brace opens, based on the word in front of it."""
    if code_before_brace.strip().startswith("guard"):
        return "guard"
    match = LAST_WORD.search(code_before_brace)
    word = match.group(1) if match else ""
    if word in CONTROL_OPENERS:
        return "control"
    if word == "else" and previous_kind in ("control", "guard"):
        return previous_kind
    if word == "catch":
        return previous_kind
    return "other"


class BraceTracker:
    """Track whether the previous line closed a control-flow or guard block."""

    def __init__(self):
        self.stack = []
        self.last_line_closed_control = False
        self.last_line_closed_guard = False
        self.pending_guard = False

    def feed(self, code: str) -> None:
        if not code.strip():
            return
        if code.strip().startswith("guard"):
            self.pending_guard = True
        closed_control = False
        closed_guard = False
        for index, char in enumerate(code):
            if char == "{":
                previous = self.stack[-1] if self.stack else "other"
                kind = opener_kind(code[:index], previous)
                word_match = LAST_WORD.search(code[:index])
                word = word_match.group(1) if word_match else ""
                if self.pending_guard and word == "else":
                    kind = "guard"
                    self.pending_guard = False
                self.stack.append(kind)
            elif char == "}":
                kind = self.stack.pop() if self.stack else "other"
                if kind == "control":
                    closed_control = True
                if kind == "guard":
                    closed_guard = True
        stripped = code.rstrip()
        ends_block = stripped.endswith("}") and not stripped.endswith("{")
        self.last_line_closed_control = closed_control and ends_block
        self.last_line_closed_guard = closed_guard and ends_block


def needs_blank_before(code_lines, index, tracker):
    """Decide whether a blank line is required before lines[index]."""
    current = code_lines[index]
    current_indent = len(current) - len(current.lstrip(" "))
    current_code = current.strip()
    previous = code_lines[index - 1]
    previous_indent = len(previous) - len(previous.lstrip(" "))
    previous_code = previous.strip()
    if not previous_code:
        return False
    if current_code.startswith(STAY_ATTACHED):
        return False
    if previous_indent != current_indent:
        return False
    if previous_code.startswith("//") or previous_code.startswith("/*"):
        return False
    if previous_code.startswith("#"):
        return False
    if previous_code.startswith("case ") or previous_code.startswith("case\t"):
        return False
    if tracker.last_line_closed_guard and previous_code.endswith("}"):
        return False
    closed_control = tracker.last_line_closed_control and previous_code.endswith("}")
    opens_block = BLOCK_START.match(current_code) is not None
    if not opens_block and not closed_control:
        return False
    if current_code.startswith("@"):
        return False
    if previous_code.endswith("{") or previous_code.endswith(",") or previous_code.endswith("("):
        return False
    if previous_code.endswith("} else {") or previous_code.endswith(" else {"):
        return False
    if (
        previous_indent == current_indent
        and DECLARATION_START.match(previous_code)
        and not current_code.startswith("return")
        and not closed_control
    ):
        return False
    return True


def block_span_end(code_lines, start):
    """Return the last line index of the statement starting at start."""
    depth = 0
    seen_open = False
    for index in range(start, len(code_lines)):
        for char in code_lines[index]:
            if char == "{":
                depth += 1
                seen_open = True
            elif char == "}":
                depth -= 1
        if not seen_open or depth <= 0:
            return index
    return len(code_lines) - 1


def grouping_removal(code_lines, tracker, index):
    """Return blank-line indexes to drop before index, or an empty set.

    Two grouping rules remove blank lines: a declaration immediately
    followed by its defining or consuming statement, and a guard clause
    followed by its protected group. A blank line before a return always
    stays.
    """
    current = code_lines[index]
    if not current.strip():
        return set()
    current_indent = len(current) - len(current.lstrip(" "))
    current_code = current.strip()
    if RETURN_START.match(current_code) or current_code.startswith(STAY_ATTACHED):
        return set()
    if MEMBER_DECLARATION.match(current_code):
        return set()

    previous = index - 1
    while previous >= 0 and not code_lines[previous].strip():
        previous -= 1
    if previous < 0:
        return set()
    previous_code = code_lines[previous].strip()
    previous_indent = len(code_lines[previous]) - len(code_lines[previous].lstrip(" "))
    if previous_indent != current_indent:
        return set()

    blanks = set(range(previous + 1, index))
    if not blanks:
        return set()

    closed_guard = tracker.last_line_closed_guard and previous_code.endswith("}")
    if closed_guard:
        return blanks

    match = DECLARATION_NAME.match(previous_code)
    if not match:
        return set()
    name = match.group(2)
    span_end = block_span_end(code_lines, index)
    span = " ".join(code_lines[index:span_end + 1])
    if re.search(r"\b" + re.escape(name) + r"\b", span):
        return blanks
    return set()


def process(path, fix):
    """Return the violations for one file and whether --fix rewrote it."""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    state = {"block_comment": False, "multiline_string": False}
    tracker = BraceTracker()
    code_lines = []
    for line in lines:
        code_lines.append(code_part(line, state))
        tracker.feed(code_lines[-1])
    insert_lines = set()
    tracker = BraceTracker()
    for index, code in enumerate(code_lines):
        if index > 0 and code.strip() and needs_blank_before(code_lines, index, tracker):
            insert_lines.add(index)
        tracker.feed(code)
    removals = {}
    tracker = BraceTracker()
    for index, code in enumerate(code_lines):
        if index > 0:
            span = grouping_removal(code_lines, tracker, index)
            if span:
                removals[index] = span
        tracker.feed(code)
    violations = []
    fixed_lines = []
    skipped_blanks = set()
    for span in removals.values():
        skipped_blanks.update(span)
    for index, line in enumerate(lines):
        if index in skipped_blanks and not line.strip():
            if not fix:
                violations.append(f"{path}:{index + 1}: blank line inside declaration/guard grouping")
            continue
        if index in insert_lines and index > 0 and fixed_lines and fixed_lines[-1].strip():
            violations.append(f"{path}:{index + 1}: missing blank line before block statement")
            if fix:
                fixed_lines.append("")
        fixed_lines.append(line.rstrip() if not line.strip() else line)
    changed = fix and fixed_lines != lines
    if changed:
        path.write_text("\n".join(fixed_lines), encoding="utf-8")
    return violations, changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fix", action="store_true", help="apply blank-line grouping fixes")
    parser.add_argument("files", nargs="+", help="swift files to check")
    args = parser.parse_args()
    violations = []
    changed_files = 0
    for name in args.files:
        file_violations, changed = process(Path(name), args.fix)
        violations.extend(file_violations)
        if changed:
            changed_files += 1
    if args.fix:
        print(f"fixed blank-line separation in {changed_files} file(s)")
        return 0
    for violation in violations:
        print(violation, file=sys.stderr)
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
