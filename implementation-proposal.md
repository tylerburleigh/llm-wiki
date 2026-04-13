# Proposal: LLM Wiki for Obsidian via Claude Code

A concrete implementation of the LLM Wiki pattern as a Claude Code skill backed by the Obsidian CLI and direct file I/O.

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
- **`wiki/log.md`** is an append-only chronological record of operations. Parseable with `grep "^### \[" log.md | tail -5`.
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

### Page Naming

Page filenames use Title Case with spaces: `Transformer Architecture.md`, linked as `[[Transformer Architecture]]`. The filename must match the wikilink text exactly — Obsidian resolves links by filename. No special characters beyond spaces and hyphens. If a page name is ambiguous, disambiguate with a parenthetical: `Mercury (Planet).md`.

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
### [YYYY-MM-DD] operation | description

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
- For long sources (books, lengthy reports), ingest chapter by chapter or section by section. Each chunk gets its own source-summary page. This produces better extraction than ingesting a full document at once.

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

### Page Naming

Page filenames use Title Case with spaces: `Transformer Architecture.md`,
linked as `[[Transformer Architecture]]`. The filename must match the
wikilink text exactly — Obsidian resolves links by filename.

No special characters beyond spaces and hyphens. If a page name is
ambiguous, disambiguate with a parenthetical: `Mercury (Planet).md`.

### Index Format

`wiki/index.md`: one wikilink + one-line TLDR per page, organized by
category (Entities, Concepts, Sources, Comparisons). Keep each entry
under ~30 words. The index must remain small enough to read in full at
the start of every query and ingest operation. When the index becomes
unwieldy, split into per-category indexes.
Rule of thumb: split when the index exceeds ~100 entries.

### Log Format

`wiki/log.md`: append-only. Each entry:
`### [YYYY-MM-DD] operation | description`
Log every ingest, every query that generates a page, every lint pass.

### Other Conventions

- Tags in frontmatter, not inline.
- Dates in ISO 8601.
- One page per entity. Search before creating to avoid duplicates.
- When sources disagree, surface the disagreement explicitly.
- Prefer targeted updates over full page rewrites.
- For source-summary pages, provenance comes from `raw_path`.
  The `sources` field is typically `[]` unless the summary draws on
  other source-summary pages (e.g., a review paper referencing
  earlier sources already in the wiki).
- Every ingest and query updates the wiki — not just answers the
  immediate question. Index, log, and synthesis updates are part of
  the deliverable, not afterthoughts.
- If a page grows past ~1,500 words, consider splitting it. An entity
  page might spawn a dedicated comparison, timeline, or sub-topic page.
  Each sub-page gets its own frontmatter, TLDR, and index entry.

## Guidance (Flexible)

These describe goals and principles. Use judgment about how to achieve them.

### Ingest

Your goal is to extract knowledge from a source and integrate it into the
wiki. Read the source, discuss what matters with the human, then update
the wiki — creating new pages and revising existing ones as needed.
Track provenance. Surface contradictions. Update the index, synthesis,
and log when done. Commit via git.

For long sources (books, lengthy reports), ingest chapter by chapter or
section by section. Each chunk gets its own source-summary page. This
produces better extraction than ingesting a full document at once.

For sources with images or diagrams: ensure attachments are stored in
`raw/assets/`. Reference images in source-summary pages using standard
Obsidian image embeds (`![[image.png]]`). When an image contains
information relevant to the wiki (a diagram, chart, or table), describe
its content in text nearby so the information is searchable and
available to future queries.

### Training Period

For the first ~10 ingests, the human should review every created and
updated page — not just spot-check. Corrections get filed to Wiki
Conventions immediately. This is what bootstraps the schema flywheel:
each correction makes the next ingest better, and the conventions
accumulate domain-specific patterns that no upfront design can
anticipate. As the Wiki Conventions section fills and corrections
become rare, the human can shift to periodic review.

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

Synthesis is analytical by nature — its `type: synthesis` signals that
all content represents your integrated understanding. Write in prose
without per-claim callout wrappers. If you reference a specific source
directly, use a `[!source]` callout for that claim. Otherwise, the page
is implicitly `[!analysis]`.

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

1. **Hash-based staleness.** Add a script that computes SHA-256 hashes for source files and compares against stored references.
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
