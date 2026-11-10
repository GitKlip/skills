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
1. **`/refine-story [issue]`**, in Claude Code, with me. It interviews me about the top Backlog issue, writes a
   `## Design` section into the issue, and moves it to Ready.
   For any visible UI change it builds a throwaway prototype with `/ui-prototype`: the app's real screens on a fake data layer,
   with only the changed parts swapped per variant, next to a `now` variant of today's UI. It never calls the backend.
   (For a state model I need to see, it uses the third-party `prototype` skill's logic branch.)
   It commits the design's docs and the prototype on the issue branch and pushes it, so the design can link the prototype
   pinned to a commit, and records which real file each copied screen came from.
2. **`build-ready-features [issue]`**, in a terminal, unattended. It is a Ralph loop: one fresh `claude -p`
   session per issue, in the issue's worktree. It plans in phases and builds with TDD and subagents.
   It validates with format, lint, types, tests and build, then checks UI changes in a browser.
   It opens a PR with "How to test" steps, without reviewing its own work.
   Then a second fresh session runs `/ship-story <issue> --prep` on the PR: every ship-story check, fixes and
   simplification, and the ship report, stopping before any question or merge. If prep fails, the PR still goes to
   In review, with a comment saying so.
   Branches are `<issue>_<two_or_three_words>` (e.g. `168_llm_judge`),
   and PR titles are `<issue title> (task #<issue>)`. It runs the prototype as its reference, diffs each copied screen against its
   original to list the UI changes, and compares its build with the prototype screen by screen before deleting the prototype
   in the branch's last commit, so the PR never ships it.
   The script moves the issue to In review once a PR exists and prep has run, otherwise to AI Blocked.
   It only takes Ready issues that have a `## Design` section, and won't start in a worktree with uncommitted changes.
   Runs on `MODEL` (opus), which hands fully specified tasks to sonnet subagents.
   Limits: `MAX_ISSUES` (3), `MAX_TURNS` (300), `MAX_BUDGET_USD` (25 per issue), and it stops after 2 blocks in a row.
   The prep run has its own: `SHIP_MAX_TURNS` (200), `SHIP_MAX_BUDGET_USD` (25). `SHIP_PREP=0` skips it.
   Logs: `~/.local/state/build-ready-features/<repo>/`.
   **`/build-story <issue>`**, in Claude Code, runs it for that one issue in the background and reports the PR or the
   block when it ends. The run stops if that session closes, so use a terminal for long or overnight runs.
3. **`/ship-story [issue]`**, in Claude Code, with me. It takes the top In review issue to merged.
   Fresh subagents review it in parallel: correctness, architecture against the agent docs, security, acceptance
   criteria and test integrity (opus for judgment, sonnet for systematic checks). It also runs the repo's UI
   run-through and a time-boxed browser QA of what changed. It confirms each finding, fixes the serious ones and the small, obvious ones test-first,
   simplifies, and posts one `🚢 Ship report` comment on the PR. That comment is kept current and lets a re-run resume.
   It brings me only design, product and scope questions, plus at most two proposed lessons for the build loop.
   It merges (squash) only when I type "merge", then watches the production deploy and smoke run. A failure becomes a
   top-of-Backlog bug and a rollback offer. Finally it cleans up the worktree and branch.
   After a prep run, it resumes from the prep report: it rechecks CI and open comments, then goes straight to the
   questions and the merge.
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
