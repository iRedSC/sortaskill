#!/usr/bin/env python3
"""Distribute this repository's global instructions and skills to agent harnesses."""

from __future__ import annotations

import argparse
from contextlib import contextmanager, nullcontext
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from typing import Iterable, Optional
import zipfile


MINIMUM_PYTHON = (3, 9)
MANIFEST_VERSION = 2
CURSOR_FRONTMATTER = "---\ndescription: Global agent instructions\nalwaysApply: true\n---\n\n"
LOCATIONS_MARKER = "<!-- locations-index: setup.py replaces this comment in installed copies -->"
LOCATION_KEY = re.compile(r"^[A-Z][A-Z0-9_]*$")


@dataclass(frozen=True)
class Harness:
    name: str
    commands: tuple[str, ...]
    marker: Path
    instructions: Optional[Path]
    skills: Path
    instruction_format: str = "markdown"


@dataclass(frozen=True)
class LocationsIndex:
    path: Path
    content: str
    keys: tuple[str, ...]


HARNESSES = (
    Harness("codex", ("codex",), Path(".codex"), Path(".codex/AGENTS.md"), Path(".codex/skills")),
    Harness(
        "cursor",
        ("cursor",),
        Path(".cursor"),
        Path(".cursor/plugins/local/global-agents/rules/global.mdc"),
        Path(".cursor/skills"),
        "cursor-mdc",
    ),
    Harness("claude", ("claude",), Path(".claude"), Path(".claude/CLAUDE.md"), Path(".claude/skills")),
    Harness("gemini", ("gemini",), Path(".gemini"), Path(".gemini/GEMINI.md"), Path(".gemini/skills")),
    Harness(
        "opencode",
        ("opencode",),
        Path(".config/opencode"),
        Path(".config/opencode/AGENTS.md"),
        Path(".config/opencode/skills"),
    ),
    Harness(
        "copilot",
        ("copilot",),
        Path(".copilot"),
        Path(".copilot/copilot-instructions.md"),
        Path(".copilot/skills"),
    ),
)


class InstallerError(RuntimeError):
    pass


def log(message: str) -> None:
    print(message)


def run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            ["git", "-C", os.fspath(repo), *args],
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise InstallerError("Git is not installed") from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.decode(errors="replace").strip()
        raise InstallerError(detail or f"git {' '.join(args)} failed") from exc


def current_branch(repo: Path) -> str:
    result = run_git(repo, "symbolic-ref", "--quiet", "--short", "HEAD", check=False)
    if result.returncode == 0:
        return result.stdout.decode().strip()
    return "main"


def remote_source(repo: Path, remote: str, branch: str, temporary_root: Path) -> Optional[Path]:
    """Return an extracted remote global directory only when remote is ahead."""
    try:
        local_revision = run_git(repo, "rev-parse", "HEAD").stdout.decode().strip()
        run_git(repo, "fetch", "--quiet", remote, branch)
        remote_revision = run_git(repo, "rev-parse", "FETCH_HEAD").stdout.decode().strip()

        if local_revision == remote_revision:
            log(f"Source: local checkout ({remote}/{branch} is current)")
            return None

        ancestor = run_git(
            repo,
            "merge-base",
            "--is-ancestor",
            local_revision,
            remote_revision,
            check=False,
        )
        if ancestor.returncode != 0:
            log(f"Source: local checkout (local and {remote}/{branch} have diverged or local is ahead)")
            return None

        archive = run_git(repo, "archive", "--format=zip", remote_revision, "global").stdout
        extracted = temporary_root / "remote"
        with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
            for member in bundle.infolist():
                member_path = Path(member.filename)
                if member_path.is_absolute() or ".." in member_path.parts:
                    raise InstallerError("The remote archive contains an unsafe path")
            bundle.extractall(extracted)

        source = extracted / "global"
        validate_source(source)
        log(f"Source: {remote}/{branch} at {remote_revision[:12]} (newer than local)")
        return source
    except (InstallerError, zipfile.BadZipFile) as exc:
        log(f"Warning: remote freshness check failed ({exc}); using local checkout")
        return None


def validate_source(source: Path) -> None:
    instructions = source / "AGENTS.md"
    skills = source / "skills"
    if not instructions.is_file():
        raise InstallerError(f"Missing global instructions: {instructions}")
    if not skills.is_dir():
        raise InstallerError(f"Missing global skills directory: {skills}")

    invalid = [path for path in skills.iterdir() if path.is_dir() and not (path / "SKILL.md").is_file()]
    if invalid:
        names = ", ".join(sorted(path.name for path in invalid))
        raise InstallerError(f"Skill directories missing SKILL.md: {names}")


