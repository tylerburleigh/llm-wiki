#!/usr/bin/env python3
"""wiki-lint.py — machine-checkable validation for an LLM wiki vault.

Enforces the invariants documented in CLAUDE.md that don't require
human judgment. Exits 0 when clean, 1 when findings were reported.

Checks implemented:
  - Frontmatter shape per type (core + per-type fields, ISO 8601 dates,
    valid status, list shapes)
  - TLDR placement (first content block after frontmatter is `> [!tldr]`)
  - Filename rules (no disallowed characters; starts with uppercase)
  - Wikilink resolution (every wikilink target in a page body resolves
    to an existing wiki page)
  - Index consistency (every non-special page has an index entry, every
    entry resolves, source counts match len(frontmatter.sources), TLDRs
    in the index match the page's first [!tldr] line)
  - Sources invariant (body cites source-summary page → frontmatter
    sources: contains it)
  - Hash drift (each source-summary raw_hash matches sha256 of the file
    at raw_path; missing files reported separately)
  - Bare-claim candidates (heuristic prose outside typed callouts;
    synthesis.md exempt)

Usage:
    python3 scripts/wiki-lint.py [--vault <dir>] [--category <name>]

Defaults to the current directory as the vault root.

No external dependencies are required for the scaffolded schema. If
PyYAML is installed, the linter uses it; otherwise it falls back to a
small parser that handles the frontmatter shapes this wiki generates.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Callable

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - exercised in smoke tests
    yaml = None


VALID_TYPES = {"entity", "concept", "source-summary", "comparison", "synthesis", "meta"}
VALID_STATUSES = {"current", "stale"}
CORE_FIELDS = {"type", "sources", "created", "updated", "status", "tags"}
PER_TYPE_FIELDS: dict[str, set[str]] = {
    "entity": {"entity_type"},
    "concept": set(),
    "source-summary": {"raw_path", "raw_hash"},
    "comparison": {"subjects"},
    "synthesis": set(),
    "meta": set(),
}

# Files inside wiki/ that don't follow the page schema (legacy plain-markdown
# infrastructure pages). The newer pattern is to give infrastructure pages
# `type: meta` frontmatter so they validate cleanly while staying out of the
# graph as knowledge nodes.
SPECIAL_FILES = {"index.md", "log.md", "conventions.md"}
# Page stems that legitimately use lowercase filenames (exempt from the
# Title Case filename rule). These still get frontmatter and TLDR checks.
LOWERCASE_STEM_EXEMPTIONS = {"synthesis"}

ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# Capture the link target, ignoring |alias and #section suffixes.
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+?)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
# Title-case-ish filename: starts uppercase; only letters, digits, spaces,
# hyphens, and parenthetical disambiguation.
FILENAME_RE = re.compile(r"^[A-Z][A-Za-z0-9 \-()]*$")
# Index entry: `- [[Page Name]] (N) — TLDR` (em dash or hyphen accepted)
INDEX_ENTRY_RE = re.compile(
    r"^\s*-\s*\[\[([^\]|#]+?)\]\]\s*\((\d+)\)\s*[—\-]\s*(.+?)\s*$"
)
LIST_LINE_RE = re.compile(r"^\s*(?:[-*+] |\d+\. )")
WIKILINK_ONLY_RE = re.compile(r"^\s*!?\[\[[^\]]+\]\]\s*$")
AUDIT_CALLOUT_RE = re.compile(
    r"^\s*>\s*\[!gap\]\s+Extraction coverage of this ingest",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass
class Finding:
    category: str
    path: Path | None
    message: str

    def render(self, vault: Path) -> str:
        loc = str(self.path.relative_to(vault)) if self.path else "-"
        return f"[{self.category}] {loc}: {self.message}"


@dataclass
class Page:
    path: Path
    frontmatter: dict | None
    body: str
    tldr: str | None  # first [!tldr] line, stripped

    @property
    def stem(self) -> str:
        return self.path.stem


@dataclass
class Vault:
    root: Path
    pages: dict[str, Page] = field(default_factory=dict)  # stem -> Page
    findings: list[Finding] = field(default_factory=list)

    def add(self, category: str, path: Path | None, message: str) -> None:
        self.findings.append(Finding(category, path, message))


@dataclass
class HealthSummary:
    total_pages: int
    by_type: dict[str, int]
    thinly_sourced_pages: int
    pages_with_open_gaps: int
    pages_with_source_no_analysis: int
    stale_hubs: int
    source_summaries_missing_audit: int


# ---------- frontmatter + body parsing ----------


def parse_yaml_scalar(text: str) -> object:
    value = text.strip()
    if value == "[]":
        return []
    if value.startswith("[") and value.endswith("]") and not value.startswith("[["):
        return parse_yaml_flow_list(value)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value[1:-1]
    return value


def split_flow_items(text: str) -> list[str]:
    items: list[str] = []
    buf: list[str] = []
    in_single = False
    in_double = False
    escape = False

    for ch in text:
        if escape:
            buf.append(ch)
            escape = False
            continue
        if ch == "\\" and in_double:
            buf.append(ch)
            escape = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            buf.append(ch)
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            buf.append(ch)
            continue
        if ch == "," and not in_single and not in_double:
            items.append("".join(buf).strip())
            buf = []
            continue
        buf.append(ch)

    tail = "".join(buf).strip()
    if tail:
        items.append(tail)
    return items


def parse_yaml_flow_list(text: str) -> list[object]:
    inner = text[1:-1].strip()
    if not inner:
        return []
    return [parse_yaml_scalar(item) for item in split_flow_items(inner)]


def parse_minimal_yaml_mapping(text: str) -> tuple[dict | None, str | None]:
    """Parse the limited YAML subset used by scaffolded wiki pages."""

    result: dict[str, object] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i].rstrip()
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if raw[:1].isspace():
            return None, f"unexpected indentation on line {i + 1}"
        if ":" not in raw:
            return None, f"invalid frontmatter line {i + 1}: `{stripped}`"

        key, rest = raw.split(":", 1)
        key = key.strip()
        value_text = rest.strip()
        if not key:
            return None, f"missing key on line {i + 1}"

        if value_text:
            result[key] = parse_yaml_scalar(value_text)
            i += 1
            continue

        items: list[object] = []
        i += 1
        while i < len(lines):
            item_raw = lines[i].rstrip()
            item_stripped = item_raw.strip()
            if not item_stripped or item_stripped.startswith("#"):
                i += 1
                continue
            if not item_raw[:1].isspace():
                break
            if not item_stripped.startswith("- "):
                return None, (
                    f"expected list item under `{key}` on line {i + 1}"
                )
            items.append(parse_yaml_scalar(item_stripped[2:].strip()))
            i += 1
        result[key] = items

    return result, None


def split_frontmatter(text: str) -> tuple[dict | None, str, str | None]:
    """Return (frontmatter dict or None, body text, error message or None).

    Frontmatter is a YAML block delimited by `---` on its own line at the
    very start of the file and a closing `---` on its own line.
    """
    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return None, text, "no frontmatter block at file start"
    # Find the closing delimiter
    lines = text.splitlines(keepends=True)
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return None, text, "frontmatter opened with `---` but never closed"
    fm_text = "".join(lines[1:end_idx])
    body = "".join(lines[end_idx + 1 :])
    if yaml is not None:
        try:
            fm = yaml.safe_load(fm_text) or {}
        except yaml.YAMLError as exc:
            return None, body, f"YAML parse error: {exc}"
    else:
        fm, err = parse_minimal_yaml_mapping(fm_text)
        if err:
            return None, body, err
        fm = fm or {}
    if not isinstance(fm, dict):
        return None, body, "frontmatter is not a mapping"
    return fm, body, None


def first_tldr_line(body: str) -> tuple[str | None, bool]:
    """Return (tldr content, is_first_content_block).

    Skips leading blank lines. If the first non-blank block starts with
    `> [!tldr]`, returns its content (everything after the marker on the
    first line or the next `>`-prefixed line) and True. Otherwise returns
    (maybe_content, False).
    """
    lines = body.splitlines()
    i = 0
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i >= len(lines):
        return None, False
    first = lines[i]
    if not first.lstrip().startswith("> [!tldr]"):
        return None, False
    # Extract content: either inline after `> [!tldr]` or on the next `>` line.
    after_marker = first.split("[!tldr]", 1)[1].strip()
    if after_marker:
        return after_marker, True
    if i + 1 < len(lines):
        nxt = lines[i + 1].lstrip()
        if nxt.startswith(">"):
            return nxt.lstrip("> ").strip(), True
    return "", True


# ---------- checks ----------


def collect_pages(vault: Vault) -> None:
    wiki_dir = vault.root / "wiki"
    if not wiki_dir.is_dir():
        vault.add("structure", vault.root, "no wiki/ directory at vault root")
        return

    for md_path in sorted(wiki_dir.rglob("*.md")):
        rel_name = md_path.name
        if rel_name in SPECIAL_FILES:
            continue
        try:
            raw = md_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            vault.add("encoding", md_path, "file is not valid UTF-8")
            continue
        fm, body, err = split_frontmatter(raw)
        if err:
            vault.add("frontmatter", md_path, err)
        tldr, is_first = first_tldr_line(body)
        if not is_first:
            vault.add(
                "tldr",
                md_path,
                "first content block after frontmatter is not `> [!tldr]`",
            )
        page = Page(path=md_path, frontmatter=fm, body=body, tldr=tldr)
        if page.stem in vault.pages:
            vault.add(
                "duplicate",
                md_path,
                f"duplicate filename stem (also: {vault.pages[page.stem].path})",
            )
        else:
            vault.pages[page.stem] = page


def check_filenames(vault: Vault) -> None:
    for page in vault.pages.values():
        if page.stem in LOWERCASE_STEM_EXEMPTIONS:
            continue
        # Meta pages (infrastructure: handoff, backlog, decisions, graph-protocol,
        # etc.) use lowercase-hyphen filenames so they read as infrastructure,
        # not knowledge.
        if page.frontmatter and page.frontmatter.get("type") == "meta":
            continue
        if not FILENAME_RE.match(page.stem):
            vault.add(
                "filename",
                page.path,
                f"filename `{page.stem}` violates Title Case / allowed-characters rule",
            )


def check_frontmatter(vault: Vault) -> None:
    for page in vault.pages.values():
        fm = page.frontmatter
        if fm is None:
            continue  # already reported in collect_pages
        missing = CORE_FIELDS - set(fm.keys())
        if missing:
            vault.add(
                "frontmatter",
                page.path,
                f"missing core fields: {sorted(missing)}",
            )
        typ = fm.get("type")
        if typ not in VALID_TYPES:
            vault.add(
                "frontmatter",
                page.path,
                f"type=`{typ}` is not one of {sorted(VALID_TYPES)}",
            )
            continue
        expected_extra = PER_TYPE_FIELDS.get(typ, set())
        missing_extra = expected_extra - set(fm.keys())
        if missing_extra:
            vault.add(
                "frontmatter",
                page.path,
                f"type=`{typ}` missing fields: {sorted(missing_extra)}",
            )
        # Shape checks
        for key in ("sources", "tags"):
            if key in fm and not isinstance(fm[key], list):
                vault.add(
                    "frontmatter",
                    page.path,
                    f"`{key}` must be a list (got {type(fm[key]).__name__})",
                )
        if typ == "comparison" and "subjects" in fm:
            if not isinstance(fm["subjects"], list):
                vault.add(
                    "frontmatter",
                    page.path,
                    "`subjects` must be a list",
                )
        if "status" in fm and fm["status"] not in VALID_STATUSES:
            vault.add(
                "frontmatter",
                page.path,
                f"status=`{fm['status']}` not in {sorted(VALID_STATUSES)}",
            )
        for date_field in ("created", "updated"):
            val = fm.get(date_field)
            if val is None:
                continue
            as_str = str(val) if not isinstance(val, str) else val
            if not ISO_DATE_RE.match(as_str):
                vault.add(
                    "frontmatter",
                    page.path,
                    f"`{date_field}` must be ISO 8601 YYYY-MM-DD (got `{as_str}`)",
                )
        if typ == "entity":
            et = fm.get("entity_type")
            if et is None or not isinstance(et, str):
                vault.add(
                    "frontmatter",
                    page.path,
                    "`entity_type` must be a string",
                )
            if "aliases" in fm:
                al = fm["aliases"]
                if not isinstance(al, list) or not all(
                    isinstance(x, str) and x for x in al
                ):
                    vault.add(
                        "frontmatter",
                        page.path,
                        "`aliases` must be a list of non-empty strings",
                    )
        if typ == "source-summary":
            for key in ("raw_path", "raw_hash"):
                val = fm.get(key)
                if val is None or not isinstance(val, str) or not val:
                    vault.add(
                        "frontmatter",
                        page.path,
                        f"`{key}` must be a non-empty string",
                    )


_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def strip_code(text: str) -> str:
    """Replace fenced code blocks and inline code spans with blank space.

    Obsidian renders wikilinks inside ``` fences and inside `inline code`
    as plain text, not as links. The graph doesn't see them. Strip both
    here so lint matches the rendered behavior — example wikilinks in
    code samples shouldn't be required to resolve.
    """
    # Strip fenced blocks line by line so line-number-based reporting
    # elsewhere stays approximately accurate.
    out: list[str] = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            out.append("\n" if line.endswith("\n") else "")
            continue
        if in_fence:
            out.append("\n" if line.endswith("\n") else "")
            continue
        out.append(line)
    fenced_stripped = "".join(out)
    return _INLINE_CODE_RE.sub("", fenced_stripped)


def extract_wikilink_targets(text: str) -> list[str]:
    return [
        m.group(1).strip()
        for m in WIKILINK_RE.finditer(strip_code(text))
    ]


def check_wikilink_resolution(vault: Vault) -> None:
    known = set(vault.pages.keys())
    for page in vault.pages.values():
        targets = extract_wikilink_targets(page.body)
        for target in targets:
            if target not in known:
                vault.add(
                    "unresolved-link",
                    page.path,
                    f"wikilink `[[{target}]]` does not resolve to an existing page",
                )


def parse_index(index_path: Path) -> tuple[list[tuple[str, int, str, int]], list[str]]:
    """Return (entries, errors).

    Each entry is (page_stem, source_count, tldr, line_number).
    """
    entries: list[tuple[str, int, str, int]] = []
    errors: list[str] = []
    try:
        text = index_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append("wiki/index.md not found")
        return entries, errors
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("- [["):
            continue
        m = INDEX_ENTRY_RE.match(line)
        if not m:
            errors.append(
                f"line {lineno}: malformed index entry `{stripped}`"
            )
            continue
        stem, count_str, tldr = m.group(1), m.group(2), m.group(3)
        entries.append((stem.strip(), int(count_str), tldr.strip(), lineno))
    return entries, errors


def check_index(vault: Vault) -> None:
    index_path = vault.root / "wiki" / "index.md"
    entries, errors = parse_index(index_path)
    for err in errors:
        vault.add("index", index_path, err)

    indexed_stems = {e[0] for e in entries}
    # synthesis.md and `type: meta` infrastructure pages may or may not appear
    # in the index; we treat them as indexed-optional since the index template
    # groups by Entities / Concepts / Sources / Comparisons (knowledge nodes).
    page_stems_for_index: set[str] = set()
    for stem, page in vault.pages.items():
        fm = page.frontmatter
        if fm is None:
            continue
        if fm.get("type") in ("synthesis", "meta"):
            continue
        page_stems_for_index.add(stem)
    page_stems = set(vault.pages.keys())

    missing_from_index = page_stems_for_index - indexed_stems
    for stem in sorted(missing_from_index):
        vault.add(
            "index",
            vault.pages[stem].path,
            "page has no entry in wiki/index.md",
        )
    unresolved_entries = indexed_stems - page_stems
    for stem in sorted(unresolved_entries):
        vault.add(
            "index",
            index_path,
            f"index entry `[[{stem}]]` does not resolve to a file",
        )

    for stem, count, tldr, lineno in entries:
        page = vault.pages.get(stem)
        if page is None:
            continue  # already reported
        fm_sources = page.frontmatter.get("sources") if page.frontmatter else None
        expected_count = len(fm_sources) if isinstance(fm_sources, list) else 0
        if count != expected_count:
            vault.add(
                "index",
                index_path,
                f"line {lineno}: `[[{stem}]]` lists ({count}) but "
                f"frontmatter sources has {expected_count}",
            )
        if page.tldr is not None and tldr != page.tldr:
            vault.add(
                "index",
                index_path,
                f"line {lineno}: TLDR mismatch for `[[{stem}]]` "
                f"(index: `{tldr[:60]}…`, page: `{page.tldr[:60]}…`)",
            )


def check_sources_invariant(vault: Vault) -> None:
    """If a page body wikilinks a source-summary, that source must be in
    the page's frontmatter `sources:` list.
    """
    source_summary_stems = {
        stem
        for stem, page in vault.pages.items()
        if page.frontmatter and page.frontmatter.get("type") == "source-summary"
    }
    for page in vault.pages.values():
        if page.frontmatter is None:
            continue
        # Skip source-summary pages themselves: their sources list
        # typically stays empty even when they cite other sources inline.
        if page.frontmatter.get("type") == "source-summary":
            continue
        body_targets = set(extract_wikilink_targets(page.body))
        cited_sources = body_targets & source_summary_stems
        fm_sources_raw = page.frontmatter.get("sources") or []
        # Frontmatter sources are wikilinks-as-strings: "[[Page Name]]"
        fm_cited: set[str] = set()
        if isinstance(fm_sources_raw, list):
            for entry in fm_sources_raw:
                if not isinstance(entry, str):
                    continue
                for m in WIKILINK_RE.finditer(entry):
                    fm_cited.add(m.group(1).strip())
        missing = cited_sources - fm_cited
        for target in sorted(missing):
            vault.add(
                "sources-invariant",
                page.path,
                f"body cites `[[{target}]]` but frontmatter sources "
                "does not list it",
            )


def check_entity_aliases(vault: Vault) -> None:
    """Aliases across entity pages must be unique and must not collide
    with any existing page stem. An alias that matches another page's
    filename would make `[[Alias]]` ambiguous for the graph.
    """
    alias_owners: dict[str, list[Path]] = {}
    page_stems = set(vault.pages.keys())
    for page in vault.pages.values():
        fm = page.frontmatter
        if fm is None or fm.get("type") != "entity":
            continue
        aliases = fm.get("aliases") or []
        if not isinstance(aliases, list):
            continue
        for alias in aliases:
            if not isinstance(alias, str) or not alias:
                continue
            alias_owners.setdefault(alias, []).append(page.path)
            if alias in page_stems and alias != page.stem:
                vault.add(
                    "aliases",
                    page.path,
                    f"alias `{alias}` collides with existing page "
                    f"`[[{alias}]]`",
                )
    for alias, owners in alias_owners.items():
        if len(owners) > 1:
            names = ", ".join(sorted(str(p.name) for p in owners))
            for p in owners:
                vault.add(
                    "aliases",
                    p,
                    f"alias `{alias}` is claimed by multiple entities: {names}",
                )


def check_hash_drift(vault: Vault) -> None:
    for page in vault.pages.values():
        if page.frontmatter is None:
            continue
        if page.frontmatter.get("type") != "source-summary":
            continue
        raw_path_str = page.frontmatter.get("raw_path")
        raw_hash = page.frontmatter.get("raw_hash")
        if not isinstance(raw_path_str, str) or not raw_path_str:
            continue  # already reported by frontmatter check
        if not isinstance(raw_hash, str) or not raw_hash:
            continue
        raw_path = (vault.root / raw_path_str).resolve()
        if not raw_path.exists():
            vault.add(
                "hash-drift",
                page.path,
                f"raw_path `{raw_path_str}` does not exist",
            )
            continue
        try:
            digest = hashlib.sha256(raw_path.read_bytes()).hexdigest()
        except OSError as exc:
            vault.add(
                "hash-drift",
                page.path,
                f"cannot read raw_path `{raw_path_str}`: {exc}",
            )
            continue
        if digest != raw_hash:
            vault.add(
                "hash-drift",
                page.path,
                f"raw_hash mismatch for `{raw_path_str}` "
                f"(frontmatter: {raw_hash[:12]}…, actual: {digest[:12]}…)",
            )


def is_structural_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith(("#", ">", "|", "<!--")):
        return True
    if stripped == "-->" or stripped in {"---", "***"}:
        return True
    if LIST_LINE_RE.match(line):
        return True
    if WIKILINK_ONLY_RE.match(stripped):
        return True
    return False


def looks_like_claim_block(text: str) -> bool:
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", text)
    if len(words) < 4:
        return False
    if re.search(r"[.!?]", text):
        return True
    return len(words) >= 9


def check_bare_claim_candidates(vault: Vault) -> None:
    for page in vault.pages.values():
        if page.frontmatter is None:
            continue
        # synthesis is implicitly [!analysis]; meta pages are infrastructure
        # (handoffs, backlogs, decisions logs) where prose-as-format is fine.
        if page.frontmatter.get("type") in ("synthesis", "meta"):
            continue

        lines = page.body.splitlines()
        in_fence = False
        block: list[str] = []
        block_start = 0

        def flush() -> None:
            nonlocal block, block_start
            if not block:
                return
            text = " ".join(part.strip() for part in block).strip()
            if looks_like_claim_block(text):
                snippet = text[:100]
                if len(text) > 100:
                    snippet += "…"
                vault.add(
                    "bare-claim-candidate",
                    page.path,
                    f"body prose outside typed callout near body line {block_start}: `{snippet}`",
                )
            block = []
            block_start = 0

        for lineno, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("```"):
                flush()
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if is_structural_line(line):
                flush()
                continue
            if not block:
                block_start = lineno
            block.append(line)

        flush()


