# Changelog

## 2026-04-13 — Revision 5

CLI test coverage, risk register corrections, and documentation fixes based on full comparative review of all planning documents against source materials (`llm-wiki.md`, `PHILOSOPHY.md`, `intermediate/`, `synthesis/`, `obsidian-cli/`) and Rounds 1-4. See `revisions/revisions-5.md` for full rationale.

### Added

- **Callout search test.** Phase 1.4 now tests whether `[!source]` callout syntax is searchable via `obsidian search:context`. Fallback: grep. New risk register entry. Lint's claim scanning depends on this. (`plan.md`, `plan-checklist.md`)
- **Link traversal test.** Phase 1.4 now tests `obsidian backlinks` and `obsidian links` with Title Case filenames. Query operations depend on these for following connections. (`plan.md`, `plan-checklist.md`)
- **README revisions section updated.** Now lists all five revision rounds instead of only the first. (`README.md`)

### Changed

- **Search `path=` risk corrected.** Risk register entry updated: `path=<folder>` IS documented in the CLI reference. Likelihood lowered from Medium to Low. Test retained to confirm behavior matches docs. (`plan.md`)
- **CHANGELOG principle count fixed.** "Seven principles" corrected to "Eight principles" — the missing one ("start simple") is the most-cited in revision rationale. (`CHANGELOG.md`)

## 2026-04-13 — Revision 4

Training period, CLI verification, data contract tightening, and guidance additions based on full comparative review of all planning documents against source materials (`llm-wiki.md`, `PHILOSOPHY.md`, `intermediate/`, `synthesis/`, `obsidian-cli/`) and Rounds 1-3. Includes a philosophy check that withdrew two candidate changes. See `revisions/revisions-4.md` for full rationale.

### Added

- **Training period formalized.** For the first ~10 ingests, human reviews every created/updated page. Corrections filed to Wiki Conventions immediately. This bootstraps the schema flywheel. Added as a new `### Training Period` subsection in CLAUDE.md Guidance, a note in Plan Phase 2, and two checklist items. (`implementation-proposal.md`, `plan.md`, `plan-checklist.md`)
- **Search directory scoping test.** Phase 1.4 now tests whether `obsidian search` supports `path=` or `folder=` filtering. Fallback: search full vault and filter by path prefix, or use grep. New risk register entry. (`plan.md`, `plan-checklist.md`)
- **Image and attachment handling guidance.** Sources with images: store in `raw/assets/`, embed with `![[image.png]]`, describe content in text for searchability. Added to CLAUDE.md Ingest guidance. (`implementation-proposal.md`)
- **Query output formats note.** Phase 3.1 now notes that diverse output formats (comparison tables, Marp slides, etc.) are supported but deferred for testing until basic query workflow is validated. (`plan.md`)

### Changed

- **Index entry conciseness specified.** "Keep entries concise" replaced with "Keep each entry under ~30 words. The index must remain small enough to read in full at the start of every query and ingest operation." Makes the ~100 entry split threshold from Round 2 actually work within context limits. (`implementation-proposal.md`, CLAUDE.md Index Format)
- **Ingestion gap threshold strengthened.** Replaced vague "minimum coverage threshold" with concrete "8-10+ sources with overlapping topics." Treat wiki answers as starting points until then. (`plan.md`, Phase 4 note)

### Withdrawn (Philosophy Check)

- **Source hash tracking** — Rated Tier 1 by critical synthesis but adding it now violates Principle 6 ("Start simple, add infrastructure when earned"). Already correctly positioned in the scaling plan.
- **Diff-before-commit promoted to Phase 2** — Mandating a procedural step on every write violates Principle 2 ("Agent as writer, not pipeline"). Already correctly positioned as a Phase 4.3 review question.

## 2026-04-13 — Revision 3

Data contract completions, risk coverage, and guidance additions based on comparative review of all planning documents against source materials (`llm-wiki.md`, `PHILOSOPHY.md`, `intermediate/`, `synthesis/`). See `revisions/revisions-3.md` for full rationale.

