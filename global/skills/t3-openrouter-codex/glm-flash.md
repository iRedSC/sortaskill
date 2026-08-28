# GLM flash profile

Install only when this invocation asked for GLM. Write these files under `~/.codex`, not `~/.codex-openrouter`. `codex exec -p glm-flash` reads the default Codex home. Create `~/.codex` and `~/.codex/agents` if they are missing. Do not invent a ChatGPT `config.toml`.

Ask before overwriting either file.

Use `env_key`. Do not add `auth.command` here. Point `model_catalog_json` at the OpenRouter catalog just fetched (`$HOME/.codex-openrouter/models_cache.json`, absolute). If that file is missing, stop; do not fall back to the ChatGPT `models_cache.json`.

Prefer slug `z-ai/glm-5.3-flash` when it is in that catalog. Otherwise pick the newest `z-ai/glm-*-flash` slug from it and tell the user which one you used.

Mode `600` on both files.

`~/.codex/glm-flash.config.toml`:

```toml
model = "<glm-flash-slug>"
model_provider = "openrouter"
model_reasoning_effort = "high"
model_catalog_json = "<absolute-openrouter-home>/models_cache.json"

[model_providers.openrouter]
name = "OpenRouter"
base_url = "https://openrouter.ai/api/v1"
env_key = "OPENROUTER_API_KEY"
wire_api = "responses"
```

`~/.codex/agents/glm-flash.toml`:

```toml
name = "glm_flash"
description = "Fast, low-cost GLM worker for bounded exploration, implementation, testing, and summarization tasks delegated by the parent agent."
developer_instructions = """
Complete the delegated task within its stated scope.
Keep findings concrete, verify work when practical, and return a concise summary to the parent agent.
Do not expand the task or spawn additional agents unless the parent explicitly requests it.
"""

model = "<glm-flash-slug>"
model_provider = "openrouter"
model_reasoning_effort = "high"
model_catalog_json = "<absolute-openrouter-home>/models_cache.json"

[model_providers.openrouter]
name = "OpenRouter"
base_url = "https://openrouter.ai/api/v1"
env_key = "OPENROUTER_API_KEY"
wire_api = "responses"
```

Check with `codex --profile glm-flash doctor --json`. Config must load and `model provider` must be `openrouter`.

## Tell the user

GLM is a Codex CLI profile, not a T3 instance. Subagents use `codex exec -p glm-flash`. T3's ChatGPT Codex process still needs `OPENROUTER_API_KEY` in its environment for those calls. Do not put that key on the ChatGPT instance's T3 env table if they want the OpenRouter picker kept off that instance; the process environment is enough.
