# Skill rules

## Description

The description is the trigger. Make selection cheap and precise.

- One or two sentences.
- Sentence one: when to invoke.
- Sentence two, if needed: when to skip, or that it must always apply.
- Include likely user language when it improves routing.
- Do not describe capabilities the body does not teach.

Keep automatic selection unless the skill is deliberately explicit-only. If it must run on every relevant turn, say so in the description.

## Body

`SKILL.md` is the procedure. Keep it short.

- Include instructions, examples, or decision criteria only when they change behavior.
- Cover the failure path and the skip path, not only the happy path.
- Do not duplicate another skill. Route to it when the dependency is reliable.
- Do not restate the global letter.
- One skill, one job.

## Siblings

Put conditional detail next to `SKILL.md` when loading it every time would waste attention.

- Keep core examples in `SKILL.md` when they define the skill's behavior. Move conditional examples, catalogs, and long patterns to sibling files.
- Link them one level deep.
- A sibling file the procedure never reads is dead weight. Delete it.

## Durable information

Prefer methods and retrieval paths over snapshots. Keep durable personal or operational constraints even when they are specific.

Do not copy versions, current tool UIs, or recipes already owned by configuration or authoritative documentation. Point at the source.

Hardcoded secrets, hostnames, and IDs do not belong. Read them from the environment or the user's source of truth. Never print secrets.

When a library, product, or path convention changes often, teach the agent how to discover it. Keep an exact value only when the skill must operate on it and no better source exists.

## Voice

Agent-facing prose is an instruction, not an essay. Prefer deletion. Match tone to scope.

Preserve deliberate user wording. Correct mistakes or ambiguity only when needed, and do not soften a strong preference into generic advice.
