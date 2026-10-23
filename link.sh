#!/usr/bin/env bash
# Symlink skills/<name> into ~/.claude/skills and bin/* into ~/.local/bin,
# so edits in this repo apply immediately.
set -euo pipefail
repo="$(cd "$(dirname "$0")" && pwd)"

link_into() {  # <dest dir> <source paths...>
  local dest="$1"; shift
  mkdir -p "$dest"
  for src in "$@"; do
    local target="$dest/$(basename "$src")"
    if [ -e "$target" ] && [ ! -L "$target" ]; then
      echo "skip $(basename "$src"): $target exists and is not a symlink" >&2
      continue
    fi
    ln -sfn "$src" "$target"
    echo "linked $target"
  done
  # Remove dangling links left by things deleted from this repo
  for link in "$dest"/*; do
    [ -L "$link" ] && [ ! -e "$link" ] && case "$(readlink "$link")" in
      "$repo"/*) rm "$link"; echo "unlinked $link" ;;
    esac
  done
  return 0
}

skills=(); for d in "$repo"/skills/*/; do [ -f "$d/SKILL.md" ] && skills+=("${d%/}"); done
bins=(); for f in "$repo"/bin/*; do [ -f "$f" ] && bins+=("$f"); done

link_into "$HOME/.claude/skills" "${skills[@]}"
link_into "$HOME/.local/bin" "${bins[@]}"

case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *) echo "Add ~/.local/bin to PATH:  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.zshrc" ;;
esac
