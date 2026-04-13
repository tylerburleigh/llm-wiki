# Implementation Plan

Implements the proposal in `implementation-proposal.md`. Eight deliverable files (1 skill file, 4 templates, 3 wiki scaffolds), a vault directory structure, and a tested end-to-end workflow.

---

## Phase 0: Prerequisites & Environment

**Goal:** Confirm the toolchain works before writing anything.

### 0.1 Verify Obsidian CLI

Obsidian 1.12.7+ required. CLI enabled in Settings > General > Command line interface.

```bash
obsidian version
```

### 0.2 Verify Git

```bash
git --version
```

### 0.3 Choose or Create the Vault

Use an existing vault or create a new one via Obsidian's UI. The vault must be open in the Obsidian desktop app for CLI search/graph commands.

### 0.4 Configure Obsidian Settings

- **Settings > Files and links > Default location for new notes:** `wiki/`
- **Settings > Files and links > Attachment folder path:** `raw/assets/`
- **Settings > Templates > Template folder location:** `templates/`
- **Settings > Core plugins:** Enable Templates

### 0.5 Initialize Git

```bash
cd /path/to/vault
git init
```

Create `.gitignore`:
```
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.trash/
```

```bash
git add .gitignore
git commit -m "Initialize vault"
```

---

## Phase 1: Minimal Setup

**Goal:** Create the directory structure, templates, wiki scaffolds, and CLAUDE.md. Everything needed to do a first ingest.

**Depends on:** Phase 0

### 1.1 Create Directories

```bash
mkdir -p raw/assets
mkdir -p wiki/entities wiki/concepts wiki/sources wiki/comparisons
mkdir -p templates
```

### 1.2 Create Wiki Scaffolds

**`wiki/index.md`:**
```markdown
# Wiki Index

## Entities

## Concepts

## Sources

## Comparisons
```

**`wiki/log.md`:**
```markdown
# Wiki Log
```

**`wiki/synthesis.md`:**
```markdown
---
type: synthesis
sources: []
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
status: current
tags: []
---

> [!tldr]
> High-level synthesis of the wiki's knowledge. Updated as the wiki grows.

## Overview

*No content yet. Updated after the first few sources are ingested.*
```

### 1.3 Write Templates

Create all four templates (entity, concept, source-summary, comparison) as specified in the proposal. These define the required frontmatter fields, TLDR callout, claim-typed sections, and default structure for each page type.

### 1.4 Test Template Creation via CLI

Verify that the Obsidian CLI can create pages from templates:

```bash
obsidian create name="Test Entity" path=wiki/entities template=entity
obsidian read path="wiki/entities/Test Entity.md"
```

Verify: page created in correct directory, frontmatter intact, `{{date}}` resolved.

If `template=` doesn't work: document the working alternative (e.g., read template content, create page with content directly). This determines how CLAUDE.md references template usage.

Clean up test page.

Also verify the graph commands used by lint:

```bash
obsidian orphans
obsidian deadends
obsidian unresolved
```

If any don't work: the agent can compute these by reading the file tree and parsing wikilinks directly. Document which commands work and which need the manual fallback. This determines how CLAUDE.md references lint operations.

Test search directory scoping:

```bash
obsidian search query=test path=wiki/entities
obsidian search query=test folder=wiki/entities
```

If neither syntax filters results by directory, the fallback is: search the full vault and filter results by path prefix in the agent's output, or use grep directly. Document the working approach in CLAUDE.md so the agent doesn't re-discover it each session.

### 1.5 Write CLAUDE.md

Create `CLAUDE.md` in the vault root as specified in the proposal. Two sections: Specifications (strict data contracts) and Guidance (flexible principles). Include empty "Wiki Conventions" section.

Adjust any CLI commands based on findings from 1.4.

### 1.6 Commit

```bash
git add -A
git commit -m "Initial vault setup: structure, templates, schema"
```

---

## Phase 2: First Ingest (Smoke Test)

**Goal:** Ingest a real source end-to-end. This is the most important phase — it validates the entire system against real content and reveals what needs adjustment.

**This is the start of the training period.** Review every page the agent creates or updates — not just the source summary. File corrections to Wiki Conventions immediately. Continue this level of review through Phase 4 (~10 ingests total). The conventions accumulated during this period are the schema's most valuable content.

**Depends on:** Phase 1

### 2.1 Add a Source

Choose a real source document — a short article or paper. Copy or clip it into `raw/`.

### 2.2 Run Ingest

Open a Claude Code session in the vault directory. CLAUDE.md loads automatically.

```
Ingest the source at raw/<filename>.md
```

### 2.3 Verify Results

**Source summary:**
- Created in `wiki/sources/`?
- Frontmatter populated (raw_path, sources, created date, tags)?
- TLDR present and accurate?
- Key takeaways use `[!source]` callouts with wikilinks?

**Entity and concept pages:**
- Created in correct directories?
- No duplicates (agent searched before creating)?
- Frontmatter includes source reference?
- Claims properly typed (source vs. analysis)?

**Index:** Updated with new pages and TLDRs?

**Log:** Entry appended to `wiki/log.md`?

**Synthesis:** `wiki/synthesis.md` updated?

**Claim typing:** No bare claims outside callout blocks? Source callouts include links? Analysis callouts show reasoning?

### 2.4 Record Issues

Problems found become the first entries in the CLAUDE.md "Wiki Conventions" section. CLI command adjustments go into the Specifications section.

### 2.5 Commit

```bash
git add -A
git commit -m "First ingest: <source-name>"
```

---

