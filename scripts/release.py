#!/usr/bin/env python3
"""Validate, plan, build, and publish repository releases.

Each package under skills/ has its own version in meta.json. The repository
has a separate root VERSION and v<semver> tag. Only the repository is
published; its release bundles the complete repository and records every
included skill version in skills-manifest.json.

Usage from the repository root:
  python scripts/release.py check --base origin/main
  python scripts/release.py plan --output release-plan.json
  python scripts/release.py build --plan release-plan.json --output-dir dist
  python scripts/release.py publish --plan release-plan.json --dist dist

The check, plan, and build commands need Git but no network access. publish
needs an authenticated GitHub CLI with permission to push tags and write
GitHub Releases.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import stat
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass
from functools import total_ordering
from pathlib import Path, PurePosixPath
from typing import Iterable, Sequence


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_PATTERN = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
PLAN_SCHEMA_VERSION = 3
REPOSITORY_NAME = "skills"
REPOSITORY_VERSION_FILE = "VERSION"
SKILL_META_FILE = "meta.json"
REPOSITORY_ARCHIVE_PREFIX = "skills"
IGNORED_NAMES = {".DS_Store"}
IGNORED_DIRECTORIES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".git", "dist"}
IGNORED_SUFFIXES = (".pyc", ".pyo")


class ReleaseError(RuntimeError):
    """A release invariant or external command failed."""


@total_ordering
@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, value: str, where: str = "version") -> "Version":
        match = SEMVER_PATTERN.fullmatch(value)
        if match is None:
            raise ReleaseError(
                f"{where}: expected stable SemVer MAJOR.MINOR.PATCH, got {value!r}"
            )
        return cls(*(int(part) for part in match.groups()))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (
            other.major,
            other.minor,
            other.patch,
        )


@dataclass(frozen=True)
class TreeEntry:
    path: str
    mode: int
    data: bytes


@dataclass(frozen=True)
class Package:
    name: str
    path: str
    version: Version | None
    entries: tuple[TreeEntry, ...]
    digest: str


@dataclass(frozen=True)
class ReleaseTag:
    name: str
    version: Version
    tag: str
    commit: str


def _run(
    command: Sequence[str],
    cwd: Path,
    *,
    check: bool = True,
) -> subprocess.CompletedProcess[bytes]:
    process = subprocess.run(
        list(command),
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and process.returncode != 0:
        stderr = process.stderr.decode("utf-8", errors="replace").strip()
        stdout = process.stdout.decode("utf-8", errors="replace").strip()
        detail = stderr or stdout or "no error output"
        raise ReleaseError(f"command failed ({process.returncode}): {' '.join(command)}\n{detail}")
    return process


def _decode(data: bytes, what: str) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ReleaseError(f"{what} is not valid UTF-8") from exc


def parse_version_bytes(data: bytes, where: str) -> Version:
    text = _decode(data, where)
    if "\r" in text or not text.endswith("\n") or text.count("\n") != 1:
        raise ReleaseError(f"{where}: VERSION must contain one version and one newline")
    value = text[:-1]
    if not value or value != value.strip():
        raise ReleaseError(f"{where}: VERSION must not contain surrounding whitespace")
    return Version.parse(value, where)


def parse_skill_meta_version(data: bytes, where: str) -> Version:
    try:
        document = json.loads(_decode(data, where))
    except json.JSONDecodeError as exc:
        raise ReleaseError(f"{where}: invalid JSON: {exc.msg}") from exc
    if not isinstance(document, dict):
        raise ReleaseError(f"{where}: expected a JSON object")
    if document.get("schemaVersion") != 1:
        raise ReleaseError(f"{where}: schemaVersion must be 1")
    version = document.get("version")
    if not isinstance(version, str):
        raise ReleaseError(f"{where}: missing string version")
    return Version.parse(version, f"{where}:version")


def package_version(
    meta_data: bytes | None,
    legacy_version_data: bytes | None,
    package_path: str,
    where: str,
) -> Version | None:
    """Read meta.json version, with VERSION support for older refs."""
    if meta_data is not None:
        return parse_skill_meta_version(
            meta_data, f"{where}:{package_path}/{SKILL_META_FILE}"
        )
    if legacy_version_data is not None:
        return parse_version_bytes(
            legacy_version_data, f"{where}:{package_path}/VERSION"
        )
    return None


def is_ignored(relative_path: str) -> bool:
    path = PurePosixPath(relative_path)
    return (
        any(part in IGNORED_NAMES or part in IGNORED_DIRECTORIES for part in path.parts)
        or any(part.endswith(IGNORED_SUFFIXES) for part in path.parts)
    )


def digest_entries(
    entries: Iterable[TreeEntry],
    *,
    exclude_paths: frozenset[str] = frozenset({"VERSION"}),
) -> str:
    digest = hashlib.sha256()
    for entry in sorted(entries, key=lambda item: item.path):
        if entry.path in exclude_paths or is_ignored(entry.path):
            continue
        kind = b"link" if stat.S_ISLNK(entry.mode) else b"file"
        executable = b"x" if entry.mode & 0o111 else b"-"
        digest.update(entry.path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(kind)
        digest.update(executable)
        digest.update(b"\0")
        digest.update(str(len(entry.data)).encode("ascii"))
        digest.update(b"\0")
        digest.update(entry.data)
    return digest.hexdigest()


class Repository:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self._package_cache: dict[str, dict[str, Package]] = {}
        self._blob_cache: dict[str, bytes] = {}
        self._index_modes: dict[str, int] | None = None

    def git(
        self, *args: str, check: bool = True
    ) -> subprocess.CompletedProcess[bytes]:
        return _run(("git", *args), self.root, check=check)

    def git_text(self, *args: str, check: bool = True) -> str:
        process = self.git(*args, check=check)
        return _decode(process.stdout, f"git {' '.join(args)} output").strip()

    def commit(self, ref: str) -> str:
        process = self.git("rev-parse", "--verify", f"{ref}^{{commit}}", check=False)
        if process.returncode != 0:
            raise ReleaseError(f"unknown Git ref: {ref}")
        return _decode(process.stdout, "commit id").strip()

    def blob(self, oid: str) -> bytes:
        if oid not in self._blob_cache:
            self._blob_cache[oid] = self.git("cat-file", "blob", oid).stdout
        return self._blob_cache[oid]

    def index_modes(self) -> dict[str, int]:
        """Return the staged Git mode for every indexed path."""
        if self._index_modes is not None:
            return self._index_modes
        modes: dict[str, int] = {}
        output = self.git("ls-files", "--stage", "-z").stdout
        for record in output.split(b"\0"):
            if not record:
                continue
            metadata, separator, raw_path = record.partition(b"\t")
            if not separator:
                continue
            fields = metadata.decode("ascii").split()
            if len(fields) != 3 or fields[2] != "0":
                continue
            path = _decode(raw_path, "Git index path")
            modes[path] = int(fields[0], 8)
        self._index_modes = modes
        return modes

    def worktree_mode(self, path: Path) -> int:
        """Return a stable file mode without relying on platform exec bits."""
        if path.is_symlink():
            return 0o120000
        relative = path.relative_to(self.root).as_posix()
        mode = self.index_modes().get(relative)
        if mode in (0o100644, 0o100755):
            return mode
        with path.open("rb") as handle:
            starts_with_shebang = handle.read(2) == b"#!"
        return 0o100755 if starts_with_shebang else 0o100644

    def tree_entries(
        self, ref: str, path: str | None = None
    ) -> list[tuple[str, int, str, str]]:
        command = ["ls-tree", "-r", "-z", "--full-tree", ref]
        if path is not None:
            command.extend(("--", path))
        output = self.git(*command).stdout
        entries: list[tuple[str, int, str, str]] = []
        for record in output.split(b"\0"):
            if not record:
                continue
            metadata, separator, raw_path = record.partition(b"\t")
            if not separator:
                raise ReleaseError(f"invalid git ls-tree output for {ref}:{path}")
            mode_text, object_type, oid = metadata.decode("ascii").split(" ")
            decoded_path = _decode(raw_path, "Git path")
            entries.append((decoded_path, int(mode_text, 8), object_type, oid))
        return entries

    def packages_at(self, ref: str) -> dict[str, Package]:
        commit = self.commit(ref)
        if commit in self._package_cache:
            return self._package_cache[commit]

        raw_entries = self.tree_entries(commit, "skills")
        skill_paths = [
            path for path, _mode, object_type, _oid in raw_entries
            if object_type == "blob" and path.endswith("/SKILL.md")
        ]
        packages: dict[str, Package] = {}
        for skill_path in skill_paths:
            package_path = str(PurePosixPath(skill_path).parent)
            name = PurePosixPath(package_path).name
            prefix = package_path + "/"
            entries: list[TreeEntry] = []
            meta_data: bytes | None = None
            legacy_version_data: bytes | None = None
            for path, mode, object_type, oid in raw_entries:
                if not path.startswith(prefix) or object_type != "blob":
                    continue
                relative = path[len(prefix):]
                data = self.blob(oid)
                entries.append(TreeEntry(relative, mode, data))
                if relative == SKILL_META_FILE:
                    meta_data = data
                elif relative == "VERSION":
                    legacy_version_data = data
            version = package_version(
                meta_data, legacy_version_data, package_path, ref
            )
            if name in packages:
                raise ReleaseError(f"duplicate skill package name {name!r}")
            packages[name] = Package(
                name=name,
                path=package_path,
                version=version,
                entries=tuple(entries),
                digest=digest_entries(
                    entries, exclude_paths=frozenset({"VERSION", SKILL_META_FILE})
                ),
            )
        self._package_cache[commit] = packages
        return packages

    def current_packages(self) -> dict[str, Package]:
        skills_dir = self.root / "skills"
        if not skills_dir.is_dir():
            raise ReleaseError(f"missing skills directory: {skills_dir}")
        packages: dict[str, Package] = {}
        for skill_file in sorted(skills_dir.rglob("SKILL.md")):
            package_dir = skill_file.parent
            name = package_dir.name
            if name in packages:
                raise ReleaseError(f"duplicate skill package name {name!r}")
            entries: list[TreeEntry] = []
            for directory, child_dirs, files in os.walk(package_dir, followlinks=False):
                directory_path = Path(directory)
                kept_dirs: list[str] = []
                for child in child_dirs:
                    child_path = directory_path / child
                    if child in IGNORED_DIRECTORIES:
                        continue
                    if child_path.is_symlink():
                        relative = child_path.relative_to(package_dir).as_posix()
                        entries.append(
                            TreeEntry(relative, 0o120000, os.readlink(child_path).encode())
                        )
                        continue
                    kept_dirs.append(child)
                child_dirs[:] = kept_dirs
                for filename in files:
                    file_path = directory_path / filename
                    relative = file_path.relative_to(package_dir).as_posix()
                    if is_ignored(relative):
                        continue
                    if file_path.is_symlink():
                        data = os.readlink(file_path).encode()
                        mode = 0o120000
                    else:
                        data = file_path.read_bytes()
                        mode = self.worktree_mode(file_path)
                    entries.append(TreeEntry(relative, mode, data))
            meta_entry = next(
                (entry for entry in entries if entry.path == SKILL_META_FILE), None
            )
            legacy_version_entry = next(
                (entry for entry in entries if entry.path == "VERSION"), None
            )
            version = package_version(
                meta_entry.data if meta_entry is not None else None,
                legacy_version_entry.data if legacy_version_entry is not None else None,
                package_dir.relative_to(self.root).as_posix(),
                "worktree",
            )
            packages[name] = Package(
                name=name,
                path=package_dir.relative_to(self.root).as_posix(),
                version=version,
                entries=tuple(entries),
                digest=digest_entries(
                    entries, exclude_paths=frozenset({"VERSION", SKILL_META_FILE})
                ),
            )
        return packages

    def release_tags(self) -> dict[str, list[ReleaseTag]]:
        output = self.git_text("tag", "--list")
        tags: dict[str, list[ReleaseTag]] = {}
        for tag in output.splitlines():
            if "/v" not in tag:
                continue
            name, raw_version = tag.rsplit("/v", 1)
            if not NAME_PATTERN.fullmatch(name):
                continue
            try:
                version = Version.parse(raw_version, f"tag {tag}")
            except ReleaseError:
                continue
            commit = self.commit(tag)
            tags.setdefault(name, []).append(
                ReleaseTag(name=name, version=version, tag=tag, commit=commit)
            )
        for values in tags.values():
            values.sort(key=lambda item: item.version)
        return tags

    def repository_release_tags(self) -> list[ReleaseTag]:
        output = self.git_text("tag", "--list")
        tags: list[ReleaseTag] = []
        for tag in output.splitlines():
            if not tag.startswith("v"):
                continue
            try:
                version = Version.parse(tag[1:], f"tag {tag}")
            except ReleaseError:
                continue
            tags.append(
                ReleaseTag(
                    name=REPOSITORY_NAME,
                    version=version,
                    tag=tag,
                    commit=self.commit(tag),
                )
            )
        tags.sort(key=lambda item: item.version)
        return tags

    def commit_time(self, commit: str) -> int:
        value = self.git_text("show", "-s", "--format=%ct", commit)
        return int(value)

    def head_has_parent(self) -> bool:
        parents = self.git_text("rev-list", "--parents", "-1", "HEAD").split()
        return len(parents) > 1

    def repository_version_at(self, ref: str) -> Version | None:
        entries = self.tree_entries(ref, REPOSITORY_VERSION_FILE)
        for _path, _mode, object_type, oid in entries:
            if object_type == "blob":
                return parse_version_bytes(
                    self.blob(oid), f"{ref}:{REPOSITORY_VERSION_FILE}"
                )
        return None

    def repository_entries_at(self, ref: str) -> tuple[TreeEntry, ...]:
        entries: list[TreeEntry] = []
        for path, mode, object_type, oid in self.tree_entries(ref):
            if (
                object_type != "blob"
                or path == REPOSITORY_VERSION_FILE
                or path.startswith("dist/")
                or path.startswith(".git/")
            ):
                continue
            if path.startswith("skills/") and not path.endswith(f"/{SKILL_META_FILE}"):
                continue
            entries.append(TreeEntry(path, mode, self.blob(oid)))
        return tuple(entries)

    def full_repository_entries_at(self, ref: str) -> tuple[TreeEntry, ...]:
        entries: list[TreeEntry] = []
        for path, mode, object_type, oid in self.tree_entries(ref):
            if (
                object_type != "blob"
                or is_ignored(path)
                or path == "dist"
                or path.startswith("dist/")
            ):
                continue
            entries.append(TreeEntry(path, mode, self.blob(oid)))
        return tuple(entries)

    def repository_digest_at(self, ref: str) -> str:
        return digest_entries(
            self.repository_entries_at(ref),
            exclude_paths=frozenset({REPOSITORY_VERSION_FILE}),
        )

    def repository_version_commit(self) -> str:
        output = self.git_text("log", "-1", "--format=%H", "--", REPOSITORY_VERSION_FILE)
        if not output:
            raise ReleaseError(
                f"no commit found for repository version file {REPOSITORY_VERSION_FILE}"
            )
        return output

    def repository_notes(self, release_commit: str, previous: ReleaseTag | None) -> str:
        skills = self.packages_at(release_commit)
        lines = ["## Included skills", "", "| Skill | Version |", "| --- | --- |"]
        for name in sorted(skills):
            version = skills[name].version
            lines.append(f"| `{name}` | {version if version is not None else 'missing'} |")
        if previous is None:
            lines.extend(
                ("", f"Initial repository release at `{release_commit[:12]}`.")
            )
        else:
            process = self.git(
                "log",
                "--format=%h\t%s",
                f"{previous.tag}..{release_commit}",
                "--",
                ".",
                ":(exclude)skills",
                f":(exclude){REPOSITORY_VERSION_FILE}",
                check=False,
            )
            changes = []
            if process.returncode == 0:
                changes = [
                    line
                    for line in process.stdout.decode("utf-8").splitlines()
                    if line
                ]
            lines.extend(("", "## Repository changes", ""))
            lines.extend(f"- {line}" for line in changes)
            if not changes:
                lines.append("No repository-level changes were recorded.")
        return "\n".join(lines) + "\n"

def _check_repository_release(
    repo: Repository,
    base_ref: str,
    repository_tags: list[ReleaseTag],
    problems: list[str],
) -> None:
    base_version = repo.repository_version_at(base_ref)
    head_version = repo.repository_version_at("HEAD")
    if head_version is None:
        problems.append(f"{REPOSITORY_VERSION_FILE}: missing repository version")
        return
    base_digest = repo.repository_digest_at(base_ref)
    head_digest = repo.repository_digest_at("HEAD")
    latest = repository_tags[-1] if repository_tags else None
    current_tag = next(
        (tag for tag in repository_tags if tag.version == head_version), None
    )
    if latest is not None and head_version < latest.version:
        problems.append(
            f"{REPOSITORY_VERSION_FILE}: {head_version} is lower than existing "
            f"release {latest.tag}"
        )
    if base_version is None:
        if current_tag is not None:
            problems.append(
                f"{REPOSITORY_VERSION_FILE}: initial version {head_version} is already "
                f"tagged as {current_tag.tag}"
            )
        return
    if head_version < base_version:
        base_is_tagged = any(tag.version == base_version for tag in repository_tags)
        if base_is_tagged:
            problems.append(
                f"{REPOSITORY_VERSION_FILE}: version decreased from released version "
                f"{base_version} to {head_version}"
            )
            return
    if head_version > base_version and current_tag is not None:
        problems.append(
            f"{REPOSITORY_VERSION_FILE}: version {head_version} is already tagged as "
            f"{current_tag.tag}"
        )
    if head_version == base_version and head_digest != base_digest:
        problems.append(
            f"{REPOSITORY_VERSION_FILE}: repository content changed but version stayed "
            f"at {head_version}"
        )
    if current_tag is not None:
        tagged_version = repo.repository_version_at(current_tag.commit)
        if tagged_version != head_version:
            problems.append(
                f"{current_tag.tag}: tag does not contain repository version {head_version}"
            )
        elif repo.repository_digest_at(current_tag.commit) != head_digest:
            problems.append(
                f"{REPOSITORY_VERSION_FILE}: repository content differs from "
                f"{current_tag.tag}"
            )


def check_releases(
    repo: Repository,
    base_ref: str,
    *,
    allow_skill_version_reset: bool = False,
) -> tuple[int, int]:
    base_packages = repo.packages_at(base_ref)
    head_packages = repo.current_packages()
    skill_tags = repo.release_tags()
    repository_tags = repo.repository_release_tags()
    problems: list[str] = []

    if REPOSITORY_NAME in head_packages:
        problems.append(
            f"{head_packages[REPOSITORY_NAME].path}: skill name {REPOSITORY_NAME!r} is "
            "reserved for repository releases"
        )
    for tag_name, tag_values in sorted(skill_tags.items()):
        if tag_name in head_packages:
            problems.extend(
                f"{tag.tag}: per-skill release tags are not supported"
                for tag in tag_values
            )
    _check_repository_release(repo, base_ref, repository_tags, problems)

    for name in sorted(head_packages):
        package = head_packages[name]
        if package.version is None:
            problems.append(f"{package.path}: missing skill version")
            continue
        base = base_packages.get(name)
        if base is None:
            continue
        if base.version is None:
            # The first skill metadata versions establish the release baseline for existing
            # packages. Bootstrap may only add metadata, or add it together with
            # the package's first reviewed content.
            continue
        if package.version < base.version:
            if not allow_skill_version_reset:
                problems.append(
                    f"{package.path}: skill version decreased from {base.version} to "
                    f"{package.version}"
                )
            continue
        if package.version == base.version:
            if package.digest != base.digest:
                problems.append(
                    f"{package.path}: package content changed but skill version stayed at "
                    f"{package.version}"
                )
        else:
            if package.digest == base.digest:
                problems.append(
                    f"{package.path}: skill version changed from {base.version} to "
                    f"{package.version} without a package content change"
                )

    if problems:
        raise ReleaseError("release check failed:\n" + "\n".join(f"- {item}" for item in problems))
    return len(head_packages), len(repository_tags)


def _make_repository_plan(
    repo: Repository,
    head: str,
    repository_tags: list[ReleaseTag],
    include_tagged: bool,
) -> dict[str, object] | None:
    version = repo.repository_version_at("HEAD")
    if version is None:
        raise ReleaseError(f"{REPOSITORY_VERSION_FILE}: missing repository version")
    latest = repository_tags[-1] if repository_tags else None
    current_tag = next(
        (tag for tag in repository_tags if tag.version == version), None
    )
    if latest is not None and version < latest.version:
        raise ReleaseError(
            f"{REPOSITORY_VERSION_FILE}: {version} is lower than {latest.tag}"
        )
    if current_tag is not None and not include_tagged:
        return None
    target_commit = repo.repository_version_commit() if repository_tags else head
    target_version = repo.repository_version_at(target_commit)
    if target_version != version:
        raise ReleaseError(
            f"{REPOSITORY_VERSION_FILE}: commit {target_commit[:12]} does not contain "
            f"version {version}"
        )
    if current_tag is not None:
        tagged_version = repo.repository_version_at(current_tag.commit)
        if tagged_version != version:
            raise ReleaseError(
                f"{current_tag.tag}: tag does not contain repository version {version}"
            )
        release_commit = current_tag.commit
        previous = next(
            (tag for tag in reversed(repository_tags) if tag.version < version),
            None,
        )
    else:
        release_commit = target_commit
        previous = latest
    if repo.repository_digest_at(release_commit) != repo.repository_digest_at("HEAD"):
        raise ReleaseError(
            f"repository content changed after {REPOSITORY_VERSION_FILE} commit "
            f"{target_commit[:12]} without a new repository version"
        )
    return {
        "version": str(version),
        "tag": f"v{version}",
        "tagExists": current_tag is not None,
        "targetCommit": target_commit,
        "releaseCommit": release_commit,
        "previousTag": previous.tag if previous else None,
        "notes": repo.repository_notes(release_commit, previous),
    }


def make_plan(repo: Repository, include_tagged: bool = False) -> dict[str, object]:
    head = repo.commit("HEAD")
    packages = repo.current_packages()
    missing_versions = [name for name, package in packages.items() if package.version is None]
    if missing_versions:
        raise ReleaseError(
            "missing skill version in meta.json for: "
            + ", ".join(sorted(missing_versions))
        )
    repository_tags = repo.repository_release_tags()
    repository = _make_repository_plan(repo, head, repository_tags, include_tagged)
    return {
        "schemaVersion": PLAN_SCHEMA_VERSION,
        "head": head,
        "includeTagged": include_tagged,
        "repository": repository,
        "skills": [
            {"name": name, "version": str(packages[name].version)}
            for name in sorted(packages)
        ],
    }


def _validate_repository_record(record: object) -> dict[str, object] | None:
    if record is None:
        return None
    if not isinstance(record, dict):
        raise ReleaseError("release plan contains an invalid repository entry")
    required = (
        "version",
        "tag",
        "tagExists",
        "targetCommit",
        "releaseCommit",
        "notes",
    )
    missing = [key for key in required if key not in record]
    if missing:
        raise ReleaseError(
            f"repository plan entry is missing: {', '.join(missing)}"
        )
    version = record["version"]
    if not isinstance(version, str):
        raise ReleaseError("repository plan contains an invalid version")
    parsed = Version.parse(version, "repository plan")
    if record["tag"] != f"v{parsed}":
        raise ReleaseError("repository tag does not match version")
    for field in ("targetCommit", "releaseCommit"):
        value = record[field]
        if not isinstance(value, str) or not COMMIT_PATTERN.fullmatch(value):
            raise ReleaseError(f"repository plan has an invalid {field}")
    if not isinstance(record["notes"], str):
        raise ReleaseError("repository plan has invalid release notes")
    record["parsedVersion"] = parsed
    return record


def load_plan(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseError(f"cannot read release plan {path}: {exc}") from exc
    if not isinstance(data, dict) or data.get("schemaVersion") != PLAN_SCHEMA_VERSION:
        raise ReleaseError(f"unsupported release plan schema in {path}")
    head = data.get("head")
    if not isinstance(head, str) or not COMMIT_PATTERN.fullmatch(head):
        raise ReleaseError(f"invalid plan head commit in {path}")
    skills = data.get("skills")
    if not isinstance(skills, list):
        raise ReleaseError(f"invalid included skills list in {path}")
    data["repository"] = _validate_repository_record(data.get("repository"))
    return data


def _archive_entries(entries: Iterable[TreeEntry], package_name: str) -> list[TreeEntry]:
    result = [entry for entry in entries if not is_ignored(entry.path)]
    return sorted(result, key=lambda entry: entry.path)


def _add_tar_directories(
    tar: tarfile.TarFile, package_name: str, paths: Iterable[str], mtime: int
) -> None:
    directories = {package_name}
    for path in paths:
        parent = str(PurePosixPath(path).parent)
        while parent not in ("", "."):
            directories.add(f"{package_name}/{parent}")
            parent = str(PurePosixPath(parent).parent)
    for directory in sorted(directories):
        info = tarfile.TarInfo(directory + "/")
        info.type = tarfile.DIRTYPE
        info.mode = 0o755
        info.uid = 0
        info.gid = 0
        info.uname = ""
        info.gname = ""
        info.mtime = mtime
        tar.addfile(info)


def _build_tar_gz(prefix: str, entries: Iterable[TreeEntry], mtime: int) -> bytes:
    ordered = _archive_entries(entries, prefix)
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w", format=tarfile.PAX_FORMAT) as tar:
        _add_tar_directories(tar, prefix, (entry.path for entry in ordered), mtime)
        for entry in ordered:
            archive_name = f"{prefix}/{entry.path}"
            if stat.S_ISLNK(entry.mode):
                info = tarfile.TarInfo(archive_name)
                info.type = tarfile.SYMTYPE
                info.linkname = entry.data.decode("utf-8")
                info.mode = 0o777
            else:
                info = tarfile.TarInfo(archive_name)
                info.size = len(entry.data)
                info.mode = 0o755 if entry.mode & 0o111 else 0o644
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            info.mtime = mtime
            if stat.S_ISLNK(entry.mode):
                tar.addfile(info)
            else:
                tar.addfile(info, io.BytesIO(entry.data))
    gzip_buffer = io.BytesIO()
    with gzip.GzipFile(
        filename="", mode="wb", compresslevel=9, fileobj=gzip_buffer, mtime=0
    ) as gzip_file:
        gzip_file.write(tar_buffer.getvalue())
    return gzip_buffer.getvalue()


def _repository_manifest(repo: Repository, record: dict[str, object]) -> bytes:
    version = str(record["version"])
    release_commit = str(record["releaseCommit"])
    packages = repo.packages_at(release_commit)
    manifest = {
        "schemaVersion": 1,
        "repository": REPOSITORY_NAME,
        "repositoryVersion": version,
        "repositoryTag": f"v{version}",
        "commit": release_commit,
        "skills": [
            {
                "name": name,
                "version": str(packages[name].version),
            }
            for name in sorted(packages)
            if packages[name].version is not None
        ],
    }
    return (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")


def build_release_assets(
    repo: Repository,
    plan: dict[str, object],
    output_dir: Path,
) -> list[Path]:
    head = repo.commit("HEAD")
    if plan.get("head") != head:
        raise ReleaseError(
            f"release plan targets {plan.get('head')}, but HEAD is {head}; regenerate the plan"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    notes_dir = output_dir / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    built: list[Path] = []
    repository_record = plan.get("repository")
    if repository_record is not None:
        record = _validate_repository_record(repository_record)
        assert record is not None
        version = str(record["version"])
        release_commit = str(record["releaseCommit"])
        if repo.repository_version_at(release_commit) != Version.parse(version):
            raise ReleaseError(
                f"repository release commit does not contain root VERSION {version}"
            )
        if repo.repository_digest_at(release_commit) != repo.repository_digest_at("HEAD"):
            raise ReleaseError(
                "repository content differs from the repository release commit"
            )
        manifest = _repository_manifest(repo, record)
        entries = list(repo.full_repository_entries_at(release_commit))
        entries = [entry for entry in entries if entry.path != "skills-manifest.json"]
        entries.append(TreeEntry("skills-manifest.json", 0o100644, manifest))
        prefix = f"{REPOSITORY_ARCHIVE_PREFIX}-{version}"
        archive_bytes = _build_tar_gz(
            prefix, entries, repo.commit_time(release_commit)
        )
        archive_path = output_dir / f"{prefix}.tar.gz"
        archive_path.write_bytes(archive_bytes)
        checksum = hashlib.sha256(archive_bytes).hexdigest()
        checksum_path = output_dir / f"{archive_path.name}.sha256"
        checksum_path.write_text(f"{checksum}  {archive_path.name}\n", encoding="utf-8")
        manifest_path = output_dir / "skills-manifest.json"
        manifest_path.write_bytes(manifest)
        notes_path = notes_dir / f"repository-{version}.md"
        notes_path.write_text(str(record["notes"]), encoding="utf-8")
        built.extend((archive_path, checksum_path, manifest_path, notes_path))

    return built


def _verify_asset_bytes(path: Path, expected: bytes) -> None:
    if path.read_bytes() != expected:
        raise ReleaseError(f"release asset {path.name} does not match the local build")


def _release_state(repo: Repository, tag: str) -> dict[str, object] | None:
    process = _run(
        ("gh", "release", "view", tag, "--json", "isDraft,publishedAt,assets"),
        repo.root,
        check=False,
    )
    if process.returncode != 0:
        message = process.stderr.decode("utf-8", errors="replace")
        if "not found" in message.lower():
            return None
        raise ReleaseError(f"cannot read GitHub release {tag}: {message.strip()}")
    data = json.loads(process.stdout.decode("utf-8"))
    if not isinstance(data, dict):
        raise ReleaseError(f"{tag}: invalid GitHub release response")
    data["isPublished"] = bool(data.get("publishedAt")) and not bool(data.get("isDraft"))
    return data


def _ensure_asset(
    repo: Repository,
    tag: str,
    release: dict[str, object],
    asset_path: Path,
) -> None:
    assets = release.get("assets", [])
    if not isinstance(assets, list):
        raise ReleaseError(f"{tag}: invalid GitHub release asset list")
    existing = {item.get("name"): item for item in assets if isinstance(item, dict)}
    if asset_path.name not in existing:
        _run(("gh", "release", "upload", tag, str(asset_path)), repo.root)
    expected = asset_path.read_bytes()
    with tempfile.TemporaryDirectory(prefix="release-verify-") as temp:
        _run(
            ("gh", "release", "download", tag, "--pattern", asset_path.name, "--dir", temp),
            repo.root,
        )
        _verify_asset_bytes(Path(temp) / asset_path.name, expected)


def publish_releases(repo: Repository, plan: dict[str, object], dist: Path) -> None:
    repository_record = plan.get("repository")
    if repository_record is None:
        print("no pending repository release")
        return
    record = _validate_repository_record(repository_record)
    assert record is not None
    version = str(record["version"])
    tag = str(record["tag"])
    release_commit = str(record["releaseCommit"])
    prefix = f"{REPOSITORY_ARCHIVE_PREFIX}-{version}"
    assets = [
        dist / f"{prefix}.tar.gz",
        dist / f"{prefix}.tar.gz.sha256",
        dist / "skills-manifest.json",
    ]
    notes_path = dist / "notes" / f"repository-{version}.md"
    for path in (*assets, notes_path):
        if not path.is_file():
            raise ReleaseError(f"missing built repository release file: {path}")
    expected_hash = hashlib.sha256(assets[0].read_bytes()).hexdigest()
    checksum_text = assets[1].read_text(encoding="utf-8")
    if checksum_text != f"{expected_hash}  {assets[0].name}\n":
        raise ReleaseError(f"checksum file does not match {assets[0].name}")

    repository_tags = repo.repository_release_tags()
    current_tag = next((item for item in repository_tags if item.tag == tag), None)
    if current_tag is not None:
        if current_tag.commit != release_commit:
            raise ReleaseError(
                f"{tag}: existing tag points to {current_tag.commit}, "
                f"plan expects {release_commit}"
            )
    else:
        _run(
            (
                "git",
                "-c",
                "user.name=github-actions[bot]",
                "-c",
                "user.email=41898282+github-actions[bot]@users.noreply.github.com",
                "tag",
                "-a",
                tag,
                release_commit,
                "-m",
                f"skills {version}",
            ),
            repo.root,
        )
        _run(("git", "push", "origin", f"refs/tags/{tag}"), repo.root)
        print(f"tagged {tag}")

    release = _release_state(repo, tag)
    if release is not None and release.get("isPublished") and not release.get("isDraft"):
        print(f"skip published {tag}")
        return
    if release is None:
        _run(
            (
                "gh",
                "release",
                "create",
                tag,
                "--draft",
                "--verify-tag",
                "--title",
                    f"skills v{version}",
                "--notes-file",
                str(notes_path),
            ),
            repo.root,
        )
        release = _release_state(repo, tag)
        if release is None:
            raise ReleaseError(f"{tag}: draft repository release was not created")
    if not release.get("isDraft"):
        raise ReleaseError(f"{tag}: repository release is not a draft")
    for asset in assets:
        _ensure_asset(repo, tag, release, asset)
    _run(("gh", "release", "edit", tag, "--draft=false"), repo.root)
    print(f"published {tag}")


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser(
        "check", help="validate skill and repository version changes"
    )
    check_parser.add_argument("--base", required=True, help="base Git ref for comparison")
    check_parser.add_argument(
        "--allow-skill-version-reset",
        action="store_true",
        help="allow an intentional baseline reset of skill versions",
    )

    plan_parser = subparsers.add_parser(
        "plan", help="emit the repository release candidate as JSON"
    )
    plan_parser.add_argument("--output", type=Path, required=True)
    plan_parser.add_argument("--include-tagged", action="store_true")

    build_parser = subparsers.add_parser("build", help="build release archives")
    build_parser.add_argument("--plan", type=Path, required=True)
    build_parser.add_argument("--output-dir", type=Path, required=True)

    publish_parser = subparsers.add_parser("publish", help="tag and publish releases")
    publish_parser.add_argument("--plan", type=Path, required=True)
    publish_parser.add_argument("--dist", type=Path, required=True)

    args = parser.parse_args(argv)
    repo = Repository(Path(__file__).resolve().parent.parent)
    try:
        if args.command == "check":
            if not args.base.strip() or set(args.base.strip()) == {"0"}:
                print("No base commit available; skipping release version check.")
                return 0
            if not repo.head_has_parent():
                print(
                    "HEAD has no parent history; skipping release version check "
                    "for the new root commit."
                )
                return 0
            package_count, tag_count = check_releases(
                repo,
                args.base,
                allow_skill_version_reset=args.allow_skill_version_reset,
            )
            print(
                f"Release check passed for {package_count} skill package(s); "
                f"{tag_count} repository release tag(s) found."
            )
        elif args.command == "plan":
            plan = make_plan(repo, args.include_tagged)
            write_json(args.output, plan)
            repository = plan.get("repository")
            if repository is None:
                print(f"Wrote no pending repository release to {args.output}.")
            else:
                assert isinstance(repository, dict)
                print(
                    f"Wrote repository release {repository['tag']} to {args.output}."
                )
        elif args.command == "build":
            plan = load_plan(args.plan)
            built = build_release_assets(repo, plan, args.output_dir)
            print(f"Built {len(built)} release file(s) in {args.output_dir}.")
        elif args.command == "publish":
            plan = load_plan(args.plan)
            publish_releases(repo, plan, args.dist)
        else:  # pragma: no cover - argparse enforces the command set
            parser.error("unknown command")
    except ReleaseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
