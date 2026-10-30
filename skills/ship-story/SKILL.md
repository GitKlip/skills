---
name: ship-story
description: Take an issue whose PR is In review to merged, with the user. Runs fresh reviews, a UI run-through and simplification, fixes what it confirms, posts a report on the PR, and merges only when the user says "merge". Pass an issue number to ship that one instead of the top of In review.
disable-model-invocation: false
argument-hint: "[issue-number]"
---

# Ship story

Take one issue from **In review** to merged. `build-ready-features` built it unattended and reviewed its own work. This skill gives it fresh eyes, exercises it in a real browser, fixes what is confirmed, and brings the user only the decisions that need them.

The user is here, but their time is the scarce part. Do the slow, mechanical work in subagents, and bring back short results and clear questions.

The board is read and changed with the `board` command (`board --help`), which reads `.claude/board.json`.
Repo-specific facts (commands, the UI run-through, risk areas, production checks) come from the project's agent docs (AGENTS.md or CLAUDE.md), especially a `## Shipping` section. Those docs win wherever they differ from this skill.

## Hard rules

- **Never merge without the user typing "merge" in this session**, after you've shown the gate is clear. Never auto-merge, and never enable GitHub auto-merge.
- Never force-push, never push to the default branch, never deploy, and never roll back production yourself. A rollback is offered, and the user does it.
- Don't widen the PR. Anything outside the issue becomes a follow-up issue, never part of this PR, unless the user says otherwise.
- Never delete a worktree with uncommitted files. List them and ask instead.

## 1. Pick the issue and set up

- If a number was passed, use it. Otherwise run `board list "In review"`, take the first, and show the next few in one line each so the user can swap.
- `board pr <n>` gives the PR URL and branch. If there's no open PR, say so and stop.
- Work in the issue's worktree: `issue-worktree <n>` prints its path, creating it from the PR's branch if this machine has none. `cd` there and stay there; never edit the main checkout. Follow the agent docs for setting up a worktree (env files, dependencies). Then `git pull --ff-only` there.
- Read the issue and its `## Design` (`gh issue view <n> --comments`), the PR and its comments (`gh pr view <url> --comments`), the ADRs the design names, and the `## Shipping` section.

**Resume.** Look for an earlier report comment on the PR, marked `<!-- ship-story -->`. It records the commit it checked and which checks ran. Skip any check already recorded for the current head commit, and say which ones you skipped.

## 2. Checks, in parallel

Start every check below at once, each as its own fresh subagent. A subagent gets the issue number, PR URL, worktree path and its brief from [reviewers.md](reviewers.md), never this session's history.

| Check | Model | How |
|---|---|---|
| Correctness | opus | `code-review` skill at `xhigh` on the branch, report only (no `--fix`, no `--comment`) |
| Architecture alignment | opus | brief in reviewers.md |
| Security | opus | `security-review` skill on the branch |
| Acceptance criteria | sonnet | brief in reviewers.md |
| Test integrity | sonnet | brief in reviewers.md |
| UI run-through | sonnet | the committed run-through command from `## Shipping`; skip if the change can't affect the UI |
| Changed-feature QA | sonnet | brief in reviewers.md; only if the change is visible in a UI |

Add these only when the diff calls for them:

- **Schema safety**, when the schema file changes: opus, using the `convex-migration-helper` skill. Check the change against the shape of the production data. It blocks the merge if it needs a migration plan.
- **Backend performance**, when queries or indexes change: opus, using the `convex-performance-audit` skill, limited to what the diff touches.
- **Real-model eval**, when prompts or model calls change (the agent docs say which): never run it. Offer it in the report with its command and rough cost.

If the `## Shipping` section names no UI run-through command, or the command doesn't exist yet, say so in the report and ask the user to do the run-through by hand.

While they run, check CI on the head commit (`gh pr checks <url>`) and list every review thread and bot comment that has no answer, including the system-map check.

## 3. Sort the findings

Read every finding yourself, against the code it points at. Keep only the ones you've confirmed are real, and note the dropped ones with a reason. Rank the confirmed ones:

- **Serious**: a bug, a missed acceptance criterion, a security hole, a weakened test that hides a failure, or a broken architecture rule. These block the merge.
- **Minor**: everything else. Listed, not fixed, unless the user says "fix".

Some findings need the user, because they're a design, product or scope call, or they conflict with the agreed design. Hold those as questions. Don't fix them.