def load_locations_index(path: Path) -> LocationsIndex:
    canonical = path.expanduser().resolve()
    try:
        content = canonical.read_text(encoding="utf-8")
    except OSError as exc:
        raise InstallerError(f"Cannot read locations index {canonical}: {exc}") from exc

    keys: list[str] = []
    for number, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in line:
            raise InstallerError(f"Invalid locations index line {number}: expected KEY=value")
        key, value = line.split("=", 1)
        key = key.strip()
        if not LOCATION_KEY.fullmatch(key):
            raise InstallerError(f"Invalid locations index key on line {number}: {key!r}")
        if key in keys:
            raise InstallerError(f"Duplicate locations index key on line {number}: {key}")
        if not value.strip():
            raise InstallerError(f"Empty locations index value on line {number}: {key}")
        keys.append(key)

    normalized = content.rstrip() + "\n"
    return LocationsIndex(canonical, normalized, tuple(keys))


def render_unknown_info(source: Path, locations: LocationsIndex) -> bytes:
    body = source.read_text(encoding="utf-8").rstrip() + "\n"
    if body.count(LOCATIONS_MARKER) != 1:
        raise InstallerError(f"unknown-info skill must contain exactly one locations marker: {source}")
    indented_content = "\n".join(f"    {line}" if line else "" for line in locations.content.splitlines())
    injected = (
        "## Installed locations index\n\n"
        "Canonical file (write new mappings here):\n\n"
        f"    {locations.path}\n\n"
        "Current contents:\n\n"
        f"{indented_content}\n"
    )
    return body.replace(LOCATIONS_MARKER, injected).encode("utf-8")


