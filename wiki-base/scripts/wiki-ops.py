#!/usr/bin/env python3
"""wiki-ops.py - deterministic wiki operation primitives.

This CLI is intentionally small. It provides machine-readable primitives
for source staging, source status, affected-page discovery, audit-callout
replacement, and operation manifests. It does not extract, synthesize,
repair, or decide ingest policy.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib
import json
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, NoReturn


SPECIAL_FILES = {"index.md", "log.md", "conventions.md"}
MANIFEST_DIR = "wiki/.ops"
KNOWLEDGE_TYPES = {
    "entity",
    "concept",
    "comparison",
    "source-summary",
    "synthesis",
}
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+?)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
AUDIT_CALLOUT_START_RE = re.compile(
    r"^\s*>\s*\[!gap\]\s+Extraction coverage of this ingest\b",
    re.IGNORECASE,
)
_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


@dataclass
class Page:
    path: Path
    frontmatter: dict[str, Any] | None
    body: str
    error: str | None = None

    @property
    def stem(self) -> str:
        return self.path.stem


class WikiOpsError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        details: dict[str, Any] | None = None,
        exit_code: int = 2,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}
        self.exit_code = exit_code


def json_default(value: object) -> str:
    if isinstance(value, Path):
        return value.as_posix()
    return str(value)


def emit_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True, default=json_default))


def success_response(command: str, **fields: Any) -> dict[str, Any]:
    return {"ok": True, "command": command, **fields}


def error_response(
    command: str | None,
    code: str,
    message: str,
    *,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "ok": False,
        "command": command,
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
    }


def fail_json(
    command: str | None,
    code: str,
    message: str,
    *,
    details: dict[str, Any] | None = None,
    exit_code: int = 2,
) -> NoReturn:
    emit_json(error_response(command, code, message, details=details))
    raise SystemExit(exit_code)


def infer_command(argv: list[str]) -> str | None:
    i = 0
    while i < len(argv):
        token = argv[i]
        if token == "--vault":
            i += 2
            continue
        if token.startswith("--vault="):
            i += 1
            continue
        if token.startswith("-"):
            i += 1
            continue
        return token
    return None


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        command = infer_command(sys.argv[1:])
        fail_json(
            command,
            "usage",
            message,
            details={"usage": self.format_usage().strip()},
            exit_code=2,
        )


# ---------- frontmatter + wikilink parsing ----------


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


def parse_minimal_yaml_mapping(text: str) -> tuple[dict[str, Any] | None, str | None]:
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
                return None, f"expected list item under `{key}` on line {i + 1}"
            items.append(parse_yaml_scalar(item_stripped[2:].strip()))
            i += 1
        result[key] = items

    return result, None


def split_frontmatter(text: str) -> tuple[dict[str, Any] | None, str, str | None]:
    """Return (frontmatter dict or None, body text, error message or None)."""

    if not text.startswith("---\n") and not text.startswith("---\r\n"):
        return None, text, "no frontmatter block at file start"
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
    fm, err = parse_minimal_yaml_mapping(fm_text)
    if err:
        return None, body, err
    if not isinstance(fm, dict):
        return None, body, "frontmatter is not a mapping"
    return fm, body, None


def strip_code(text: str) -> str:
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
        match.group(1).strip()
        for match in WIKILINK_RE.finditer(strip_code(text))
    ]


def read_markdown_page(path: Path) -> Page:
    text = path.read_text(encoding="utf-8")
    frontmatter, body, error = split_frontmatter(text)
    return Page(path=path, frontmatter=frontmatter, body=body, error=error)


def collect_wiki_pages(vault: Path) -> dict[str, Page]:
    pages: dict[str, Page] = {}
    wiki_dir = vault / "wiki"
    for md_path in sorted(wiki_dir.rglob("*.md")):
        if md_path.name in SPECIAL_FILES:
            continue
        page = read_markdown_page(md_path)
        pages.setdefault(page.stem, page)
    return pages


# ---------- vault paths ----------


def resolve_vault(vault_arg: str) -> Path:
    vault = Path(vault_arg).expanduser().resolve()
    if not vault.is_dir():
        raise WikiOpsError(
            "vault_not_found",
            f"Vault directory does not exist: {vault}",
            details={"vault": vault.as_posix()},
        )
    missing = [
        name for name in ("wiki", "raw") if not (vault / name).is_dir()
    ]
    if missing:
        raise WikiOpsError(
            "invalid_vault",
            "Vault must contain wiki/ and raw/ directories.",
            details={"vault": vault.as_posix(), "missing": missing},
        )
    return vault


def ensure_within_vault(vault: Path, path: Path) -> None:
    try:
        path.resolve().relative_to(vault.resolve())
    except ValueError as exc:
        raise WikiOpsError(
            "path_outside_vault",
            "Path is outside the vault.",
            details={"vault": vault.as_posix(), "path": path.as_posix()},
        ) from exc


def resolve_vault_path(vault: Path, value: str | Path, *, must_exist: bool = False) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = vault / path
    resolved = path.resolve()
    ensure_within_vault(vault, resolved)
    if must_exist and not resolved.exists():
        raise WikiOpsError(
            "path_not_found",
            "Path does not exist.",
            details={"path": vault_relative_path(vault, resolved)},
        )
    return resolved


def vault_relative_path(vault: Path, path: str | Path) -> str:
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = vault / candidate
    resolved = candidate.resolve()
    ensure_within_vault(vault, resolved)
    return resolved.relative_to(vault.resolve()).as_posix()


def is_under_relpath(vault: Path, path: Path, dirname: str) -> bool:
    try:
        rel = Path(vault_relative_path(vault, path))
    except WikiOpsError:
        return False
    prefix = Path(dirname).parts
    return len(rel.parts) >= len(prefix) and rel.parts[: len(prefix)] == prefix


def require_under_relpath(vault: Path, path: Path, dirname: str, label: str) -> None:
    if not is_under_relpath(vault, path, dirname):
        raise WikiOpsError(
            f"invalid_{label}",
            f"{label.replace('_', ' ').capitalize()} must be under {dirname}/.",
            details={
                label: vault_relative_path(vault, path),
                "required_prefix": f"{dirname}/",
            },
        )


# ---------- source staging ----------


def resolve_existing_input_path(vault: Path, value: str) -> Path:
    path = Path(value).expanduser()
    candidates = [path] if path.is_absolute() else [vault / path, Path.cwd() / path]
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.exists():
            if not resolved.is_file():
                raise WikiOpsError(
                    "not_a_file",
                    "Input path must be a file.",
                    details={"path": resolved.as_posix()},
                )
            return resolved
    raise WikiOpsError(
        "path_not_found",
        "Path does not exist.",
        details={"path": value},
    )


def source_kind_for_path(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".md", ".markdown"}:
        return "markdown"
    if suffix == ".pdf":
        return "pdf"
    raise WikiOpsError(
        "unsupported_source_kind",
        "Source must be a markdown file or PDF.",
        details={"path": path.as_posix(), "suffix": suffix},
    )


def next_available_raw_path(vault: Path, source_path: Path) -> Path:
    raw_dir = vault / "raw"
    destination = raw_dir / source_path.name
    if not destination.exists() or destination.resolve() == source_path.resolve():
        return destination
    try:
        if destination.read_bytes() == source_path.read_bytes():
            return destination
    except OSError:
        pass

    stem = source_path.stem
    suffix = source_path.suffix
    counter = 2
    while True:
        candidate = raw_dir / f"{stem}-{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def stage_source_file(vault: Path, source_path: Path) -> tuple[Path, list[str]]:
    warnings: list[str] = []
    if is_under_relpath(vault, source_path, "raw"):
        return source_path, warnings

    destination = next_available_raw_path(vault, source_path)
    if destination.exists():
        warnings.append(
            f"raw/{destination.name} already existed with identical bytes; reused it."
        )
    else:
        shutil.copy2(source_path, destination)
    return destination, warnings


def convert_pdf_to_markdown(vault: Path, pdf_path: Path) -> tuple[Path, list[str]]:
    warnings: list[str] = []
    try:
        pymupdf4llm = importlib.import_module("pymupdf4llm")
    except ModuleNotFoundError as exc:
        raise WikiOpsError(
            "pdf_conversion_unavailable",
            "PDF staging requires pymupdf4llm. Install it or provide a markdown source.",
            details={"raw_path": vault_relative_path(vault, pdf_path)},
        ) from exc

    markdown = pymupdf4llm.to_markdown(str(pdf_path))
    if not isinstance(markdown, str):
        raise WikiOpsError(
            "pdf_conversion_failed",
            "pymupdf4llm.to_markdown did not return markdown text.",
            details={"raw_path": vault_relative_path(vault, pdf_path)},
        )

    markdown_path = pdf_path.with_suffix(".md")
    if markdown_path.exists():
        warnings.append(
            f"{vault_relative_path(vault, markdown_path)} already existed and was replaced."
        )
    markdown_path.write_text(markdown, encoding="utf-8")
    return markdown_path, warnings


# ---------- source summaries + citations ----------


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify_source_status(vault: Path, raw_path: Path) -> dict[str, Any]:
    require_under_relpath(vault, raw_path, "raw", "raw_path")
    raw_path_rel = vault_relative_path(vault, raw_path)
    raw_hash = sha256_file(raw_path)
    matches = find_source_summaries_for_raw_path(vault, raw_path_rel)
    source_summary_paths = [
        vault_relative_path(vault, page.path)
        for page in sorted(matches, key=lambda page: page.stem)
    ]

    if not matches:
        status = "new"
        message = "No source summary claims this raw path."
    elif len(matches) > 1:
        status = "ambiguous"
        message = "Multiple source summaries claim this raw path."
    else:
        recorded_hash = (
            matches[0].frontmatter.get("raw_hash")
            if matches[0].frontmatter
            else None
        )
        if recorded_hash == raw_hash:
            status = "match"
            message = "Existing source summary hash matches this raw path."
        else:
            status = "drift"
            message = "Existing source summary hash differs from this raw path."

    return {
        "status": status,
        "raw_path": raw_path_rel,
        "raw_hash": raw_hash,
        "source_summary_paths": source_summary_paths,
        "message": message,
    }


def source_summary_pages(vault: Path) -> list[Page]:
    source_dir = vault / "wiki" / "sources"
    pages: list[Page] = []
    if not source_dir.is_dir():
        return pages
    for md_path in sorted(source_dir.rglob("*.md")):
        page = read_markdown_page(md_path)
        if page.frontmatter and page.frontmatter.get("type") == "source-summary":
            pages.append(page)
    return pages


def frontmatter_raw_path_rel(vault: Path, raw_path: object) -> str | None:
    if not isinstance(raw_path, str) or not raw_path.strip():
        return None
    try:
        return vault_relative_path(vault, raw_path.strip())
    except WikiOpsError:
        return None


def find_source_summaries_for_raw_path(vault: Path, raw_path_rel: str) -> list[Page]:
    matches: list[Page] = []
    for page in source_summary_pages(vault):
        page_raw_rel = frontmatter_raw_path_rel(
            vault,
            page.frontmatter.get("raw_path") if page.frontmatter else None,
        )
        if page_raw_rel == raw_path_rel:
            matches.append(page)
    return matches


def target_from_source_summary_arg(value: str) -> str:
    targets = extract_wikilink_targets(value)
    if targets:
        return targets[0]
    return value.strip()


def resolve_source_summary_page(vault: Path, value: str) -> Page:
    target = target_from_source_summary_arg(value)
    candidate = Path(target).expanduser()
    looks_like_path = (
        candidate.is_absolute()
        or candidate.suffix == ".md"
        or "/" in target
        or "\\" in target
    )

    if looks_like_path:
        path = resolve_vault_path(vault, target, must_exist=True)
        page = read_markdown_page(path)
        if not page.frontmatter or page.frontmatter.get("type") != "source-summary":
            raise WikiOpsError(
                "not_source_summary",
                "Resolved page is not a source-summary page.",
                details={"path": vault_relative_path(vault, path)},
            )
        return page

    matches = [page for page in source_summary_pages(vault) if page.stem == target]
    if not matches:
        raise WikiOpsError(
            "source_summary_not_found",
            "No source-summary page matches the provided reference.",
            details={"source_summary": value},
        )
    if len(matches) > 1:
        raise WikiOpsError(
            "ambiguous_source_summary",
            "Multiple source-summary pages match the provided reference.",
            details={
                "source_summary": value,
                "matches": [
                    vault_relative_path(vault, page.path) for page in matches
                ],
            },
        )
    return matches[0]


def frontmatter_sources_targets(sources: object) -> set[str]:
    targets: set[str] = set()
    if not isinstance(sources, list):
        return targets
    for entry in sources:
        if not isinstance(entry, str):
            continue
        entry_targets = extract_wikilink_targets(entry)
        if entry_targets:
            targets.update(entry_targets)
            continue
        stripped = entry.strip()
        if stripped:
            targets.add(stripped)
    return targets


def page_cites_source_summary(page: Page, source_stem: str) -> bool:
    fm_targets = frontmatter_sources_targets(
        page.frontmatter.get("sources") if page.frontmatter else None
    )
    if source_stem in fm_targets:
        return True
    return source_stem in set(extract_wikilink_targets(page.body))


def unresolved_wikilinks_from_page(vault: Path, page: Page) -> list[str]:
    pages = collect_wiki_pages(vault)
    known = set(pages) | {Path(name).stem for name in SPECIAL_FILES}
    unresolved = sorted(
        {
            f"[[{target}]]"
            for target in extract_wikilink_targets(page.body)
            if target not in known
        }
    )
    return unresolved


# ---------- audit appending ----------


def normalize_audit_callout(report_text: str) -> str:
    stripped = report_text.strip()
    if not stripped:
        raise WikiOpsError(
            "empty_audit_report",
            "Audit report is empty.",
        )

    lines = stripped.splitlines()
    if lines and AUDIT_CALLOUT_START_RE.match(lines[0]):
        return "\n".join(line.rstrip() for line in lines).rstrip() + "\n"

    callout_lines = ["> [!gap] Extraction coverage of this ingest"]
    for line in lines:
        if line.strip():
            callout_lines.append(f"> {line.rstrip()}")
        else:
            callout_lines.append(">")
    return "\n".join(callout_lines).rstrip() + "\n"


def read_audit_report(vault: Path, value: str) -> str:
    if value == "-":
        return sys.stdin.read()
    path = resolve_existing_input_path(vault, value)
    return path.read_text(encoding="utf-8")


def replace_updated_frontmatter_line(text: str, updated: str) -> str:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise WikiOpsError(
            "missing_frontmatter",
            "Source-summary page has no frontmatter block.",
        )

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        raise WikiOpsError(
            "missing_frontmatter",
            "Source-summary frontmatter is not closed.",
        )

    for i in range(1, end_idx):
        if lines[i].lstrip().startswith("updated:"):
            newline = "\n" if lines[i].endswith("\n") else ""
            lines[i] = f'updated: "{updated}"{newline}'
            return "".join(lines)

    raise WikiOpsError(
        "missing_updated",
        "Source-summary frontmatter has no updated field.",
    )


def find_audit_callout_span(lines: list[str]) -> tuple[int, int] | None:
    for start, line in enumerate(lines):
        if not AUDIT_CALLOUT_START_RE.match(line):
            continue
        end = start + 1
        while end < len(lines) and lines[end].lstrip().startswith(">"):
            end += 1
        return start, end
    return None


def append_callout_lines(lines: list[str], callout: str) -> list[str]:
    insert_idx = len(lines)
    for i, line in enumerate(lines):
        if line.strip() == "## Notes":
            insert_idx = len(lines)
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("## "):
                    insert_idx = j
                    break
            break

    callout_lines = callout.splitlines(keepends=True)
    if callout_lines and not callout_lines[-1].endswith("\n"):
        callout_lines[-1] += "\n"

    insertion: list[str] = []
    if insert_idx > 0 and lines[insert_idx - 1].strip():
        insertion.append("\n")
    insertion.extend(callout_lines)
    if insert_idx < len(lines) and lines[insert_idx].strip():
        insertion.append("\n")

    return lines[:insert_idx] + insertion + lines[insert_idx:]


def replace_or_append_audit_callout(text: str, callout: str) -> tuple[str, bool]:
    lines = text.splitlines(keepends=True)
    span = find_audit_callout_span(lines)
    callout_lines = callout.splitlines(keepends=True)
    if callout_lines and not callout_lines[-1].endswith("\n"):
        callout_lines[-1] += "\n"

    if span is not None:
        start, end = span
        return "".join(lines[:start] + callout_lines + lines[end:]), True

    return "".join(append_callout_lines(lines, callout)), False


# ---------- manifests ----------


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00",
        "Z",
    )


def safe_manifest_stem(raw_path_rel: str) -> str:
    stem = Path(raw_path_rel).stem.lower()
    safe = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
    return safe or "source"


def manifest_filename(raw_path_rel: str, raw_hash: str, created: str) -> str:
    compact_time = (
        created.replace("-", "")
        .replace(":", "")
        .replace("+00:00", "Z")
        .replace("T", "T")
    )
    return f"{compact_time}-{safe_manifest_stem(raw_path_rel)}-{raw_hash[:12]}.json"


def manifest_dir(vault: Path) -> Path:
    return vault / MANIFEST_DIR


def build_manifest(vault: Path, raw_path: Path) -> dict[str, Any]:
    status_payload = classify_source_status(vault, raw_path)
    timestamp = utc_timestamp()
    raw_suffix = raw_path.suffix.lower()
    source_md_path = None
    if raw_suffix in {".md", ".markdown"}:
        source_md_path = status_payload["raw_path"]
    elif raw_suffix == ".pdf" and raw_path.with_suffix(".md").is_file():
        source_md_path = vault_relative_path(vault, raw_path.with_suffix(".md"))

    return {
        "manifest_version": 1,
        "created": timestamp,
        "updated": timestamp,
        "raw_path": status_payload["raw_path"],
        "raw_hash": status_payload["raw_hash"],
        "hash_status": status_payload["status"],
        "hash_status_message": status_payload["message"],
        "source_summary_paths": status_payload["source_summary_paths"],
        "source_md_path": source_md_path,
        "precheck_summary": None,
        "planned_pages": [],
        "touched_pages": [],
        "auditor_report": {
            "path": None,
            "inline": None,
        },
        "deferred_items": [],
        "timestamps": {
            "created": timestamp,
            "updated": timestamp,
        },
    }


def write_manifest(vault: Path, manifest: dict[str, Any]) -> Path:
    ops_dir = manifest_dir(vault)
    ops_dir.mkdir(parents=True, exist_ok=True)
    name = manifest_filename(
        str(manifest["raw_path"]),
        str(manifest["raw_hash"]),
        str(manifest["created"]),
    )
    path = ops_dir / name
    counter = 2
    while path.exists():
        path = ops_dir / f"{Path(name).stem}-{counter}.json"
        counter += 1
    manifest["manifest_path"] = vault_relative_path(vault, path)
    path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def resolve_manifest_path(vault: Path, value: str) -> Path:
    path = resolve_vault_path(vault, value, must_exist=True)
    if not is_under_relpath(vault, path, MANIFEST_DIR):
        raise WikiOpsError(
            "invalid_manifest_path",
            "Manifest path must be under wiki/.ops/.",
            details={"manifest_path": vault_relative_path(vault, path)},
        )
    if path.suffix.lower() != ".json":
        raise WikiOpsError(
            "invalid_manifest_path",
            "Manifest path must be a JSON file.",
            details={"manifest_path": vault_relative_path(vault, path)},
        )
    return path


# ---------- command handlers ----------


def not_implemented(command: str) -> NoReturn:
    raise WikiOpsError(
        "not_implemented",
        f"`{command}` is defined but not implemented in this phase.",
        details={"command": command},
        exit_code=2,
    )


def handle_stage_source(args: argparse.Namespace, vault: Path) -> dict[str, Any]:
    source_path = resolve_existing_input_path(vault, args.path)
    source_kind = source_kind_for_path(source_path)
    raw_path, warnings = stage_source_file(vault, source_path)

    if source_kind == "markdown":
        source_md_path = raw_path
        converted = False
    else:
        source_md_path, conversion_warnings = convert_pdf_to_markdown(vault, raw_path)
        warnings.extend(conversion_warnings)
        converted = True

    return success_response(
        "stage-source",
        raw_path=vault_relative_path(vault, raw_path),
        source_md_path=vault_relative_path(vault, source_md_path),
        source_kind=source_kind,
        converted=converted,
        warnings=warnings,
    )


def handle_source_status(args: argparse.Namespace, vault: Path) -> dict[str, Any]:
    raw_path = resolve_vault_path(vault, args.raw_path, must_exist=True)
    return success_response(
        "source-status",
        **classify_source_status(vault, raw_path),
    )


def handle_affected_pages(args: argparse.Namespace, vault: Path) -> dict[str, Any]:
    source_page = resolve_source_summary_page(vault, args.source_summary)
    source_page_rel = vault_relative_path(vault, source_page.path)
    source_stem = source_page.stem

    knowledge_pages: list[str] = []
    meta_pages: list[str] = []
    for page in collect_wiki_pages(vault).values():
        if page.path == source_page.path:
            continue
        if not page_cites_source_summary(page, source_stem):
            continue

        page_rel = vault_relative_path(vault, page.path)
        page_type = page.frontmatter.get("type") if page.frontmatter else None
        if page_type == "meta":
            meta_pages.append(page_rel)
        elif page_type in KNOWLEDGE_TYPES:
            knowledge_pages.append(page_rel)

    return success_response(
        "affected-pages",
        source_summary_path=source_page_rel,
        knowledge_pages=sorted(knowledge_pages),
        meta_pages=sorted(meta_pages),
        unresolved_references=unresolved_wikilinks_from_page(vault, source_page),
    )


def handle_append_audit(args: argparse.Namespace, vault: Path) -> dict[str, Any]:
    source_page = resolve_source_summary_page(vault, args.source_summary)
    source_page_rel = vault_relative_path(vault, source_page.path)
    report_text = read_audit_report(vault, args.audit_report)
    callout = normalize_audit_callout(report_text)
    updated = date.today().isoformat()

    original = source_page.path.read_text(encoding="utf-8")
    with_updated = replace_updated_frontmatter_line(original, updated)
    revised, replaced_existing = replace_or_append_audit_callout(
        with_updated,
        callout,
    )
    source_page.path.write_text(revised, encoding="utf-8")

    return success_response(
        "append-audit",
        source_summary_path=source_page_rel,
        replaced_existing=replaced_existing,
        updated=updated,
    )


def handle_manifest(args: argparse.Namespace, vault: Path) -> dict[str, Any]:
    if args.manifest_action == "new":
        raw_path = resolve_vault_path(vault, args.raw_path, must_exist=True)
        manifest = build_manifest(vault, raw_path)
        write_manifest(vault, manifest)
        return success_response(
            "manifest new",
            manifest_path=manifest["manifest_path"],
            raw_path=manifest["raw_path"],
            raw_hash=manifest["raw_hash"],
            hash_status=manifest["hash_status"],
            created=manifest["created"],
            updated=manifest["updated"],
        )

    if args.manifest_action == "show":
        manifest_path = resolve_manifest_path(vault, args.manifest_path)
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise WikiOpsError(
                "invalid_manifest_json",
                "Manifest file is not valid JSON.",
                details={
                    "manifest_path": vault_relative_path(vault, manifest_path),
                    "line": exc.lineno,
                    "column": exc.colno,
                },
            ) from exc
        if not isinstance(manifest, dict):
            raise WikiOpsError(
                "invalid_manifest_json",
                "Manifest JSON must be an object.",
                details={"manifest_path": vault_relative_path(vault, manifest_path)},
            )
        manifest.setdefault("manifest_path", vault_relative_path(vault, manifest_path))
        return success_response("manifest show", **manifest)

    not_implemented(f"manifest {args.manifest_action}")


def build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(
        description="Deterministic wiki operation primitives.",
    )
    parser.add_argument(
        "--vault",
        default=".",
        help="vault root (directory containing wiki/ and raw/)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    stage = subparsers.add_parser("stage-source")
    stage.add_argument("path")
    stage.set_defaults(handler=handle_stage_source)

    status = subparsers.add_parser("source-status")
    status.add_argument("raw_path")
    status.set_defaults(handler=handle_source_status)

    affected = subparsers.add_parser("affected-pages")
    affected.add_argument("source_summary")
    affected.set_defaults(handler=handle_affected_pages)

    audit = subparsers.add_parser("append-audit")
    audit.add_argument("source_summary")
    audit.add_argument("audit_report")
    audit.set_defaults(handler=handle_append_audit)

    manifest = subparsers.add_parser("manifest")
    manifest_subparsers = manifest.add_subparsers(
        dest="manifest_action",
        required=True,
    )
    manifest_new = manifest_subparsers.add_parser("new")
    manifest_new.add_argument("raw_path")
    manifest_new.set_defaults(handler=handle_manifest)

    manifest_show = manifest_subparsers.add_parser("show")
    manifest_show.add_argument("manifest_path")
    manifest_show.set_defaults(handler=handle_manifest)

    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command

    try:
        vault = resolve_vault(args.vault)
        handler: Callable[[argparse.Namespace, Path], dict[str, Any]] = args.handler
        emit_json(handler(args, vault))
        return 0
    except WikiOpsError as exc:
        emit_json(
            error_response(
                command,
                exc.code,
                exc.message,
                details=exc.details,
            )
        )
        return exc.exit_code
    except UnicodeDecodeError as exc:
        emit_json(
            error_response(
                command,
                "encoding_error",
                "File is not valid UTF-8.",
                details={"encoding": exc.encoding, "reason": exc.reason},
            )
        )
        return 2
    except OSError as exc:
        emit_json(
            error_response(
                command,
                "io_error",
                str(exc),
                details={"errno": exc.errno},
            )
        )
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
