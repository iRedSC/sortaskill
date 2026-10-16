---
name: memory
description: Use before choices the user's standing preferences could shape (tools, style, workflow, replies), when they refer to something they told you before, or when they react strongly (preference, dislike, anger, amazement) or ask you to remember something. Never write a memory without their approval.
metadata:
  location-key: MEMORY
---

# Memory

Read the locations index at the injected path and look up `MEMORY`. Memories live in `INDEX.md` inside that directory.

If the key is undefined and `~/.memory/INDEX.md` exists, append `MEMORY=<absolute path of ~/.memory>` to the canonical index and use it. Otherwise ask the user where their memories are, or where to create them, suggesting `~/.memory`. After they answer, create the directory and `INDEX.md` if missing, then append the mapping.

## Recall

Read `INDEX.md` before acting. Apply entries scoped `global` or to the current project. Memories are defaults; an instruction in the current conversation wins. When the two conflict, follow the current instruction and propose updating the memory.

If no memory covers a preference-shaped choice, such as picking a tool, ask before recommending. Ask only what affects this choice and future ones: existing stack, hard exclusions, operating constraints, and which tradeoffs matter most.

## Propose

Propose a memory only when the user:

- reacts strongly: preference, dislike, anger, amazement, or similar;
- states a standing rule, even calmly ("always", "never", "remember this");
- contradicts an existing memory.

Never propose generic events, one-task details, facts another file already owns, or secrets.

Record the durable rule, not the reaction. Anger often comes from a one-off failure; propose only the rule it implies.

- Reaction: "Why do you keep using em dashes?!"
- Good: `- Never use em dashes in prose. (global, 2026-10-16)`
- Bad: `- User got angry about em dashes.`

## Approve

Add each proposal as a **[M]** line in the Your call section, quoting the exact entry. When it replaces an entry, quote the old one too.

"yes" or "rcm" approves every pending **[M]** line. "<number> no" rejects one. An unanswered **[M]** line expires; write nothing.

Subagents never propose or write memories.

## Write

`INDEX.md` groups entries under `## <topic>` headings, one line each:

    - <rule> (<global or project name>, <YYYY-MM-DD>)

Replace a contradicted entry instead of adding a second one. After writing, tell the user which lines changed.

<!-- locations-index: setup.py replaces this comment in installed copies -->
