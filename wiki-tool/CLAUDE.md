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

- `raw/` — Immutable source documents. Read from here, never write
  (except converted `.md` files derived from non-markdown sources).
- `wiki/` — Your knowledge base. You own this directory entirely.
  - `wiki/index.md` — Content catalog. Update on every ingest.
  - `wiki/log.md` — Chronological operation log. Append on every operation.
  - `wiki/synthesis.md` — Evolving high-level synthesis. Revise on every ingest.
  - `wiki/entities/` — Entity pages (people, orgs, tools, places).
  - `wiki/concepts/` — Concept pages (ideas, theories, patterns).
  - `wiki/sources/` — Source summary pages (one per raw source).
  - `wiki/comparisons/` — Analysis and comparison pages.
- `templates/` — Page templates. Use as starting points for new pages.
- `purpose.md` — Human-owned research direction. Read for context
  during ingest and query. Never modify this file.

### Frontmatter (Required on Every Wiki Page)

type: entity | concept | source-summary | comparison | synthesis
sources: []          # Wikilinks to source summary pages
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
status: current | stale
tags: []

Additional by type:
- entity: entity_type (string)
- source-summary: raw_path (string), raw_hash (string, SHA256 of raw source)
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

When multiple sources support the same claim, cite all of them:
`> [!source] Claim text. [[Source A]], [[Source B]], [[Source C]]`

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

`wiki/index.md`: one wikilink + parenthetical source count + one-line
TLDR per page, organized by category (Entities, Concepts, Sources,
Comparisons). Example: `- [[Page Name]] (3) — One-line TLDR.`
The number is the count of entries in the page's `sources: []` list.
Keep each entry under ~30 words. The index must remain small enough to read in full at
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

### Tooling Approaches

The Obsidian CLI is the preferred interface; direct file I/O (grep, file
reads, wikilink parsing) is the fallback when the CLI can't run (e.g.,
the Obsidian desktop app isn't open, or you're in a sandboxed subshell
that can't reach the running app). CLI tests from Phase 1.4 confirmed
the commands below work against a running vault.

| Operation | CLI (preferred) | Direct fallback |
|-----------|-----------------|-----------------|
| Create page | `obsidian create name="..." path=<dir> template=<template-name>` | Read template file, write new page with content |
| Read page | `obsidian read path=<path>` | Direct file read |
| Full-text search | `obsidian search query="..." path=<dir>` | `grep -ri "..." wiki/` |
| Search with context | `obsidian search:context query="..." path=<dir>` | `grep -ri -C 3 "..." wiki/` |
| Callout search | `obsidian search:context query="[!source]" path=wiki` | `grep -r "\[!source\]" wiki/` |
| Backlinks | `obsidian backlinks file="<page>"` or `path=<path>` | `grep -rl "\[\[<page>\]\]" wiki/` |
| Outgoing links | `obsidian links path=<path>` | Parse wikilinks from file content |
| Orphans | `obsidian orphans` | Parse all files, diff wikilinks against filenames |
| Dead ends | `obsidian deadends` | Parse all files, find those with no outgoing wikilinks |
| Unresolved links | `obsidian unresolved` | Collect wikilinks, diff against filenames |
| Convert PDF | — | `pymupdf4llm` |
| Compute source hash | — | `shasum -a 256 <file>` |

Tested gotchas (from Phase 1.4):
- **Use `path=<dir>` to scope search, not `folder=<dir>`.** `folder=` is
  silently ignored and searches the whole vault.
- `obsidian create ... template=<name>` requires the Templates core
  plugin enabled and the template folder configured in Obsidian
  settings. The `template=` value is the template filename without
  extension (e.g., `template=entity`).
- `obsidian backlinks file="Test Entity"` works with the page name
  (no extension); `path=<full-path>` also works.
- `orphans`/`deadends` report every page on a freshly scaffolded vault
  because nothing is cross-linked yet. Expected.

If a CLI command becomes unreliable, file the replacement under
"Wiki Conventions" below so the choice persists across sessions.

## Guidance (Flexible)

