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
- When code replaces a validated input with a computed value, validate the computed value or the inputs it comes from — not just the field it replaced.
- Never merge, never push to the default branch, and never force-push.
- Put throwaway files (one-off browser-check scripts, screenshots) in the scratch folder the project's agent docs name, and delete them when you're done. If the docs name none, put them outside the repo. A scratch file anywhere else can fail the pre-commit hook's format or lint check even when git ignores it, and then every commit fails.
- Your run ends the moment you end your turn, and a turn that ends "waiting for X" is reported as blocked. So run the browser check and other long steps in the foreground, never as a background agent or background command, and never end your turn while anything you started is still running.

## Steps

1. Read the issue: `gh issue view <n> --comments`. If its design names a **Prototype**, read it. For a prototype folder, open it in this worktree, where refinement committed it, and look at its `screenshots/`; if it is missing, check out the folder from the commit the design links, or go by the design's description of it. For a v0 link, fetch the page; if you can't open it, go by the design's description of it. The prototype shows how the result should look and behave. Its code is throwaway: rebuild it properly rather than copying it.
2. Write an implementation plan with the `writing-plans` skill. Split it into phases that can each be tested on their own, and map every acceptance criterion to the test that proves it. Skip the skill's human review step and its choice of execution approach, and go straight to step 3.
3. Implement the plan with the `subagent-driven-development` skill. Every task follows the `tdd` skill: write a failing test, make it pass, then refactor.
4. Validate: run the project's format check, lint, type-check, tests and production build, using the commands in its agent docs or package scripts. Everything must pass.
5. If the change is visible in a UI, run the app and check it in a browser (Playwright), the way the project's docs describe. Walk through the design's **Human test** steps yourself. Note what you saw. This check is hit and miss, so it doesn't replace the human test.
6. Review once: run the `requesting-code-review` skill, asking only for bugs and missed acceptance criteria. Fix the serious findings, then run step 4 again. Don't simplify or run a security review: `/ship-story` does both later, with fresh reviewers, before anything merges.
7. If the branch has a prototype folder, delete it in its own commit (`git rm -r <folder>`), so the PR never ships it. The design's link to it keeps working.
   Finish with the `finishing-a-development-branch` skill, choosing "push and create a PR" without showing its menu.
   The PR title is the issue title followed by ` (task #<n>)`, for example `[CORE] LLM scene adjudication and grounding judge (task #168)`.
   The PR body must have:
   - `Closes #<n>`
   - a summary of what changed
   - test evidence: the validation commands you ran and their result, plus what the browser check showed
   - **How to test**: the design's Human test steps, adjusted to what was actually built, for the human to run on the preview deploy
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
