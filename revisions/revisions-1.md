# Revisions (Round 1)

Revised implementation proposal, plan, and checklist for the LLM Wiki. Changes are based on `suggestions.md` and follow-up discussion. See that file for rationale behind each change.

Key themes of this revision:
1. **Strict on data contracts, flexible on workflows.** Frontmatter schemas, callout syntax, directory layout, wikilink format, and log entry format are non-negotiable specifications that enable tooling. How the agent ingests, queries, and maintains the wiki is guided by principles, not step-by-step procedures.
2. **Restore missing pieces from the original.** log.md, synthesis workflow, generative lint, diverse query output formats.
3. **Simplify V1 infrastructure.** Drop shell scripts and hash-based provenance. The LLM performs these operations natively. Add automation later when concrete bottlenecks appear.
4. **Get to first ingest faster.** Reorganize the plan so real content is created early, not after four phases of setup.
5. **Relax CLI exclusivity.** Use Obsidian CLI for search and graph operations. Use direct file I/O for reads and writes.

---

# Part 1: Revised Implementation Proposal

---

## Design Principles

1. **Markdown is the source of truth.** No databases, no embeddings, no infrastructure beyond Obsidian and git.
2. **Strict data contracts, flexible workflows.** Frontmatter schemas, directory layout, callout syntax, wikilink format, and log/index entry format are non-negotiable — tools, scripts, and queries depend on them. How the agent plans and executes its work is guided by principles and goals, not rigid step-by-step procedures.
3. **Obsidian CLI for search and graph; direct I/O for reads and writes.** Use `obsidian search`, `obsidian backlinks`, `obsidian orphans`, `obsidian unresolved`, and similar commands for operations where the CLI adds value. Read and write markdown files directly — don't route basic file operations through the CLI.
4. **Epistemic integrity over convenience.** Every wiki claim is typed (Source, Analysis, Unverified, Gap). Provenance is tracked via source links in frontmatter. The system knows what it doesn't know.
5. **Human as editor-in-chief.** The LLM writes; the human directs, reviews, and corrects. The schema is a living document the agent co-maintains based on experience.
6. **Complexity is added only when earned.** Start with conventions and the LLM's native capabilities. Add infrastructure (scripts, search engines, databases) only when concrete failures demand it.

---

## Prerequisites

- **Obsidian 1.12.7+** with the CLI enabled (Settings > General > Command line interface)
- **Obsidian desktop app running** (required for CLI search and graph commands)
- **Claude Code** with CLAUDE.md loaded
- **Git** initialized in the vault root

---

## Vault Structure

```
vault/
  raw/                          # Layer 1: Immutable source documents
    assets/                     # Downloaded images, PDFs
    <source-files>.md           # Clipped articles, papers, notes
  wiki/                         # Layer 2: LLM-generated knowledge base
    index.md                    # Content catalog
    log.md                      # Chronological operation log
    synthesis.md                # Evolving high-level synthesis
    entities/                   # Entity pages (people, orgs, tools, etc.)
    concepts/                   # Concept pages (ideas, theories, patterns)
    sources/                    # Source summary pages (one per raw source)
    comparisons/                # Comparison and analysis pages
  templates/                    # Obsidian templates for each page type
    entity.md
    concept.md
    source-summary.md
    comparison.md
  CLAUDE.md                     # Layer 3: Schema (specifications + guidance)
```

### Why This Structure

- **`raw/`** is never modified by the LLM. It's the source of truth the human curates.
- **`wiki/`** is entirely LLM-owned. The human reads it; the LLM writes and maintains it.
- **`wiki/log.md`** is an append-only chronological record of operations. Parseable with `grep "^## \[" log.md | tail -5`.
- **`wiki/synthesis.md`** is the evolving high-level synthesis. Updated on every ingest. Readable as a standalone summary.
- **`templates/`** are Obsidian templates. The LLM uses them as starting points for new pages.
- **`CLAUDE.md`** is the schema — loaded automatically by Claude Code. It defines specifications (data contracts) and guidance (principles and goals).

---

## Specifications (Strict)

These data contracts enable programmatic parsing, CLI tooling, graph traversal, search indexing, and Dataview queries. They are non-negotiable.

### Directory Placement

| Page type | Directory |
|-----------|-----------|
| Entity | `wiki/entities/` |
| Concept | `wiki/concepts/` |
| Source summary | `wiki/sources/` |
| Comparison/analysis | `wiki/comparisons/` |

