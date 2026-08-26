import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "setup.py"
AUTOMATION = REPO / "automation.py"
SKILL_NAMES = sorted(path.name for path in (REPO / "global" / "skills").iterdir() if path.is_dir())


class SetupScriptTests(unittest.TestCase):
    def run_setup(self, home: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        locations = home.parent / f"{home.name}-locations.env"
        if not locations.exists():
            locations.write_text("# Test locations\nHOMELAB=/private/homelab/docs\n", encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(locations), "--home", str(home), "--no-fetch", *arguments],
            cwd=REPO,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_all_harnesses_receive_instructions_and_skills(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            result = self.run_setup(home, "--all")
            self.assertEqual(result.returncode, 0, result.stderr)

            instruction_paths = (
                ".codex/AGENTS.md",
                ".cursor/plugins/local/global-agents/rules/global.mdc",
                ".claude/CLAUDE.md",
                ".gemini/GEMINI.md",
                ".config/opencode/AGENTS.md",
                ".copilot/copilot-instructions.md",
            )
            canonical = (REPO / "global" / "AGENTS.md").read_text(encoding="utf-8").rstrip() + "\n"
            for relative in instruction_paths:
                installed = (home / relative).read_text(encoding="utf-8")
                if relative.endswith(".mdc"):
                    self.assertTrue(installed.startswith("---\n"))
                    self.assertTrue(installed.endswith(canonical))
                else:
                    self.assertEqual(installed, canonical)

            skill_roots = (
                ".codex/skills",
                ".cursor/skills",
                ".claude/skills",
                ".gemini/skills",
                ".config/opencode/skills",
                ".copilot/skills",
            )
            for relative in skill_roots:
                actual = sorted(path.name for path in (home / relative).iterdir())
                self.assertEqual(actual, SKILL_NAMES)
                for skill in SKILL_NAMES:
                    self.assertTrue((home / relative / skill / "SKILL.md").is_file())

            injected = (home / ".codex" / "skills" / "unknown-info" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("HOMELAB=/private/homelab/docs", injected)
            self.assertIn("Canonical file", injected)
            preferred = (home / ".codex" / "skills" / "preferred-tools" / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("HOMELAB=/private/homelab/docs", preferred)
            self.assertIn("location-key: PREFERRED_TOOLS", preferred)
            self.assertNotIn("locations-index: setup.py replaces", preferred)

    def test_unmanaged_skill_collision_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            collision = home / ".codex" / "skills" / SKILL_NAMES[0]
            collision.mkdir(parents=True)
            custom = collision / "SKILL.md"
            custom.write_text("custom\n", encoding="utf-8")

            result = self.run_setup(home)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(custom.read_text(encoding="utf-8"), "custom\n")
            self.assertIn("unmanaged skill collision", result.stdout)

    def test_manifest_removes_only_stale_managed_skills(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            managed = home / ".codex" / "skills" / "removed-skill"
            unmanaged = home / ".codex" / "skills" / "keep-me"
            managed.mkdir(parents=True)
            unmanaged.mkdir(parents=True)
            manifest = home / ".agents-sync" / "manifest.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(
                json.dumps({"version": 1, "harnesses": {"codex": {"skills": ["removed-skill"]}}}),
                encoding="utf-8",
            )

            result = self.run_setup(home)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(managed.exists())
            self.assertTrue(unmanaged.exists())

    def test_dry_run_does_not_write(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            result = self.run_setup(home, "--all", "--dry-run")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((home / ".codex").exists())
            self.assertFalse((home / ".agents-sync").exists())

    def test_unchanged_second_run_is_a_no_op(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            first = self.run_setup(home, "--all")
            self.assertEqual(first.returncode, 0, first.stderr)
            instructions = home / ".codex" / "AGENTS.md"
            original_mtime = instructions.stat().st_mtime_ns

            second = self.run_setup(home, "--all")
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertIn("codex: up to date", second.stdout)
            self.assertIn("0 of 6 harness(es) changed", second.stdout)
            self.assertEqual(instructions.stat().st_mtime_ns, original_mtime)

    def test_scheduler_dry_runs_are_cross_platform(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            expectations = {
                "linux": "agents-global-sync.timer",
                "macos": "LaunchAgents",
                "windows": "schtasks",
            }
            locations = home.parent / "scheduler-locations.env"
            locations.write_text("DOCS=/private/docs\n", encoding="utf-8")
            for platform, expected in expectations.items():
                with self.subTest(platform=platform):
                    result = subprocess.run(
                        [
                            sys.executable,
                            str(AUTOMATION),
                            "install",
                            str(locations),
                            "--platform",
                            platform,
                            "--home",
                            str(home),
                            "--interval",
                            "7",
                            "--dry-run",
                        ],
                        cwd=REPO,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn(expected, result.stdout)
            self.assertEqual(list(home.rglob("*")), [])

    def test_newer_origin_revision_is_used(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            remote = root / "origin.git"
            publisher = root / "publisher"
            checkout = root / "checkout"
            home = root / "home"

            def git(cwd: Path, *arguments: str):
                subprocess.run(
                    ["git", *arguments],
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )

            remote.mkdir()
            git(remote, "init", "--bare")
            publisher.mkdir()
            git(publisher, "init")
            git(publisher, "config", "user.name", "Setup Test")
            git(publisher, "config", "user.email", "setup-test@example.invalid")
            shutil.copy2(SCRIPT, publisher / "setup.py")
            shutil.copytree(REPO / "global", publisher / "global")
            git(publisher, "add", "setup.py", "global")
            git(publisher, "commit", "-m", "base")
            git(publisher, "remote", "add", "origin", str(remote))
            git(publisher, "push", "origin", "HEAD:main")
            git(root, "clone", "--branch", "main", str(remote), str(checkout))

            remote_text = "# Remote revision\n\nThis content came from the newer origin revision.\n"
            (publisher / "global" / "AGENTS.md").write_text(remote_text, encoding="utf-8")
            git(publisher, "add", "global/AGENTS.md")
            git(publisher, "commit", "-m", "newer instructions")
            git(publisher, "push", "origin", "HEAD:main")
            (root / "locations.env").write_text("DOCS=/private/docs\n", encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(checkout / "setup.py"),
                    str(root / "locations.env"),
                    "--home",
                    str(home),
                    "--all",
                ],
                cwd=checkout,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("newer than local", result.stdout)
            self.assertEqual((home / ".codex" / "AGENTS.md").read_text(encoding="utf-8"), remote_text)

    def test_locations_index_is_required_and_validated(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "home"
            missing = subprocess.run(
                [sys.executable, str(SCRIPT)],
                cwd=REPO,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(missing.returncode, 2)

            invalid_index = Path(directory) / "invalid.env"
            invalid_index.write_text("not a mapping\n", encoding="utf-8")
            invalid = subprocess.run(
                [sys.executable, str(SCRIPT), str(invalid_index), "--home", str(home), "--no-fetch"],
                cwd=REPO,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(invalid.returncode, 1)
            self.assertIn("expected KEY=value", invalid.stderr)


if __name__ == "__main__":
    unittest.main()
