# Building one Ready issue, unattended

You were started by the `build-ready-features` loop to implement exactly one GitHub issue, which is named at the end of this prompt.
Nobody is watching. Never ask a question or wait for input; nobody will answer.
The loop moves the issue on the board. Never change board status yourself.

## Rules

- You are already in a fresh git worktree. First rename its branch: `git branch -m <branch>`, using the branch name given below.
- Follow the project's own agent docs (AGENTS.md, CLAUDE.md) wherever they differ from this prompt. That includes where plans go, how tests are run, what to check in a worktree, and any steps they require before finishing a branch.
- The issue's `## Design` section is the agreed design. Build it. Don't redesign it.
  If it is silent or ambiguous on something, make the most conservative choice, and record it under "Decisions made without a human" in the PR.
- Stay inside the issue. Don't fix unrelated things you notice; mention them in the PR instead.
- Never merge, never push to the default branch, and never force-push.

## Steps

1. Read the issue: `gh issue view <n> --comments`.
2. Write an implementation plan with the `writing-plans` skill. Skip its human review step and its choice of execution approach, and go straight to step 3.
3. Implement the plan with the `subagent-driven-development` skill. Every task follows the `tdd` skill: write a failing test, make it pass, then refactor.
4. Run the project's full validation (the test and type-check commands its agent docs name). Everything must pass.
5. Polish: run the `code-simplification` skill on the changed code, then the `requesting-code-review` skill. Fix real findings, then run validation again.
6. If the change is visible in a UI and the project's docs say how to check it visually, do that check.
7. Finish with the `finishing-a-development-branch` skill, choosing "push and create a PR" without showing its menu.
   The PR body must have:
   - `Closes #<n>`
   - a summary of what changed
   - test evidence: the validation commands you ran and their result
   - Decisions made without a human
   - anything left undone

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
