# Changelog

## 2026-04-13 — Revision 1

Major revision to `implementation-proposal.md`, `plan.md`, and `plan-checklist.md`. Added `PHILOSOPHY.md`. See `revisions/revisions-1.md` for full rationale.

### Added

- **`PHILOSOPHY.md`** — Design philosophy document. Seven principles: compilation over retrieval, agent as writer, strict/flexible split, epistemic integrity, human as editor-in-chief, schema co-evolution, compounding value.
- **`wiki/log.md`** — Chronological operation log restored from the original `llm-wiki.md`. Append-only, parseable with `grep "^## \[" log.md | tail -5`. Integrated into all three operations.
- **`wiki/synthesis.md`** — Given a real operational role. Updated on every ingest, reviewed during lint.
- **Generative lint** — Lint now includes a conceptual review phase: the agent identifies thinly covered topics, unanswered questions, and suggested investigations. Not just structural janitorial work.
- **Specifications vs. guidance split** — CLAUDE.md reorganized into two sections: strict data contracts (frontmatter, callouts, directories, formats) and flexible guidance (goals and principles for each operation).
- **Wiki Conventions section** — Replaces "Accumulated Corrections" in CLAUDE.md. The agent actively maintains learned patterns, domain conventions, and workflow refinements — not just reactive error fixes.
- **Query output formats** — Queries can produce markdown pages, comparison tables, Marp slide decks, or other formats as appropriate. Agent chooses based on the question.

### Changed

- **Plan condensed from 9 phases to 5.** First ingest now happens in Phase 2 (second phase of work), not Phase 5. Templates, directories, CLAUDE.md, and scaffolds are all created in a single Phase 1.
- **Obsidian CLI role narrowed.** CLI used for search and graph operations (`obsidian search`, `obsidian backlinks`, `obsidian orphans`, `obsidian deadends`, `obsidian unresolved`). Direct file I/O used for reading and writing markdown. Removes hard dependency on desktop app for basic operations.
- **Operations described by goals and principles**, not numbered step-by-step procedures. The agent exercises judgment about how to accomplish each operation based on the specific source, question, or wiki state.
- **Templates: strict structure, flexible sections.** Frontmatter schema, TLDR callout, and claim typing syntax are mandatory (tools depend on them). Default section headings adapt to the domain.
- **Deliverables changed from 8 files to 8 files** (same count, different composition): 1 skill file, 4 templates, 3 wiki scaffolds. Replaces: 1 skill file, 4 templates, 3 shell scripts.
- **Risk register updated.** Removed script-related risks. Added risks for duplicate page creation and claim typing errors.
- **Success criteria updated.** Now includes log entries, synthesis updates, and Wiki Conventions entries.

### Removed

- **Shell scripts** (`hash-sources.sh`, `check-stale.sh`, `build-index.sh`) — removed from V1 deliverables. The LLM performs these operations natively. Hash-based staleness deferred to the scaling plan.
- **SHA-256 source hashes in frontmatter** (`source_hashes` field) — removed from templates. Provenance tracked via `sources` wikilinks. Git provides change history. Hash tracking available in the scaling plan if needed later.
- **Token budget on index** (was 3,000 tokens) — removed. Convention is to keep entries concise and split into per-category indexes when the single file becomes unwieldy. Agent judges when.
- **`scripts/` directory** — removed from vault structure.
- **`shasum` prerequisite** — no longer needed without hash scripts.

## 2026-04-13 — Initial documents

- `implementation-proposal.md` — Initial proposal with Obsidian CLI exclusivity, shell scripts, hash-based provenance, 8 deliverables (1 skill file, 4 templates, 3 scripts).
- `plan.md` — 9-phase plan with dependency graph.
- `plan-checklist.md` — 72-item checklist.
