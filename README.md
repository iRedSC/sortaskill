# Agents

My global instructions and reusable skills for coding agents.

The goal is not to give an agent every piece of context up front. It is to give the agent durable direction and teach it how to find the right context when needed.

## Where information belongs

| Home | Responsibility |
|---|---|
| Global `AGENTS.md` | Durable philosophy, judgment, and authority |
| Global skills | Reusable methods and personal workflows |
| Project `AGENTS.md` | Project-specific goals, constraints, and standards |
| Project skills | Recurring procedures specific to that project |
| Repository and runtime | Current facts |
| Compiler, lint, tests, and CI | Mechanical enforcement |

Treat the agent like a capable engineer entering a codebase for the first time. Give it direction, retrieval paths, and the constraints it cannot infer. Let it inspect the system for everything else.

## Install

Create a private locations index outside this repository:

```dotenv
HOMELAB=homelab
PREFERRED_TOOLS=preferred_tools.md
```

Values may be absolute, or relative to the directory that contains the index file. Do not put credentials in the file or commit it to this repository.

```sh
python3 setup.py /path/to/locations.env
```

This installs `global/AGENTS.md` and `global/skills/` into the agent harnesses found on the machine. Start a new session afterward.

## Credits

Several skills began as copies or adaptations from other collections:

- [`tdd`](global/skills/tdd), [`typescript-best-practices`](global/skills/typescript-best-practices), and [`unslop`](global/skills/unslop) come from [pstack](https://github.com/cursor/plugins/tree/main/pstack).
- [`grilling`](global/skills/grilling) comes from [Matt Pocock's skills](https://github.com/mattpocock/skills).
- [`skill-writing`](global/skills/skill-writing) draws from Matt Pocock's [`writing-great-skills`](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-great-skills).

They have been modified for my workflow. Credit for the original ideas and implementations belongs to their authors.

## Development

```sh
python3 -m unittest discover -s tests
```
