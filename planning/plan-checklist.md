# Implementation Checklist

Tracks progress on the LLM Wiki implementation. See `plan.md` for details on each step.

Phases 0-1 (Init) are the domain-agnostic setup — repeatable for any new vault. Phases 2-4 are per-wiki.

---

## Phase 0: Prerequisites & Environment

- [x] **0.1** Obsidian 1.12.7+ installed, CLI enabled, `obsidian version` works (1.12.7)
- [x] **0.2** `git --version` works (git 2.50.1)
- [x] **0.3** `pymupdf4llm` installed (1.27.2.1)
- [x] **0.4** Vault created or chosen, open in Obsidian desktop app (`wiki-tool/`)
- [x] **0.5** Obsidian settings configured:
  - [x] Default note location -> `wiki/`
  - [x] Attachment folder -> `raw/assets/`
  - [x] Template folder -> `templates/`
  - [x] Templates core plugin enabled
- [x] **0.6** Git initialized with `.gitignore`
  - `wiki-tool/` is a portable scaffold, not its own repo. `wiki-tool/.gitignore` ships with it so new vaults instantiated from it skip Obsidian workspace files. Actual `git init` happens when the scaffold is copied into a real vault location.

---

## Phase 1: Minimal Setup

All paths below are under `wiki-tool/` (the vault root for this build).

- [x] **1.1** Directories created: `raw/assets/`, `wiki/entities/`, `wiki/concepts/`, `wiki/sources/`, `wiki/comparisons/`, `templates/`
- [x] **1.2** Wiki scaffolds and human-owned files created:
  - [x] `wiki/index.md` (category headers)
  - [x] `wiki/log.md` (empty scaffold)
  - [x] `wiki/synthesis.md` (frontmatter + TLDR + placeholder)
  - [x] `purpose.md` (template scaffolded at vault root)
  - [x] `writing-style.md` (full reference at vault root, per proposal)
- [x] **1.3** Templates written:
  - [x] `templates/entity.md`
  - [x] `templates/concept.md`
  - [x] `templates/source-summary.md`
  - [x] `templates/comparison.md`
- [x] **1.4** CLI and direct approaches tested:
  - [x] Page creation: `obsidian create ... template=entity` works ✓
  - [x] Frontmatter intact, `{{date}}` resolved (`2026-04-16`)
  - [x] Test page cleaned up
  - [x] Orphan/dead-end/unresolved detection: `obsidian orphans` / `deadends` / `unresolved` all work ✓
  - [x] Search: `path=<dir>` scopes correctly; `folder=` is silently ignored (use `path=`)
  - [x] Callout search: `obsidian search:context query="[!source]" path=wiki` works ✓
  - [x] Link traversal: `backlinks file="<name>"` and `links path=<path>` work ✓
- [x] **1.5** `CLAUDE.md` written:
  - [x] Specifications section (vault layout, frontmatter, TLDR, claim typing, cross-refs, page naming, index format, log format, conventions)
  - [x] Guidance section (writing style, ingest, query, lint, synthesis)
  - [x] Writing Style subsection includes operational rules and points to `writing-style.md` for detail
  - [x] `purpose.md` referenced in vault layout, ingest, and query sections
  - [x] Wiki Conventions section (empty)
  - [x] CLI commands adjusted based on 1.4 findings (Tooling Approaches table + gotchas)
- [x] **1.6** Committed to git (under parent repo; scaffold is not its own repo)

---

## Phase 2: First Ingest

Smoke-tested against Williamson, Xi, & Breyer 2012 on the `smoke-test` branch. Content is throwaway and not merged to main; the scaffold edits it produced were merged.

- [x] **2.1** Real source added to `raw/` (williamson2012.pdf)
- [x] **2.2** Ingest run via Claude Code (`/wiki-ingest` end-to-end: convert, hash, pre-check, extract, audit, append gap callout)
- [x] **2.3** Results verified:
  - [x] Source summary page in `wiki/sources/` with correct frontmatter (including `raw_hash`) and TLDR
  - [x] Entity pages in `wiki/entities/` (no duplicates, Title Case naming)
  - [x] Concept pages in `wiki/concepts/` (no duplicates, Title Case naming)
  - [x] All claims properly typed (auditor caught 4 attribution errors — fixed post-audit)
  - [x] Agent read `purpose.md` during ingest (recognized as unpopulated template; no false steering)
  - [x] `wiki/index.md` updated
  - [x] `wiki/log.md` entry appended
  - [x] `wiki/synthesis.md` updated
- [x] Every created/updated page reviewed (via independent auditor — caught attribution errors and coverage gaps the extractor missed)
- [x] Corrections filed to Wiki Conventions (six rules; see CLAUDE.md)
- [x] **2.4** Issues recorded in CLAUDE.md Wiki Conventions
- [x] **2.5** Committed to git (scaffold → main; smoke-test content preserved on `smoke-test` branch only)

---

## Phase 3: Query & Lint Smoke Tests