def page_has_callout(page: Page, callout: str) -> bool:
    pattern = re.compile(
        rf"^\s*>\s*\[!{re.escape(callout)}\]",
        re.IGNORECASE | re.MULTILINE,
    )
    return bool(pattern.search(page.body))


def parse_iso_date(value: object) -> date | None:
    if not isinstance(value, str) or not ISO_DATE_RE.match(value):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def compute_backlink_counts(vault: Vault) -> dict[str, int]:
    counts = {stem: 0 for stem in vault.pages}
    for page in vault.pages.values():
        # Meta pages are infrastructure. Their links should resolve, but they
        # should not make knowledge pages look like graph hubs.
        if page.frontmatter and page.frontmatter.get("type") == "meta":
            continue
        for target in set(extract_wikilink_targets(page.body)):
            if target in counts:
                counts[target] += 1
    return counts


def compute_health_summary(vault: Vault) -> HealthSummary:
    by_type = {typ: 0 for typ in sorted(VALID_TYPES)}
    backlinks = compute_backlink_counts(vault)
    today = date.today()

    thinly_sourced_pages = 0
    pages_with_open_gaps = 0
    pages_with_source_no_analysis = 0
    stale_hubs = 0
    source_summaries_missing_audit = 0

    for page in vault.pages.values():
        fm = page.frontmatter or {}
        typ = fm.get("type")
        if isinstance(typ, str) and typ in by_type:
            by_type[typ] += 1

        sources = fm.get("sources")
        if (
            isinstance(sources, list)
            and len(sources) == 1
            and typ not in {"source-summary", "synthesis", "meta"}
        ):
            thinly_sourced_pages += 1

        # Meta pages (backlog, handoff, decisions, graph-protocol) often carry
        # [!gap] callouts as part of their format — surfacing those as
        # "open gaps" double-counts the gaps surfaced from content pages.
        if typ != "meta" and page_has_callout(page, "gap"):
            pages_with_open_gaps += 1

        if (
            typ != "meta"
            and page_has_callout(page, "source")
            and not page_has_callout(page, "analysis")
        ):
            pages_with_source_no_analysis += 1

        updated = parse_iso_date(fm.get("updated"))
        if typ != "meta" and updated is not None and backlinks.get(page.stem, 0) >= 5:
            if (today - updated).days > 30:
                stale_hubs += 1

        if typ == "source-summary" and not AUDIT_CALLOUT_RE.search(page.body):
            source_summaries_missing_audit += 1

    return HealthSummary(
        total_pages=len(vault.pages),
        by_type=by_type,
        thinly_sourced_pages=thinly_sourced_pages,
        pages_with_open_gaps=pages_with_open_gaps,
        pages_with_source_no_analysis=pages_with_source_no_analysis,
        stale_hubs=stale_hubs,
        source_summaries_missing_audit=source_summaries_missing_audit,
    )


