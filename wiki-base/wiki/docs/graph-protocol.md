---
type: meta
sources: []
created: "{{date}}"
updated: "{{date}}"
status: current
tags: []
---

> [!tldr]
> The wiki's knowledge graph: node types, edge types, and bidirectionality rules. Definitive reference for ingest, audit, and lint — what kinds of pages exist, how they connect, and which connections must reciprocate.

`CLAUDE.md` says what the rules are. This file says what the *graph* looks like — node kinds, edge kinds, and the invariants the lint pass enforces. Read it before extracting or auditing if you need to refresh on how new pages should connect to existing ones.

## Node Types

| Type | Directory | Represents | Key Frontmatter |
|------|-----------|------------|-----------------|
| `entity` | `wiki/entities/` | People, organizations, products, places, named tools, named systems | `entity_type` (string), `aliases` (list, optional) |
| `concept` | `wiki/concepts/` | Ideas, theories, patterns, frameworks, named methods | — |
| `source-summary` | `wiki/sources/` | One per ingested source | `raw_path` (string), `raw_hash` (SHA256) |
| `comparison` | `wiki/comparisons/` | Head-to-head analysis of two or more entities/concepts | `subjects` (list of wikilinks) |
| `synthesis` | `wiki/synthesis.md` (singleton) | Evolving thesis: the wiki's integrated understanding | — |
| `meta` | `wiki/` and `wiki/docs/` | Infrastructure pages (handoff, backlog, decisions, this protocol, the index, the log, conventions) | — |

`entity`, `concept`, `source-summary`, and `comparison` are *knowledge nodes* — they show up in the index, get indexed by source count, and participate in the orphan/dead-end checks. `synthesis` is the wiki's thesis page. `meta` pages are infrastructure, not knowledge — they are exempt from the index requirement and from the Title Case filename rule. They still get full frontmatter and TLDR validation.

## Edge Types

### Provenance (content → source)

Every knowledge node links to its source-summary pages. Two mechanisms must agree:

- `sources: []` in the frontmatter — list of wikilinks to source-summary pages
- `[[source]]`-style wikilinks inside every `[!source]` callout in the body

This is the "why do we believe this" edge. The lint pass enforces consistency: if the body wikilinks a source-summary page, the page's frontmatter `sources:` list must include it. The reverse is not enforced — a page may declare a source in frontmatter without citing it in any specific callout (e.g., when the source informed the page's framing without a single quotable claim).

### Reverse Provenance (source → content)

Source-summary pages link forward to the content they produced:

- `## Entities Mentioned` — wikilinks to entity pages created or updated from this source
- `## Concepts Covered` — wikilinks to concept pages created or updated from this source

This makes the question "what pages did this source produce?" a one-page lookup instead of a vault scan.

### Cross-Reference

Knowledge nodes link to each other freely via `[[Page Name]]`-style wikilinks in the body. There is no schema constraint on which kinds of nodes can link to which — an entity can link an entity, a concept can link an entity, a comparison can link both. Wikilinks are the graph; everything else is metadata.

### Comparison

Comparison pages declare their subjects in two places that must agree:

- `subjects: []` in the frontmatter — list of wikilinks
- The body table or prose, which must reference each subject

A comparison page is a hub: it exists to make a relationship between two or more pages explicit and queryable.

## Bidirectionality Rules

The lint pass enforces these:

1. **Wikilinks must resolve.** Every wikilink in a body must point at an existing page. Unresolved wikilinks are silent rot.
2. **Provenance is consistent.** If a page body wikilinks a source-summary page, the page's frontmatter `sources:` list must include the same wikilink.
3. **Index consistency.** Every knowledge node has an entry in `wiki/index.md`. Every index entry resolves to a page. Source counts in index entries match `len(sources)`. TLDRs in the index match the page's first `[!tldr]` line.
4. **Hash integrity.** Each source-summary's `raw_hash` matches the SHA256 of the file at `raw_path`. Hash drift means the source has changed since ingest — re-extract or refresh.

The lint pass *reports but does not fail* on these (judgment-dependent):

- **Orphans** — knowledge nodes with no incoming wikilinks. Sometimes legitimate (a freshly-ingested page hasn't been linked yet); sometimes a sign the page should be merged or deleted.
- **Dead ends** — knowledge nodes with no outgoing wikilinks. Usually a sign the page hasn't been integrated; review during lint.

## Special Pages

`wiki/index.md`, `wiki/log.md`, `wiki/conventions.md` are legacy plain-markdown infrastructure pages — they carry no frontmatter and are exempt from page-shape checks. Newer infrastructure pages (`handoff.md`, `backlog.md`, `decisions.md`, `wiki/docs/graph-protocol.md`) use `type: meta` with full frontmatter so they validate cleanly while staying out of the graph as knowledge nodes.

When in doubt, follow the newer pattern: give a new infrastructure page `type: meta` with frontmatter rather than adding it to the legacy SPECIAL_FILES list.

## Ingest Sequence

The order pages are created during an ingest. Every step depends on earlier ones; reversing any of these produces broken wikilinks or a stale synthesis.

1. **Source-summary first.** Other pages will wikilink back to it; if it doesn't exist, those links resolve to nothing.
2. **Entity pages.** Concepts often name entities ("X is the canonical implementation of Y"); writing concepts first forces the extractor to invent entity names that don't yet exist.
3. **Concept pages.** The entities they reference now exist.
4. **Comparison pages** (if any). They reference both entities and concepts, so they go last among content pages.
5. **Update existing pages** flagged in the plan. These may gain wikilinks to pages just created, which now resolve.
6. **Update `wiki/index.md`.** Add entries for new pages with one-line TLDRs and source counts.
7. **Append `wiki/log.md`.** A single entry summarizing the ingest.
8. **Update `wiki/synthesis.md`.** Revise the thesis to reflect what the new source changed.
9. **Append `wiki/handoff.md`.** Note what was worked on, what's deferred, what the next session needs to know.

## Calibration Trail

When new evidence confirms or contradicts a past `[!analysis]` callout, attach a follow-up directly below the original — do not rewrite the original:

```
> [!analysis] Original inference. (reasoning)
> **[YYYY-MM-DD update]:** Confirmed by [[New Source]].

> [!analysis] Original inference. (reasoning)
> **[YYYY-MM-DD update]:** Contradicted by [[New Source]] — the source shows X, where the analysis predicted Y.
```

The point is a track record. Over time, the wiki accumulates evidence about which kinds of inferences held up and which didn't, which the agent can use to calibrate confidence on similar inferences in the future. Rewriting the original loses that signal.
