from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests import wiki_ops_fixtures as fixtures


REPO_ROOT = Path(__file__).resolve().parents[1]
LINT = REPO_ROOT / "wiki-base/scripts/wiki-lint.py"


def run_lint(vault: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(LINT), "--vault", str(vault)],
        check=False,
        text=True,
        capture_output=True,
    )


class WikiOpsFixtureTests(unittest.TestCase):
    def test_raw_source_vault_has_one_raw_source_and_no_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = fixtures.make_raw_source_vault(Path(tmpdir))

            self.assertEqual(
                (vault / fixtures.RAW_REL).read_text(encoding="utf-8"),
                fixtures.RAW_BODY,
            )
            self.assertEqual(list((vault / "wiki/sources").glob("*.md")), [])

    def test_matching_source_summary_records_current_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = fixtures.make_matching_source_vault(Path(tmpdir))
            summary = vault / "wiki/sources/Test Source.md"

            text = summary.read_text(encoding="utf-8")
            self.assertIn(f'raw_path: "{fixtures.RAW_REL}"', text)
            self.assertIn(f'raw_hash: "{fixtures.RAW_HASH}"', text)

    def test_drifted_source_summary_records_old_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = fixtures.make_drifted_source_vault(Path(tmpdir))
            summary = vault / "wiki/sources/Test Source.md"

            text = summary.read_text(encoding="utf-8")
            self.assertIn(f'raw_path: "{fixtures.RAW_REL}"', text)
            self.assertIn(f'raw_hash: "{fixtures.DRIFT_RECORDED_HASH}"', text)
            self.assertNotIn(f'raw_hash: "{fixtures.RAW_HASH}"', text)

    def test_ambiguous_source_summaries_claim_same_raw_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = fixtures.make_ambiguous_source_vault(Path(tmpdir))
            summaries = sorted((vault / "wiki/sources").glob("*.md"))

            self.assertCountEqual(
                [p.stem for p in summaries],
                ["Test Source", "Test Source Duplicate"],
            )
            for summary in summaries:
                self.assertIn(
                    f'raw_path: "{fixtures.RAW_REL}"',
                    summary.read_text(encoding="utf-8"),
                )

    def test_affected_pages_fixture_has_knowledge_and_meta_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = fixtures.make_affected_pages_vault(Path(tmpdir))

            expected = {
                "wiki/entities/Test Entity.md",
                "wiki/concepts/Test Concept.md",
                "wiki/comparisons/Test Comparison.md",
                "wiki/dashboard.md",
            }
            actual = {
                str(path.relative_to(vault))
                for path in vault.rglob("*.md")
                if "[[Test Source]]" in path.read_text(encoding="utf-8")
            }
            self.assertTrue(expected.issubset(actual))

            lint = run_lint(vault)
            self.assertEqual(lint.returncode, 0, lint.stdout + lint.stderr)


if __name__ == "__main__":
    unittest.main()
