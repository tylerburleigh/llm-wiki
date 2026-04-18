# LLM Wiki

A large language model (LLM) that builds and maintains a personal knowledge wiki from your source documents. You feed it sources — papers, articles, reports, transcripts — and it extracts the knowledge, integrates it with what's already known, and surfaces contradictions. It builds cross-references and maintains the whole thing over time. The result is a persistent, compounding knowledge base in plain markdown, browsable in Obsidian.

Based on [Karpathy's LLM Wiki gist](https://gist.github.com/karpathy/1dd0294ef9567971c1e4348a90d69285) and the 387 community comments it received.

## Why this exists

Most systems that combine LLMs with documents treat the LLM as a search engine — retrieve relevant chunks at query time, generate an answer, discard everything. The system rebuilds the knowledge from scratch on every question. Nothing accumulates.

The LLM Wiki makes a different bet: **compilation over retrieval**. When the LLM reads a source, it doesn't just index it — it extracts claims and labels each one (sourced fact, inference, unverified, gap). It integrates them with existing knowledge and builds cross-references. The synthesis has already been done. The connections are already there. The contradictions have already been flagged.

## Who it's for

The sweet spot is domains where knowledge accumulates across many sources and the connections between sources matter more than any individual source. It shines when sources overlap, contradict each other, and change over time — and when you need to explain the whole picture, not just find one fact.

**A researcher** building a knowledge base on automated scoring in education ingests 20 key papers. The wiki builds entity pages for each scoring system, concept pages for evaluation metrics and fairness criteria, and source summaries with provenance. After 10 ingests, asking "which approaches have been validated for formative vs. summative use?" draws from compiled knowledge across all sources. The wiki traces claims to their origins and surfaces contradictions.

**A product manager (PM)** doing competitive landscape research ingests product docs, analyst reports, and customer interviews. Entity pages track each competitor's capabilities and market position. As new reports come out, re-ingesting updates existing pages rather than creating disconnected notes. The synthesis page evolves into a living landscape doc.

**A software engineer (SWE)** onboarding onto a complex system ingests architecture docs, design docs, incident postmortems, and key PR descriptions. The wiki builds a map of the system that no single document contains — the kind of cross-referenced knowledge that normally lives only in senior engineers' heads.

In every case, the value is the same: the LLM handles the maintenance burden (cross-references, index updates, contradiction tracking, synthesis revision) that causes humans to abandon knowledge bases. The human directs, reviews, and asks questions. The wiki compounds.

## Why Obsidian CLI

The system is implemented as a Claude Code skill backed by the Obsidian command-line interface (CLI) and direct file I/O. This choice is deliberate:

- **Graph for free.** Wikilinks create an implicit knowledge graph. Obsidian's CLI commands (`orphans`, `deadends`, `unresolved`, `backlinks`, `links`) let the agent traverse and audit that graph without building graph infrastructure.
- **Search without a search engine.** `obsidian search` provides full-text search across the vault, delaying the need for SQLite Full-Text Search (FTS5) or vector search until real scale problems appear.
- **The human's reading environment.** The wiki isn't just for the LLM — the human browses it in Obsidian with graph view, backlinks panel, and Dataview queries. The same tool serves both the agent's maintenance work and the human's exploration.
- **Markdown stays the source of truth.** Obsidian is a thin layer over plain files. If you stop using Obsidian, the wiki is still markdown in git. No lock-in.

This aligns with the design philosophy: start with what markdown and existing tools give you for free, add infrastructure only when concrete bottlenecks demand it.

## What's here

### Source material

- **`wiki-tool/`** — Scaffolding for a new wiki: an empty Obsidian vault skeleton (`CLAUDE.md` schema, templates, empty `index.md`/`log.md`/`synthesis.md`) plus the `/wiki-ingest` Claude Code skill and its `wiki-extractor` + `wiki-auditor` subagents. This is the headline deliverable — copy or clone it to start a new wiki, then point `/wiki-ingest` at your sources.

- **`PHILOSOPHY.md`** — The principles behind the LLM Wiki design. Covers: compilation over retrieval, agent as writer (not pipeline), strict data contracts with flexible workflows, epistemic integrity via claim typing, human-as-editor-in-chief, schema co-evolution, and compounding value.

- **`CHANGELOG.md`** — Revision-by-revision log of changes to the proposal and plan during the design phase.

- **`planning/`** — Archive of the planning and analysis work that produced `wiki-tool/`. Kept for context and provenance; not needed to use the tool.
  - `llm-wiki.md` — Karpathy's original gist.
  - `comments/` — 387 individual comment files from the gist's comment thread.
  - `intermediate/` — Thematic syntheses of the comment thread (questions, implementations, discussion).
  - `synthesis/` — Higher-order analysis: `04_intermediate_synthesis.md` consolidates findings; `05_critical_synthesis.md` ranks challenges and tiers solutions.
  - `implementation-proposal.md` — The design proposal (vault structure, templates, CLAUDE.md schema, four operations).
  - `plan.md` — Five-phase implementation plan with risk register and success criteria.
  - `plan-checklist.md` — Trackable checklist version of the plan.
  - `revisions/` — Revision rounds 1-5 with rationale.
  - `obsidian-cli/` — Reference docs (`cli-reference.md`, `headless-sync.md`) collected during design.

## Reading order

To use the tool: `wiki-tool/CLAUDE.md` (+ `wiki-tool/.claude/skills/wiki-ingest/SKILL.md`).

For the design rationale: `PHILOSOPHY.md` -> `planning/implementation-proposal.md`.

For the origin and analysis: `planning/llm-wiki.md` -> `planning/intermediate/` -> `planning/synthesis/`.