## 4. Fix, simplify, validate

1. Fix every confirmed serious finding that doesn't need the user. Work test-first: write a test that fails because of the bug, then fix it. Use a sonnet subagent when the fix is fully specified, and opus when it isn't.
2. Simplify. Run the `simplify` skill on the PR's changed code only (sonnet). Behavior must not change.
3. Validate locally with the project's validate command (see the agent docs) before each push, then push. CI on the new head commit is the final word.
4. If the fixes touched UI code, run the UI run-through again.

If a fix keeps failing, stop fixing it, revert your own change to it, and make it a question for the user.

## 5. Post the report

Post the report on the PR as soon as the checks are done, before asking the user anything. That way it survives a lost terminal. Then edit **that same comment** as things change. Find it by its marker, and use `gh api` to edit it in place.

```markdown
<!-- ship-story -->
## 🚢 Ship report

**Checked commit:** <sha> · **Checks run:** <list> · **Skipped (already done for this commit):** <list or none>

**Status:** <Blocked: n items | Ready to merge | Merged | Smoke failed>

### Needs your decision
1. <question> — **My recommendation:** <answer>

### Fixed
- <finding> → <what changed, commit>

### Minor (not fixed)
- <finding>

### Dropped findings
- <finding> — <why it isn't real>

### Acceptance criteria
- [x] <criterion> — <test or evidence>

### UI
- Run-through: <passed / failed / missing, with what was seen>
- Changed-feature QA: <what was checked, what was seen>
- Couldn't verify: <steps a human should try on the preview, or none>

### Offered, not run
- <e.g. real-model eval: command, rough cost>

### Lessons proposed
- <change> — <applied / skipped>

**Work done:** <how many subagents, fix rounds and QA runs, so an unusually heavy run stands out>
```

## 6. Decisions with the user

Show the user a short summary: status, then the numbered questions. These rules apply:

- Ask at most 4 questions per round, the most consequential first.
- Under each question, write `**My recommendation:** <answer>`.
- End each round with: `Reply per question — "1 yes", "2 no: <what instead>", or "all yes".` Then wait.

Out-of-scope work the user agrees to becomes a new Backlog issue, filed with the `create-story` skill.

**Lessons.** If this review caught something the build loop should have caught, propose at most two concrete changes as questions: an agent-docs pitfall, a guard test, or a line in the build prompt (`prompts/build-ready-feature.md` in the skills repo). Show the exact text. Apply only the ones the user approves.

Update the report after each round.

## 7. Merge gate

Before offering the merge, bring the branch up to date with the default branch by **merging it in** (never rebase, since that would need a force-push):

- Resolve mechanical conflicts yourself: lockfiles, generated files, import lists, the system map. If the PR adds an ADR whose number the default branch already uses, renumber it, following the agent docs. For a conflict in logic, show the user both sides with a recommendation, and wait.
- If the default branch moved, validate again, run the UI run-through again, and push.

The gate is clear only when all of these are true:

- CI passed on the head commit. If CI didn't run (for example, its path filters skip this diff), the full local validation passed instead.
- The UI run-through passed, or the user did it by hand.
- No serious finding is open, and no question is unanswered.
- Every acceptance criterion has evidence.
- The PR contains no prototype folder (the agent docs name it). If the build left one, delete it in its own commit.
- Every review thread and bot comment is answered.
- Schema safety passed, if it ran.

Then offer the merge in one message: the gate results, the preview link, and the "couldn't verify" list, so the user can try those steps first if they want. Wait for "merge".

On "merge", squash-merge with the PR title as the subject and `Closes #<n>` in the body (`gh pr merge <url> --squash`). Don't move the board yourself. The board's own automation moves the issue to Done when the PR merges.

## 8. After the merge

- Watch the production deploy and the post-deploy smoke run that the `## Shipping` section names, and report the result.
- **If either fails**, file a bug issue linked to this one with the `create-story` skill, put it at the top of Backlog (`board set <bug> Backlog --top`), and offer the user a rollback with the exact steps. Don't roll back yourself.
- **Clean up**, with the `finishing-a-development-branch` skill's safety rules: remove the PR's worktree, local branch and remote branch, if GitHub didn't already delete it. The prototype went with the branch, and the design's link to it still works.
- Update the report's status for the last time, and confirm in one line. Offer to ship the next In review issue.
