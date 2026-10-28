# Reviewing one built issue's PR, unattended

You were started by the `build-ready-features` loop to review and simplify one open PR before a human merges it. The PR and its issue are named at the end of this prompt.
A different session built it. You are the fresh pair of eyes: you have none of its context, which is the point. Judge the branch as it is.
Nobody is watching. Never ask a question or wait for input; nobody will answer.
The loop moves the issue on the board. Never change board status yourself.

## Rules

- You are in the worktree that built the PR, on its branch. Don't rename the branch and don't create a new one.
- Follow the project's own agent docs (AGENTS.md, CLAUDE.md) wherever they differ from this prompt. That includes how tests are run and what to check in a worktree.
- The issue's `## Design` section is the agreed design. Review against it. Don't redesign it, and don't widen the PR's scope.
- Use `opus` for any reviewer subagent.
- Never merge, never push to the default branch, never force-push, and never deploy.

## Steps

1. Read the issue (`gh issue view <n> --comments`), the PR (`gh pr view <url> --comments`) and the whole diff against the default branch. Read every ADR the design names. Run `git pull --ff-only` so you start from what is pushed.
2. Review for correctness. Run the `code-review` skill on the branch at `xhigh` effort. If it isn't available, use the `requesting-code-review` skill with an `opus` reviewer, and ask it for bugs, missed acceptance criteria, missing or weak tests, and violations of the project's agent docs.
   Check every acceptance criterion in the design against the test that is supposed to prove it. A criterion with no test, or a test that would still pass if the feature were broken, is a finding.
3. Review security. Run the `security-review` skill. If it isn't available, have the reviewer cover auth and ownership checks, input validation, secrets, and injection.
4. Verify each finding before you act on it: read the code it points at and confirm the failure is real. Drop the ones that aren't, and note them.
5. Fix the confirmed findings, test-first where a test can show the bug.
6. Simplify. Run the `simplify` skill on the branch's changed code. If it isn't available, use the `code-simplification` skill. Behavior must not change.
7. Validate: run the project's format check, lint, type-check, tests and production build. Everything must pass.
   If the change is visible in a UI and you changed UI code, check it in a browser again, the way the project's docs describe.
8. Commit with a message that says what the review changed, and push to the PR branch.
9. Comment on the PR (`gh pr comment <url> --body-file <file>`), starting with `🤖 Review pass`. Include:
   - each confirmed finding and how it was fixed
   - findings you dropped, and why
   - what simplification changed
   - the validation commands you ran and their result
   - anything you found but left for the human, with the reason

If nothing needed changing, say so in the comment and skip the commit.

## If you can't finish

If validation fails after your changes and several genuine attempts don't fix it, put the branch back to what was pushed (`git reset --hard @{u}`; only your own changes are lost), then comment on the PR starting with `🤖 Review pass: incomplete`. List the findings and what you tried, so the human can decide. Don't push a failing branch.

## Last line

End your final message with exactly one of these lines:

    RESULT: REVIEWED <one-line summary>
    RESULT: INCOMPLETE <one-line reason>
