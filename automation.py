#!/usr/bin/env python3
"""Install, inspect, or remove periodic global-agent synchronization."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import plistlib
import shlex
import subprocess
import sys
from typing import Optional


LABEL = "com.iredsc.agents-global-sync"
WINDOWS_TASK = "Agents Global Sync"


class AutomationError(RuntimeError):
    pass


def run(command: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(command, check=check, text=True)
    except FileNotFoundError as exc:
        raise AutomationError(f"Required command is unavailable: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        raise AutomationError(f"Command failed with exit code {exc.returncode}: {command[0]}") from exc


def write_atomic(path: Path, content: bytes, dry_run: bool) -> None:
    print(f"write {path}")
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        temporary.write_bytes(content)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def remove_file(path: Path, dry_run: bool) -> None:
    if not path.exists():
        return
    print(f"remove {path}")
    if not dry_run:
        path.unlink()


def systemd_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def linux_paths(home: Path) -> tuple[Path, Path]:
    root = home / ".config" / "systemd" / "user"
    return root / "agents-global-sync.service", root / "agents-global-sync.timer"


def install_linux(home: Path, setup: Path, python: Path, locations: Path, minutes: int, dry_run: bool) -> None:
    service_path, timer_path = linux_paths(home)
    command = " ".join(systemd_quote(os.fspath(path)) for path in (python, setup, locations))
    service = f"""[Unit]
Description=Synchronize global agent instructions and skills

[Service]
Type=oneshot
ExecStart={command}
"""
    timer = f"""[Unit]
Description=Check for global agent updates

[Timer]
OnBootSec=1m
OnUnitActiveSec={minutes}m
AccuracySec=30s
Unit=agents-global-sync.service