def render_health_summary(summary: HealthSummary) -> list[str]:
    return [
        "wiki-health: "
        f"{summary.total_pages} pages "
        f"({summary.by_type['source-summary']} sources, "
        f"{summary.by_type['entity']} entities, "
        f"{summary.by_type['concept']} concepts, "
        f"{summary.by_type['comparison']} comparisons, "
        f"{summary.by_type['synthesis']} synthesis, "
        f"{summary.by_type['meta']} meta)",
        f"thinly sourced pages: {summary.thinly_sourced_pages}",
        f"pages with open gaps: {summary.pages_with_open_gaps}",
        f"pages with [!source] but no [!analysis]: {summary.pages_with_source_no_analysis}",
        f"stale hub pages (>30 days old, 5+ backlinks): {summary.stale_hubs}",
        f"source summaries missing extraction audit callout: {summary.source_summaries_missing_audit}",
    ]


# ---------- entry point ----------


CHECKS: dict[str, Callable[["Vault"], None]] = {
    "filenames": check_filenames,
    "frontmatter": check_frontmatter,
    "wikilinks": check_wikilink_resolution,
    "index": check_index,
    "sources-invariant": check_sources_invariant,
    "aliases": check_entity_aliases,
    "hash-drift": check_hash_drift,
    "bare-claims": check_bare_claim_candidates,
}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=(__doc__ or "").splitlines()[0] if __doc__ else None
    )
    parser.add_argument(
        "--vault",
        default=".",
        help="vault root (directory containing wiki/ and raw/)",
    )
    parser.add_argument(
        "--category",
        action="append",
        choices=sorted(CHECKS.keys()),
        help="run only the named category (repeatable); default: all",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="print a health summary after validation output",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="print only the health summary and skip validation checks",
    )
    args = parser.parse_args(argv)

    root = Path(args.vault).resolve()
    if not (root / "wiki").is_dir():
        print(f"error: no wiki/ under {root}", file=sys.stderr)
        return 2

    vault = Vault(root=root)
    collect_pages(vault)

    if args.summary_only:
        for line in render_health_summary(compute_health_summary(vault)):
            print(line)
        return 0

    selected = args.category or list(CHECKS.keys())
    for name in selected:
        CHECKS[name](vault)

    if not vault.findings:
        print(f"wiki-lint: clean ({len(vault.pages)} pages checked)")
        if args.summary:
            for line in render_health_summary(compute_health_summary(vault)):
                print(line)
        return 0

    by_category: dict[str, list[Finding]] = {}
    for f in vault.findings:
        by_category.setdefault(f.category, []).append(f)

    for cat in sorted(by_category):
        print(f"\n## {cat} ({len(by_category[cat])})")
        for f in by_category[cat]:
            print(f"  {f.render(root)}")
    print(f"\nwiki-lint: {len(vault.findings)} finding(s) across "
          f"{len(by_category)} categor(ies); {len(vault.pages)} pages")
    if args.summary:
        for line in render_health_summary(compute_health_summary(vault)):
            print(line)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
