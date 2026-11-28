#!/usr/bin/env bash
# Rewrite Swift sources with the repository's .swift-format and the
# structural blank-line rule.
# Usage: format-swift.sh [paths...]
# Without paths, every tracked and untracked-unignored Swift file is rewritten.
# Run from anywhere inside the project's git worktree.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "format-swift.sh: run this script inside a git worktree" >&2
  exit 2
}
cd "$root"

if command -v swift >/dev/null 2>&1 && swift format --help >/dev/null 2>&1; then
  swift_format=(swift format)
elif command -v swift-format >/dev/null 2>&1; then
  swift_format=(swift-format)
else
  echo "format-swift.sh: neither 'swift format' nor 'swift-format' is available; install a Swift 6 toolchain or swift-format" >&2
  exit 2
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "format-swift.sh: 'python3' not found; the blank-line rule needs it" >&2
  exit 2
fi

config_file="$root/.swift-format"
if [[ ! -f "$config_file" ]]; then
  echo "format-swift.sh: no .swift-format in $root" >&2
  echo "Copy $script_dir/../templates/.swift-format to the repository root first." >&2
  exit 2
fi

files=()
if [[ $# -gt 0 ]]; then
  for file in "$@"; do
    if [[ ! -f "$file" ]]; then
      echo "format-swift.sh: not a file: $file" >&2
      exit 2
    fi
    case "$file" in
      *.swift) files+=("$file") ;;
      *) echo "format-swift.sh: not a Swift source: $file" >&2; exit 2 ;;
    esac
  done
else
  while IFS= read -r -d '' file; do
    [[ -f "$file" ]] || continue
    case "$file" in
      *.swift) files+=("$file") ;;
    esac
  done < <(git ls-files --cached --others --exclude-standard -z)
fi

if [[ ${#files[@]} -eq 0 ]]; then
  echo "format-swift.sh: no Swift sources found"
  exit 0
fi

"${swift_format[@]}" format --in-place --configuration "$config_file" "${files[@]}"
python3 "$script_dir/check-block-separation.py" --fix "${files[@]}"
echo "formatted ${#files[@]} Swift file(s)"
