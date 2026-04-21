# LLM Wiki

A large language model (LLM) that builds and maintains a personal knowledge wiki from your source documents. You feed it sources (papers, articles, reports, transcripts) and it extracts the knowledge, integrates it with what's already known, and surfaces contradictions. It builds cross-references and maintains the whole thing over time. The result is a persistent, compounding knowledge base in plain markdown, browsable in any editor or in Obsidian for graph view and backlinks.

Based on [Karpathy's LLM Wiki gist](https://gist.github.com/karpathy/1dd0294ef9567971c1e4348a90d69285) and the 387 community comments it received. Karpathy's proposal: instead of pointing an LLM at a pile of documents and re-deriving the answer on every query, have the LLM *compile* your sources into a structured, cross-linked markdown wiki that sits between you and the raw corpus. Raw sources are the ground truth; the wiki is the compiled artifact; the LLM is the writer, not the search engine. This repo is an implementation of that pattern, with the hard parts filled in: a schema that stays stable across ingests, claim typing so inferences don't get laundered into facts, and a human-as-editor-in-chief workflow.

## Why this exists

**The problem.** Knowledge workers accumulate sources faster than they can integrate them. Reading a new paper, report, or spec is the cheap part. The expensive part is what comes after: noticing it contradicts something you read last month, updating the places where the old claim was cited, deciding whether to revise your view or doubt the source, keeping it all navigable six months later. Most people skip the integration step — which is also the step that produces understanding. The reading was largely wasted.

**Why existing tools don't close the gap.**

- *Retrieval-Augmented Generation (RAG) and document-aware chatbots* (NotebookLM, ChatGPT with files, Claude Projects) treat the LLM as a search engine. They retrieve chunks at query time, generate an answer, discard everything. The system re-derives knowledge on every question, never notices contradictions across sources, and produces nothing you can read without prompting it.
- *Note-taking apps* (Obsidian, Notion, Roam) give you a place to write, not a partner that writes. The maintenance burden — linking, re-summarizing, reconciling — still falls on the human. When that burden outgrows the perceived value, the wiki gets abandoned.
- *"Second brain" and personal knowledge management (PKM) methodologies* describe a discipline but don't execute it. They assume a human who can sustain the overhead of curation over years. Most can't.
- *Deep-research assistants* (OpenAI Deep Research, Perplexity) produce a report for a single question and stop. Nothing accumulates between sessions.

**The bet: compilation over retrieval.** The LLM's most valuable work on a corpus isn't searching it — it's *compiling* it. When the LLM reads a source, it extracts claims and labels each one (sourced fact, inference, unverified, gap), integrates them with existing knowledge, updates cross-references, and surfaces contradictions. The synthesis has already been done. The connections are already there. The contradictions have already been flagged. The human reads a compiled wiki instead of interrogating an opaque model.

The human keeps the judgment calls — what to read, what matters, what to believe. The LLM absorbs the bookkeeping that causes humans to quit.

## Who it's for

The sweet spot is domains where knowledge accumulates across many sources and the connections between sources matter more than any individual source. It shines when sources overlap, contradict each other, and change over time — and when you need to explain the whole picture, not just find one fact.

**A researcher** studying automated scoring in education has 20 papers spanning scoring systems, datasets, and fairness metrics that don't agree on definitions. By paper 10, they can no longer remember which system was validated on which dataset, or which "fairness" the last author meant. The wiki builds entity pages per scoring system, concept pages per metric, and source summaries with provenance. Asking "which approaches have been validated for formative vs. summative use?" draws from compiled knowledge across every source — each claim traceable to its origin, contradictions surfaced rather than averaged away.

**A product manager (PM)** doing competitive landscape research has stacks of analyst reports, product docs, and customer interviews that disagree about who does what. Entity pages track each competitor's capabilities and positioning; when a new report lands, re-ingesting updates the existing pages rather than spawning another disconnected note. The synthesis page becomes the landscape doc the team actually reads before the next planning cycle — and it's still accurate next quarter, because the wiki updated when the inputs did.

**A software engineer (SWE)** onboarding onto a complex system faces architecture docs, design docs, incident postmortems, and PR descriptions, each correct in isolation and none telling the whole story. The wiki builds a cross-referenced map of the system that no single document contains — the kind of knowledge that normally lives only in senior engineers' heads. When next quarter's redesign ships, the wiki absorbs the new design docs instead of going stale.

In every case, the value is the same: the LLM handles the maintenance burden (cross-references, index updates, contradiction tracking, synthesis revision) that causes humans to abandon knowledge bases. The human directs, reviews, and asks questions. The wiki compounds.

## Why Obsidian CLI (preferred, not required)

The LLM Wiki is a Claude Code skill that reads and writes plain markdown. When Obsidian's command-line interface (CLI) is available, the agent prefers it; otherwise it falls back to grep and direct file I/O. Every operation in the schema has a fallback defined, so a vault with no Obsidian installed works the same way at the markdown level.

The CLI is worth preferring because Obsidian gives us things for free that would otherwise need infrastructure:

- **Graph for free.** Wikilinks create an implicit knowledge graph. Obsidian's CLI commands (`orphans`, `deadends`, `unresolved`, `backlinks`, `links`) let the agent traverse and audit that graph without building graph infrastructure.
- **Search without a search engine.** `obsidian search` provides full-text search across the vault, delaying the need for SQLite Full-Text Search (FTS5) or vector search until real scale problems appear.
- **The human's reading environment.** The wiki isn't just for the LLM. The human browses it in Obsidian with graph view, backlinks panel, and Dataview queries. The same tool serves both the agent's maintenance work and the human's exploration.
- **Markdown stays the source of truth.** Obsidian is a thin layer over plain files. If you stop using Obsidian, the wiki is still markdown in git. No lock-in.

This aligns with the design philosophy: start with what markdown and existing tools give you for free, add infrastructure only when concrete bottlenecks demand it.

## Getting started

Install the repo and a launcher on your `PATH`:

```sh
curl -fsSL https://raw.githubusercontent.com/foundry-works/llm-wiki/main/install.sh | sh
```

This clones the repo to `~/.local/share/llm-wiki` and symlinks `scripts/new-wiki.sh` and `scripts/wiki-doctor.sh` to `~/.local/bin/llm-wiki-new` and `~/.local/bin/llm-wiki-doctor`. Override with `LLM_WIKI_DIR` / `LLM_WIKI_BIN` if you prefer different paths. Re-run the installer to update.

Then spawn your first wiki:

```sh
llm-wiki-new ~/wikis/my-wiki --git
cd ~/wikis/my-wiki
llm-wiki-doctor .
python3 -m pip install -r requirements.txt   # optional: PDF ingest support
# edit purpose.md, drop a source into raw/, then:
claude     # and invoke: /wiki-ingest raw/<your-source>
```

If you'd rather not pipe `install.sh` into a shell, clone manually and run `scripts/new-wiki.sh` directly — the launcher is just a convenience.

`wiki-lint.py` runs on the scaffolded schema with Python's standard library. The only packaged Python dependency is `pymupdf4llm` for PDF ingest.

Obsidian is optional. The vault is plain markdown and every agent operation has a grep/file-I/O fallback; Obsidian only adds graph view, backlinks panel, and live wikilink rendering for human browsing.

## What's here

### Source material

- **`wiki-base/`** — Scaffolding for a new wiki: an empty Obsidian vault skeleton (`CLAUDE.md` schema, templates, empty `index.md`/`log.md`/`synthesis.md`), four Claude Code skills (`/wiki-ingest`, `/wiki-query`, `/wiki-purpose`, `/wiki-lint`), the `wiki-extractor` and `wiki-auditor` subagents that back ingest, `scripts/wiki-lint.py` for deterministic schema validation, and `scripts/wiki-doctor.sh` for first-run health checks. This is the headline deliverable — `llm-wiki-new` (after `install.sh`) spawns a fresh wiki from it.

- **`scripts/new-wiki.sh`** — Spawns a new wiki from `wiki-base/` into a target directory. Creates the expected subdirectories (entities, concepts, sources, comparisons, raw/assets) with `.gitkeep` files. Pass `--git` to initialize a fresh git repo for the new wiki, `--force` to overwrite an existing target. `install.sh` symlinks this as `llm-wiki-new` on your `PATH`; direct invocation is the manual-install path.

- **`scripts/wiki-doctor.sh`** — Wrapper around the scaffolded doctor check. Point it at a wiki root (or run `llm-wiki-doctor .` inside one) to verify structure, run `wiki-lint.py`, and surface optional-tooling gaps.

- **`install.sh`** — One-shot installer. Clones the repo to `~/.local/share/llm-wiki` and symlinks `scripts/new-wiki.sh` / `scripts/wiki-doctor.sh` as `llm-wiki-new` / `llm-wiki-doctor` in `~/.local/bin`. See [Getting started](#getting-started).

- **`PHILOSOPHY.md`** — The principles behind the LLM Wiki design. Covers: compilation over retrieval, agent as writer (not pipeline), strict data contracts with flexible workflows, epistemic integrity via claim typing, human-as-editor-in-chief, schema co-evolution, and compounding value.

- **`CHANGELOG.md`** — Revision-by-revision log of changes to the proposal and plan during the design phase.

## Reading order

To use the tool: [Getting started](#getting-started) -> `wiki-base/CLAUDE.md` (schema reference) -> the relevant skill docs under `wiki-base/.claude/skills/`.

For the design rationale: `PHILOSOPHY.md`.
