---
name: subagents
description: Use when the user says GLM.
---

# Call an external agent

Treat GLM as a direct request to call GLM 5.3 Flash through the existing `glm-flash` Codex profile. If it fails, report the failure; do not substitute another agent.

```sh
codex exec -p glm-flash -C "$workspace" --ephemeral \
  -c 'web_search="disabled"' \
  -c 'model_reasoning_effort="high"' \
  '<prompt>'
```
