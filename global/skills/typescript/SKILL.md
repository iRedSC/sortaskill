---
name: typescript
description: Use when designing or substantially changing TypeScript types, public APIs, or untrusted data boundaries. Skip routine edits where type design is not at issue.
---

# TypeScript best practices

Model the problem before choosing a TypeScript pattern. Use types to expose real distinctions and remove real invalid states, not to maximize type sophistication.

| Signal | Consider |
|---|---|
| Variants have different valid fields or behavior | A discriminated union and exhaustive handling |
| Identical primitives represent domains that must not mix | A branded or opaque type with controlled construction |
| A loose collection forces assertions or impossible-case throws | A stronger input type or an explicit optional result |
| Data enters from network, files, environment, persistence, or users | Parse `unknown` once at the boundary, then trust the result |
| An assertion or non-null escape hatch appears necessary | Find the missing information before weakening the compiler |
| Another schema or function already owns the same contract | Derive the type when it preserves that ownership |
| Positional arguments are easy to confuse | An object parameter |

Prefer normal TypeScript narrowing and `satisfies` when they express the fact. User-defined guards and assertions are valid at controlled boundaries, but they must earn the claim they introduce.

Read [patterns.md](references/patterns.md) when one of these signals applies or an example would clarify the choice.