[Install]
WantedBy=timers.target
"""
    write_atomic(service_path, service.encode("utf-8"), dry_run)
    write_atomic(timer_path, timer.encode("utf-8"), dry_run)
    commands = (
        ["systemctl", "--user", "daemon-reload"],
        ["systemctl", "--user", "enable", "--now", "agents-global-sync.timer"],
    )
    for command_parts in commands:
        print("run " + shlex.join(command_parts))
        if not dry_run:
            run(command_parts)


def uninstall_linux(home: Path, dry_run: bool) -> None:
    command = ["systemctl", "--user", "disable", "--now", "agents-global-sync.timer"]
    print("run " + shlex.join(command))
    if not dry_run:
        run(command, check=False)
    for path in linux_paths(home):
        remove_file(path, dry_run)
    reload_command = ["systemctl", "--user", "daemon-reload"]
    print("run " + shlex.join(reload_command))
    if not dry_run:
        run(reload_command)


def status_linux() -> int:
    return run(["systemctl", "--user", "status", "agents-global-sync.timer", "--no-pager"], check=False).returncode


def macos_path(home: Path) -> Path:
    return home / "Library" / "LaunchAgents" / f"{LABEL}.plist"


def launch_domain() -> str:
    if not hasattr(os, "getuid"):
        raise AutomationError("Cannot determine the current macOS user ID")
    return f"gui/{os.getuid()}"


def install_macos(home: Path, setup: Path, python: Path, locations: Path, minutes: int, dry_run: bool) -> None:
    path = macos_path(home)
    log_path = home / ".agents-sync" / "automation.log"
    if not dry_run:
        log_path.parent.mkdir(parents=True, exist_ok=True)
    definition = {
        "Label": LABEL,
        "ProgramArguments": [os.fspath(python), os.fspath(setup), os.fspath(locations)],
        "RunAtLoad": True,
        "StartInterval": minutes * 60,
        "StandardOutPath": os.fspath(log_path),
        "StandardErrorPath": os.fspath(log_path),
    }
    write_atomic(path, plistlib.dumps(definition, sort_keys=True), dry_run)
    domain = launch_domain()
    bootout = ["launchctl", "bootout", domain, os.fspath(path)]
    bootstrap = ["launchctl", "bootstrap", domain, os.fspath(path)]
    print("run " + shlex.join(bootout))
    print("run " + shlex.join(bootstrap))
    if not dry_run:
        run(bootout, check=False)
        run(bootstrap)


def uninstall_macos(home: Path, dry_run: bool) -> None:
    path = macos_path(home)
    command = ["launchctl", "bootout", launch_domain(), os.fspath(path)]
    print("run " + shlex.join(command))
    if not dry_run:
        run(command, check=False)
    remove_file(path, dry_run)


def status_macos() -> int:
    return run(["launchctl", "print", f"{launch_domain()}/{LABEL}"], check=False).returncode


def windows_task_command(python: Path, setup: Path, locations: Path) -> str:
    return subprocess.list2cmdline([os.fspath(python), os.fspath(setup), os.fspath(locations)])


def install_windows(setup: Path, python: Path, locations: Path, minutes: int, dry_run: bool) -> None:
    command = [
        "schtasks",
        "/Create",
        "/TN",
        WINDOWS_TASK,
        "/TR",
        windows_task_command(python, setup, locations),
        "/SC",
        "MINUTE",
        "/MO",
        str(minutes),
        "/F",
    ]
    print("run " + subprocess.list2cmdline(command))
    if not dry_run:
        run(command)


def uninstall_windows(dry_run: bool) -> None:
    command = ["schtasks", "/Delete", "/TN", WINDOWS_TASK, "/F"]
    print("run " + subprocess.list2cmdline(command))
    if not dry_run:
        run(command, check=False)


def status_windows() -> int:
    return run(["schtasks", "/Query", "/TN", WINDOWS_TASK, "/V", "/FO", "LIST"], check=False).returncode


def normalized_platform(value: str) -> str:
    if value.startswith("linux"):
        return "linux"
    if value == "darwin":
        return "macos"
    if value in ("win32", "cygwin", "msys"):
        return "windows"
    if value in ("linux", "macos", "windows"):
        return value
    raise AutomationError(f"Unsupported operating system: {value}")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("install", "status", "uninstall"))
    parser.add_argument("locations_index_file", nargs="?", type=Path, help="dotenv-style index of private locations")
    parser.add_argument("--interval", type=int, default=5, metavar="MINUTES", help="polling interval (default: 5)")
    parser.add_argument("--dry-run", action="store_true", help="show scheduler changes without applying them")
    parser.add_argument("--home", type=Path, default=Path.home(), help=argparse.SUPPRESS)
    parser.add_argument("--platform", default=sys.platform, help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    if args.interval < 1:
        print("Error: --interval must be at least one minute", file=sys.stderr)
        return 2

    try:
        platform = normalized_platform(args.platform)
        home = args.home.expanduser().resolve()
        setup = Path(__file__).resolve().with_name("setup.py")
        python = Path(sys.executable).resolve()
        if not setup.is_file():
            raise AutomationError(f"Cannot find setup.py beside automation.py: {setup}")

        if args.action == "install":
            if args.locations_index_file is None:
                raise AutomationError("install requires locations_index_file")
            locations = args.locations_index_file.expanduser().resolve()
            if not locations.is_file():
                raise AutomationError(f"Cannot read locations index: {locations}")
            if platform == "linux":
                install_linux(home, setup, python, locations, args.interval, args.dry_run)
            elif platform == "macos":
                install_macos(home, setup, python, locations, args.interval, args.dry_run)
            else:
                install_windows(setup, python, locations, args.interval, args.dry_run)
            print(f"Installed {platform} polling every {args.interval} minute(s).")
            return 0

        if args.action == "uninstall":
            if platform == "linux":
                uninstall_linux(home, args.dry_run)
            elif platform == "macos":
                uninstall_macos(home, args.dry_run)
            else:
                uninstall_windows(args.dry_run)
            print(f"Removed {platform} automation.")
            return 0

        if args.dry_run:
            print("Error: --dry-run is only valid with install or uninstall", file=sys.stderr)
            return 2
        if platform == "linux":
            return status_linux()
        if platform == "macos":
            return status_macos()
        return status_windows()
    except AutomationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
