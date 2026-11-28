#!/usr/bin/env python3
"""Check the runtime command dependencies declared by every skill.

Each skill package carries a ``meta.json`` file with its required
executables. Each matching SKILL.md must carry the generated Agent Skills
``compatibility`` string. ``check-format.py`` verifies that the dependency
files and the skill packages stay in sync.

Usage: python scripts/check-dependencies.py [SKILL ...]
       python scripts/check-dependencies.py --quiet
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


EXECUTABLE_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]*$")
VERSION_PATTERN = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
SKILL_META_FILE = "meta.json"
METADATA_SCHEMA_VERSION = 1


class SkillMetadataError(ValueError):
    """Skill metadata is missing or invalid."""


@dataclass(frozen=True)
class SkillMetadata:
    """Version and runtime commands for one skill.

    Every command must exist. There are no alternative or optional commands.
    """

    version: str
    required: tuple[str, ...] = ()
    detail: str | None = None


def load_skill_metadata(root: Path) -> dict[str, SkillMetadata]:
    """Load one metadata document from every skill package."""
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        raise SkillMetadataError(f"skills directory not found: {skills_dir}")

    registry: dict[str, SkillMetadata] = {}
    for skill_file in sorted(skills_dir.rglob("SKILL.md")):
        if ".git" in skill_file.relative_to(skills_dir).parts:
            continue
        package = skill_file.parent
        name = package.name
        if name in registry:
            raise SkillMetadataError(f"duplicate skill name {name!r}")

        metadata_path = package / SKILL_META_FILE
        relative = metadata_path.relative_to(root).as_posix()
        if not metadata_path.is_file():
            raise SkillMetadataError(f"{relative}: missing skill metadata")
        try:
            document = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SkillMetadataError(f"{relative}: invalid JSON: {exc}") from exc
        if not isinstance(document, dict):
            raise SkillMetadataError(f"{relative}: expected a JSON object")
        schema_version = document.get("schemaVersion")
        if type(schema_version) is not int or schema_version != METADATA_SCHEMA_VERSION:
            raise SkillMetadataError(
                f"{relative}: schemaVersion must be {METADATA_SCHEMA_VERSION}"
            )
        unknown_keys = set(document) - {"schemaVersion", "version", "requires", "detail"}
        if unknown_keys:
            raise SkillMetadataError(
                f"{relative}: unknown field(s): {', '.join(sorted(unknown_keys))}"
            )
        version = document.get("version")
        if not isinstance(version, str) or VERSION_PATTERN.fullmatch(version) is None:
            raise SkillMetadataError(
                f"{relative}: version must be stable SemVer MAJOR.MINOR.PATCH"
            )
        required = document.get("requires")
        if not isinstance(required, list) or not all(
            isinstance(command, str) for command in required
        ):
            raise SkillMetadataError(f"{relative}: requires must be a string list")
        detail = document.get("detail")
        if detail is not None and not isinstance(detail, str):
            raise SkillMetadataError(f"{relative}: detail must be a string")
        spec = SkillMetadata(
            version=version,
            required=tuple(required),
            detail=detail,
        )
        registry[name] = spec
    if not registry:
        raise SkillMetadataError(f"no skill packages found in {skills_dir}")
    return registry


def human_join(items: tuple[str, ...] | list[str]) -> str:
    """Join names with natural-language punctuation."""
    values = list(items)
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]} and {values[1]}"
    return f"{', '.join(values[:-1])}, and {values[-1]}"


def compatibility_for(spec: SkillMetadata) -> str | None:
    """Return the canonical compatibility text for a dependency spec."""
    if not spec.required:
        return None
    text = f"Requires {human_join(spec.required)}."
    if spec.detail:
        text += f" {spec.detail}"
    return text


def validate_skill_metadata(registry: dict[str, SkillMetadata]) -> list[str]:
    """Return structural problems in loaded skill metadata."""
    problems: list[str] = []
    for name, spec in registry.items():
        if not EXECUTABLE_PATTERN.fullmatch(name):
            problems.append(f"{name}: invalid skill name")
        if VERSION_PATTERN.fullmatch(spec.version) is None:
            problems.append(f"{name}: invalid version {spec.version!r}")
        if spec.required != tuple(sorted(spec.required)) or len(spec.required) != len(
            set(spec.required)
        ):
            problems.append(f"{name}: required commands must be unique and sorted")
        for command in spec.required:
            if not EXECUTABLE_PATTERN.fullmatch(command):
                problems.append(f"{name}: invalid executable name {command!r}")
        if spec.detail is not None:
            if not spec.detail or spec.detail != spec.detail.strip():
                problems.append(f"{name}: detail must be a non-empty trimmed string")
            if not spec.required:
                problems.append(f"{name}: detail requires at least one required command")
        compatibility = compatibility_for(spec)
        if compatibility is not None and len(compatibility) > 500:
            problems.append(f"{name}: compatibility exceeds 500 characters")
    return problems


def command_succeeds(path: str, args: tuple[str, ...]) -> bool:
    """Return whether an executable can run the required subcommand."""
    try:
        result = subprocess.run(
            [path, *args],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def command_candidates(command: str) -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Return executable and argument candidates for a logical command."""
    if command == "python3":
        return (
            ("python3", ()),
            ("python", ()),
            ("py", ("-3",)),
        )
    return ((command, ()),)


def has_command(command: str) -> bool:
    """Return whether a command and its required capabilities are available."""
    if command == "start" and sys.platform.startswith("win"):
        return True
    for executable, prefix in command_candidates(command):
        path = shutil.which(executable)
        if path is None:
            continue
        if command == "swift":
            if command_succeeds(path, (*prefix, "format", "--help")):
                return True
            continue
        if command == "cargo":
            rustdoc = shutil.which("rustdoc")
            if (
                rustdoc
                and command_succeeds(path, (*prefix, "fmt", "--version"))
                and command_succeeds(path, (*prefix, "clippy", "--version"))
                and command_succeeds(rustdoc, ("--version",))
            ):
                return True
            continue
        if command == "python3":
            if command_succeeds(
                path,
                (*prefix, "-c", "raise SystemExit(__import__('sys').version_info < (3, 10))"),
            ):
                return True
            continue
        return True
    return False


def missing_commands(spec: SkillMetadata) -> list[str]:
    """Return required commands that are unavailable."""
    return [command for command in spec.required if not has_command(command)]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check runtime commands declared in each skill's meta.json."
    )
    parser.add_argument(
        "skills",
        nargs="*",
        help="skill directory names to check; omit to check every registered skill",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="print only missing dependencies and the summary",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    try:
        registry = load_skill_metadata(root)
    except SkillMetadataError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    problems = validate_skill_metadata(registry)
    if problems:
        print("Dependency specification problems:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 2

    unknown = sorted(set(args.skills) - set(registry))
    if unknown:
        print(f"unknown skill(s): {', '.join(unknown)}", file=sys.stderr)
        return 2
    selected = args.skills or list(registry)

    print("Dependency check:")
    missing_required = 0
    failing_skills = 0
    for name in selected:
        spec = registry[name]
        missing = missing_commands(spec)
        if missing:
            failing_skills += 1
            missing_required += len(missing)
            print(f"  MISSING  {name}: {', '.join(missing)}")
        elif not args.quiet:
            if spec.required:
                print(f"  OK       {name}")
            else:
                print(f"  OK       {name}: no external commands")

    print(
        f"Summary: {len(selected)} skill(s) checked; {missing_required} missing required "
        f"command(s) in {failing_skills} skill(s)."
    )
    return 1 if missing_required else 0


if __name__ == "__main__":
    sys.exit(main())
