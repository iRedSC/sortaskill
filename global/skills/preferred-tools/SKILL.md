---
name: preferred-tools
description: Use when choosing a new tool, library, framework, service, or platform for a project.
metadata:
  location-key: PREFERRED_TOOLS
---

# Preferred tools

Read the locations index at the injected path, look up `PREFERRED_TOOLS`, then read that file before comparing candidates.

If the key or file does not exist, interview the user before recommending anything. Ask only what affects this choice and future ones, such as their existing stack, hard exclusions, operating constraints, and which tradeoffs matter most. Ask where the preference file should live when the key is missing. Create it and append `PREFERRED_TOOLS=<location>` to the canonical index after they answer.

Use recorded preferences as defaults, not as a reason to ignore project requirements. When the file does not cover a relevant tradeoff, ask a focused follow-up. Research current candidates from primary sources, explain departures from recorded preferences, and separate durable preferences from one-project constraints.

After the user chooses, ask whether the decision should become a durable preference. Update the preference file only when they confirm.

<!-- locations-index: setup.py replaces this comment in installed copies -->
