---
name: ui-prototype
description: Build a throwaway UI prototype from the app's real screens on a fake data layer, with each design variant next to today's UI. Use when a UI change needs to be seen in a browser before it is built, or when refine-story asks for a UI prototype.
---

# UI prototype

A UI prototype is the app's real screens, fed by a fake data layer, with only the changed parts swapped per variant.
The user judges a design inside the app it will live in, and the implementer can see exactly what changes.
A freehand mockup looks nothing like the app, so nobody can build from it.

The project's agent docs say where prototypes live, how to run them, and which port to use. Follow them.
If they name no prototype folder, propose one to the user, set it up (excluded from lint, typecheck and format), and document it in the agent docs before building.

## Rules

- Never call the backend. Every read and write goes to the fake data layer.
- Always include a `now` variant: today's real UI, untouched, on the same fake data. Today next to the new design shows what changes, and often shows current bugs.
- Copy only the screens that change. Import everything else from the real code.
- Variants differ in what they decide (layout, hierarchy, the main control), not in colour.
- Every control responds, even if it only changes the fake data.

A brand-new screen with no existing parent is the one case for a fresh layout.
Even then, build it from the app's own components, theme and page frame, and mount it where it will live.

## 1. Find the real screen and its data

- Start from the route the user sees and follow it down to the top-level screen component that takes plain props (ids, names). Mount that, not the route's page, so auth and routing stay out.
- List every data hook under it: queries, mutations, actions, presence, subscriptions. Grep the screen and its children for the data library's hooks. Each one needs a fake answer.
- Note every server-side rule that changes what a viewer sees, such as another player's hidden action or a host-only field. The fake applies it too, or the prototype shows what the real app hides.

## 2. Fake the data layer

Replace the data client, not the components. Most data libraries read through one client passed to a provider, so the real hooks run unchanged against a fake one.

- Keep the dummy state in a small in-memory store with a version number that goes up on every change.
- Answer each query by its function name (and args) from the store. Cache each answer per state version, so the same state returns the same object. A new object on every read makes React re-render forever.
- Handle each mutation or action by changing the store, and return what the real one returns.
- `console.warn` any name you don't handle. An unanswered query usually shows as loading forever.

[convex.md](convex.md) is the worked example, for Convex.
For another stack, find the one object its hooks read from and fake that: an Apollo or urql client, a TanStack Query `QueryClient` filled with `setQueryData`, an SWR `fallback`, or `fetch` mocked with MSW.

## 3. Copy only the changed screens

- Copy each screen that changes into the prototype folder, as `<name>-b.tsx` for variant B. Point its imports at the real modules (`@/components/...`), not at other copies, unless that one changes too.
- Put new pieces in their own files.
- Start each copy with a comment naming its original and the commit it was copied from: `// copy of src/components/player/PlayerLobby.tsx @ a0ec2d8`. The design records the same list, so the implementer can diff each copy against its original.
- Change only what the variant needs. That diff is the implementer's list of changes, so any unrelated edit becomes work.

## 4. Wire it up

One page reads its settings from the URL, so every state is a link:

- `?variant=` picks the variant: `now`, `B`, `C`…
- `?screen=` picks who is looking, when more than one person sees the change (the TV, each player's phone, the host).
- `?phase=` picks a starting state, so a screenshot or a comparison can jump straight there.
- `?panel=hidden` hides the control panel.

Key each mounted screen by variant, screen and a reset counter. A reset bumps the counter, which remounts the screen and clears its local state (open dialogs, typed text) along with the store.

## 5. The control panel

A small floating panel, in a loud colour so it is clearly not part of the design. It:

- switches the variant (buttons, plus `←`/`→` when no input has focus) and the viewer
- acts for each simulated user (submit, roll, step away) and shows each one's state
- resets to each starting state
- collapses to one bar, and disappears with `?panel=hidden`
- renders nothing in a production build

## 6. Hand it over

- Start the dev server. Open every variant and screen, and check each renders with no console errors.
- Give the user the run command (with the worktree path) and every URL, in one fenced block. Give it again whenever the prototype changes or the server restarts.

When a variant is chosen, fold in the changes the user asked for. Then screenshot each screen of the chosen variant, and of `now` at the same states, with `?panel=hidden`:

- Use the viewport the screen is used at: 390×844 for a phone, 1920×1080 for a TV or desktop.
- Save them in the prototype's `screenshots/` folder as `<screen>-<phase>-<variant>.png`.
- Put the screenshot script in the scratch folder the agent docs name, and delete it when you're done.
