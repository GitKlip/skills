---
name: refine-next
description: Refine the next Backlog issue on the project board into a Ready issue with an agreed design, by interviewing the user. Pass an issue number to refine that one instead.
disable-model-invocation: true
argument-hint: "[issue-number]"
---

# Refine next

Turn one issue into something an unattended agent can build without asking anyone anything.
The output is a `## Design` section in the issue body, and the issue moved to **Ready**.
`build-ready-features` picks up only Ready issues that have that section, so the heading must be exactly `## Design`.

The board is read and changed with the `board` command (`board --help`). It reads `.claude/board.json` at the repo root.
If that file is missing, ask the user for the board owner and project number, and write it.

## 1. Pick the issue

- If an issue number was passed, use it, whatever column it is in.
- Otherwise run `board list Backlog`, and take the first issue. Show the next four too, in one line each, so the user can swap.

## 2. Build your own view first

Read the issue and its comments (`gh issue view <n> --comments`), any issues it links to, the code it touches, and the project's agent docs (AGENTS.md or CLAUDE.md, plus any decision log they point to).
Form a recommendation before asking anything. Never ask what the code or docs already answer.

## 3. Interview

Load the `grilling` and `domain-modeling` skills. That pair is what `/grill-with-docs` runs, and it can't be called from another skill because it is user-only.
`grilling` drives the interview. `domain-modeling` challenges fuzzy terms and records them as they are resolved: terms go in `GLOSSARY.md`, and the rare hard-to-reverse decision goes in an ADR.
If the project's agent docs name their own decision log (for example `DECISIONS.md`), offer decisions there, in its format, instead of creating `docs/adr/`. Tell the user which doc files you changed. They are left uncommitted.

Steer the questions toward what an unattended implementer would otherwise have to guess:

- the behavior a user sees, including edge cases and failure states
- what is out of scope
- which existing patterns, modules or conventions to follow, and which to avoid
- how "done" is verified: tests that should exist, and any manual or visual check

The decisions are the user's. Your recommendations are proposals until the user replies. These rules override `grilling`'s round format:

- Ask at most 4 questions per round, the most consequential first. Hold the rest for later rounds.
- Under each question, write `**My recommendation:** <answer>`. Never start it with "Yes", because that reads as if the question was already answered.
- End every round with this line, then stop and wait for the reply:
  `Reply per question — "1 yes", "2 no: <what instead>", or "all yes".`
- Only treat a decision as settled after the user has answered it.

If the work is bigger than one reviewable PR, say so and propose a split. Either narrow this issue and file the remainder as new Backlog issues, or stop and leave the user to run `/to-tickets`.

## 3b. Check your assumptions

Before you draft, list everything you are assuming that the user has not explicitly confirmed. That includes facts you found in the code that shaped a decision, conservative defaults, and anything you decided without asking. Number each one, and give the evidence for any fact in one line.
End with `Anything wrong or missing? Reply "all good" or correct by number.`, then stop and wait. Don't draft until the user replies.

## 4. Write the design

Draft the section below and show it to the user. Revise it until they approve.

```markdown
## Design

**Approach** — what will be built, in a few sentences.

**Decisions**
- <decision> — <why>; rejected <alternative> because <reason>

**Touches** — files or modules expected to change.

**Acceptance criteria**
- [ ] <observable behavior, written so a test can check it>

**Verification** — tests to add, and any manual or visual check before review.

**Out of scope** — what not to do, even if tempting.
```

Keep the existing issue body. Replace an existing `## Design` section if there is one, otherwise append it.
Write the body to a temp file and run `gh issue edit <n> --body-file <file>`, which avoids shell-quoting problems.

## 5. Mark it Ready

Run `board set <n> Ready`. Confirm in one line, and offer to refine the next one.