def directory_fingerprint(source: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(candidate for candidate in source.rglob("*") if candidate.is_file()):
        relative = path.relative_to(source).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def installation_fingerprint(source: Path, locations: LocationsIndex) -> str:
    digest = hashlib.sha256()
    digest.update(directory_fingerprint(source).encode("ascii"))
    digest.update(b"\0")
    digest.update(os.fspath(locations.path).encode("utf-8"))
    digest.update(b"\0")
    digest.update(locations.content.encode("utf-8"))
    return digest.hexdigest()


def available_harnesses(home: Path, install_all: bool) -> list[Harness]:
    if install_all:
        return list(HARNESSES)
    return [
        harness
        for harness in HARNESSES
        if (home / harness.marker).exists() or any(shutil.which(command) for command in harness.commands)
    ]


def instruction_bytes(source: Path, instruction_format: str) -> bytes:
    body = source.read_text(encoding="utf-8").rstrip() + "\n"
    if instruction_format == "cursor-mdc":
        body = CURSOR_FRONTMATTER + body
    return body.encode("utf-8")


def write_atomic(path: Path, content: bytes, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        path.unlink()
    temporary = path.with_name(f".{path.name}.agents-sync-{os.getpid()}")
    try:
        temporary.write_bytes(content)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_manifest(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("version") in (1, MANIFEST_VERSION):
            data["version"] = MANIFEST_VERSION
            return data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return {"version": MANIFEST_VERSION, "harnesses": {}}


@contextmanager
def single_run_lock(path: Path):
    """Hold a non-blocking per-user lock on POSIX and Windows."""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+b")
    acquired = False
    try:
        if os.name == "nt":
            import msvcrt

            if path.stat().st_size == 0:
                handle.write(b"\0")
                handle.flush()
            handle.seek(0)
            try:
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                acquired = True
            except OSError:
                acquired = False
        else:
            import fcntl

            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
            except BlockingIOError:
                acquired = False
        yield acquired
    finally:
        if acquired:
            if os.name == "nt":
                import msvcrt

                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def is_legacy_repo_link(path: Path, repo: Path) -> bool:
    if not path.is_symlink():
        return False
    try:
        target = (path.parent / os.readlink(path)).resolve(strict=False)
        target.relative_to(repo.resolve())
        return True
    except (OSError, ValueError):
        return False


def remove_path(path: Path, dry_run: bool) -> None:
    if dry_run:
        return
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def copy_skill(
    source: Path,
    destination: Path,
    repo: Path,
    managed: bool,
    force: bool,
    dry_run: bool,
    locations: LocationsIndex,
) -> bool:
    exists = destination.exists() or destination.is_symlink()
    replaceable = managed or is_legacy_repo_link(destination, repo)
    if exists and not replaceable and not force:
        log(f"  Warning: skipped unmanaged skill collision at {destination} (use --force to replace it)")
        return False
    if dry_run:
        return True
    if exists:
        remove_path(destination, False)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)
    if source.name == "unknown-info":
        write_atomic(destination / "SKILL.md", render_unknown_info(source / "SKILL.md", locations), False)
    return True


def tree_contains_source(source: Path, destination: Path, locations: LocationsIndex) -> bool:
    if not destination.is_dir():
        return False
    for source_file in (path for path in source.rglob("*") if path.is_file()):
        destination_file = destination / source_file.relative_to(source)
        try:
            expected = (
                render_unknown_info(source_file, locations)
                if source.name == "unknown-info" and source_file.name == "SKILL.md"
                else source_file.read_bytes()
            )
            if not destination_file.is_file() or destination_file.read_bytes() != expected:
                return False
        except OSError:
            return False
    return True


def harness_is_current(
    harness: Harness,
    source: Path,
    home: Path,
    entry: dict,
    fingerprint: str,
    locations: LocationsIndex,
) -> bool:
    if entry.get("fingerprint") != fingerprint:
        return False

    source_skills = {path.name: path for path in (source / "skills").iterdir() if path.is_dir()}
    if set(entry.get("skills", [])) != set(source_skills):
        return False

    if harness.instructions is not None:
        destination = home / harness.instructions
        try:
            if destination.read_bytes() != instruction_bytes(source / "AGENTS.md", harness.instruction_format):
                return False
        except OSError:
            return False

    return all(tree_contains_source(skill, home / harness.skills / name, locations) for name, skill in source_skills.items())


def sync_harness(
    harness: Harness,
    source: Path,
    repo: Path,
    home: Path,
    previous_skills: Iterable[str],
    force: bool,
    dry_run: bool,
    locations: LocationsIndex,
) -> list[str]:
    log(f"{harness.name}:")
    if harness.instructions is not None:
        destination = home / harness.instructions
        write_atomic(destination, instruction_bytes(source / "AGENTS.md", harness.instruction_format), dry_run)
        log(f"  instructions -> {destination}")

    skill_root = home / harness.skills
    source_skills = {path.name: path for path in (source / "skills").iterdir() if path.is_dir()}
    previously_managed = set(previous_skills)

    for stale_name in sorted(previously_managed - source_skills.keys()):
        stale = skill_root / stale_name
        if stale.exists() or stale.is_symlink():
            remove_path(stale, dry_run)
            log(f"  removed stale managed skill: {stale_name}")

    # The repository previously used skills/ instead of global/skills. Clean up
    # broken or stale links from that layout without touching unrelated entries.
    if skill_root.is_dir():
        for candidate in skill_root.iterdir():
            if candidate.name not in source_skills and is_legacy_repo_link(candidate, repo):
                remove_path(candidate, dry_run)
                log(f"  removed stale legacy skill link: {candidate.name}")

    installed: list[str] = []
    for name, skill_source in sorted(source_skills.items()):
        destination = skill_root / name
        if copy_skill(
            skill_source,
            destination,
            repo,
            name in previously_managed,
            force,
            dry_run,
            locations,
        ):
            installed.append(name)
    log(f"  skills -> {skill_root} ({len(installed)} installed)")
    return installed


def save_manifest(path: Path, manifest: dict, dry_run: bool) -> None:
    if dry_run:
        return
    content = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    write_atomic(path, content, False)


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("locations_index_file", type=Path, help="dotenv-style index of private locations")
    parser.add_argument("--all", action="store_true", help="install for every supported harness")
    parser.add_argument("--dry-run", action="store_true", help="show destinations without writing")
    parser.add_argument("--no-fetch", action="store_true", help="skip origin and use local content")
    parser.add_argument("--force", action="store_true", help="replace unmanaged skill folders with matching names")
    parser.add_argument("--home", type=Path, default=Path.home(), help=argparse.SUPPRESS)
    parser.add_argument("--remote", default="origin", help=argparse.SUPPRESS)
    parser.add_argument("--branch", help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    if sys.version_info < MINIMUM_PYTHON:
        print("Python 3.9 or newer is required", file=sys.stderr)
        return 2

    args = parse_args(argv)
    repo = Path(__file__).resolve().parent
    local_source = repo / "global"
    try:
        validate_source(local_source)
        locations = load_locations_index(args.locations_index_file)
    except InstallerError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    home = args.home.expanduser().resolve()
    harnesses = available_harnesses(home, args.all)
    if not harnesses:
        log("No supported agent harnesses were detected. Use --all to create every target.")
        return 0

    state_root = home / ".agents-sync"
    manifest_path = state_root / "manifest.json"
    lock = nullcontext(True) if args.dry_run else single_run_lock(state_root / "run.lock")
    with lock as acquired:
        if not acquired:
            log("Another agents sync is already running; nothing to do.")
            return 0

        manifest = load_manifest(manifest_path)
        manifest.setdefault("harnesses", {})
        changed = 0

        with tempfile.TemporaryDirectory(prefix="agents-sync-") as temporary:
            source = local_source
            if args.no_fetch:
                log("Source: local checkout (--no-fetch)")
            else:
                branch = args.branch or current_branch(repo)
                source = remote_source(repo, args.remote, branch, Path(temporary)) or local_source

            fingerprint = installation_fingerprint(source, locations)
            if args.dry_run:
                log("Dry run: no files will be changed")

            for harness in harnesses:
                entry = manifest["harnesses"].get(harness.name, {})
                if harness_is_current(harness, source, home, entry, fingerprint, locations):
                    log(f"{harness.name}: up to date")
                    continue
                installed = sync_harness(
                    harness,
                    source,
                    repo,
                    home,
                    entry.get("skills", []),
                    args.force,
                    args.dry_run,
                    locations,
                )
                manifest["harnesses"][harness.name] = {
                    "fingerprint": fingerprint,
                    "skills": installed,
                }
                changed += 1

        save_manifest(manifest_path, manifest, args.dry_run)
    log(f"Done: {changed} of {len(harnesses)} harness(es) changed. Start new sessions after an update.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
