---
name: build-story
description: Run build-ready-features on one issue from inside Claude Code, in the background, and report the PR or the block when it ends. Requires an issue number. Use when the user types /build-story <n>.
disable-model-invocation: true
argument-hint: "<issue-number>"
---

# Build story

A thin wrapper around the `build-ready-features` command for one issue. The script does all the work and all the checks (Ready with a design, clean `main` checkout, clean worktree, board moves, comments). This skill only starts it, waits and reports. Never copy the script's logic here, so the two can't drift apart.

## Steps

1. **Require one issue number.** If the argument is missing or isn't a number, stop and ask for one. Never run the script with no argument: that builds up to `MAX_ISSUES` issues, each with its own budget.
2. **Say what it costs and where it runs**, in one line: up to $25 for the build and $25 for ship prep (more if `MAX_BUDGET_USD` or `SHIP_MAX_BUDGET_USD` are set), often an hour or more, and it stops if this session closes. Then start it without asking again; typing the command was the go-ahead.
3. **Run it from the repo's main checkout in the background**: `build-ready-features <n>` with Bash `run_in_background: true`. Don't poll its output while it runs; you are notified when it exits. The script itself refuses to run from a worktree or off the default branch, so if it exits at once, report its message and stop.
4. **When it exits, report the outcome first**, from the script's own lines:
   - `✔ #<n> → <PR url>` plus the `↳` ship-prep line: the PR link, whether prep finished (`RESULT: PREPPED`) or not, and that `/ship-story <n>` is next.
   - `✖ #<n> blocked: …`: the reason, and that the issue is now in AI Blocked with a comment.
   - `#<n> is not Ready with a design`: say to run `/refine-next <n>` first.
   Then give the log path(s) from the `▶` and `↳ ship prep — log:` lines, written in full.
