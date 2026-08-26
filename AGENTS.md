# Project

This repository is the canonical home for personal agent instructions and skills. `setup.py` distributes the contents of `global/` to every supported agent harness installed for the current user.

# Run the installer

The installer requires Python 3.9 or newer; Git is optional but required for the remote freshness check. It works on Linux, macOS, and Windows and does not require administrator privileges.

```sh
# Linux or macOS
python3 setup.py /path/to/locations.env

# Windows
py setup.py C:\path\to\locations.env
```

Before running setup, obtain the `locations_index_file` path from the user; ask for it when it has not already been provided. The file is an external dotenv-style registry such as `HOMELAB=homelab`. Values may be absolute, or relative to the directory that contains the index file. It must not contain credentials or be committed to this repository. Setup injects only that file's path into location-aware skills; index content changes do not require re-running setup.

By default, the script detects installed harnesses, fetches the current branch from `origin`, and uses that revision only when it is strictly ahead of the local checkout. If the fetch fails, the histories diverge, or the local checkout is already current or ahead, it uses the local `global/` directory.

Useful options:

```sh
python3 setup.py locations.env --dry-run   # Show changes without writing them
python3 setup.py locations.env --no-fetch  # Always use the local checkout
python3 setup.py locations.env --all       # Install for every supported harness
python3 setup.py locations.env --force     # Replace unmanaged skill collisions
python3 setup.py --help          # Show every option
```

Start a new agent session after installation because most harnesses discover instructions and skills at session startup.

# Automatic updates

`automation.py` registers a per-user background check using a systemd user timer on Linux, a LaunchAgent on macOS, or Task Scheduler on Windows. The default interval is five minutes and does not require administrator privileges.

```sh
# Install and start automatic checks
python3 automation.py install /path/to/locations.env

# Use a different polling interval
python3 automation.py install /path/to/locations.env --interval 15

# Inspect or remove the scheduled job
python3 automation.py status
python3 automation.py uninstall
```

The scheduled command fetches `origin`, but only rewrites a harness when its selected global content changed. Private repositories need Git credentials that work non-interactively; if a fetch fails, the local checkout remains the fallback. Re-run `automation.py install` after moving the repository because the scheduler stores absolute paths to Python and `setup.py`.

# Maintain the installer

- Edit global instructions in `global/AGENTS.md` and skills in `global/skills/<name>/SKILL.md`.
- A skill that requires a specific directory must declare its dotenv lookup key as `metadata.location-key` in `SKILL.md`. Its instructions must say to ask the user and append the mapping to the canonical index when that key is undefined.
- Add or change harness paths in `HARNESSES` in `setup.py`; keep all paths relative to the user's home directory.
- Maintain scheduler integrations in `automation.py`; installation and removal must remain per-user operations.
- Run `python3 -m unittest discover -s tests` (or `py -m unittest discover -s tests` on Windows) after changing the installer.
- Commit and push canonical changes so other machines can select the newer `origin` revision automatically.