One page per entity. One source summary per raw source. The agent searches before creating to avoid duplicates.

### Frontmatter Schema

Every wiki page must have YAML frontmatter with these fields:

```yaml
---
type: entity | concept | source-summary | comparison | synthesis
sources: []          # List of wikilinks to source summary pages
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
status: current | stale
tags: []
---
```

Additional fields by page type:

- **Entity:** `entity_type: ""` (person, org, tool, place, etc.)
- **Source summary:** `raw_path: ""` (path to the raw source file)
- **Comparison:** `subjects: []` (list of wikilinks to the compared pages)

Field types must be consistent. Dates in ISO 8601. Tags as a YAML list. Sources as a list of wikilinks. Tools depend on these formats.

### TLDR Requirement

Every wiki page must have `> [!tldr]` as its first content block (immediately after frontmatter). One sentence. The index builder extracts this from a known position.

### Claim Typing

Every substantive claim uses one of four Obsidian callout types:

| Callout | Meaning | Rule |
|---------|---------|------|
| `> [!source]` | Fact directly from a source | Must include `[[source-summary]]` link. If you can't cite it, it's not Source. |
| `> [!analysis]` | Inference drawn from sourced facts | Must show reasoning. Must link to the Source claims it's derived from. |
| `> [!unverified]` | Claim without an authoritative source | Flagged for verification. Never present as fact. |
| `> [!gap]` | Explicitly missing knowledge | Never fill with a guess. Marks what the wiki doesn't know. |

The critical distinction is Source vs. Analysis. If the LLM is paraphrasing, synthesizing, or inferring — even if it feels obvious — it's Analysis, not Source. These callout names are exact — they are grep-parseable and form the basis of lint checks.

### Cross-References

All cross-references use wikilinks (`[[Page Name]]`). Not raw markdown links. The graph, backlink resolution, and orphan detection depend on this.

### Index Format

`wiki/index.md` lists every wiki page organized by category. Each entry: one wikilink and a one-line TLDR.

```markdown
## Entities

- [[Entity Name]] — One-line TLDR.

## Concepts

- [[Concept Name]] — One-line TLDR.
```

No token budget. Keep entries concise. When the index becomes unwieldy to scan, split into per-category indexes (`wiki/entities/index.md`, etc.).

### Log Format

`wiki/log.md` is append-only. Each entry uses a consistent prefix so it's parseable with simple unix tools.

```markdown
## [YYYY-MM-DD] operation | description

Brief details. What was ingested/queried/linted, what changed.
```

Operations logged: every ingest, every query that generates a wiki page, every lint pass.

---

## Templates

Each page type has a template enforcing the required structure above. Templates define the **required structural elements** (frontmatter, TLDR, callout syntax) and **default sections** (which the agent may adapt to the domain).

### Entity Template (`templates/entity.md`)

```markdown
---
type: entity
entity_type: ""
sources: []
created: "{{date}}"
updated: "{{date}}"
status: current
tags: []
---

> [!tldr]
> One-sentence summary of this entity.

## Overview

> [!source] Key facts
> Verbatim or closely paraphrased facts with `[[source]]` links.

> [!analysis] Interpretation
> Inferences drawn from sourced facts. Reasoning shown.

## Relationships

- Links to related entity and concept pages.

## Open Questions

> [!gap] What's missing
> Explicitly stated gaps in knowledge about this entity.
```

### Concept Template (`templates/concept.md`)

```markdown
---
type: concept
sources: []
created: "{{date}}"
updated: "{{date}}"
status: current
tags: []
---

> [!tldr]
> One-sentence summary of this concept.

## Definition

> [!source] Core definition
> Definition with source attribution.

## Key Claims

> [!source] Claim 1
> Sourced claim.

> [!analysis] Claim 2
> Inferred claim with reasoning.

> [!unverified] Claim 3
> Claim without authoritative source. Needs verification.

## Connections

- Links to related concepts, entities, and sources.

## Contradictions & Tensions

- Where sources disagree about this concept.

## Open Questions

> [!gap] What's missing
> Explicitly stated gaps.
```

### Source Summary Template (`templates/source-summary.md`)