- [x] **3.1** Query tested (accuracy-thresholds / source-disagreement question; `smoke-test` branch):
  - [x] Index consulted, search used, pages read, links followed
  - [x] Answer cites specific wiki pages
  - [x] Sourced claims distinguished from inferences
  - [x] Dual output (log entry appended; no new page — existing comparison covers the question)
  - [x] Log entry appended (query side effect; no new page was warranted)
- [x] **3.2** Lint tested:
  - [x] Orphans, dead ends, unresolved links checked (no wiki orphans/dead-ends; no unresolved)
  - [x] Schema checks ran:
    - [x] Frontmatter completeness per type (35 pages; all required fields present; ISO dates; YAML block lists)
    - [x] TLDR is the first content block after frontmatter on every page
    - [x] Filenames in Title Case, match wikilink text (`e-rater` brand-name exception documented)
    - [x] Index consistency (34/34 pages; counts match `len(sources)`; TLDR keyword overlap ≥ 2)
  - [x] Source drift check ran (both `raw_hash` values OK against `raw/williamson2012.pdf` and Wood PDF)
  - [x] Bare-claim heuristic ran (1 candidate found at `Human-Automated Score Agreement.md:21`, wrapped as `[!analysis]` with approval)
  - [x] Unverified claims and gaps scanned (~70 `[!gap]` callouts, most pointing at future-ingest targets)
  - [x] Claim-audit sampling ran (3 of 201 `[!source]` claims verified; seed `phase3-lint-sample-1`; references logged for rotation)
  - [x] Conceptual review produced specific findings (23 thinly-sourced, 8 bio-stub pages without `[!analysis]` — both expected at 2-source stage; no stale hubs)
  - [x] Report presented, no fixes without approval
  - [x] Log entry appended with audited claim references
- [ ] **3.3** Issues recorded, committed to git

---

## Phase 4: Iteration & Refinement

Scaffold validation only — throwaway content used to exercise remaining scaffold behaviors. Building a real wiki is a downstream project.

- [ ] **4.1** Cross-reference and contradiction patterns exercised (2-3 throwaway ingests):
  - [x] Ingest 2 (overlapping entities/concepts with Phase 2 source) — Wood et al. 2021 on `smoke-test` branch
  - [ ] Ingest 3 (contradicts a prior claim)
  - [x] Cross-references correct, existing pages updated not duplicated
  - [x] Contradictions surfaced (not smoothed) — Wood 2021 ingest surfaced the CTB 0.12 vs Williamson 0.15 SMD disagreement in [[Standardized Mean Score Difference]] and [[Williamson 2012 vs Wood 2021 - Automated Scoring Standards]]; Phase 3.1 query confirmed it remains unresolved rather than collapsed
  - [x] Index clean, log accumulating, synthesis evolving
  - [x] Auditor catches gaps/attribution errors on each ingest
- [ ] **4.2** Source update tested:
  - [ ] Raw source modified
  - [ ] Agent detects change via `raw_hash` comparison
  - [ ] Re-ingest updates affected pages
  - [ ] Updated dates refreshed
  - [ ] Unchanged source re-ingest correctly skipped (hash match)
- [ ] **4.3** Schema reviewed and evolved:
  - [ ] Wiki Conventions has entries from real use
  - [ ] Templates assessed for domain fitness
  - [ ] New page type added if needed
  - [ ] Reviewed whether diff-before-commit convention is needed
- [ ] **4.4** Committed to git

---

## Completion Criteria

The scaffold is complete when the items below are checked. A real wiki built on top of the scaffold is a separate project and is not part of completion.

- [x] All 10 scaffold deliverables committed:
  - [x] `CLAUDE.md`
  - [x] `purpose.md`
  - [x] `writing-style.md`
  - [x] `templates/entity.md`
  - [x] `templates/concept.md`
  - [x] `templates/source-summary.md`
  - [x] `templates/comparison.md`
  - [x] `wiki/index.md`
  - [x] `wiki/log.md`
  - [x] `wiki/synthesis.md`
- [x] Claude Code skills committed (added during Phase 2 reflection):
  - [x] `.claude/agents/wiki-extractor.md`
  - [x] `.claude/agents/wiki-auditor.md`
  - [x] `.claude/skills/wiki-ingest/SKILL.md` (full ingest + audit-only mode)
- [x] End-to-end ingest with correct claim typing, provenance, and independent audit report
- [x] Query with citations and dual output
- [x] Lint with structural + conceptual checks (produces report; applies no fixes without approval)
- [ ] Cross-reference and contradiction behaviors exercised across at least 2 overlapping throwaway ingests (1 overlapping ingest done; cross-ref + contradiction surfacing exercised, but 2nd overlap still pending)
- [ ] Source-update (hash drift) and hash-match audit-only paths both exercised
- [x] Log has entries for ingests, queries, and lint
- [ ] Synthesis updated across multiple ingests (2 ingests integrated; Phase 3 query did not warrant synthesis revision)
- [x] CLAUDE.md Wiki Conventions has entries from real use
