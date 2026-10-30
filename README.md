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

One issue keeps one worktree (`.claude/worktrees/issue-<n>`) and one branch (`<issue>_<two_or_three_words>`, e.g. `168_llm_judge`)
from refinement to merge. Steps 1–3 all get it from `issue-worktree <n>`, which finds or creates it, so each step picks up
where the last one stopped, and the main checkout stays clean on the default branch. That lets several issues be in
different steps at once.

0. **`/create-story`**, in Claude Code. Files an issue in Backlog: a plain-language top half (user story, intent,
   acceptance criteria), a `---` rule, then implementer Details. `story.py lint` enforces the format.
   Area tags for each repo live under `tags` in `.claude/board.json`.
1. **`/refine-next [issue]`**, in Claude Code, with me. It interviews me about the top Backlog issue, writes a
   `## Design` section into the issue, and moves it to Ready.
   For any visible UI change it builds a throwaway prototype (and for a state model when I need to see it) in the repo's prototype folder,
   or writes a prompt for me to paste into v0. It commits the design's docs and the prototype on the issue branch and pushes it,
   so the design can link the prototype pinned to a commit.
   The prototype is frontend only, with dummy data.
2. **`build-ready-features [issue]`**, in a terminal, unattended. It is a Ralph loop: one fresh `claude -p`
   session per issue, in the issue's worktree. It plans in phases and builds with TDD and subagents.
   It validates with format, lint, types, tests and build, then checks UI changes in a browser.
   It runs one quick code review for bugs and missed acceptance criteria, and opens a PR with "How to test" steps.
   Simplification and the security review are left to `/ship-story`.
   Branches are `<issue>_<two_or_three_words>` (e.g. `168_llm_judge`),
   and PR titles are `<issue title> (task #<issue>)`. It deletes the prototype in the branch's last commit, so the PR never ships it.
   The script moves the issue to In review if a PR exists, otherwise to AI Blocked.
   It only takes Ready issues that have a `## Design` section, and won't start in a worktree with uncommitted changes.
   Runs on `MODEL` (opus), which hands fully specified tasks to sonnet subagents.
   Limits: `MAX_ISSUES` (3), `MAX_TURNS` (300), `MAX_BUDGET_USD` (25 per issue), and it stops after 2 blocks in a row.
   Logs: `~/.local/state/build-ready-features/<repo>/`.
3. **`/ship-story [issue]`**, in Claude Code, with me. It takes the top In review issue to merged.
   Fresh subagents review it in parallel: correctness, architecture against the agent docs, security, acceptance
   criteria and test integrity (opus for judgment, sonnet for systematic checks). It also runs the repo's UI
   run-through and a time-boxed browser QA of what changed. It confirms each finding, fixes the serious ones test-first,
   simplifies, and posts one `🚢 Ship report` comment on the PR. That comment is kept current and lets a re-run resume.
   It brings me only design, product and scope questions, plus at most two proposed lessons for the build loop.
   It merges (squash) only when I type "merge", then watches the production deploy and smoke run. A failure becomes a
   top-of-Backlog bug and a rollback offer. Finally it cleans up the worktree and branch.
   Repo-specific commands come from a `## Shipping` section in the repo's AGENTS.md.

`board --help` shows the board commands these all use.

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
