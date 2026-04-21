# Changelog

## 2026-04-21 — Revision 12

Contract alignment, first-run fixes, and smoke coverage.

### Added

- **`/wiki-lint` skill.** The scaffold now ships a real lint skill under `wiki-base/.claude/skills/wiki-lint/`, covering deterministic validation, bare-claim review, sampled claim audits, conceptual weak-spot review, and log updates. (`wiki-base/.claude/skills/wiki-lint/SKILL.md`, `wiki-base/CLAUDE.md`)
- **`wiki-doctor.sh`.** Added to spawned wikis and exposed as an installed launcher (`llm-wiki-doctor`). Checks vault structure, runs `wiki-lint.py`, and reports optional-tooling gaps without failing on them. (`wiki-base/scripts/wiki-doctor.sh`, `scripts/wiki-doctor.sh`, `install.sh`, `README.md`, `scripts/new-wiki.sh`)
- **Smoke tests.** Added a stdlib `unittest` smoke suite covering wiki scaffolding, doctor flow, and the no-PyYAML lint parser path. (`tests/test_smoke.py`)

### Changed

- **`wiki-lint.py` no longer requires PyYAML on first run.** The script now falls back to a schema-sized frontmatter parser when PyYAML is unavailable, so scaffolded vaults lint clean on a stock Python 3 install. (`wiki-base/scripts/wiki-lint.py`)
- **Runtime guidance standardized on `python3`.** README, scaffold output, skill docs, and requirements comments now use `python3` / `python3 -m pip` consistently. (`README.md`, `install.sh`, `scripts/new-wiki.sh`, `wiki-base/.claude/skills/wiki-ingest/SKILL.md`, `wiki-base/requirements.txt`)
- **Cold-start path shortened.** Getting started now runs `llm-wiki-doctor` immediately after spawning a wiki and treats `requirements.txt` as optional PDF-ingest support, not a universal setup step. (`README.md`, `install.sh`, `scripts/new-wiki.sh`)
- **Docs and shipped behavior re-aligned.** Philosophy now matches the current query contract (queries surface stale/gap findings rather than silently repairing pages), and repo docs now list the shipped lint skill plus doctor tooling. (`PHILOSOPHY.md`, `README.md`, `wiki-base/CLAUDE.md`)

## 2026-04-21 — Revision 11

First-time-setup ergonomics and repo cleanup. Goal: collapse the cold-start path from "clone → cd → script → cd → edit → claude → ingest" to "install → new-wiki → ingest."

### Added

- **`install.sh`.** One-shot installer. Clones the repo to `~/.local/share/llm-wiki` (override with `LLM_WIKI_DIR`) and symlinks `scripts/new-wiki.sh` to `~/.local/bin/llm-wiki-new` (override with `LLM_WIKI_BIN`). Re-runnable: updates the clone in place. No skill installation, no global Claude Code state beyond the launcher symlink. (`install.sh`)
- **"Getting started" section in README.** `curl | sh` install line, first-wiki example, manual-install fallback, Obsidian-optional note. Placed before "What's here" so new users hit it on first scroll. (`README.md`)

### Changed

- **`wiki-tool/` renamed to `wiki-base/`.** The directory is a skeleton copied on every `new-wiki.sh` invocation, so "base" reads truer than "tool." Nine references updated across `scripts/new-wiki.sh` and `README.md`; no other callers in the repo. (`scripts/new-wiki.sh`, `README.md`)
- **README tagline softened.** "browsable in Obsidian" → "browsable in any editor, or in Obsidian for graph view and backlinks." Reflects that Obsidian is optional. (`README.md`)
- **"Why Obsidian CLI" closing sentence added.** Notes the grep/file-I/O fallback exists for every CLI call, so Obsidian is the preferred path, not a required one. Resolves the apparent tension between the section's framing and the new Obsidian-optional claim. (`README.md`)
- **`wiki-base/` entry in "What's here" expanded.** Lists all three skills (`/wiki-ingest`, `/wiki-query`, `/wiki-purpose`), both subagents, and `scripts/wiki-lint.py`. Previous copy named only `/wiki-ingest`. (`README.md`)
- **`scripts/new-wiki.sh` entry reframed.** Leads with `llm-wiki-new` as the primary invocation; direct `scripts/new-wiki.sh` documented as the manual-install path. (`README.md`)
- **"Reading order" simplified.** Now points at Getting started → `wiki-base/CLAUDE.md` (schema) → skill docs. (`README.md`)

### Removed

- **`planning/` archive.** 700+ files covering Karpathy's gist, comments, intermediate syntheses, higher-order analyses, revisions, and Obsidian CLI reference docs. The archive served its purpose during design; now deadweight in the repo. README's `planning/` entry and reading-order references removed. (`README.md`, `planning/`)

## 2026-04-16 — Revision 10

Research-driven additions to the proposal and plan. 29 related projects surveyed in `research/` informed these changes.

### Added

