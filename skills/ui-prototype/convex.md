# Faking Convex

`convex/react` hooks read everything through the client given to `ConvexProvider`. Give it a fake one. Checked against convex 1.46.

What the hooks call:

- `useQuery` calls `client.watchQuery(ref, args)`. It uses three methods of the result: `localQueryResult()` (the value, or `undefined` while loading), `onUpdate(cb)` (subscribe; returns an unsubscribe function) and `journal()` (return `undefined`).
- `useMutation` calls `client.mutation(ref, args)`, and `useAction` calls `client.action(ref, args)`. Both return promises.
- `usePaginatedQuery` uses a different client method. If a screen uses it, read `node_modules/convex/dist/esm/react/client.js` and fake that one too.
- `getFunctionName(ref)` from `convex/server` gives the name, like `queries/game:getGame`.
- `@convex-dev/presence` heartbeats are mutations. Return dummy tokens.

```tsx
'use client';
import { useMemo } from 'react';
import { ConvexProvider, type ConvexReactClient } from 'convex/react';
import { getFunctionName, type FunctionReference } from 'convex/server';

class FakeConvexClient {
  url = 'https://prototype.invalid';
  private cache = new Map<string, { version: number; value: unknown }>();
  // viewer: who is looking (a player id), or null for the host. Apply the server's visibility rules per viewer.
  constructor(private store: Store, private viewer: string | null) {}

  watchQuery(ref: FunctionReference<'query'>, args: unknown = {}) {
    const name = getFunctionName(ref);
    const key = `${name} ${JSON.stringify(args)}`;
    return {
      localQueryResult: () => {
        const v = this.store.state.version;
        const hit = this.cache.get(key);
        if (hit?.version === v) return hit.value; // same state → same object
        const value = answer(name, args, this.store.state, this.viewer);
        this.cache.set(key, { version: v, value });
        return value;
      },
      onUpdate: (cb: () => void) => this.store.subscribe(cb),
      journal: () => undefined,
    };
  }

  async mutation(ref: FunctionReference<'mutation'>, args: Record<string, unknown>) {
    return handle(getFunctionName(ref), args, this.store, this.viewer);
  }

  async action(ref: FunctionReference<'action'>, args: Record<string, unknown>) {
    return handle(getFunctionName(ref), args, this.store, this.viewer);
  }
}

export function FakeConvex({ store, viewer, children }: { store: Store; viewer: string | null; children: React.ReactNode }) {
  const client = useMemo(() => new FakeConvexClient(store, viewer), [store, viewer]);
  return <ConvexProvider client={client as unknown as ConvexReactClient}>{children}</ConvexProvider>;
}
```

`Store` holds the dummy state plus `version`, and calls its listeners on every change. `answer` switches on the function name, returns the dummy rows the real query would, and warns on any name it doesn't know. `handle` does the same for writes.

If a screen also needs auth (`useConvexAuth`, Clerk's `useUser`), give it the props or a fake provider the app already has for tests. Don't sign in.
