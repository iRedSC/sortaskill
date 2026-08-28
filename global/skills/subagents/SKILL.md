---
name: subagents
description: Use when requiring a subagent, or when user says GLM or GROK.
---

# Call an external agent

Treat GLM and GROK as direct requests to call that specific external agent; default to Grok when none is specified.

## Select

- `GLM` means GLM 5.3 Flash through the existing `glm-flash` Codex profile.
- `GROK` means Cursor Grok 4.6. Default to `cursor-grok-4.6-high` unless the user names another Grok variant.
- A subagent request that names neither means Grok.
- Do not substitute one for the other if the selected agent fails.

## GLM

```sh
codex exec -p glm-flash -C "$workspace" --ephemeral \
  -c 'web_search="disabled"' \
  -c 'model_reasoning_effort="high"' \
  '<prompt>'
```

## Grok

```sh
agent --print --output-format text --model cursor-grok-4.6-high \
  --workspace "$workspace" '<prompt>'
```

For a read-only request, add `--mode ask`. Add `--force` only when the user has already authorized implementation in that workspace.
