# Building one Ready issue, unattended

You were started by the `build-ready-features` loop to implement exactly one GitHub issue, which is named at the end of this prompt.
Nobody is watching. Never ask a question or wait for input; nobody will answer.
The loop moves the issue on the board. Never change board status yourself.

## Rules

- You are already in the issue's own git worktree. Refinement may have left commits on its branch: the design's docs (ADRs, glossary) and a prototype. Keep them, except the prototype, which you delete at the end (step 7).
- If the branch name doesn't start with the issue number and an underscore yet, rename it: the issue number, an underscore, and 2–3 lowercase words naming the task's concept, joined by underscores. For example, issue #168 "LLM scene adjudication and grounding judge" becomes `git branch -m 168_llm_judge`. The loop finds your PR by the `<n>_` prefix, so keep it exact. If it already has that prefix, keep its name.
- If the default branch has moved on since the branch was cut, merge it in first (`git fetch origin && git merge origin/<default>`). Never rebase.
- Follow the project's own agent docs (AGENTS.md, CLAUDE.md) wherever they differ from this prompt. That includes where plans go, how tests are run, what to check in a worktree, and any steps they require before finishing a branch.
- The issue's `## Design` section is the agreed design. Build it. Don't redesign it.
  If it is silent or ambiguous on something, make the most conservative choice, and record it under "Decisions made without a human" in the PR.
- Choose subagent models deliberately. Use `sonnet` for an implementer subagent whose task the plan specifies fully. Use `opus` for code review, for fixing a failure that keeps coming back, and for any task that turns out to be ambiguous. Keep the judgment calls in this session.
- Stay inside the issue. Don't fix unrelated things you notice; mention them in the PR instead.
- When a change reclassifies something (a class becomes a caster, a condition starts stopping actions), grep prompts, UI copy and docs for the old classification and update them in the same PR.
- When you change how a command is run or guarded, grep the agent docs and docs/ for every instruction that names the old command, and update each one in the same PR.
- When a change makes a function refuse in a new case (a mutation that now throws, a query that now rejects some callers), grep every caller, including scripts, simulations and end-to-end tests, and check that each one handles the refusal.
- When code replaces a validated input with a computed value, validate the computed value or the inputs it comes from — not just the field it replaced.
- For any screen that offers an action (a button, a link), check it still works in every later state of the thing it acts on — e.g. a game that leaves the lobby — and test that state. #216's removed screen kept offering "Join again" after the game started, which led only to a refusal.
- When the design or an ADR rejects an outcome ("Considered options"), search for existing code paths that still produce it, and refuse them in the same PR with a test.
- Never merge, never push to the default branch, and never force-push.
- Apart from the per-task reviews in `subagent-driven-development`, don't run a code review, simplify or run a security review. After your PR opens, the loop starts a fresh session that runs `/ship-story <n> --prep` on it: fresh reviewers check it, fix what they confirm and post a ship report before a human looks. Reviewing your own work here would repeat that work, less well.
- Keep this session's context small. It is re-read on every step, so it is most of the run's cost. Leave exploring code, browser checks and screenshot comparisons to subagents that write their results to a file or return a short report. Read code here only to settle a judgment call.
- Put throwaway files (one-off browser-check scripts, screenshots) in the scratch folder the project's agent docs name, and delete them when you're done. If the docs name none, put them outside the repo. A scratch file anywhere else can fail the pre-commit hook's format or lint check even when git ignores it, and then every commit fails.
- Your run ends the moment you end your turn, and a turn that ends "waiting for X" is reported as blocked. So run the browser check and other long steps in the foreground, never as a background agent or background command, and never end your turn while anything you started is still running.

## Steps

1. Read the issue: `gh issue view <n> --comments`. If its design names a **Prototype**, it is the reference for how the result looks and behaves. It is committed in this worktree; if the folder is missing, check it out from the commit the design links (`git checkout <sha> -- <folder>`).
   - Run it with the design's command (on this worktree's port, per the agent docs) and open each URL the design lists, for the chosen variant and `now`. It runs on fake data, so it needs no backend. Look at its `screenshots/` too.
   - For each copied file the design lists, diff the copy against its original at the recorded commit: `git show <sha>:<original> | diff -u - <copy>`. That diff is close to the exact list of UI changes to build. Put each change in the plan.
   - If an original changed since that commit (`git diff <sha> HEAD -- <original>`), or the prototype doesn't render, refresh the copy before relying on it: `git show <sha>:<original> > <scratch>/base` then `git merge-file <copy> <scratch>/base <original>` applies the copy's changes onto today's original. Resolve any conflict by keeping the prototype's intent. If it still won't render, go by the diff, the screenshots and the design's description.
   - Never copy prototype code into product code. Rebuild each change properly in the real files, with tests.
