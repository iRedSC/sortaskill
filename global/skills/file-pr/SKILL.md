---
name: file-pr
description: Use when the user asks to create, file, or open a pull request.
---

# File PR

Before filing, check whether a PR for the branch already exists. Determine the repository's target branch and PR conventions, then review the full branch diff against that target.

Follow the repository's title convention. Otherwise, use a conventional-commit title that names the behavioral outcome rather than the implementation activity.

BAD > fix(lighting): Show movers in freecam overview
GOOD > fix(lighting): Remove entity-hide filter from freecam

Start the description with a plain explanation of the problem, then briefly explain the resulting behavior and verification. Do not open with a file-level implementation list.

BAD > "Define pack-authored particles, assign chunk effects, expose decorations, validate texture references, and document authoring."

GOOD > "Resource hits had no material-specific debris. This adds pack-defined chunk particles and uses the same textures for matching decorations."

Open a ready PR unless the user requests a draft or repository policy requires one. Return the PR link and any unresolved CI state.
