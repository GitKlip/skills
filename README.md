# skills

A small set of skills for how I work with AI coding agents. They're personal and reused across projects.
Stack-specific skills (Clerk, Convex, Vercel…) stay in each project, not here.

## Layout

```
skills/<name>/SKILL.md   # my own skills, plus forks I've customized
bin/                     # commands, linked into ~/.local/bin
prompts/                 # prompts the bin/ commands hand to Claude
third-party.sh           # the third-party skills I use, as install commands
link.sh                  # links skills/* and bin/* for live editing
```

## Backlog → PR workflow

Uses a GitHub Projects board with the columns Backlog, Ready, In progress, AI Blocked, In review, Done.
Each repo names its board in `.claude/board.json`: `{"owner": "<org-or-user>", "project": <number>}`.

0. **`/create-story`**, in Claude Code. Files an issue in Backlog: a plain-language top half (user story, intent,
   acceptance criteria), a `---` rule, then implementer Details. `story.py lint` enforces the format.
   Area tags for each repo live under `tags` in `.claude/board.json`.
1. **`/refine-next [issue]`**, in Claude Code, with me. It interviews me about the top Backlog issue, writes a
   `## Design` section into the issue, and moves it to Ready.
   For any visible UI change it builds a throwaway prototype on a `proto/<n>_…` branch (and for a state model when I need to see it),
   or writes a prompt for me to paste into v0.
   The prototype is frontend only, with dummy data.
2. **`build-ready-features [issue]`**, in a terminal, unattended. It is a Ralph loop: one fresh `claude -p`
   session per issue, each in its own worktree. It plans in phases and builds with TDD and subagents.
   It validates with format, lint, types, tests and build, then checks UI changes in a browser.
   It simplifies, runs a security review and a code review, and opens a PR with "How to test" steps.
   Branches are `<issue>_<two_or_three_words>` (e.g. `168_llm_judge`),
   and PR titles are `<issue title> (task #<issue>)`. The script moves the issue to In review if a PR exists, otherwise to AI Blocked.
   It only takes Ready issues that have a `## Design` section.
   Runs on `MODEL` (opus), which hands fully specified tasks to sonnet subagents.
   Limits: `MAX_ISSUES` (3), `MAX_TURNS` (300), `MAX_BUDGET_USD` (25 per issue), and it stops after 2 blocks in a row.
   Logs: `~/.local/state/build-ready-features/<repo>/`.
   With `REVIEW=1`, each PR then gets a second, fresh session (`prompts/review-ready-feature.md`): an in-depth
   correctness and security review against the design, fixes for the confirmed findings, a simplify pass, validation,
   a push, and a `🤖 Review pass` comment on the PR. Only then does the issue move to In review. I still merge.
   `build-ready-features --review <issue>` runs just that pass on an already-open PR.
3. I follow the PR's "How to test" steps on the preview deploy, review it, and merge. Merging is the deploy. Worktrees stay in `.claude/worktrees/issue-<n>` until I remove them.

`board --help` shows the board commands both of these use.

## Three kinds of skill

| Kind | Where it lives | How it updates |
|---|---|---|
| Mine | `skills/<name>/` in this repo | edit, commit, push |
| Third-party, used as-is | listed in `third-party.sh`, installed by `npx skills add -g` | `npx skills check -g` / `npx skills update -g` |
| Third-party, customized | copied into `skills/<name>/`, with an `upstream:` note at the top | diff against upstream by hand when it changes |

## Setup on a machine

```bash
git clone https://github.com/GitKlip/skills ~/Documents/projects/skills
cd ~/Documents/projects/skills
./link.sh          # my skills, as live symlinks (edits apply immediately)
./third-party.sh   # third-party picks
```

On a machine where I won't edit skills, I can skip the clone and install a snapshot:
`npx skills add GitKlip/skills -g -s '*'`

## Rules that keep this small

- Add a skill only after I've given Claude the same instruction about three times.
- Each skill should be readable in about a minute. If it isn't, split it or cut it.
- Delete skills I don't use.
- Never give a skill the same name as a plugin or third-party skill. Duplicate names trigger unpredictably.
- When a tweak only matters in one repo, put it in that repo's `AGENTS.md` rather than forking the skill.
