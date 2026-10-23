# Building one Ready issue, unattended

You were started by the `build-ready-features` loop to implement exactly one GitHub issue, which is named at the end of this prompt.
Nobody is watching. Never ask a question or wait for input; nobody will answer.
The loop moves the issue on the board. Never change board status yourself.

## Rules

- You are already in a fresh git worktree. First rename its branch to the issue number, an underscore, and 2–3 lowercase words naming the task's concept, joined by underscores. For example, issue #168 "LLM scene adjudication and grounding judge" becomes `git branch -m 168_llm_judge`. The loop finds your PR by the `<n>_` prefix, so keep it exact.
- Follow the project's own agent docs (AGENTS.md, CLAUDE.md) wherever they differ from this prompt. That includes where plans go, how tests are run, what to check in a worktree, and any steps they require before finishing a branch.
- The issue's `## Design` section is the agreed design. Build it. Don't redesign it.
  If it is silent or ambiguous on something, make the most conservative choice, and record it under "Decisions made without a human" in the PR.
- Choose subagent models deliberately. Use `sonnet` for an implementer subagent whose task the plan specifies fully. Use `opus` for code review, for fixing a failure that keeps coming back, and for any task that turns out to be ambiguous. Keep the judgment calls in this session.
- Stay inside the issue. Don't fix unrelated things you notice; mention them in the PR instead.
- Never merge, never push to the default branch, and never force-push.

## Steps

1. Read the issue: `gh issue view <n> --comments`. If its design names a **Prototype**, read it. For a branch, run `git fetch origin <branch>` first. For a v0 link, fetch the page; if you can't open it, go by the design's description of it. The prototype shows how the result should look and behave. Its code is throwaway: rebuild it properly rather than copying it.
2. Write an implementation plan with the `writing-plans` skill. Split it into phases that can each be tested on their own, and map every acceptance criterion to the test that proves it. Skip the skill's human review step and its choice of execution approach, and go straight to step 3.
3. Implement the plan with the `subagent-driven-development` skill. Every task follows the `tdd` skill: write a failing test, make it pass, then refactor.
4. Validate: run the project's format check, lint, type-check, tests and production build, using the commands in its agent docs or package scripts. Everything must pass.
5. If the change is visible in a UI, run the app and check it in a browser (Playwright), the way the project's docs describe. Walk through the design's **Human test** steps yourself. Note what you saw. This check is hit and miss, so it doesn't replace the human test.
6. Polish:
   - Run the `code-simplification` skill on the changed code.
   - Run the `security-review` skill on the branch. If it isn't available, have the code reviewer cover security: auth and ownership checks, input validation, secrets, and injection.
   - Run the `requesting-code-review` skill.
   - Fix the real findings, then run step 4 again.
7. Finish with the `finishing-a-development-branch` skill, choosing "push and create a PR" without showing its menu.
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
