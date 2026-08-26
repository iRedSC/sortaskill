---
name: skill-writing
description: Use when creating, editing, or reviewing an agent skill. Skip when the user only asks how an existing skill works.
---

# Skill writing

Read [rules.md](rules.md) before changing a skill. Read [examples.md](examples.md) when designing a trigger, deciding where information belongs, or resolving an ambiguous rule.

Locate the canonical personal-agents repository from the current checkout or installed locations index. If it is unknown, ask the user and add the mapping to the canonical index. Author under its `global/skills/<name>/` directory; do not edit tool-managed installed copies.

Preserve examples when they align behavior more efficiently than prose. Keep only examples that clarify a boundary, taste, failure mode, or output contract.

If the request is a question about an existing skill, answer it. Do not edit.
