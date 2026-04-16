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

- [ ] **2.1** Real source added to `raw/`
- [ ] **2.2** Ingest run via Claude Code
- [ ] **2.3** Results verified:
  - [ ] Source summary page in `wiki/sources/` with correct frontmatter (including `raw_hash`) and TLDR
  - [ ] Entity pages in `wiki/entities/` (no duplicates, Title Case naming)
  - [ ] Concept pages in `wiki/concepts/` (no duplicates, Title Case naming)
  - [ ] All claims properly typed (source callouts have links, analysis shows reasoning, multi-source claims cite all sources)
  - [ ] Agent read `purpose.md` during ingest (if populated)
  - [ ] `wiki/index.md` updated
  - [ ] `wiki/log.md` entry appended
  - [ ] `wiki/synthesis.md` updated
- [ ] Every created/updated page reviewed (not just spot-checked)
- [ ] Corrections filed to Wiki Conventions
- [ ] **2.4** Issues recorded in CLAUDE.md Wiki Conventions
- [ ] **2.5** Committed to git

---

## Phase 3: Query & Lint Smoke Tests

- [ ] **3.1** Query tested:
  - [ ] Index consulted, search used, pages read, links followed
  - [ ] Answer cites specific wiki pages
  - [ ] Sourced claims distinguished from inferences
  - [ ] Dual output (wiki updates as side effect, if applicable)
  - [ ] Log entry appended if a new page was created
- [ ] **3.2** Lint tested:
  - [ ] Orphans, dead ends, unresolved links checked
  - [ ] Schema checks ran:
    - [ ] Frontmatter completeness per type (core + per-type fields; ISO 8601 dates; `sources`/`tags`/`subjects` as YAML lists)
    - [ ] TLDR is the first content block after frontmatter on every page
    - [ ] Filenames in Title Case, match wikilink text
    - [ ] Index consistency (every page has an entry; every entry resolves; source counts match; TLDRs match)
  - [ ] Source drift check ran (recomputed `raw_hash` for each source-summary, flagged mismatches)
  - [ ] Bare-claim heuristic ran (prose claims outside typed callouts reported as candidates; `synthesis.md` exempt)
  - [ ] Unverified claims and gaps scanned
  - [ ] Claim-audit sampling ran (2-3 `[!source]` claims verified against cited sources; rotation honored)
  - [ ] Conceptual review produced specific findings (not generic suggestions)
  - [ ] Report presented, no fixes without approval
  - [ ] Log entry appended with audited claim references
- [ ] **3.3** Issues recorded, committed to git

---

## Phase 4: Iteration & Refinement

- [ ] **4.1** Additional sources ingested (target: 3-5):
  - [ ] Source 2 ingested and reviewed
  - [ ] Source 3 ingested and reviewed
  - [ ] Source 4 ingested and reviewed
  - [ ] Cross-references correct, existing pages updated not duplicated
  - [ ] Contradictions surfaced
  - [ ] Index clean, log accumulating, synthesis evolving
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

- [ ] All 10 deliverables committed:
  - [ ] `CLAUDE.md`
  - [ ] `purpose.md`
  - [ ] `writing-style.md`
  - [ ] `templates/entity.md`
  - [ ] `templates/concept.md`
  - [ ] `templates/source-summary.md`
  - [ ] `templates/comparison.md`
  - [ ] `wiki/index.md`
  - [ ] `wiki/log.md`
  - [ ] `wiki/synthesis.md`
- [ ] End-to-end ingest with correct claim typing and provenance
- [ ] Query with citations and dual output
- [ ] Lint with structural + conceptual checks
- [ ] 4+ sources ingested with cross-referenced pages
- [ ] Log has entries for ingests, queries, and lint
- [ ] Synthesis updated across multiple ingests
- [ ] CLAUDE.md Wiki Conventions has entries from real use
