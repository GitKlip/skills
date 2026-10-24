---
name: refine-next
description: Refine the next Backlog issue on the project board into a Ready issue with an agreed design, by interviewing the user. Pass an issue number to refine that one instead.
disable-model-invocation: false
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

Decide whether the issue changes anything a user sees: a new or changed screen, component, layout, flow or visual state. If it does, say so in your first message, because step 3a then applies.

## 3. Interview

Load the `grilling` and `domain-modeling` skills. That pair is what `/grill-with-docs` runs, and it can't be called from another skill because it is user-only.
`grilling` drives the interview. `domain-modeling` challenges fuzzy terms and records them as they are resolved: terms go in `GLOSSARY.md`, and the rare hard-to-reverse decision goes in an ADR.
Follow the project's agent docs on where decisions and terms go and how ADRs are numbered and titled. Without such guidance, use `domain-modeling`'s defaults (`docs/adr/`, `GLOSSARY.md`).
Record in the issue's design which ADRs this refinement created, so the implementer reads them. Tell the user which doc files you changed. They are left uncommitted.

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

## 3a. Prototype every UI change

If the issue changes anything a user sees, a prototype is required, not optional. Don't wait for the user to ask, and don't skip it because the interview went smoothly: an unattended implementer guesses the look far more often than the behavior.
Build it once the first interview round has settled what the user sees and does, so the prototype shows decided behavior. Load the `prototype` skill and use its UI branch. In the same message, offer v0 as an alternative (below).

Skip it only when the visible change is trivial: copy text, one label, one extra field in an existing form that already shows the pattern. When you skip it, say so in one line with the reason, and the user can overrule you.

Outside UI, offer a logic prototype (the skill's logic branch) when the interview stalls on whether a state model feels right. Skip it for anything a sentence can decide.

For a UI prototype, these rules override the skill where they differ:

- Frontend only. Use dummy JSON for data, and never call the backend.
- Link every screen, so the user can click through the navigation.
- Make every button respond, even if it only changes the dummy data.

Commit it to a throwaway branch named `proto/<n>_<two_or_three_words>`, push it, and tell the user the one command that runs it.

For a UI question, offer v0 (v0.app) as an alternative. The user runs it by hand, so give them a prompt to paste into v0. Put the prompt in one fenced block, and include:

- the screen or screens and what the user does on each
- the dummy data, as a short JSON sample
- the rules above
- the project's stack: Next.js App Router, Tailwind and shadcn/ui
- the look of the existing pages, from the code you read
- a request for 2–3 clearly different variants

Then wait for the user to share the v0 link, or describe what they picked.

Once the user has picked a variant, record the branch or v0 link and the variant under **Prototype** in the design. Never merge the branch.

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

**Prototype** — `proto/<n>_<words>` or the v0 link, variant <name>: what it settled. For a UI change with no prototype, write why it was skipped. Omit this line only when nothing a user sees changes.

**Verification** — the tests to add, and how the agent checks the result in a browser if the change is visible.

**Human test** — the 2–5 things the user should try on the PR's preview before merging, as steps.

**Out of scope** — what not to do, even if tempting.
```

Keep the existing issue body. Replace an existing `## Design` section if there is one, otherwise append it.
Write the body to a temp file and run `gh issue edit <n> --body-file <file>`, which avoids shell-quoting problems.

## 5. Mark it Ready

Run `board set <n> Ready --bottom`, so it goes to the bottom of the Ready column and the issues refined earlier get built first. Confirm in one line, and offer to refine the next one.
