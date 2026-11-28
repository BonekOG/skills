#!/usr/bin/env python3
"""Run the repository CI checks on the current operating system.

Hosted CI runs only for pull requests targeting ``main``. Run this command on
the implementation machine before opening a pull request into ``dev`` so the
same checks execute once for the current platform.

Usage:
  python scripts/check-local.py [--base origin/dev]

Exit codes:
  0  all checks passed
  1  a check failed
  2  invalid command-line invocation
"""

from __future__ import annotations

import argparse
import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parent.parent


def run(command: Sequence[str]) -> None:
    display = subprocess.list2cmdline(list(command))
    print(f"+ {display}", flush=True)
    result = subprocess.run(command, cwd=ROOT, check=False)
    if result.returncode != 0:
        raise SystemExit(1)


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run repository CI checks for the current operating system."
    )
    parser.add_argument(
        "--base",
        default="origin/dev",
        help="Git ref used by the history-aware version check (default: origin/dev)",
    )
    parser.add_argument(
        "--allow-skill-version-reset",
        action="store_true",
        help="allow an intentional baseline reset of skill versions",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    print(
        f"Running local CI checks on {platform.system()} {platform.machine()}; "
        f"base={args.base}"
    )
    python = sys.executable
    with tempfile.TemporaryDirectory(prefix="skills-local-ci-") as temp:
        target = Path(temp) / "skills"
        release_check = [
            python,
            str(ROOT / "scripts" / "release.py"),
            "check",
            "--base",
            args.base,
        ]
        if args.allow_skill_version_reset:
            release_check.append("--allow-skill-version-reset")
        commands = (
            (python, str(ROOT / "scripts" / "check-format.py")),
            tuple(release_check),
            (
                python,
                str(ROOT / "scripts" / "install-skills.py"),
                "--target",
                str(target),
                "--dry-run",
            ),
            (
                python,
                str(ROOT / "scripts" / "install-skills.py"),
                "--target",
                str(target),
            ),
        )
        for command in commands:
            run(command)
    print("All local CI checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