```markdown
---
type: source-summary
raw_path: ""
sources: []
created: "{{date}}"
updated: "{{date}}"
status: current
tags: []
---

> [!tldr]
> One-sentence summary of this source.

## Key Takeaways

> [!source] Takeaway 1
> Direct extraction from source.

## Entities Mentioned

- Links to entity pages created or updated from this source.

## Concepts Covered

- Links to concept pages created or updated from this source.

## Notes

> [!analysis] Editorial notes
> Context, significance, or interpretation added during ingest.
```

### Comparison Template (`templates/comparison.md`)

```markdown
---
type: comparison
subjects: []
sources: []
created: "{{date}}"
updated: "{{date}}"
status: current
tags: []
---

> [!tldr]
> One-sentence summary of what's being compared and the key finding.

## Comparison

| Dimension | Subject A | Subject B |
|-----------|-----------|-----------|
|           |           |           |

## Analysis

> [!analysis] Interpretation
> What the comparison reveals, with reasoning.

## Open Questions

> [!gap] What's missing
> Gaps in the comparison.
```

### Template Flexibility

Default sections (Overview, Key Claims, Relationships, etc.) adapt to the domain. An entity page about a historical figure might need a "Timeline" section. A concept page in a cooking wiki might not need "Contradictions & Tensions." The agent may propose new page types — any new template must include the standard frontmatter fields and a TLDR callout so it integrates with the index, search, and lint systems.

---

## Operations

The three core operations. Each is described by its **goal** and **principles**, not a rigid step-by-step procedure. The agent exercises judgment about how to accomplish the goal based on the specific source, question, or wiki state.

### Ingest

**Goal:** Extract knowledge from a new source and integrate it into the wiki — creating new pages and revising existing ones so the wiki reflects everything it's been fed.

**Principles:**
- Read the source. Discuss key takeaways with the human (unless batch mode or the human signals to proceed).
- Search the wiki for existing relevant pages before creating new ones. Avoid duplicates.
- Create a source summary page in `wiki/sources/`. Create or update entity and concept pages as warranted by the source content.
- Every claim extracted from the source is typed: direct extractions are `[!source]` with a link to the source summary page. Inferences are `[!analysis]`. Claims the source makes without evidence are `[!unverified]`. Questions raised but not answered are `[!gap]`.
- Track provenance: every page created or updated records the source in its frontmatter `sources` list.
- When new information contradicts existing wiki content, surface the disagreement explicitly. Do not smooth contradictions into false coherence.
- Update `wiki/index.md` with entries for new pages and revised TLDRs for updated pages.
- Update `wiki/synthesis.md` — consider what the new source changes about the big picture.
- Append an entry to `wiki/log.md`.
- Commit via git.

**Available tools:**
```
obsidian search query="<terms>" path=wiki       # Find existing pages
obsidian search:context query="<terms>" path=wiki  # Search with surrounding context
Direct file read/write for all page creation and editing
```

### Query

**Goal:** Answer a question using the wiki's accumulated knowledge. Cite sources. Distinguish what the wiki says from what the LLM infers. Optionally file valuable answers back into the wiki so insights compound.

**Principles:**
- Read `wiki/index.md` to identify candidate pages. Search for specifics with `obsidian search`.
- Read relevant pages. Follow links via backlinks and outgoing links to discover related content.
- Synthesize an answer with citations to specific wiki pages. Distinguish sourced claims from inferences.
- If the answer is valuable (a comparison, a synthesis, a connection), consider filing it as a new page in the appropriate wiki directory. This is how explorations compound.
- If the query reveals gaps, stale content, or missing connections — update affected wiki pages as a side effect (dual output).
- Answers can take different forms depending on the question: a markdown page (default), a comparison table, a Marp slide deck, or other formats as appropriate. The agent chooses the format that best serves the question.
- If a new page is created or existing pages are updated, update the index and append to the log.

**Available tools:**
```
obsidian search query="<terms>" path=wiki
obsidian search:context query="<terms>" path=wiki
obsidian backlinks file="<page>"
obsidian links file="<page>"
Direct file read for all page access
```

### Lint

**Goal:** Health-check the wiki. Find structural problems and conceptual gaps. Report findings; apply fixes only with human approval.

