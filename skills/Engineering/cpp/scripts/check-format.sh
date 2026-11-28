#!/usr/bin/env bash
# Verify the repository's C++ formatting gate without changing files.
# Usage: check-format.sh [paths...]
# Without paths, every tracked and untracked-unignored C/C++ file is checked.
# Run from anywhere inside the project's git worktree.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "check-format.sh: run this script inside a git worktree" >&2
  exit 2
}
cd "$root"

clang_format="${CLANG_FORMAT:-clang-format}"
if ! command -v "$clang_format" >/dev/null 2>&1; then
  echo "check-format.sh: '$clang_format' not found; install clang-format or set CLANG_FORMAT" >&2
  exit 2
fi

if [[ ! -f "$root/.clang-format" ]]; then
  echo "check-format.sh: no .clang-format in $root" >&2
  if [[ -f "$script_dir/../templates/.clang-format" ]]; then
    echo "Copy $script_dir/../templates/.clang-format to the repository root first." >&2
  else
    echo "Create one at the repository root; the cpp skill ships templates/.clang-format." >&2
  fi
  exit 2
fi

files=()
if [[ $# -gt 0 ]]; then
  for file in "$@"; do
    if [[ ! -f "$file" ]]; then
      echo "check-format.sh: not a file: $file" >&2
      exit 2
    fi
    case "$file" in
      *.c|*.cc|*.cpp|*.cxx|*.h|*.hh|*.hpp|*.hxx) files+=("$file") ;;
      *) echo "check-format.sh: not a C/C++ source: $file" >&2; exit 2 ;;
    esac
  done
else
  while IFS= read -r -d '' file; do
    [[ -f "$file" ]] || continue
    case "$file" in
      *.c|*.cc|*.cpp|*.cxx|*.h|*.hh|*.hpp|*.hxx) files+=("$file") ;;
    esac
  done < <(git ls-files --cached --others --exclude-standard -z)
fi

if [[ ${#files[@]} -eq 0 ]]; then
  echo "check-format.sh: no C or C++ sources found"
  exit 0
fi

python3 "$script_dir/add-blank-lines.py" --check "${files[@]}"

if ! "$clang_format" --dry-run --Werror --style=file "${files[@]}" >/dev/null; then
  echo "check-format.sh: formatting differs from .clang-format" >&2
  echo "Run format-cpp.sh, then review the diff." >&2
  exit 1
fi

echo "C++ formatting clean on ${#files[@]} file(s)"
