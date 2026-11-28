#!/usr/bin/env python3
"""Validate skill package format, metadata, versions, links, and bundled tooling.

Every directory under skills/ that contains a SKILL.md is treated as a skill
package, so category subdirectories do not change validation.

Version changes are checked separately by ``release.py check --base`` because
they depend on Git history.

Usage: python scripts/check-format.py (from any working directory).
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
VERSION_PATTERN = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
DESCRIPTION_TRIGGER = re.compile(r"Use (?:when|for|this)\b", re.IGNORECASE)
FENCE_PATTERN = re.compile(r"^ {0,3}(`{3,}|~{3,})")
FIELD_PATTERN = re.compile(r"^(name|description):[ \t]*(.*?)\s*$", re.MULTILINE)
COMPATIBILITY_PATTERN = re.compile(r"^compatibility:[ \t]*(.*?)\s*$", re.MULTILINE)
DISABLE_MODEL_INVOCATION_PATTERN = re.compile(
    r"^disable-model-invocation:[ \t]*(.*?)\s*$", re.MULTILINE
)
OBSOLETE_REQUIRES_PATTERN = re.compile(
    r"(?:^[ \t]*requires[ \t]*:|^metadata:[ \t]*\{[^\n}]*\brequires[ \t]*:)",
    re.MULTILINE,
)
YAML_FIELD_PATTERN = re.compile(
    r"^(?P<indent> *)(?P<key>[A-Za-z_][A-Za-z0-9_]*):(?:[ \t]*(?P<value>.*))?$"
)
OPENAI_METADATA_FILE = "agents/openai.yaml"


def mask_code(text: str) -> str:
    """Replace fenced blocks and inline code spans with spaces."""
    lines = text.splitlines(keepends=True)
    masked_lines: list[str] = []
    fence_char: str | None = None
    fence_size = 0

    for line in lines:
        match = FENCE_PATTERN.match(line)
        if fence_char is None and match:
            marker = match.group(1)
            fence_char, fence_size = marker[0], len(marker)
            masked_lines.append("".join("\n" if char == "\n" else " " for char in line))
            continue
        if fence_char is not None:
            close_pattern = rf"^ {{0,3}}{re.escape(fence_char)}{{{fence_size},}}[ \t]*\r?\n?$"
            if re.match(close_pattern, line):
                fence_char = None
                fence_size = 0
            masked_lines.append("".join("\n" if char == "\n" else " " for char in line))
            continue
        masked_lines.append(line)

    text = "".join(masked_lines)
    result = list(text)
    index = 0
    while index < len(text):
        if text[index] != "`":
            index += 1
            continue
        end_run = index + 1
        while end_run < len(text) and text[end_run] == "`":
            end_run += 1
        run_size = end_run - index
        search = end_run
        close_start = -1
        while search < len(text):
            candidate = text.find("`", search)
            if candidate < 0:
                break
            candidate_end = candidate + 1
            while candidate_end < len(text) and text[candidate_end] == "`":
                candidate_end += 1
            if candidate_end - candidate == run_size:
                close_start = candidate
                break
            search = candidate_end
        if close_start < 0:
            index = end_run
            continue
        close_end = close_start + run_size
        for position in range(index, close_end):
            if result[position] != "\n":
                result[position] = " "
        index = close_end
    return "".join(result)


def find_bracket_end(text: str, opening: int) -> int | None:
    depth = 1
    index = opening + 1
    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 2
            continue
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return index
        index += 1
    return None


def find_link_end(text: str, index: int) -> int | None:
    depth = 0
    quote: str | None = None
    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 2
            continue
        if quote is not None:
            if char == quote:
                quote = None
        elif char in ("'", '"'):
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            if depth == 0:
                return index
            depth -= 1
        index += 1
    return None


def parse_inline_destination(text: str, opening: int) -> tuple[str, int] | None:
    index = opening + 1
    while index < len(text) and text[index].isspace():
        index += 1
    if index >= len(text):
        return None

    if text[index] == "<":
        destination_start = index + 1
        index = destination_start
        while index < len(text):
            if text[index] == "\\":
                index += 2
                continue
            if text[index] == ">":
                destination = text[destination_start:index]
                end = find_link_end(text, index + 1)
                return (destination, end + 1) if end is not None else None
            index += 1
        return None

    destination_start = index
    nested_parentheses = 0
    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 2
            continue
        if char == "(":
            nested_parentheses += 1
        elif char == ")":
            if nested_parentheses == 0:
                return text[destination_start:index], index + 1
            nested_parentheses -= 1
        elif char.isspace() and nested_parentheses == 0:
            end = find_link_end(text, index)
            return (text[destination_start:index], end + 1) if end is not None else None
        index += 1
    return None


def inline_destinations(text: str) -> list[str]:
    text = mask_code(text)
    destinations: list[str] = []
    index = 0
    while index < len(text):
        if text[index] == "\\":
            index += 2
            continue
        opening = index + 1 if text[index] == "!" and index + 1 < len(text) and text[index + 1] == "[" else index
        if text[opening] != "[":
            index += 1
            continue
        closing = find_bracket_end(text, opening)
        if closing is None or closing + 1 >= len(text) or text[closing + 1] != "(":
            index = closing + 1 if closing is not None else opening + 1
            continue
        parsed = parse_inline_destination(text, closing + 1)
        if parsed is None:
            index = closing + 1
            continue
        destination, next_index = parsed
        destinations.append(destination)
        index = next_index
    return destinations


def parse_scalar(raw: str) -> str:
    """Parse the simple quoted or plain scalars used by skill frontmatter."""
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def has_metadata_version(frontmatter: str) -> bool:
    """Return whether frontmatter keeps an obsolete metadata.version field."""
    in_metadata = False
    for line in frontmatter.splitlines():
        if line.startswith("metadata:"):
            if re.search(r"\bversion\s*:", line):
                return True
            in_metadata = True
            continue
        if not in_metadata:
            continue
        if not line.strip():
            continue
        if not line.startswith((" ", "\t")):
            in_metadata = False
            continue
        if re.match(r"^[ \t]+version[ \t]*:", line):
            return True
    return False


def validate_frontmatter(
    skill_file: Path, relative: str, problems: list[str]
) -> dict[str, str]:
    text = skill_file.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        problems.append(f"{relative}: missing opening YAML frontmatter delimiter")
        return {}
    try:
        closing = lines.index("---", 1)
    except ValueError:
        problems.append(f"{relative}: missing closing YAML frontmatter delimiter")
        return {}

    frontmatter = "\n".join(lines[1:closing])
    fields = dict(FIELD_PATTERN.findall(frontmatter))
    name = fields.get("name", "").strip().strip("\"'").strip()
    description = fields.get("description", "").strip().strip("\"'").strip()
    compatibility_match = COMPATIBILITY_PATTERN.search(frontmatter)
    compatibility = (
        parse_scalar(compatibility_match.group(1)) if compatibility_match else ""
    )
    disable_match = DISABLE_MODEL_INVOCATION_PATTERN.search(frontmatter)
    disable_model_invocation = ""
    if disable_match:
        value = parse_scalar(disable_match.group(1)).lower()
        if value not in ("true", "false"):
            problems.append(
                f"{relative}: disable-model-invocation must be true or false"
            )
        else:
            disable_model_invocation = value
    if not name:
        problems.append(f"{relative}: missing or empty frontmatter name")
    else:
        if name != skill_file.parent.name:
            problems.append(
                f"{relative}: name {name!r} does not match directory {skill_file.parent.name!r}"
            )
        if not NAME_PATTERN.fullmatch(name):
            problems.append(f"{relative}: name {name!r} is not lowercase kebab-case")
    if not description:
        problems.append(f"{relative}: missing or empty frontmatter description")
    elif not DESCRIPTION_TRIGGER.match(description):
        problems.append(
            f"{relative}: description must begin with a use trigger such as 'Use when'"
        )
    if len(compatibility) > 500:
        problems.append(f"{relative}: compatibility exceeds 500 characters")
    if OBSOLETE_REQUIRES_PATTERN.search(frontmatter):
        problems.append(
            f"{relative}: replace metadata.requires with the compatibility field"
        )
    if has_metadata_version(frontmatter):
        problems.append(
            f"{relative}: remove metadata.version; store the skill version in meta.json"
        )
    result = {
        "name": name,
        "description": description,
        "compatibility": compatibility,
    }
    if disable_model_invocation:
        result["disable_model_invocation"] = disable_model_invocation
    return result


def validate_repository_version(root: Path, problems: list[str]) -> bool:
    """Validate the independent stable SemVer version of the repository."""
    version_file = root / "VERSION"
    if not version_file.is_file():
        problems.append("VERSION: missing repository version file at the repository root")
        return False
    raw = version_file.read_text(encoding="utf-8", errors="replace")
    if "\r" in raw or not raw.endswith("\n") or raw.count("\n") != 1:
        problems.append("VERSION: root file must contain one version and one newline")
        return False
    version = raw[:-1]
    if not version or version != version.strip():
        problems.append("VERSION: root file must not contain surrounding whitespace")
        return False
    if VERSION_PATTERN.fullmatch(version) is None:
        problems.append(
            f"VERSION: root file must be stable SemVer MAJOR.MINOR.PATCH, got {version!r}"
        )
        return False
    return True


def load_dependency_checker(root: Path, problems: list[str]):
    """Load the skill metadata parser and executable checker."""
    script = root / "scripts" / "check-dependencies.py"
    if not script.is_file():
        problems.append(f"{script.relative_to(root).as_posix()}: missing dependency checker")
        return None
    spec = importlib.util.spec_from_file_location("skill_dependency_checker", script)
    if spec is None or spec.loader is None:
        problems.append(f"{script.relative_to(root).as_posix()}: cannot load dependency checker")
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # pragma: no cover - import failure is reported below
        sys.modules.pop(spec.name, None)
        problems.append(
            f"{script.relative_to(root).as_posix()}: dependency checker failed to load: {exc}"
        )
        return None
    return module


def validate_dependency_metadata(
    skills: list[Path],
    frontmatter: dict[str, dict[str, str]],
    root: Path,
    problems: list[str],
) -> None:
    """Require skill metadata, compatibility text, and packages to stay in sync."""
    checker = load_dependency_checker(root, problems)
    if checker is None:
        return
    try:
        registry = checker.load_skill_metadata(root)
    except checker.SkillMetadataError as exc:
        problems.append(str(exc))
        return
    for problem in checker.validate_skill_metadata(registry):
        problems.append(f"scripts/check-dependencies.py: {problem}")

    actual = {skill_file.parent.name: skill_file for skill_file in skills}
    for name, skill_file in actual.items():
        legacy_version = skill_file.parent / "VERSION"
        if legacy_version.exists() or legacy_version.is_symlink():
            problems.append(
                f"{legacy_version.relative_to(root).as_posix()}: remove legacy VERSION; "
                "store the skill version in meta.json"
            )
    for name in sorted(set(registry) - set(actual)):
        problems.append(f"meta.json: skill {name!r} has no package")
    for name in sorted(set(actual) - set(registry)):
        problems.append(
            f"{actual[name].relative_to(root).as_posix()}: missing meta.json"
        )

    for name, spec in registry.items():
        if name not in frontmatter:
            continue
        expected = checker.compatibility_for(spec)
        actual_compatibility = frontmatter[name].get("compatibility", "")
        relative = actual[name].relative_to(root).as_posix()
        if expected is None and actual_compatibility:
            problems.append(
                f"{relative}: compatibility is declared but meta.json has no commands"
            )
        elif expected is not None and not actual_compatibility:
            problems.append(f"{relative}: missing compatibility: {expected}")
        elif expected is not None and actual_compatibility != expected:
            problems.append(
                f"{relative}: compatibility must exactly match meta.json: "
                f"{expected}"
            )


def strip_yaml_comment(line: str) -> str:
    """Remove an unquoted YAML comment from one line."""
    quote: str | None = None
    index = 0
    while index < len(line):
        char = line[index]
        if quote is not None:
            if char == "\\" and quote == '"':
                index += 2
                continue
            if char == quote:
                quote = None
        elif char in ("'", '"'):
            quote = char
        elif char == "#":
            return line[:index].rstrip()
        index += 1
    return line.rstrip()


def parse_openai_metadata(
    path: Path, relative: str, problems: list[str]
) -> dict[str, dict[str, str]]:
    """Parse the small mapping subset used by agents/openai.yaml."""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        problems.append(f"{relative}: cannot read file: {exc}")
        return {}

    sections: dict[str, dict[str, str]] = {}
    current: str | None = None
    for line_number, raw in enumerate(lines, 1):
        line = strip_yaml_comment(raw)
        if not line.strip():
            continue
        leading = raw[: len(raw) - len(raw.lstrip())]
        if "\t" in leading:
            problems.append(
                f"{relative}:{line_number}: tabs are not allowed for indentation"
            )
            continue
        match = YAML_FIELD_PATTERN.match(line)
        if match is None:
            problems.append(f"{relative}:{line_number}: expected 'key: value'")
            continue
        indent = len(match.group("indent"))
        key = match.group("key")
        value = (match.group("value") or "").strip()
        if indent == 0:
            if value:
                problems.append(
                    f"{relative}:{line_number}: top-level {key!r} must be a mapping"
                )
                current = None
                continue
            if key in sections:
                problems.append(f"{relative}:{line_number}: duplicate section {key!r}")
            sections.setdefault(key, {})
            current = key
            continue
        if current is None:
            problems.append(
                f"{relative}:{line_number}: field {key!r} is not inside a section"
            )
            continue
        if not value:
            problems.append(
                f"{relative}:{line_number}: {current}.{key} must have a value"
            )
            continue
        if key in sections[current]:
            problems.append(
                f"{relative}:{line_number}: duplicate field {current}.{key}"
            )
        sections[current][key] = parse_scalar(value)
    return sections


def validate_openai_metadata(
    skill_file: Path,
    frontmatter: dict[str, str],
    root: Path,
    problems: list[str],
) -> None:
    """Validate optional agent metadata and invocation policy consistency."""
    package_relative = skill_file.parent.relative_to(root).as_posix()
    metadata_path = skill_file.parent / OPENAI_METADATA_FILE
    metadata_relative = metadata_path.relative_to(root).as_posix()
    disable_value = frontmatter.get("disable_model_invocation")

    if not metadata_path.is_file():
        if disable_value is not None:
            problems.append(
                f"{package_relative}/SKILL.md: disable-model-invocation is set but "
                f"{metadata_relative} is missing"
            )
        return

    sections = parse_openai_metadata(metadata_path, metadata_relative, problems)
    interface = sections.get("interface")
    if interface is None:
        problems.append(f"{metadata_relative}: missing interface section")
    else:
        for field in ("display_name", "short_description"):
            if not interface.get(field, "").strip():
                problems.append(
                    f"{metadata_relative}: missing or empty interface.{field}"
                )
        if "default_prompt" in interface and not interface["default_prompt"].strip():
            problems.append(
                f"{metadata_relative}: interface.default_prompt must not be empty"
            )

    policy = sections.get("policy")
    allow_present = policy is not None and "allow_implicit_invocation" in policy
    allow_value: bool | None = None
    if policy is not None:
        if not allow_present:
            problems.append(
                f"{metadata_relative}: missing policy.allow_implicit_invocation"
            )
        else:
            raw_allow = policy["allow_implicit_invocation"].strip().lower()
            if raw_allow not in ("true", "false"):
                problems.append(
                    f"{metadata_relative}: policy.allow_implicit_invocation must be "
                    "true or false"
                )
            else:
                allow_value = raw_allow == "true"

    if disable_value is None and policy is None:
        return
    if disable_value is None:
        problems.append(
            f"{metadata_relative}: policy.allow_implicit_invocation is set but "
            f"{package_relative}/SKILL.md is missing disable-model-invocation"
        )
        return
    if policy is None:
        problems.append(
            f"{package_relative}/SKILL.md: disable-model-invocation is set but "
            f"{metadata_relative} has no policy.allow_implicit_invocation"
        )
        return
    if not allow_present or allow_value is None:
        return
    expected_allow = disable_value == "false"
    if allow_value != expected_allow:
        expected_text = "true" if expected_allow else "false"
        problems.append(
            f"{metadata_relative}: policy.allow_implicit_invocation must be "
            f"{expected_text} when {package_relative}/SKILL.md sets "
            f"disable-model-invocation: {disable_value}"
        )


def check_link(markdown_file: Path, destination: str) -> str | None:
    try:
        parsed = urlsplit(destination)
    except ValueError:
        return f"invalid link target {destination!r}"
    if parsed.scheme or destination.startswith("/") or not parsed.path:
        return None
    target_path = (markdown_file.parent / unquote(parsed.path)).resolve()
    if target_path.exists():
        return None
    return f"broken link target {destination!r}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check skill package format, links, versions, and routed files."
    )
    parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    problems: list[str] = []
    skills_dir = root / "skills"
    skills = sorted(skills_dir.rglob("SKILL.md")) if skills_dir.is_dir() else []
    markdown_files = sorted(
        path for path in root.rglob("*.md") if ".git" not in path.relative_to(root).parts
    )
    checked_links = 0
    checked_references = 0
    checked_assets = 0
    checked_versions = 0
    checked_repository_version = validate_repository_version(root, problems)
    frontmatter_by_name: dict[str, dict[str, str]] = {}

    for skill_file in skills:
        relative_skill = skill_file.relative_to(root).as_posix()
        skill_frontmatter = validate_frontmatter(skill_file, relative_skill, problems)
        if skill_frontmatter:
            frontmatter_by_name[skill_file.parent.name] = skill_frontmatter
        validate_openai_metadata(skill_file, skill_frontmatter, root, problems)
        checked_versions += 1
        skill_text = skill_file.read_text(encoding="utf-8", errors="replace")
        references_dir = skill_file.parent / "references"
        if references_dir.is_dir():
            for reference in sorted(path for path in references_dir.rglob("*") if path.is_file()):
                checked_references += 1
                relative_reference = reference.relative_to(skill_file.parent).as_posix()
                if relative_reference not in skill_text and reference.name not in skill_text:
                    problems.append(
                        f"{reference.relative_to(root).as_posix()}: reference is not mentioned "
                        f"in {relative_skill}"
                    )
        for bundle in ("scripts", "templates"):
            bundle_dir = skill_file.parent / bundle
            if not bundle_dir.is_dir():
                continue
            for asset in sorted(path for path in bundle_dir.rglob("*") if path.is_file()):
                if asset.name.startswith("."):
                    continue
                checked_assets += 1
                if asset.name not in skill_text:
                    problems.append(
                        f"{asset.relative_to(root).as_posix()}: bundled file is not mentioned "
                        f"in {relative_skill}"
                    )

    validate_dependency_metadata(skills, frontmatter_by_name, root, problems)

    for markdown_file in markdown_files:
        relative_markdown = markdown_file.relative_to(root).as_posix()
        text = markdown_file.read_text(encoding="utf-8", errors="replace")
        for destination in inline_destinations(text):
            checked_links += 1
            issue = check_link(markdown_file, destination)
            if issue:
                problems.append(f"{relative_markdown}: {issue}")

    print(
        f"Checked {len(skills)} skill files, {len(markdown_files)} Markdown files, "
        f"{checked_links} inline links, {checked_references} reference files, and "
        f"{checked_assets} bundled assets, plus {checked_versions} skill versions"
        f" and {'one repository version' if checked_repository_version else 'no valid repository version'}."
    )
    if problems:
        print(f"Problems ({len(problems)}):")
        for problem in problems:
            print(problem)
        print(f"Summary: {len(problems)} problem(s) found.")
        return 1
    print("Summary: no problems found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