### Added

- **Page naming convention.** Title Case with spaces, matching wikilink text exactly. Disambiguate with parentheticals. Added to Specifications in both the proposal body and the CLAUDE.md content. (`implementation-proposal.md`)
- **Lint graph command testing.** `obsidian orphans`, `deadends`, `unresolved` now tested in Phase 1.4 alongside template creation. Fallback documented: agent reads file tree and parses wikilinks manually. (`plan.md`, `plan-checklist.md`)
- **Source granularity guidance.** For long sources, ingest chapter by chapter. Each chunk gets its own source-summary page. Added to Ingest principles and CLAUDE.md Ingest guidance. (`implementation-proposal.md`)
- **Bare-claims risk.** New risk register entry: LLM writes substantive claims as regular prose outside any callout. Rated High/High. Mitigation: review in Phase 2, add explicit correction to Wiki Conventions if it occurs. (`plan.md`)
- **Page length guidance.** If a page grows past ~1,500 words, consider splitting it. Same pattern as the ~100-entry index split threshold. (`implementation-proposal.md`, CLAUDE.md Other Conventions)

### Changed

- **Log format: H2 to H3.** Log entries now use `### [YYYY-MM-DD]` instead of `## [YYYY-MM-DD]`. Preserves grep-parsability (`grep "^### \["`) while keeping the Obsidian outline usable at scale. Updated in Specifications, CLAUDE.md, and the grep example. (`implementation-proposal.md`)

## 2026-04-13 — Revision 2

Refinements to `implementation-proposal.md`, `plan.md`, and `plan-checklist.md` based on comparative review against source material. See `revisions/revisions-2.md` for full rationale.

### Changed

- **synthesis.md scaffold frontmatter completed.** Added missing `sources`, `created`, `tags` fields to comply with the spec's "every wiki page" requirement. (`plan.md`)
- **Claim typing guidance for synthesis.md.** Synthesis is implicitly analytical — `type: synthesis` signals the page is the agent's integrated understanding. Prose is fine without per-claim callout wrappers; `[!source]` used only when referencing a specific source directly. (`implementation-proposal.md`, CLAUDE.md Synthesis section)
- **Source-summary `sources` field clarified.** Convention added: provenance comes from `raw_path`; `sources` is typically `[]` unless the summary draws on other source-summary pages. (`implementation-proposal.md`, CLAUDE.md Other Conventions)
- **Index split threshold added.** Rule of thumb: split when the index exceeds ~100 entries. Based on community-reported ~200-page retrieval ceiling. (`implementation-proposal.md`, CLAUDE.md Index Format)
- **Dual output elevated to universal convention.** Every ingest and query updates the wiki — index, log, and synthesis updates are part of the deliverable, not afterthoughts. (`implementation-proposal.md`, CLAUDE.md Other Conventions)
- **Ingestion gap acknowledged.** Note added to Phase 4: a partially-built wiki can underperform no wiki at all. The wiki's value compounds after a minimum coverage threshold. (`plan.md`)
- **Diff-before-commit flagged for Phase 4 review.** Question added to schema review: is "prefer targeted updates" sufficient, or should the agent show proposed diffs? (`plan.md`, `plan-checklist.md`)

### Meta

- **Revisions format established.** `revisions-2.md` contains rationale and diffs only — no full document copies. `revisions-1.md` is a frozen historical snapshot.

## 2026-04-13 — Revision 1

Major revision to `implementation-proposal.md`, `plan.md`, and `plan-checklist.md`. Added `PHILOSOPHY.md`. See `revisions/revisions-1.md` for full rationale.

### Added

- **`PHILOSOPHY.md`** — Design philosophy document. Eight principles: compilation over retrieval, agent as writer, strict/flexible split, epistemic integrity, human as editor-in-chief, schema co-evolution, start simple, compounding value.
- **`wiki/log.md`** — Chronological operation log restored from the original `llm-wiki.md`. Append-only, parseable with `grep "^### \[" log.md | tail -5`. Integrated into all three operations.
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
