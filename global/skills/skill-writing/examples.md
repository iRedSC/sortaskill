# Examples

## Description

Bad: "Helps with documents."
Good: "Invoke this when the user asks for a report, summary, plan, overview, or just says HTML."

Bad: "A TDD helper for high-quality tests."
Good: "Use when the user or project instructions require test-driven development. Project instructions override this default method."

Bad: "Cut AI tells from writing."
Good: "Cut AI tells from any writing. Must always apply."

The bad lines describe the skill. The good lines tell the agent when to invoke.

## Immortality

Bad: "Use the v2 API. If this is before August 2026, use v1."
Good: "Call the current API in the project's docs. Do not keep a compatibility path unless the user asked for one."

Bad: "Use API v2 until the service migrates."
Good: "Use the API version selected by the project's current configuration and documentation."

Bad: a `SKILL.md` that lists every endpoint, model, or package version.
Good: a short procedure plus a sibling file, or a pointer to the source that owns those facts.

## Shape

Bad: one 200-line `SKILL.md` that loads every language and provider workflow for every invocation.
Good:

```
skill-name/
  SKILL.md      # procedure
  rules.md      # durable bar, if needed
  examples.md   # good/bad, if needed
```

Good: an 80-line checklist kept in `SKILL.md` because every item is used on every invocation and removing it measurably worsens the result.
