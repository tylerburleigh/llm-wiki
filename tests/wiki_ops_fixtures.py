from __future__ import annotations

import hashlib
from pathlib import Path


FIXTURE_DATE = "2026-04-21"
RAW_REL = "raw/test-source.md"
RAW_BODY = "Fixture source body.\n"
RAW_HASH = hashlib.sha256(RAW_BODY.encode("utf-8")).hexdigest()
DRIFT_RECORDED_BODY = "Previous fixture source body.\n"
DRIFT_RECORDED_HASH = hashlib.sha256(
    DRIFT_RECORDED_BODY.encode("utf-8")
).hexdigest()
SOURCE_STEM = "Test Source"
SOURCE_LINK = "[[Test Source]]"
MANIFEST_DIR_REL = "wiki/.ops"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_index(
    vault: Path,
    *,
    entities: tuple[tuple[str, int, str], ...] = (),
    concepts: tuple[tuple[str, int, str], ...] = (),
    sources: tuple[tuple[str, int, str], ...] = (),
    comparisons: tuple[tuple[str, int, str], ...] = (),
) -> None:
    sections = (
        ("Entities", entities),
        ("Concepts", concepts),
        ("Sources", sources),
        ("Comparisons", comparisons),
    )
    lines = ["# Wiki Index", ""]
    for heading, entries in sections:
        lines.append(f"## {heading}")
        for stem, count, tldr in entries:
            lines.append(f"- [[{stem}]] ({count}) - {tldr}")
        lines.append("")
    write(vault / "wiki/index.md", "\n".join(lines).rstrip() + "\n")


def make_raw_source_vault(root: Path) -> Path:
    """Create the smallest vault shape needed by wiki-ops source fixtures."""

    for rel in (
        "raw",
        "wiki/sources",
        "wiki/entities",
        "wiki/concepts",
        "wiki/comparisons",
    ):
        (root / rel).mkdir(parents=True, exist_ok=True)

    write(root / RAW_REL, RAW_BODY)
    write_index(root)
    write(root / "wiki/log.md", "# Wiki Log\n")
    write(root / "wiki/conventions.md", "# Wiki Conventions\n")
    return root


def source_summary_markdown(
    *,
    stem: str = SOURCE_STEM,
    raw_path: str = RAW_REL,
    raw_hash: str = RAW_HASH,
    extra_body: str = "",
) -> str:
    extra = f"\n{extra_body.rstrip()}\n" if extra_body.strip() else ""
    return f"""---
type: source-summary
raw_path: "{raw_path}"
raw_hash: "{raw_hash}"
sources: []
created: "{FIXTURE_DATE}"
updated: "{FIXTURE_DATE}"
status: current
tags: []
---

> [!tldr]
> {stem} fixture.

## Key Takeaways

> [!source]
> Fixture source body.
{extra}"""


def add_source_summary(
    vault: Path,
    *,
    stem: str = SOURCE_STEM,
    raw_hash: str = RAW_HASH,
    update_index: bool = True,
) -> Path:
    path = vault / "wiki/sources" / f"{stem}.md"
    write(path, source_summary_markdown(stem=stem, raw_hash=raw_hash))
    if update_index:
        write_index(vault, sources=((stem, 0, f"{stem} fixture."),))
    return path


def add_matching_source_summary(vault: Path) -> Path:
    return add_source_summary(vault, raw_hash=RAW_HASH)


def add_drifted_source_summary(vault: Path) -> Path:
    return add_source_summary(vault, raw_hash=DRIFT_RECORDED_HASH)


def add_ambiguous_source_summaries(vault: Path) -> tuple[Path, Path]:
    first = add_source_summary(vault, stem=SOURCE_STEM, update_index=False)
    second = add_source_summary(
        vault,
        stem="Test Source Duplicate",
        update_index=False,
    )
    write_index(
        vault,
        sources=(
            (SOURCE_STEM, 0, "Test Source fixture."),
            ("Test Source Duplicate", 0, "Test Source Duplicate fixture."),
        ),
    )
    return first, second


def add_affected_pages(vault: Path) -> dict[str, Path]:
    source_path = vault / "wiki/sources" / f"{SOURCE_STEM}.md"
    write(
        source_path,
        source_summary_markdown(
            extra_body=f"""
## Entities Mentioned

- [[Test Entity]]

## Concepts Covered

- [[Test Concept]]
""",
        ),
    )

    entity_path = vault / "wiki/entities/Test Entity.md"
    write(
        entity_path,
        f"""---
type: entity
entity_type: "tool"
aliases:
  - TE
sources:
  - "{SOURCE_LINK}"
created: "{FIXTURE_DATE}"
updated: "{FIXTURE_DATE}"
status: current
tags: []
---

> [!tldr]
> Test entity cites the fixture source.

## Overview

> [!source]
> Test entity appears in the fixture source. {SOURCE_LINK}
""",
    )

    concept_path = vault / "wiki/concepts/Test Concept.md"
    write(
        concept_path,
        f"""---
type: concept
sources:
  - "{SOURCE_LINK}"
created: "{FIXTURE_DATE}"
updated: "{FIXTURE_DATE}"
status: current
tags: []
---

> [!tldr]
> Test concept cites the fixture source.

## Key Claims

> [!source]
> Test concept is described by the fixture source. {SOURCE_LINK}

> [!analysis]
> Test concept relates to [[Test Entity]] because the source names both.
""",
    )

    comparison_path = vault / "wiki/comparisons/Test Comparison.md"
    write(
        comparison_path,
        f"""---
type: comparison
subjects:
  - "[[Test Entity]]"
  - "[[Test Concept]]"
sources:
  - "{SOURCE_LINK}"
created: "{FIXTURE_DATE}"
updated: "{FIXTURE_DATE}"
status: current
tags: []
---

> [!tldr]
> Test comparison cites the fixture source.

## Comparison

> [!source]
> The fixture supports comparing [[Test Entity]] and [[Test Concept]]. {SOURCE_LINK}
""",
    )

    meta_path = vault / "wiki/dashboard.md"
    write(
        meta_path,
        f"""---
type: meta
sources:
  - "{SOURCE_LINK}"
created: "{FIXTURE_DATE}"
updated: "{FIXTURE_DATE}"
status: current
tags: []
---

> [!tldr]
> Dashboard fixture cites the source for affected-page discovery.

## Recent Activity

> [!source]
> The fixture operation touched {SOURCE_LINK}.
""",
    )

    write_index(
        vault,
        entities=(("Test Entity", 1, "Test entity cites the fixture source."),),
        concepts=(("Test Concept", 1, "Test concept cites the fixture source."),),
        sources=((SOURCE_STEM, 0, "Test Source fixture."),),
        comparisons=(("Test Comparison", 1, "Test comparison cites the fixture source."),),
    )

    return {
        "source": source_path,
        "entity": entity_path,
        "concept": concept_path,
        "comparison": comparison_path,
        "meta": meta_path,
    }


def make_matching_source_vault(root: Path) -> Path:
    vault = make_raw_source_vault(root)
    add_matching_source_summary(vault)
    return vault


def make_drifted_source_vault(root: Path) -> Path:
    vault = make_raw_source_vault(root)
    add_drifted_source_summary(vault)
    return vault


def make_ambiguous_source_vault(root: Path) -> Path:
    vault = make_raw_source_vault(root)
    add_ambiguous_source_summaries(vault)
    return vault


def make_affected_pages_vault(root: Path) -> Path:
    vault = make_matching_source_vault(root)
    add_affected_pages(vault)
    return vault