These describe goals and principles. Use judgment about how to achieve them.

### Writing Style

Apply to prose on every wiki page. See `writing-style.md` for examples and
before/after pairs.

- **Funnel structure.** Each page, section, and paragraph leads with its
  conclusion. A reader skimming first sentences should get the full story.
- **Plain language, short sentences.** Prefer concrete, everyday words.
  Split sentences with more than one clause doing real work.
- **No hedging stacks.** One qualifier max ("this suggests X"), not
  "this might potentially suggest X could possibly be Y."
- **Emdashes sparingly.** At most one emdash pair per paragraph. Use
  commas, colons, or periods otherwise. Use hyphens (not emdashes or
  en-dashes) for numeric ranges (0.70-0.80).
- **Define acronyms on first use per page.** Wiki pages are read standalone.
- **Name recurring concepts.** Give compact labels on first introduction
  so later references stay short.
- **Lead in to tables and figures.** Tell the reader what to look for.
  Caption as `**Table N.** ...` / `**Figure N.** ...`.
- **Anchor thresholds to names.** "Corroboration threshold (≥ 3 cited
  sources)" not bare "≥ 3."
- **State assumptions explicitly.** Bullet them before analysis that
  rests on them.
- **Consistent numbers.** Pick a rounding convention per page. Commas in
  thousands (18,000). Spell out numbers under 10 in prose unless grouped
  with larger numbers.

For `comparisons/` and `synthesis.md`: translate findings into practical
implications ("so what"), and qualify cross-source comparisons when the
sources differ in scope or method.

### Ingest

Your goal is to extract knowledge from a source and integrate it into the
wiki. Read `purpose.md` for context on the human's research direction.
Read the source. Before writing any pages, present the human with:
(1) key takeaways, (2) planned new pages, (3) existing pages to update,
(4) potential contradictions. Proceed after approval. In batch mode or
when the human signals to proceed, skip the pre-check. Then update
the wiki — creating new pages and revising existing ones as needed.
Track provenance. Surface contradictions. Update the index, synthesis,
and log when done. Commit via git.

If the source is a PDF, convert it to markdown first using `pymupdf4llm`.
Store the converted `.md` alongside the original in `raw/`. The source
summary's `raw_path` points to the original file; ingest from the
converted markdown. The original PDF stays immutable.

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
Read `purpose.md` for context on the human's research direction.
Search the index and wiki, read relevant pages, follow links. Cite
specific pages. Distinguish sourced claims from your inferences. If the
answer is valuable, file it as a new page. If you find gaps or stale
content, update affected pages.

Answers can take different forms: markdown page, comparison table,
Marp slide deck, or other formats as appropriate.

### Lint

Your goal is to health-check the wiki — structurally, schema-wise, and
conceptually. Check for orphans, dead ends, unresolved links, unverified
claims, and gaps.

Validate schema: frontmatter completeness per `type` (core fields plus
per-type fields; ISO 8601 dates; `sources`/`tags`/`subjects` as YAML
lists of the right shape); TLDR is the first content block after
frontmatter on every page; filenames are Title Case and match wikilink
text; index consistency (every wiki page has an entry, every entry
resolves to an existing file, source counts match `len(sources)`, TLDRs
match). For each source-summary, recompute `raw_hash` against the file
at `raw_path` and flag drift. Flag prose that looks like a factual or
analytical claim but sits outside a typed callout — report as candidates,
not verdicts (`synthesis.md` is exempt).

Select 2-3 `[!source]` claims at random, preferring claims not audited
in recent lint log entries, trace them to cited sources, and verify
they are actually supported. Record the audited claim references in
the lint log entry so coverage rotates.

For the conceptual pass, name specific weak spots: thinly-sourced pages
(one cited source), pages with sourced facts but no `[!analysis]`, hub
pages (5+ backlinks) with `updated` older than 30 days, unanswered
`[!gap]` callouts, and entity/concept pairs that co-occur in sources
but aren't cross-linked. Present these as specific next steps, not
generic suggestions.

Report findings by category. Append a log entry including the audited
claim references. Apply fixes only with human approval.

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