2. Have one `opus` subagent write the implementation plan with the `writing-plans` skill, so its exploration of the code stays out of this session. Give it the issue number, the worktree path, the ADRs the design names, the UI changes you listed in step 1, and these instructions: split the plan into phases that can each be tested on their own, map every acceptance criterion to the test that proves it, skip the skill's human review step and its choice of execution approach, save the plan where the agent docs say, and reply with only the plan's path and a list of open questions with the conservative answer it chose for each. Read the plan once, check it against the design, and record those answers under "Decisions made without a human".
3. Implement the plan with the `subagent-driven-development` skill. Every task follows the `tdd` skill: write a failing test, make it pass, then refactor. Keep its per-task reviews, but skip the whole-branch review and fix wave in its `references/final-review.md`: the ship prep runs fresher reviews of the whole branch. Do its **Finish** part: put every `Ruling:` from the ledger under "Decisions made without a human" in the PR, and delete the plan's workspace.
4. Validate: run the project's format check, lint, type-check, tests and production build, using the commands in its agent docs or package scripts. Everything must pass.
5. If the change is visible in a UI, have a `sonnet` subagent run the app and check it in a browser (Playwright), the way the project's docs describe. It walks through the design's **Human test** steps and returns, in under 300 words, what it saw at each step and the paths of its screenshots. Read a screenshot yourself only when the report leaves a doubt. This check is hit and miss, so it doesn't replace the human test.
   If the agent docs' `## Shipping` section names a UI run-through command (in wego-rpg, `npm run test:e2e:game`, which costs a little model money), also run it before opening the PR whenever the change touches a screen the run-through passes through. Run it in the foreground. It plays the whole flow, including teardown, against the real backend, which is how it caught #76's story pane throwing on every player's page once the host deleted the game. Fix what it finds, then run step 4 again.
6. If the design names a prototype, compare your build with it before deleting it. The prototype's `now` variant mounts the real components, so it now shows your build on the same fake data. If your build reads data the fake doesn't answer yet, or a screen takes a new prop, update the prototype's fake or page to match first.
   Then have a `sonnet` subagent do the comparison. Give it the design's **Prototype** section and the screens and phases it lists. For each one, it opens `?variant=now` and the chosen variant side by side, at the viewport the screen is used at, with `?panel=hidden`, screenshots both into the scratch folder, and returns a list of differences, each with both screenshot paths. Look at the screenshots of each difference yourself, and decide which ones the design explains. Fix the rest, run step 4 again, and have the subagent compare again. List the differences you kept, with why, for the PR body.
7. If the branch has a prototype folder, delete it in its own commit (`git rm -r <folder>`), so the PR never ships it. The design's link to it keeps working. Then run `rm -rf src/.next`: a dev cache that still lists the deleted route makes Turbopack panic on every page, and the UI run-through then fails at sign-in.
   Finish with the `finishing-a-development-branch` skill, choosing "push and create a PR" without showing its menu.
   The PR title is the issue title followed by ` (task #<n>)`, for example `[CORE] LLM scene adjudication and grounding judge (task #168)`.
   The PR body must have:
   - `Closes #<n>`
   - a summary of what changed
   - test evidence: the validation commands you ran and their result, plus what the browser check showed
   - **Prototype comparison**, if the design named a prototype: each screen and state compared, and every difference from the prototype with its reason, or "none"
   - **How to test**: the design's Human test steps, adjusted to what was actually built, for the human to run on the preview deploy
   - **Pitfalls checked**: before opening the PR, re-read the agent docs' known pitfalls ("Common Pitfalls" and the Convex rules in AGENTS.md, or the equivalent). For each one the diff touches, one line saying how it is handled
   - Decisions made without a human
   - anything left undone
   Never deploy. Merging the PR is the human's deploy step.

## If you are blocked

You are blocked when validation still fails after several genuine attempts, when a needed secret or service is missing, when the design contradicts the code in a way you can't resolve conservatively, or when required tools keep being denied.

Then:
1. Commit your work in progress on the branch, and push it.
2. Comment on the issue (`gh issue comment <n> --body-file <file>`), starting with `🤖 AI Blocked:`. Say what you tried, what failed, and exactly what a human needs to decide or provide.
3. Stop. Don't open a PR.

## Last line

End your final message with exactly one of these lines:

    RESULT: PR <url>
    RESULT: BLOCKED <one-line reason>