**Principles — structural checks:**
- Find orphan pages (no incoming links): `obsidian orphans`
- Find dead-end pages (no outgoing links): `obsidian deadends`
- Find unresolved links (wikilinks pointing to non-existent pages): `obsidian unresolved`
- Scan for `[!unverified]` claims — assess whether any can now be verified or should be removed.
- Scan for `[!gap]` claims — assess whether new sources or existing wiki content could fill them.
- Check whether `wiki/index.md` is consistent with actual wiki pages.

**Principles — conceptual review:**
- Review `wiki/synthesis.md` and several hub pages. Identify: topics that are thinly covered, questions the wiki raises but doesn't answer, connections between entities/concepts that aren't yet linked, domains where a web search could fill gaps.
- Present these as "Suggested Investigations" — new questions to explore, new sources to look for.
- This is what makes lint a knowledge-building operation, not just janitorial.

**Report format:** Summary organized by category (orphans, dead ends, unresolved links, unverified claims, gaps, conceptual suggestions). Recommended actions listed. No fixes applied without human approval.

**Available tools:**
```
obsidian orphans
obsidian deadends
obsidian unresolved
obsidian search:context query="[!unverified]" path=wiki
obsidian search:context query="[!gap]" path=wiki
obsidian backlinks file="<page>"
Direct file read for page content
```

---

## The Skill File (CLAUDE.md)

The schema document loaded by Claude Code. Organized into two clearly separated sections: specifications (strict data contracts) and guidance (principles and goals).

```markdown
# LLM Wiki Schema

You maintain a personal knowledge wiki in this Obsidian vault.

## Your Role

You are the writer. The human is the editor-in-chief. You propose changes;
the human directs, reviews, and corrects.

You co-maintain this schema. When you learn something about the domain,
discover a better pattern, or receive a correction — update the
"Wiki Conventions" section at the bottom of this file.

## Specifications (Strict)

These data contracts enable tooling. Do not deviate from them.

### Vault Layout

- `raw/` — Immutable source documents. Read from here, never write.
- `wiki/` — Your knowledge base. You own this directory entirely.
  - `wiki/index.md` — Content catalog. Update on every ingest.
  - `wiki/log.md` — Chronological operation log. Append on every operation.
  - `wiki/synthesis.md` — Evolving high-level synthesis. Revise on every ingest.
  - `wiki/entities/` — Entity pages (people, orgs, tools, places).
  - `wiki/concepts/` — Concept pages (ideas, theories, patterns).
  - `wiki/sources/` — Source summary pages (one per raw source).
  - `wiki/comparisons/` — Analysis and comparison pages.
- `templates/` — Page templates. Use as starting points for new pages.

### Frontmatter (Required on Every Wiki Page)

type: entity | concept | source-summary | comparison | synthesis
sources: []          # Wikilinks to source summary pages
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
status: current | stale
tags: []

Additional by type:
- entity: entity_type (string)
- source-summary: raw_path (string)
- comparison: subjects (list of wikilinks)

### TLDR (Required)

Every wiki page: `> [!tldr]` as the first content block after frontmatter.
One sentence. The index extracts this.

### Claim Typing (Required)

- `> [!source]` — Fact from a source. MUST include `[[source]]` link.
- `> [!analysis]` — Your inference. MUST show reasoning.
- `> [!unverified]` — No authoritative source. Flagged for verification.
- `> [!gap]` — Explicitly missing. NEVER fill with a guess.

If you are paraphrasing, synthesizing, or inferring — even if it seems
obvious — use `[!analysis]`, not `[!source]`.

### Cross-References

All cross-references use wikilinks: `[[Page Name]]`.
Not markdown links. The graph depends on this.

### Index Format

`wiki/index.md`: one wikilink + one-line TLDR per page, organized by
category (Entities, Concepts, Sources, Comparisons). Keep entries concise.
When the index becomes unwieldy, split into per-category indexes.

### Log Format

`wiki/log.md`: append-only. Each entry:
`## [YYYY-MM-DD] operation | description`
Log every ingest, every query that generates a page, every lint pass.

### Other Conventions

- Tags in frontmatter, not inline.
- Dates in ISO 8601.
- One page per entity. Search before creating to avoid duplicates.
- When sources disagree, surface the disagreement explicitly.
- Prefer targeted updates over full page rewrites.

## Guidance (Flexible)

These describe goals and principles. Use judgment about how to achieve them.

### Ingest

Your goal is to extract knowledge from a source and integrate it into the
wiki. Read the source, discuss what matters with the human, then update
the wiki — creating new pages and revising existing ones as needed.
Track provenance. Surface contradictions. Update the index, synthesis,
and log when done. Commit via git.

