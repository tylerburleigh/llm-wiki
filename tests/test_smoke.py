from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd or REPO_ROOT,
        check=False,
        text=True,
        capture_output=True,
    )


class SmokeTests(unittest.TestCase):
    def test_new_wiki_scaffold_includes_doctor_and_clean_git(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "example"
            created = run(
                ["bash", "scripts/new-wiki.sh", str(target), "--git"],
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            self.assertTrue((target / "scripts/wiki-lint.py").is_file())
            self.assertTrue((target / "scripts/wiki-doctor.sh").is_file())

            synthesis = (target / "wiki/synthesis.md").read_text(encoding="utf-8")
            self.assertNotIn("{{date}}", synthesis)
            self.assertIn('created: "', synthesis)

            status = run(["git", "-C", str(target), "status", "--short"])
            self.assertEqual(status.returncode, 0, status.stderr)
            self.assertEqual(status.stdout.strip(), "")

    def test_root_doctor_wrapper_passes_on_fresh_wiki(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "example"
            created = run(["bash", "scripts/new-wiki.sh", str(target)])
            self.assertEqual(created.returncode, 0, created.stderr)

            doctor = run(["bash", "scripts/wiki-doctor.sh", str(target)])
            self.assertEqual(doctor.returncode, 0, doctor.stdout + doctor.stderr)
            self.assertIn("Wiki doctor: OK", doctor.stdout)
            self.assertNotIn("FAIL lint:", doctor.stdout)

    def test_lint_fallback_parser_handles_block_lists(self) -> None:
        lint_path = REPO_ROOT / "wiki-base/scripts/wiki-lint.py"
        spec = importlib.util.spec_from_file_location("wiki_lint", lint_path)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        module.yaml = None

        sample = """---
type: entity
entity_type: "organization"
aliases:
  - ETS
  - "Educational Testing Service"
sources:
  - "[[Source Summary]]"
created: "2026-04-21"
updated: "2026-04-21"
status: current
tags: []
---

> [!tldr]
> Example.
"""
        frontmatter, _, err = module.split_frontmatter(sample)
        self.assertIsNone(err)
        self.assertEqual(frontmatter["type"], "entity")
        self.assertEqual(frontmatter["aliases"], ["ETS", "Educational Testing Service"])
        self.assertEqual(frontmatter["sources"], ["[[Source Summary]]"])


if __name__ == "__main__":
    unittest.main()
