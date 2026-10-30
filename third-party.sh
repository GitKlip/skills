#!/usr/bin/env bash
# Third-party skills I use as-is, installed globally for Claude Code.
# See what a repo offers:  npx skills add <owner/repo> --list
# Check for updates:       npx skills check -g
set -euo pipefail

install() {
  local repo="$1"; shift
  local args=()
  for s in "$@"; do args+=(-s "$s"); done
  npx -y skills add "$repo" -g -a claude-code -y "${args[@]}"
}

# brainstorming hands off to writing-plans; subagent-driven-development calls
# using-git-worktrees, requesting-code-review and finishing-a-development-branch.
install obra/superpowers \
  brainstorming writing-plans \
  subagent-driven-development using-git-worktrees requesting-code-review finishing-a-development-branch

# grill-with-docs only calls grilling + domain-modeling, so those come with it.
install mattpocock/skills \
  diagnosing-bugs grill-with-docs grilling domain-modeling tdd to-tickets prototype

# Not installable on its own: garrytan/gstack office-hours calls ~20 gstack/bin/*
# helpers and needs the full gstack setup (https://github.com/garrytan/gstack).