### Query

Your goal is to answer questions using the wiki's accumulated knowledge.
Search the index and wiki, read relevant pages, follow links. Cite
specific pages. Distinguish sourced claims from your inferences. If the
answer is valuable, file it as a new page. If you find gaps or stale
content, update affected pages.

Answers can take different forms: markdown page, comparison table,
Marp slide deck, or other formats as appropriate.

### Lint

Your goal is to health-check the wiki — both structurally and
conceptually. Check for orphans, dead ends, unresolved links, unverified
claims, and gaps. Also step back and ask: what's missing from this wiki's
understanding? What questions should be investigated? What sources would
fill the gaps? Report findings. Apply fixes only with human approval.

### Synthesis

`wiki/synthesis.md` is your evolving thesis — a standalone summary of
everything the wiki knows. Revise it on every ingest. Keep it readable
and under ~1,000 words. It should reflect the current state of the wiki's
knowledge, not just the latest source.

## Wiki Conventions

<!-- Maintained by the agent. Add learned patterns, domain-specific
     conventions, corrections from the human, and workflow refinements.
     Format: date, convention, context. -->
```

---

## Scaling Plan

The design above works at personal scale (~100 sources, hundreds of pages) with no infrastructure beyond Obsidian, git, and the LLM's native capabilities. When concrete bottlenecks appear, add infrastructure in this order:

### When search becomes insufficient

The `obsidian search` commands provide full-text search. The index file serves as a curated entry point. If search results become noisy at scale:

1. **Per-category indexes.** Split `wiki/index.md` into `wiki/entities/index.md`, `wiki/concepts/index.md`, etc. Read only the relevant category index per query.
2. **Tag-based navigation.** Use `obsidian tags` and `obsidian tag name=<tag>` to navigate by topic.
3. **Dedicated search engine.** Add [qmd](https://github.com/tobi/qmd) or a SQLite FTS5 index for hybrid search. Keep markdown as source of truth; treat search indexes as rebuildable caches.

### When staleness management becomes burdensome

At small scale, the LLM can check for staleness by comparing source modification dates to page `updated` dates during lint. At larger scale:

1. **Hash-based staleness.** Add a script that computes SHA-256 hashes for source files and compares against stored references. This is the hash-sources.sh / check-stale.sh approach from the original proposal — deferred to when it's needed.
2. **Lazy recompilation.** Don't recompile all stale pages at once. Recompile each the next time it's accessed by a query.
3. **Diff-based ingest.** When a source is updated (not new), diff it to identify what changed. Update only affected wiki pages.

### When compilation quality becomes a concern

1. **Periodic audit.** Sample random wiki pages per lint pass. Read the page and its cited sources. Check whether claims are actually supported.
2. **Wiki + RAG verification.** When answering a query, verify the wiki's answer against raw sources directly (not just wiki pages).

---

## What This Proposal Deliberately Excludes

- **Multi-model verification.** 4x cost for marginal accuracy at personal scale.
- **Cryptographic receipts.** Solving a problem personal wikis don't have.
- **Formal ontologies.** OWL-RL and SPARQL add a second knowledge management problem.
- **Multi-agent coordination.** Unproven at single-agent scale.
- **Knowledge graph databases.** Wikilinks are an implicit graph. Making it explicit adds infrastructure without clear benefit at personal scale.
- **Autonomous operation.** No cron-based maintenance. Errors compound without human review.
- **Shell scripts in V1.** The LLM performs hash computation, index building, and staleness checking natively. Scripts are added when automation is needed at scale.

---

## Deliverables

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Skill file / schema (specifications + guidance) |
| `templates/entity.md` | Template for entity pages |
| `templates/concept.md` | Template for concept pages |
| `templates/source-summary.md` | Template for source summary pages |
| `templates/comparison.md` | Template for comparison/analysis pages |
| `wiki/index.md` | Content catalog (scaffold) |
| `wiki/log.md` | Chronological operation log (scaffold) |
| `wiki/synthesis.md` | Evolving high-level synthesis (scaffold) |

Total: 1 skill file, 4 templates, 3 wiki scaffolds. No external dependencies beyond Obsidian, git, and standard Unix tools.

---
---

# Part 2: Revised Plan

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

**Goal:** Create the directory structure, templates, wiki scaffolds, and a minimal CLAUDE.md. Everything needed to do a first ingest.

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
updated: ""
status: current
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

Verify:
- Index consulted, search used, relevant pages read
- Links followed (backlinks/outgoing)
- Answer cites specific wiki pages
- Sourced claims distinguished from inferences
- Dual output: wiki pages updated as side effect if applicable
- Log entry appended if a new page was created

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

---

## Phase 4: Iteration & Refinement

**Goal:** Stress-test with more sources. Build real cross-references. Refine the schema.

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

---
---

# Part 3: Revised Checklist

---

## Phase 0: Prerequisites & Environment

- [ ] **0.1** Obsidian 1.12.7+ installed, CLI enabled, `obsidian version` works
- [ ] **0.2** `git --version` works
- [ ] **0.3** Vault created or chosen, open in Obsidian desktop app
- [ ] **0.4** Obsidian settings configured:
  - [ ] Default note location -> `wiki/`
  - [ ] Attachment folder -> `raw/assets/`
  - [ ] Template folder -> `templates/`
  - [ ] Templates core plugin enabled
- [ ] **0.5** Git initialized with `.gitignore`

---

## Phase 1: Minimal Setup

- [ ] **1.1** Directories created: `raw/assets/`, `wiki/entities/`, `wiki/concepts/`, `wiki/sources/`, `wiki/comparisons/`, `templates/`
- [ ] **1.2** Wiki scaffolds created:
  - [ ] `wiki/index.md` (category headers)
  - [ ] `wiki/log.md` (empty scaffold)
  - [ ] `wiki/synthesis.md` (frontmatter + TLDR + placeholder)
- [ ] **1.3** Templates written:
  - [ ] `templates/entity.md`
  - [ ] `templates/concept.md`
  - [ ] `templates/source-summary.md`
  - [ ] `templates/comparison.md`
- [ ] **1.4** CLI template creation tested:
  - [ ] `obsidian create ... template=entity` works (or fallback documented)
  - [ ] Frontmatter intact, `{{date}}` resolved
  - [ ] Test page cleaned up
- [ ] **1.5** `CLAUDE.md` written:
  - [ ] Specifications section (vault layout, frontmatter, TLDR, claim typing, cross-refs, index format, log format, conventions)
  - [ ] Guidance section (ingest, query, lint, synthesis)
  - [ ] Wiki Conventions section (empty)
  - [ ] CLI commands adjusted based on 1.4 findings
- [ ] **1.6** Committed to git

---

## Phase 2: First Ingest

- [ ] **2.1** Real source added to `raw/`
- [ ] **2.2** Ingest run via Claude Code
- [ ] **2.3** Results verified:
  - [ ] Source summary page in `wiki/sources/` with correct frontmatter and TLDR
  - [ ] Entity pages in `wiki/entities/` (no duplicates)
  - [ ] Concept pages in `wiki/concepts/` (no duplicates)
  - [ ] All claims properly typed (source callouts have links, analysis shows reasoning)
  - [ ] `wiki/index.md` updated
  - [ ] `wiki/log.md` entry appended
  - [ ] `wiki/synthesis.md` updated
- [ ] **2.4** Issues recorded in CLAUDE.md Wiki Conventions
- [ ] **2.5** Committed to git

---

## Phase 3: Query & Lint Smoke Tests

- [ ] **3.1** Query tested:
  - [ ] Index consulted, search used, pages read, links followed
  - [ ] Answer cites specific wiki pages
  - [ ] Sourced claims distinguished from inferences
  - [ ] Dual output (wiki updates as side effect, if applicable)
- [ ] **3.2** Lint tested:
  - [ ] Orphans, dead ends, unresolved links checked
  - [ ] Unverified claims and gaps scanned
  - [ ] Index consistency checked
  - [ ] Conceptual review performed (suggested investigations)
  - [ ] Report presented, no fixes without approval
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
  - [ ] Re-ingest updates affected pages
  - [ ] Updated dates refreshed
- [ ] **4.3** Schema reviewed and evolved:
  - [ ] Wiki Conventions has entries from real use
  - [ ] Templates assessed for domain fitness
  - [ ] New page type added if needed
- [ ] **4.4** Committed to git

---

## Completion Criteria

- [ ] All 8 deliverables committed:
  - [ ] `CLAUDE.md`
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
