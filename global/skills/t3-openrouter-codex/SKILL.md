---
name: t3-openrouter-codex
description: Set up a dedicated T3 Codex instance on OpenRouter when explicitly invoked.
disable-model-invocation: true
---

# Dedicated OpenRouter Codex in T3

Create the Codex home on this machine. Tell the user the T3 form values. Do not operate the T3 UI unless they ask. Never print `OPENROUTER_API_KEY`.

Leave `~/.codex` as the ChatGPT home. Install the `glm-flash` profile only when this invocation asked for GLM. If it did, follow [glm-flash.md](glm-flash.md) after the OpenRouter home is in place.

## Preconditions

Stop and tell the user what is missing:

- `codex` on PATH
- `OPENROUTER_API_KEY` set in this session. Check with `echo ${OPENROUTER_API_KEY:+yes}` (or `$env:OPENROUTER_API_KEY` on Windows). Do not echo the value.
- `~/.codex` exists if they want shared skills and `AGENTS.md`

## Agent work

Home: `$HOME/.codex-openrouter`. Expand `$HOME` before writing paths.

1. If `config.toml` already exists, show it and ask before overwriting.
2. Write `config.toml` mode `600` using the block below. `model_catalog_json` must be absolute. Do not add `env_key` next to `auth.command`; that pairing fails to load.
3. Auth command: Unix `sh` with `echo $OPENROUTER_API_KEY`. Windows `powershell` with `Write-Output $env:OPENROUTER_API_KEY`.
4. Fetch the catalog with `CODEX_HOME=<home> codex debug models`, discarding stdout. Confirm `models_cache.json` exists and its slugs contain `/`.
5. If `~/.codex/skills` exists, replace `<home>/skills` with a symlink to it unless that symlink is already in place. If `<home>/skills` has user content besides a Codex `.system` directory, ask first.
6. If `~/.codex/AGENTS.md` exists, symlink it to `<home>/AGENTS.md`.
7. Run `CODEX_HOME=<home> codex doctor --json`. Config must load, `model provider` must be `openrouter`, and OpenAI auth must not be required.
8. If this invocation asked for GLM, follow [glm-flash.md](glm-flash.md).

```toml
model_provider = "openrouter"
model = "~openai/gpt-latest"
model_reasoning_effort = "high"
model_catalog_json = "<absolute-home>/models_cache.json"

[model_providers.openrouter]
name = "OpenRouter"
base_url = "https://openrouter.ai/api/v1"
wire_api = "responses"

[model_providers.openrouter.auth]
command = "sh"
args = ["-c", "echo $OPENROUTER_API_KEY"]
```

## Tell the user

Give them this and wait.

New Codex instance:

- Binary path: `codex`
- CODEX_HOME path: `~/.codex-openrouter` (the tilde is required; T3 does not expand a leading `.`)
- Shadow home path: empty. A relative value like `openrouter` creates a Codex home in the current working directory.
- Launch arguments: empty. T3 passes these after `app-server`, so `--profile` is rejected.
- Identity: add sensitive env `OPENROUTER_API_KEY` on this instance.

After they save, tell them to reopen the OpenRouter provider. The picker should list OpenRouter slugs. T3 may still say authentication could not be verified. That is T3 looking for ChatGPT `auth.json`. Ignore it.

If OpenRouter models also appear on the default Codex instance, tell them to add this launch argument on that instance only, and only if `$HOME/.codex/models_cache.json` exists:

```text
-c model_catalog_json=<absolute $HOME/.codex/models_cache.json>
```

## Do not

- Copy `~/.codex/auth.json` into the OpenRouter home
- Put `--profile` in T3 launch arguments
- Combine `env_key` with `auth.command`
- Add a T3 instance for GLM. It is a CLI profile on `~/.codex`, not a second T3 Codex.
- Install `glm-flash` unless this invocation asked for it
