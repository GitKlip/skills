# Reviewer briefs

Each brief is given, whole, to a fresh subagent with the issue number, the PR URL and the worktree path.
Each subagent reports only. It never edits files, commits, pushes or comments on GitHub. `ship-story` confirms and fixes.

Every brief shares this frame:

> You are reviewing one PR before a human merges it. A different, unattended session built it, and you have none of its context, which is the point: judge the branch as it is.
> Read the issue and its `## Design` (`gh issue view <n> --comments`), the PR (`gh pr view <url>`), and the full diff against the default branch (`git diff origin/<default>...HEAD` in the worktree). Follow the project's agent docs (AGENTS.md or CLAUDE.md).
> Report each finding as: **severity** (serious or minor), **file:line**, **what is wrong**, and **how it fails** (the concrete input or state, and the wrong result). Leave out anything you couldn't tie to a concrete failure. Say "no findings" if there are none. Keep it under 500 words.

## Architecture alignment (opus)

Check the diff against the project's own rules, not general taste:

- Read the agent docs in full, plus every ADR the design names and every ADR the diff's area cites.
- Go through the docs' list of known pitfalls, and for each one the diff touches, check that it was handled. Name the pitfall in the finding.
- Check layer and module boundaries the docs define: what may import what, where logic of each kind belongs, and what must stay internal.
- If the PR changes a convention, check that it updated the docs that state it. If it changes architecture, check the system map or equivalent the docs name.
- If the PR adds a failure or degrade path, check where a human can see it.

## Acceptance criteria (sonnet)

For each acceptance criterion in the design:

- Find the test that proves it. Name the file and test.
- Judge whether that test would fail if the feature were broken. Read the test, don't trust its name. A test that only inspects an intermediate value, mocks the thing under test, or would pass on an empty implementation does not prove it.
- Report one line per criterion: **proven** (test named), **weak** (why), or **missing**.

Also check:

- Nothing listed under **Out of scope** was built.
- Every entry under "Decisions made without a human" in the PR body. List each with one line on whether it looks like the conservative choice, so the human can accept or reject it.

## Test integrity (sonnet)

List, by file and test name, every change in the diff that weakens the test suite:

- a removed or skipped test
- a loosened assertion (exact value → `toBeTruthy`, fewer fields checked, a widened regex)
- a longer timeout or an added retry
- an updated snapshot
- an added lint, type or coverage suppression
- a mock that replaces the code under test

For each one, say whether the diff justifies it. Also check that each new test sits in the test class and location the agent docs prescribe.

## Changed-feature QA (sonnet)

Exercise what this PR changed, in a real browser, time-boxed to about 20 minutes. Run the app from the worktree the way the agent docs describe (local server, test accounts, sign-in helpers).

1. Before touching the browser, write a short charter: the changed screens, what the user does on each, and the expected result of each step. Take it from the design's acceptance criteria, its **Human test** steps and the prototype variant, if one is named.
2. Walk the charter. Then try the edge cases it suggests: empty states, a second user, a refresh mid-flow, a failure state the design describes.
3. Report each step as **matched**, **differed** (what you saw), or **couldn't verify** (why). Note console errors and failed network requests. Save screenshots of anything that differed, and give their paths.

Don't fix anything, and don't widen the charter to unchanged areas.