## Phase 3: Query and Lint Smoke Tests

**Goal:** Validate the remaining two operations.

**Depends on:** Phase 2

### 3.1 Query Test

Ask a question that requires reading multiple wiki pages:

```
What are the main themes in the wiki so far?
```

Or a more specific question based on the ingested source.

Verify:
- Index consulted, search used, relevant pages read
- Links followed (backlinks/outgoing)
- Answer cites specific wiki pages
- Sourced claims distinguished from inferences
- Dual output: wiki pages updated as side effect if applicable
- Log entry appended if a new page was created

**Future:** Query output formats (comparison tables, Marp slides, etc.) are supported but not tested in this phase. Exercise them once the basic query workflow is validated.

### 3.2 Lint Test

```
Run a lint check on the wiki.
```

Verify:
- Structural checks ran (orphans, dead ends, unresolved links)
- Unverified claims and gaps scanned
- Index consistency checked
- Conceptual review performed (suggested investigations, not just structural findings)
- Report presented with categories and recommended actions
- No fixes applied without approval
- Log entry appended

### 3.3 Record Issues and Commit

Same pattern as Phase 2.

---

## Phase 4: Iteration & Refinement

**Goal:** Stress-test with more sources. Build real cross-references. Refine the schema.

**Note:** A partially-built wiki can underperform no wiki at all — incomplete cross-references and partial synthesis can mislead rather than help. Until the wiki has 8-10+ sources with overlapping topics, treat wiki answers as starting points, not authoritative. Cross-references and synthesis only become reliable when multiple sources cover the same entities and concepts. This phase is where the wiki crosses that threshold.

**Depends on:** Phases 2-3

### 4.1 Ingest 3-5 More Sources

Choose sources that overlap (shared entities/concepts) to test cross-referencing. Include at least one source that contradicts or updates a claim from an earlier source.

After each ingest, review:
- Cross-references created correctly?
- Existing pages updated (not duplicated)?
- Contradictions surfaced (not smoothed)?
- Index staying clean?
- Synthesis evolving meaningfully?
- Log accumulating?

### 4.2 Test Source Update (Staleness)

Modify one raw source. Tell the agent to re-ingest the updated source. Verify:
- Affected wiki pages updated
- Frontmatter `updated` dates refreshed
- Contradictions from the update surfaced

### 4.3 Review and Evolve the Schema

By this point the "Wiki Conventions" section in CLAUDE.md should have several entries. Review them:
- Are the corrections specific and useful?
- Has the agent learned patterns about the domain?
- Do the templates need adjustment for this domain?
- Is a new page type needed?
- Is "prefer targeted updates" sufficient, or should the agent show proposed diffs before committing? (More important as supervision decreases.)

Adjust CLAUDE.md, templates, or conventions as needed. This is the schema co-evolution the original describes.

### 4.4 Commit

```bash
git add -A
git commit -m "Complete initial wiki buildout (<N> sources, <M> wiki pages)"
```

---

## Dependency Graph

```
Phase 0 (Prerequisites)
  |
  v
Phase 1 (Minimal Setup: dirs, templates, CLAUDE.md, scaffolds)
  |
  v
Phase 2 (First Ingest — smoke test)
  |
  v
Phase 3 (Query + Lint — smoke tests)
  |
  v
Phase 4 (Iteration & Refinement)
```

Linear, but only 5 phases instead of 9. First real content appears in Phase 2 (second phase of actual work).

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `obsidian create ... template=` doesn't work as expected | Medium | Medium | Test in Phase 1.4. Fallback: read template, create page with content directly. |
| `obsidian search ... path=wiki` doesn't filter by path | Medium | Low | Test in Phase 1.4. Fallback: `folder=wiki` parameter or grep. |
| Obsidian desktop app not running when CLI commands execute | Low | Medium | Only affects search/graph commands. Document clearly. Direct file I/O works without the app. |
| LLM creates duplicate pages instead of updating existing ones | Medium | Medium | CLAUDE.md specifies "search before creating." Review in Phase 2. Add correction if needed. |
| LLM marks inferences as `[!source]` | Medium | High | CLAUDE.md emphasizes this distinction. Review claim typing in Phase 2. Correct aggressively. |
| Context compaction drops CLAUDE.md conventions mid-session | Medium | High | Keep CLAUDE.md concise. For long sessions, the agent can re-read it. |
| Lint graph commands (`obsidian orphans/deadends/unresolved`) don't work as expected | Medium | Medium | Test in Phase 1.4. Fallback: agent reads file tree and parses wikilinks manually. More expensive but no CLI dependency. |
| LLM writes substantive claims as regular prose (no callout) | High | High | CLAUDE.md claim typing spec emphasizes this. Review in Phase 2. If it happens, add an explicit correction to Wiki Conventions: "Every factual or analytical statement must be inside a typed callout." |
| `obsidian search` has no directory scoping parameter | Medium | Low | Test in Phase 1.4. Fallback: search full vault and filter by path prefix, or use grep. Document in CLAUDE.md. |

---

## Success Criteria

The implementation is complete when:

1. All 8 deliverable files exist and are committed to git
2. A source has been ingested end-to-end with correct claim typing and provenance
3. A query has been answered using wiki content with proper citations
4. A lint pass has run all checks (structural + conceptual) and produced a report
5. The wiki has 4+ sources ingested with cross-referenced entity and concept pages
6. `wiki/log.md` has entries for ingests, queries, and lint
7. `wiki/synthesis.md` has been updated across multiple ingests
8. CLAUDE.md "Wiki Conventions" section has entries from real use
