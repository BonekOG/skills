#!/usr/bin/env python3
"""Install skill packages into a Codex skills directory on any platform.

The installer discovers every package below ``skills/``, stages installable
copies, and then replaces installed packages with the same directory name.

Runtime commands reported by ``check-dependencies.py`` are advisory here: a
missing language toolchain does not prevent copying the skill files. The
dependency checker remains available for a strict machine-specific report.

Usage:
  python scripts/install-skills.py [--target DIR] [--skill NAME[,NAME...]] [--dry-run]
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Sequence


SKILL_META_FILE = "meta.json"


class InstallError(RuntimeError):
    """An installation invariant could not be satisfied."""


def default_target() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    root = Path(codex_home).expanduser() if codex_home else Path.home() / ".codex"
    return root / "skills"


def parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install skill packages without shell-specific tooling."
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=default_target(),
        help="installation directory (default: $CODEX_HOME/skills or ~/.codex/skills)",
    )
    parser.add_argument(
        "--skill",
        action="append",
        default=[],
        metavar="NAME[,NAME...]",
        help="install only these comma-separated packages",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report changes without copying or removing anything",
    )
    return parser.parse_args(argv)


def parse_skill_selection(values: Sequence[str]) -> list[str]:
    selected: list[str] = []
    for value in values:
        for name in value.split(","):
            name = name.strip()
            if not name:
                raise InstallError("--skill requires comma-separated skill names")
            selected.append(name)
    return sorted(set(selected))


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise InstallError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        sys.modules.pop(spec.name, None)
        raise InstallError(f"cannot load {path}: {exc}") from exc
    return module


def discover_packages(skills_dir: Path) -> dict[str, Path]:
    if not skills_dir.is_dir():
        raise InstallError(f"skills directory not found: {skills_dir}")
    packages: dict[str, Path] = {}
    for skill_file in sorted(skills_dir.rglob("SKILL.md")):
        if ".git" in skill_file.relative_to(skills_dir).parts:
            continue
        package = skill_file.parent
        name = package.name
        if name in packages:
            raise InstallError(
                f"duplicate skill directory name {name!r}; refusing to install"
            )
        packages[name] = package
    if not packages:
        raise InstallError(f"no skill packages found in {skills_dir}")
    return packages


def validate_dependencies(
    root: Path, packages: dict[str, Path], selected: list[str]
) -> None:
    checker = load_module(root / "scripts" / "check-dependencies.py", "skill_dependencies")
    try:
        registry = checker.load_skill_metadata(root)
    except checker.SkillMetadataError as exc:
        raise InstallError(str(exc)) from exc
    problems = checker.validate_skill_metadata(registry)
    if problems:
        raise InstallError(
            "dependency specification problems:\n"
            + "\n".join(f"- {problem}" for problem in problems)
        )

    missing_packages = sorted(set(registry) - set(packages))
    unregistered = sorted(set(packages) - set(registry))
    if missing_packages or unregistered:
        details: list[str] = []
        if missing_packages:
            details.append("metadata without packages: " + ", ".join(missing_packages))
        if unregistered:
            details.append("packages without metadata: " + ", ".join(unregistered))
        raise InstallError("skill metadata and packages disagree:\n- " + "\n- ".join(details))

    warnings = 0
    for name in selected:
        missing = checker.missing_commands(registry[name])
        if missing:
            warnings += 1
            print(
                f"warning: {name}: missing runtime command(s): {', '.join(missing)}",
                file=sys.stderr,
            )
    if warnings:
        print(
            "warning: skill files will still be installed; install the missing "
            "commands before using the affected skills.",
            file=sys.stderr,
        )


def path_exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def copy_package(source: Path, destination: Path) -> None:
    shutil.copytree(
        source,
        destination,
        symlinks=True,
        ignore=shutil.ignore_patterns(
            ".DS_Store", "__pycache__", "*.pyc", "*.pyo", SKILL_META_FILE
        ),
    )


def replace_package(staged: Path, destination: Path) -> bool:
    existed = path_exists(destination)
    backup: Path | None = None
    if existed:
        backup = destination.with_name(
            f".{destination.name}.skills-backup-{uuid.uuid4().hex}"
        )
        destination.rename(backup)
    try:
        shutil.move(str(staged), str(destination))
    except Exception:
        if path_exists(destination):
            remove_path(destination)
        if backup is not None and path_exists(backup):
            backup.rename(destination)
        raise
    if backup is not None and path_exists(backup):
        remove_path(backup)
    return existed


def install(
    packages: dict[str, Path],
    selected: list[str],
    target_dir: Path,
    dry_run: bool,
) -> int:
    installed = sum(1 for name in selected if not path_exists(target_dir / name))
    replaced = len(selected) - installed

    print(f"Source: {Path(__file__).resolve().parent.parent / 'skills'}")
    print(f"Target: {target_dir}")
    if dry_run:
        print("Mode:   dry run")
        for name in selected:
            action = "replace" if path_exists(target_dir / name) else "install"
            print(f"would {action:<7} {target_dir / name}")
        print(
            f"Summary: {installed} would be installed, {replaced} would be replaced."
        )
        return 0

    target_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".skills-install-", dir=target_dir.parent
    ) as temp:
        stage_root = Path(temp)
        for name in selected:
            copy_package(packages[name], stage_root / name)

        target_dir.mkdir(parents=True, exist_ok=True)
        for name in selected:
            destination = target_dir / name
            existed = replace_package(stage_root / name, destination)
            action = "replace" if existed else "install"
            print(f"{action:<7} {destination}")
    print(
        f"Summary: {installed} installed, {replaced} replaced, {len(selected)} total."
    )
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    root = Path(__file__).resolve().parent.parent
    try:
        packages = discover_packages(root / "skills")
        selected = parse_skill_selection(args.skill) if args.skill else sorted(packages)
        unknown = sorted(set(selected) - set(packages))
        if unknown:
            raise InstallError("unknown skill(s): " + ", ".join(unknown))

        validate_dependencies(root, packages, selected)
        return install(
            packages,
            selected,
            args.target.expanduser().resolve(),
            args.dry_run,
        )
    except (InstallError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