- **Research corpus.** 29 notes in `research/` covering related LLM-wiki / knowledge-base projects (Karpathy's gist, Obsidian-CLI-based wikis, MCP-Obsidian integrations, semantic graph tools, compiler-analogy framings, etc.). Each note captures the project's approach, what's worth borrowing, and what diverges from this proposal. (`research/01-*` through `research/29-*`)
- **`purpose.md` (human-owned research direction).** New vault-root file scaffolded during Init. Holds the human's goal, key questions, scope, and working thesis. The LLM reads it for context during ingest and query but never modifies it. Steers what the agent emphasizes. (`implementation-proposal.md`, `plan.md`, `plan-checklist.md`)
- **`writing-style.md` (separate reference file).** Full writing-style reference extracted to its own vault-root file with examples and before/after pairs. CLAUDE.md keeps only the operational summary and points here for detail. (`implementation-proposal.md`, `plan.md`, `plan-checklist.md`)
- **Writing Style Reference section in the proposal.** Full content of `writing-style.md` documented in the proposal: funnel structure, plain language, short sentences, no hedging stacks, emdash limits, acronym rules, figure/table leads, threshold anchoring, explicit assumptions, number formatting, comparison/synthesis guidance. (`implementation-proposal.md`)
- **`raw_hash` frontmatter on source-summary pages.** SHA256 of the raw source file, captured at ingest time. Enables source-drift detection during lint and skip-on-unchanged during re-ingest. (`implementation-proposal.md`, `plan.md`, `plan-checklist.md`)
- **Multi-source citations.** `[!source]` callouts can cite multiple sources when they corroborate the same claim: `> [!source] Claim text. [[Source A]], [[Source B]]`. Makes corroboration visible at the claim level. (`implementation-proposal.md`)
- **Source count in index entries.** `wiki/index.md` format updated to include a parenthetical source count per entry: `- [[Page Name]] (3) — One-line TLDR.` The number is `len(sources)` from frontmatter. Lint checks consistency. (`implementation-proposal.md`)
- **Ingest pre-check step.** Before writing pages, the agent presents key takeaways, planned new pages, existing pages that will be updated, and potential contradictions. Human approves before the write phase. Skipped in batch mode. (`implementation-proposal.md`, `plan.md`)
- **Expanded Lint checks.**
  - **Schema checks:** frontmatter completeness per `type`, ISO 8601 dates, YAML-list fields, TLDR-position enforcement, Title Case filenames, full index consistency (membership, resolution, source counts, TLDRs).
  - **Source drift:** recompute `raw_hash` for each source-summary against its `raw_path`; flag mismatches.
  - **Bare-claim heuristic:** report prose claims outside typed callouts as candidates; `synthesis.md` exempt.
  - **Claim-audit sampling:** 2-3 `[!source]` claims per pass traced back to cited sources; audited references logged for rotation.
  - **Specific conceptual review:** thinly-sourced pages, pages lacking `[!analysis]`, stale hubs (5+ backlinks, >30d old), unanswered gaps, missing cross-links between co-occurring entities — not generic suggestions.
  (`implementation-proposal.md`, `plan.md`, `plan-checklist.md`)
- **CLI-vs-direct approach tables per operation.** Each operation (Init, Ingest, Query, Lint) now documents both the Obsidian CLI approach and the direct alternative (grep, file I/O, wikilink parsing) for every tool. Phase 1.4 tests both and records which works best. Replaces the prior "fallback" framing. (`implementation-proposal.md`, `plan.md`)
- **Init operation tool table.** Init gets its own tool table covering page creation, search, orphans, backlinks, outgoing links. (`implementation-proposal.md`)

### Changed

- **Phase 1.4 reframed.** "Test Template Creation via CLI" → "Test CLI and Direct Approaches." Tests both paths for each operation rather than assuming CLI primary with fallback secondary. (`plan.md`, `plan-checklist.md`)
- **Phase 1.2 scope expanded.** Wiki scaffolds step now includes human-owned files: scaffolds `purpose.md` at vault root and writes `writing-style.md` from the proposal's reference section. (`plan.md`, `plan-checklist.md`)
- **Phase 1.5 CLAUDE.md contents expanded.** Guidance section now includes Writing Style subsection (operational rules + pointer to `writing-style.md`); Vault Layout, Ingest, and Query sections reference `purpose.md`. (`plan.md`, `plan-checklist.md`)
- **Deliverables count: 8 → 10.** Adds `purpose.md` and `writing-style.md`. (`plan.md`, `plan-checklist.md`)
- **`raw/` description updated.** Reflects that the LLM may write converted `.md` files derived from non-markdown sources (the one documented exception to raw/ immutability). (`implementation-proposal.md`)
- **Lint report format.** New categories in the summary: schema violations, source drift, bare-claim candidates, audit findings. Every lint pass appends a log entry including audited claim references so future passes can rotate. (`implementation-proposal.md`, `plan.md`)

## 2026-04-15 — Revision 9

Writing style review of PHILOSOPHY.md and README.md against the writing style guide.

### Changed

- **PHILOSOPHY.md: document-level lead added.** One-paragraph summary of the core principles so a reader who stops early gets the key ideas. (`PHILOSOPHY.md`)
- **PHILOSOPHY.md: emdash overuse fixed.** "Everything compounds" paragraph had three emdashes; restructured to use periods and colons. (`PHILOSOPHY.md`)
- **PHILOSOPHY.md: plain language fixes.** "epistemic hygiene" → "claims", "instantiation" → "setup", passive "get recorded" → active "records". (`PHILOSOPHY.md`)
- **README.md: plain language fixes.** "types them by epistemic status" → "labels each one", "re-derived" → "rebuilt". (`README.md`)
- **README.md: long sentence split.** Researcher example's final sentence split into two for clarity. (`README.md`)
- **README.md: Obsidian CLI link removed.** Link pointed to Obsidian's main site, not CLI docs. Reference docs in the repo serve this purpose. (`README.md`)

## 2026-04-15 — Revision 8

README rewritten to explain what the LLM Wiki is, who it's for, and why it uses the Obsidian CLI.

### Added

- **"Why this exists" section.** Explains the core bet (compilation over retrieval) in two paragraphs. (`README.md`)
- **"Who it's for" section.** Three concrete use cases — researcher, PM, SWE — each showing how the wiki works in practice. Identifies the common thread: the LLM handles the maintenance burden that causes humans to abandon knowledge bases. (`README.md`)
- **"Why Obsidian CLI" section.** Justifies the Obsidian CLI choice: graph traversal for free via wikilinks, search without a search engine, the human's reading environment, and markdown as source of truth with no lock-in. (`README.md`)

### Changed

- **README intro rewritten.** One-paragraph description of what the tool is, replacing the previous one-line summary. (`README.md`)

## 2026-04-15 — Revision 7

PDF ingestion support. `pymupdf4llm` added as a required dependency for converting PDFs to markdown at ingest time.

### Added

- **`pymupdf4llm` as a required dependency.** PDFs are the primary source format in research workflows. Converting to markdown before ingestion is a required step, not an optional one. Added to prerequisites in the proposal and Phase 0 in the plan. (`implementation-proposal.md`, `plan.md`, `plan-checklist.md`)
- **PDF conversion principle in Ingest operation.** When a source is a PDF, convert it to markdown using `pymupdf4llm`, store the `.md` alongside the original in `raw/`, then ingest from the converted markdown. The original PDF stays immutable; `raw_path` points to the original. (`implementation-proposal.md`)
- **PDF conversion guidance in CLAUDE.md content.** Added to the Ingest guidance section within the skill file. (`implementation-proposal.md`)
- **`pymupdf4llm` in Ingest available tools.** (`implementation-proposal.md`)
- **Risk register entry.** `pymupdf4llm` producing poor markdown from complex PDFs (tables, multi-column, scanned). Mitigation: review converted markdown, supplement with Claude's native PDF reading. (`plan.md`)

### Changed

- **Vault structure updated.** `raw/` description now mentions PDFs and non-markdown sources alongside markdown. Converted `.md` files live alongside originals. (`implementation-proposal.md`)
- **`raw/` description in CLAUDE.md content updated.** Notes the exception for converted `.md` files derived from non-markdown sources. (`implementation-proposal.md`)
- **Phase 0 step numbering updated.** New step 0.3 (verify pymupdf4llm) inserted; subsequent steps renumbered 0.4-0.6. (`plan.md`, `plan-checklist.md`)
- **Deliverables dependency note updated.** "No external dependencies beyond Obsidian, git, and standard Unix tools" → "External dependencies: Obsidian, git, pymupdf4llm, and standard Unix tools." (`implementation-proposal.md`)

## 2026-04-15 — Revision 6

Reusability and Init operation. The system is now explicitly designed as a general-purpose tool that can be instantiated for any Obsidian vault and any domain.

### Added

- **New philosophy principle: "The pattern is reusable; each wiki is unique."** The directory structure, templates, data contracts, and operations are domain-agnostic. Domain adaptation happens through the training period and Wiki Conventions, not upfront configuration. (`PHILOSOPHY.md`)
- **New design principle (7).** Mirrors the philosophy principle in the proposal's design principles list. (`implementation-proposal.md`)
- **Init operation.** Fourth operation alongside Ingest, Query, and Lint. Instantiates a new wiki in a fresh vault: creates directories, templates, scaffolds, CLAUDE.md, initializes git, verifies CLI. Run once per wiki; repeatable for any new vault. (`implementation-proposal.md`)
- **Deliverables reusability note.** Deliverables are domain-agnostic. Each wiki instance is independent with its own git history, evolved schema, and compiled knowledge. (`implementation-proposal.md`)
- **Init workflow framing in plan.** Phases 0-1 are the repeatable Init workflow (domain-agnostic). Phases 2-4 are per-wiki (domain-specific content and refinement). Dependency graph updated to show the boundary. (`plan.md`, `plan-checklist.md`)

### Changed

- **Operations intro updated.** "Three core operations" → "Four operations. Init is run once per wiki; the other three are ongoing." (`implementation-proposal.md`)
- **Phase 0 goal updated.** Now notes that prerequisite checks are the same for every new wiki. (`plan.md`)
- **Phase 1 goal updated.** Now notes that the scaffold is the same for any domain with no customization needed. (`plan.md`)
- **README updated.** Reflects Init operation and reusability framing. (`README.md`)

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
