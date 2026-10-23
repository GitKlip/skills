---
name: create-story
description: File GitHub issues as "stories" on the repo's project board — a plain-language top half (user story, intent, acceptance criteria), then implementer details below a rule. Handles one story or a bulk import in dependency order. Use when the user wants to file a feature or backlog item, turn a discussion or playtest feedback into an issue, or says "make this a story", "add this to the board", or "file an issue for X".
---

# Create a story

A story is a GitHub issue that anyone can understand in 30 seconds, followed by what an implementer needs.
It lands on the project board in **Backlog**. `/refine-next` later adds the design and moves it to Ready.

## When to use

| Use this skill | Not this skill |
|---|---|
| Filing a feature, a backlog item, or a bug worth real investigation | A quick bug note with an obvious fix: `gh issue create` is enough |
| Turning a discussion or playtest feedback into an issue | Designing the solution: that's `/refine-next` |
| Importing a file or list of stories in dependency order | Splitting an agreed plan into build tickets: that's `/to-tickets` |

## The format

```markdown
## User story
As a <real role>, I want <capability>, so that <outcome>.

## Intent
<2–5 sentences: why this matters now.>

## Acceptance criteria
- [ ] <checkable outcome>
(3 to 6 items)

---

## Details
<For the implementer: context, scope, out of scope, code links pinned to a commit, references, Depends on.>
```

- **Title:** a tag plus 3–5 plain words, like `[HOST] Mute a player`. Name the task, not the mechanism. Nothing cute.
- **Above the rule: no code.** No file names, function names, identifiers or backticks. Write what a player, host or operator would notice.
- **User story:** a real role that exists in the product, such as a player, a host, the operator or a developer. Never an invented persona with a name.
- **Intent:** the reason, and why now. If you can't state one beyond restating the capability, the story isn't ready. Ask.
- **Acceptance criteria:** outcomes someone can check off, not tasks. "A muted player's actions are not sent to the DM", not "Add a mute button". Put the most important one first.
- **Details:** this is where code goes. Link code with `story.py permalink`, never a branch link. Put `Depends on: #<n> <title>` here, for hard prerequisites only.
- **Tags:** the repo's tags are listed under `tags` in `.claude/board.json`. Use a new tag only after the user agrees, because it creates a new `area:` label.

## Commands

All commands run from the repo. `<skill>` is this skill's directory.

| Command | What it does |
|---|---|
| `python3 <skill>/scripts/story.py lint --title T --body-file F` | Checks the format. Fix every error. Treat warnings as questions. |
| `python3 <skill>/scripts/story.py permalink path/to/file.ts:10-24` | Prints a link to those lines, pinned to the latest pushed commit |
| `python3 <skill>/scripts/story.py create --title T --body-file F --type Feature [--priority High]` | Lints, then creates the issue, labels it, sets the type, adds it to the board in Backlog. Reuses an issue with the same title. |
| `python3 <skill>/scripts/story.py verify <n>` | Re-checks the issue as GitHub stored it, plus its label, type and board column |

## Single story

1. **Get the substance.** You need a real role, a capability, a reason, and enough to write checkable outcomes. If anything is thin, ask. Don't invent a reason.
2. **Read the code** the story touches. Every claim in Details about current behavior must come from a file you read, linked with `permalink`. If you haven't verified something, say it needs confirming.
3. **Draft** the title and body in a temp file. Pick a type: `Spike` for research that ends in a decision, `Feature` otherwise. Suggest a priority only if the user gave you a basis, and say why.
4. **Lint** it. Fix all errors.
5. **Preview.** Show the user the title, type, priority and the full rendered body. Ask "Create this?" and wait for an explicit yes. "Looks good" counts. Silence or a new question doesn't.
6. **Create** it.
7. **Verify** it. Open what `verify` reports. Fix any problem with `gh issue edit`, then verify again.
8. **Report** the issue URL.

## Bulk import

1. **Read the whole source** and split it into stories. Keep the author's content. Reshape it to the format, but don't rewrite its meaning.
2. **Order by dependency.** Create prerequisites before the stories that need them. If a dependency doesn't match a story in the source, or you find a cycle, stop and ask.
3. **Lint every story.** Fix the format, and list anything you can't fix without the author.
4. **Preview the batch.** Show one line per story: order, title, type, priority, depends on. Ask "Create these N stories?" and wait for an explicit yes. One yes covers the batch.
5. **Create in order.** Keep a map from title to issue number, and rewrite each `Depends on: <title>` as `Depends on: #<n> <title>` before creating the story that has it.
6. **Re-run safely.** If the run stops partway, run it again. Stories that already exist come back as `"created": false` with their number.
7. **Verify** every story, then report how many were created and reused, with their URLs.

## Guardrails

- Never create, edit or relabel an issue without an explicit yes to the preview.
- Never link code that isn't pushed. `permalink` refuses it.
- Never state a fact about the code that you didn't read.
- Don't set Size, Sprint, Milestone or Estimate. Those are decided when work is picked up.
- Don't set any status other than Backlog unless the user asks.

## Example

Title: `[STORY] Show rolls before reveal`

```markdown
## User story
As a player, I want to see what everyone did and rolled while the DM is resolving, so that the wait becomes the best moment of the turn.

## Intent
Right now the shared screen sits on "resolving" for the whole model call. That wait is dead air in every turn. Playtesters asked for exactly this: see the party's actions and rolls before the outcome lands. It needs no new AI calls.

## Acceptance criteria
- [ ] Every party member's action and roll appears on the shared screen as soon as the turn locks
- [ ] They stay visible until the narration lands, and never appear at the same time as it
- [ ] Rolls show the die, modifier and total, never the target number
- [ ] Players see the same thing on their own devices

---

## Details
**Context.** Narration is one blocking structured call ([openrouter.ts#L14](https://github.com/<repo>/blob/<sha>/src/convex/adapters/ai/openrouter.ts#L14)). The shared screen shows a static message meanwhile ([PlayerLobby.tsx#L1360](https://github.com/<repo>/blob/<sha>/src/components/player/PlayerLobby.tsx#L1360)). Locked actions and fulfilled rolls are already in the database.

**In scope.** Shared screen and player app, reading existing queries.

**Out of scope.** Streaming narration. Any change to canonical state.

**References.** Playtest feedback, round 2.
```

## Done checklist

- [ ] Title is a tag plus 3–5 plain words
- [ ] Top half has no code and reads in 30 seconds
- [ ] 3–6 acceptance criteria, each one checkable
- [ ] Every code claim in Details is linked to a pushed commit
- [ ] The user said yes to the preview
- [ ] `verify` passed, and the URL was reported
