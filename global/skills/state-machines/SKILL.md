---
name: state-machines
description: Use when writing or changing code where something moves through stages over time, such as async requests, retries, jobs, connections, sessions, payments, persisted status columns, or multi-step UI. Skip stateless transforms and two-state toggles.
---

# Find the hidden state machine

Obvious tells: several booleans describing one thing's progress, or a `status` field that some other fields only make sense under. You will catch these. Check for the ones you won't:

- **Correlated optionals.** `result?`, `error?`, `startedAt?` whose presence depends on each other. Nullability is encoding the state.
- **Await gaps.** Something can happen during an `await`: a second click, a newer request resolving first, unmount, cancel, reconnect while reconnecting. If a handler can re-enter or a stale result can land, the in-flight period is a state.
- **Partial resets.** A `catch`, `finally`, or teardown path that resets some fields and forgets others.
- **State hidden in values.** `retries < 3`, `expiresAt > now`, `lastSyncedAt == null`. Comparisons standing in for named states.
- **Unguarded persisted status.** Any code path can write `status = 'paid'`. Ask what a crash between two writes leaves behind and what recovers it after a restart.
- **Duplicate delivery.** Webhooks, queue messages, and retried requests arriving twice.
- **Split ownership.** The same lifecycle tracked in the database, memory, and UI, each able to disagree.
- **"Shouldn't happen."** A comment, assertion, or throw guarding a combination the types allow.

When a tell applies:

1. Name the states. Attach to each only the data valid in it.
2. Route every change through one transition function `(state, event) -> state` that rejects illegal transitions loudly. For persisted state, guard the write itself, such as `UPDATE ... WHERE status = 'pending'`.
3. Handle every state exhaustively, so a new state breaks the build or a test.
4. Test the transitions, including one illegal transition and one stale or duplicate event when the await or delivery tells applied.

Use the language's plain tools: tagged unions, enums with a match, a reducer. Reach for a library only for hierarchical or parallel states, timers, or actors.
