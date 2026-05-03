from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import ModuleType

from tests import wiki_ops_fixtures as fixtures


REPO_ROOT = Path(__file__).resolve().parents[1]
WIKI_OPS = REPO_ROOT / "wiki-base/scripts/wiki-ops.py"
LINT = REPO_ROOT / "wiki-base/scripts/wiki-lint.py"


def run_ops(
    args: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
    python_args: list[str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *(python_args or []), str(WIKI_OPS), *args],
        cwd=cwd or REPO_ROOT,
        check=False,
        text=True,
        capture_output=True,
        env=env,
        input=input_text,
    )


def parse_json_output(result: subprocess.CompletedProcess[str]) -> dict:
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"stdout was not JSON:\n{result.stdout}\nstderr:\n{result.stderr}"
        ) from exc


def load_wiki_ops() -> ModuleType:
    spec = importlib.util.spec_from_file_location("wiki_ops", WIKI_OPS)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load wiki-ops module spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_lint(vault: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(LINT), "--vault", str(vault)],
        check=False,
        text=True,
        capture_output=True,
    )


class WikiOpsCoreTests(unittest.TestCase):
    def test_missing_subcommand_returns_json_usage_error(self) -> None:
        result = run_ops([])
        payload = parse_json_output(result)

        self.assertEqual(result.returncode, 2)
        self.assertFalse(payload["ok"])
        self.assertIsNone(payload["command"])
        self.assertEqual(payload["error"]["code"], "usage")

    def test_missing_vault_returns_json_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            missing = Path(tmpdir) / "missing"
            result = run_ops(
                ["--vault", str(missing), "source-status", fixtures.RAW_REL]
            )
            payload = parse_json_output(result)

            self.assertEqual(result.returncode, 2)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["command"], "source-status")
            self.assertEqual(payload["error"]["code"], "vault_not_found")

    def test_invalid_vault_returns_json_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_ops(
                ["--vault", tmpdir, "source-status", fixtures.RAW_REL]
            )
            payload = parse_json_output(result)

            self.assertEqual(result.returncode, 2)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error"]["code"], "invalid_vault")
            self.assertEqual(payload["error"]["details"]["missing"], ["wiki", "raw"])

    def test_source_status_uses_default_current_directory_vault(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = fixtures.make_raw_source_vault(Path(tmpdir))
            result = run_ops(["source-status", fixtures.RAW_REL], cwd=vault)
            payload = parse_json_output(result)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "source-status")
            self.assertEqual(payload["status"], "new")
            self.assertEqual(payload["raw_path"], fixtures.RAW_REL)
            self.assertEqual(payload["raw_hash"], fixtures.RAW_HASH)
            self.assertEqual(payload["source_summary_paths"], [])

    def test_manifest_new_creates_local_json_with_status_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = fixtures.make_matching_source_vault(Path(tmpdir))
            result = run_ops(
                ["--vault", str(vault), "manifest", "new", fixtures.RAW_REL]
            )
            payload = parse_json_output(result)
            manifest_path = vault / payload["manifest_path"]
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "manifest new")
            self.assertTrue(payload["manifest_path"].startswith("wiki/.ops/"))
            self.assertTrue(payload["manifest_path"].endswith(".json"))
            self.assertEqual(payload["raw_path"], fixtures.RAW_REL)
            self.assertEqual(payload["raw_hash"], fixtures.RAW_HASH)
            self.assertEqual(payload["hash_status"], "match")
            self.assertEqual(payload["created"], payload["updated"])

            self.assertEqual(manifest["manifest_version"], 1)
            self.assertEqual(manifest["manifest_path"], payload["manifest_path"])
            self.assertEqual(manifest["raw_path"], fixtures.RAW_REL)
            self.assertEqual(manifest["raw_hash"], fixtures.RAW_HASH)
            self.assertEqual(manifest["hash_status"], "match")
            self.assertEqual(
                manifest["source_summary_paths"],
                ["wiki/sources/Test Source.md"],
            )
            self.assertEqual(manifest["source_md_path"], fixtures.RAW_REL)
            self.assertIsNone(manifest["precheck_summary"])
            self.assertEqual(manifest["planned_pages"], [])
            self.assertEqual(manifest["touched_pages"], [])
            self.assertEqual(
                manifest["auditor_report"],
                {"path": None, "inline": None},
            )
            self.assertEqual(manifest["deferred_items"], [])
            self.assertEqual(
                manifest["timestamps"],
                {"created": manifest["created"], "updated": manifest["updated"]},
            )
            self.assertEqual(list((vault / fixtures.MANIFEST_DIR_REL).glob("*.md")), [])

            lint = run_lint(vault)
            self.assertEqual(lint.returncode, 0, lint.stdout + lint.stderr)

    def test_manifest_new_records_drift_status_without_editing_source_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = fixtures.make_drifted_source_vault(Path(tmpdir))
            summary = vault / "wiki/sources/Test Source.md"
            before = summary.read_text(encoding="utf-8")

            result = run_ops(
                ["--vault", str(vault), "manifest", "new", fixtures.RAW_REL]
            )
            payload = parse_json_output(result)
            manifest = json.loads((vault / payload["manifest_path"]).read_text())

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(payload["hash_status"], "drift")
            self.assertEqual(manifest["hash_status"], "drift")
            self.assertEqual(summary.read_text(encoding="utf-8"), before)

    def test_manifest_show_returns_manifest_without_mutating_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = fixtures.make_matching_source_vault(Path(tmpdir))
            created = run_ops(
                ["--vault", str(vault), "manifest", "new", fixtures.RAW_REL]
            )
            created_payload = parse_json_output(created)
            manifest_path = vault / created_payload["manifest_path"]
            before = manifest_path.read_text(encoding="utf-8")

            shown = run_ops(
                [
                    "--vault",
                    str(vault),
                    "manifest",
                    "show",
                    created_payload["manifest_path"],
                ]
            )
            payload = parse_json_output(shown)
            after = manifest_path.read_text(encoding="utf-8")

            self.assertEqual(shown.returncode, 0, shown.stderr)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "manifest show")
            self.assertEqual(payload["manifest_path"], created_payload["manifest_path"])
            self.assertEqual(payload["raw_path"], fixtures.RAW_REL)
            self.assertEqual(payload["raw_hash"], fixtures.RAW_HASH)
            self.assertEqual(before, after)

    def test_manifest_show_rejects_paths_outside_ops_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = fixtures.make_raw_source_vault(Path(tmpdir))
            outside_ops = vault / "raw/not-a-manifest.json"
            outside_ops.write_text("{}\n", encoding="utf-8")

            result = run_ops(
                [
                    "--vault",
                    str(vault),
                    "manifest",
                    "show",
                    "raw/not-a-manifest.json",
                ]
            )
            payload = parse_json_output(result)

            self.assertEqual(result.returncode, 2)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["command"], "manifest")
            self.assertEqual(payload["error"]["code"], "invalid_manifest_path")

    def test_frontmatter_parser_handles_block_lists(self) -> None:
        module = load_wiki_ops()
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
        frontmatter, body, err = module.split_frontmatter(sample)

        self.assertIsNone(err)
        self.assertIn("> [!tldr]", body)
        self.assertEqual(frontmatter["type"], "entity")
        self.assertEqual(frontmatter["aliases"], ["ETS", "Educational Testing Service"])
        self.assertEqual(frontmatter["sources"], ["[[Source Summary]]"])

    def test_wikilink_parser_ignores_code_and_normalizes_targets(self) -> None:
        module = load_wiki_ops()
        text = (
            "See [[Real Link|alias]] and [[Sectioned#Part]].\n"
            "Ignore `[[Inline Example]]`.\n\n"
            "```\n"
            "[[Fenced Example]]\n"
            "```\n"
        )
        targets = module.extract_wikilink_targets(text)

        self.assertEqual(targets, ["Real Link", "Sectioned"])

    def test_path_helpers_return_vault_relative_posix_paths(self) -> None:
        module = load_wiki_ops()
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = fixtures.make_raw_source_vault(Path(tmpdir))
            raw_path = module.resolve_vault_path(vault, fixtures.RAW_REL, must_exist=True)

            self.assertEqual(
                module.vault_relative_path(vault, raw_path),
                fixtures.RAW_REL,
            )
            self.assertTrue(module.is_under_relpath(vault, raw_path, "raw"))

    def test_path_helpers_reject_paths_outside_vault(self) -> None:
        module = load_wiki_ops()
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = fixtures.make_raw_source_vault(Path(tmpdir) / "vault")
            outside = Path(tmpdir) / "outside.md"
            outside.write_text("outside\n", encoding="utf-8")

            with self.assertRaises(module.WikiOpsError) as raised:
                module.resolve_vault_path(vault, outside)
            self.assertEqual(raised.exception.code, "path_outside_vault")

    def test_source_status_classifies_new_match_drift_and_ambiguous(self) -> None:
        scenarios = (
            (fixtures.make_raw_source_vault, "new", []),
            (
                fixtures.make_matching_source_vault,
                "match",
                ["wiki/sources/Test Source.md"],
            ),
            (
                fixtures.make_drifted_source_vault,
                "drift",
                ["wiki/sources/Test Source.md"],
            ),
            (
                fixtures.make_ambiguous_source_vault,
                "ambiguous",
                [
                    "wiki/sources/Test Source.md",
                    "wiki/sources/Test Source Duplicate.md",
                ],
            ),
        )

        for make_vault, expected_status, expected_summaries in scenarios:
            with self.subTest(status=expected_status):
                with tempfile.TemporaryDirectory() as tmpdir:
                    vault = make_vault(Path(tmpdir))
                    result = run_ops(
                        ["--vault", str(vault), "source-status", fixtures.RAW_REL]
                    )
                    payload = parse_json_output(result)

                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertTrue(payload["ok"])
                    self.assertEqual(payload["status"], expected_status)
                    self.assertEqual(payload["raw_path"], fixtures.RAW_REL)
                    self.assertEqual(payload["raw_hash"], fixtures.RAW_HASH)
                    self.assertEqual(
                        payload["source_summary_paths"],
                        expected_summaries,
                    )

    def test_affected_pages_resolves_source_summary_path_stem_and_wikilink(self) -> None:
        refs = (
            "wiki/sources/Test Source.md",
            fixtures.SOURCE_STEM,
            fixtures.SOURCE_LINK,
        )

        for source_ref in refs:
            with self.subTest(source_ref=source_ref):
                with tempfile.TemporaryDirectory() as tmpdir:
                    vault = fixtures.make_affected_pages_vault(Path(tmpdir))
                    result = run_ops(
                        ["--vault", str(vault), "affected-pages", source_ref]
                    )
                    payload = parse_json_output(result)

                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertTrue(payload["ok"])
                    self.assertEqual(payload["command"], "affected-pages")
                    self.assertEqual(
                        payload["source_summary_path"],
                        "wiki/sources/Test Source.md",
                    )
                    self.assertEqual(
                        payload["knowledge_pages"],
                        [
                            "wiki/comparisons/Test Comparison.md",
                            "wiki/concepts/Test Concept.md",
                            "wiki/entities/Test Entity.md",
                        ],
                    )
                    self.assertEqual(payload["meta_pages"], ["wiki/dashboard.md"])
                    self.assertEqual(payload["unresolved_references"], [])

    def test_affected_pages_discovers_frontmatter_only_and_body_only_citations(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = fixtures.make_matching_source_vault(Path(tmpdir))
            fixtures.write(
                vault / "wiki/concepts/Frontmatter Only.md",
                f"""---
type: concept
sources:
  - "{fixtures.SOURCE_LINK}"
created: "{fixtures.FIXTURE_DATE}"
updated: "{fixtures.FIXTURE_DATE}"
status: current
tags: []
---

> [!tldr]
> Frontmatter-only citation.
""",
            )
            fixtures.write(
                vault / "wiki/entities/Body Only.md",
                f"""---
type: entity
entity_type: "fixture"
sources: []
created: "{fixtures.FIXTURE_DATE}"
updated: "{fixtures.FIXTURE_DATE}"
status: current
tags: []
---

> [!tldr]
> Body-only citation.

> [!source]
> Cites the source in body only. {fixtures.SOURCE_LINK}
""",
            )

            result = run_ops(
                ["--vault", str(vault), "affected-pages", fixtures.SOURCE_STEM]
            )
            payload = parse_json_output(result)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                payload["knowledge_pages"],
                [
                    "wiki/concepts/Frontmatter Only.md",
                    "wiki/entities/Body Only.md",
                ],
            )

    def test_stage_source_keeps_markdown_already_under_raw(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = fixtures.make_raw_source_vault(Path(tmpdir))
            result = run_ops(
                ["--vault", str(vault), "stage-source", fixtures.RAW_REL]
            )
            payload = parse_json_output(result)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["command"], "stage-source")
            self.assertEqual(payload["raw_path"], fixtures.RAW_REL)
            self.assertEqual(payload["source_md_path"], fixtures.RAW_REL)
            self.assertEqual(payload["source_kind"], "markdown")
            self.assertFalse(payload["converted"])
            self.assertEqual(payload["warnings"], [])

    def test_stage_source_copies_markdown_outside_raw_without_changing_original(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            vault = fixtures.make_raw_source_vault(root / "vault")
            outside = root / "outside-source.md"
            outside.write_text("outside source\n", encoding="utf-8")

            result = run_ops(
                ["--vault", str(vault), "stage-source", str(outside)]
            )
            payload = parse_json_output(result)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(payload["raw_path"], "raw/outside-source.md")
            self.assertEqual(payload["source_md_path"], "raw/outside-source.md")
            self.assertEqual(payload["source_kind"], "markdown")
            self.assertFalse(payload["converted"])
            self.assertEqual(outside.read_text(encoding="utf-8"), "outside source\n")
            self.assertEqual(
                (vault / "raw/outside-source.md").read_text(encoding="utf-8"),
                "outside source\n",
            )

    def test_stage_source_reports_missing_pdf_conversion_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            vault = fixtures.make_raw_source_vault(root / "vault")
            pdf = root / "sample.pdf"
            pdf.write_bytes(b"%PDF-1.7\n")

            result = run_ops(
                ["--vault", str(vault), "stage-source", str(pdf)],
                python_args=["-S"],
            )
            payload = parse_json_output(result)

            self.assertEqual(result.returncode, 2)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["command"], "stage-source")
            self.assertEqual(
                payload["error"]["code"],
                "pdf_conversion_unavailable",
            )
            self.assertIn("pymupdf4llm", payload["error"]["message"])

    def test_stage_source_converts_pdf_with_pymupdf4llm_when_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            vault = fixtures.make_raw_source_vault(root / "vault")
            pdf = root / "sample.pdf"
            pdf.write_bytes(b"%PDF-1.7\n")
            (vault / "raw/sample.md").write_text("old conversion\n", encoding="utf-8")

            fake_module_dir = root / "fake"
            fake_module_dir.mkdir()
            (fake_module_dir / "pymupdf4llm.py").write_text(
                "def to_markdown(path):\n"
                "    return '# Converted PDF\\n\\nsource=' + path + '\\n'\n",
                encoding="utf-8",
            )
            env = {
                **os.environ,
                "PYTHONPATH": str(fake_module_dir),
            }

            result = run_ops(
                ["--vault", str(vault), "stage-source", str(pdf)],
                env=env,
            )
            payload = parse_json_output(result)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(payload["raw_path"], "raw/sample.pdf")
            self.assertEqual(payload["source_md_path"], "raw/sample.md")
            self.assertEqual(payload["source_kind"], "pdf")
            self.assertTrue(payload["converted"])
            self.assertEqual(
                (vault / "raw/sample.pdf").read_bytes(),
                b"%PDF-1.7\n",
            )
            self.assertIn(
                "# Converted PDF",
                (vault / "raw/sample.md").read_text(encoding="utf-8"),
            )
            self.assertTrue(payload["warnings"])

    def test_append_audit_reads_report_file_and_appends_first_callout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            vault = fixtures.make_matching_source_vault(root / "vault")
            summary = vault / "wiki/sources/Test Source.md"
            report = root / "audit.md"
            report.write_text(
                "- Covered the source summary.\n"
                "- Gap: no comparison page was created.\n",
                encoding="utf-8",
            )

            result = run_ops(
                [
                    "--vault",
                    str(vault),
                    "append-audit",
                    fixtures.SOURCE_STEM,
                    str(report),
                ]
            )
            payload = parse_json_output(result)
            text = summary.read_text(encoding="utf-8")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(payload["replaced_existing"])
            self.assertEqual(payload["updated"], date.today().isoformat())
            self.assertIn(f'updated: "{date.today().isoformat()}"', text)
            self.assertIn("> [!gap] Extraction coverage of this ingest", text)
            self.assertIn("> - Covered the source summary.", text)
            self.assertIn("> [!source]\n> Fixture source body.", text)

    def test_append_audit_reads_stdin(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = fixtures.make_matching_source_vault(Path(tmpdir))
            summary = vault / "wiki/sources/Test Source.md"

            result = run_ops(
                [
                    "--vault",
                    str(vault),
                    "append-audit",
                    fixtures.SOURCE_LINK,
                    "-",
                ],
                input_text="Stdin audit report.\n",
            )
            payload = parse_json_output(result)
            text = summary.read_text(encoding="utf-8")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(payload["replaced_existing"])
            self.assertIn("> Stdin audit report.", text)

    def test_append_audit_replaces_existing_callout_and_preserves_other_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            vault = fixtures.make_matching_source_vault(root / "vault")
            summary = vault / "wiki/sources/Test Source.md"
            summary.write_text(
                fixtures.source_summary_markdown(
                    extra_body="""
## Notes

> [!analysis] Keep this note
> This note should stay untouched.

> [!gap] Extraction coverage of this ingest
> Old audit finding.

## Entities Mentioned

- [[Test Entity]]
"""
                ),
                encoding="utf-8",
            )
            report = root / "audit.md"
            report.write_text("New audit finding.\n", encoding="utf-8")

            result = run_ops(
                [
                    "--vault",
                    str(vault),
                    "append-audit",
                    "wiki/sources/Test Source.md",
                    str(report),
                ]
            )
            payload = parse_json_output(result)
            text = summary.read_text(encoding="utf-8")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(payload["replaced_existing"])
            self.assertIn("> New audit finding.", text)
            self.assertNotIn("Old audit finding.", text)
            self.assertIn("> [!analysis] Keep this note", text)
            self.assertIn("## Entities Mentioned\n\n- [[Test Entity]]", text)
            self.assertEqual(
                text.count("> [!gap] Extraction coverage of this ingest"),
                1,
            )


if __name__ == "__main__":
    unittest.main()
