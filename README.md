# LLM Wiki

Compile your source documents into a persistent, auditable markdown wiki maintained by an AI agent.

LLM Wiki gives Claude Code a structured place to keep papers, reports, specs, transcripts, notes, and links integrated over time. You put sources in `raw/`. The agent reads them, writes wiki pages, links related ideas, flags gaps and contradictions, and keeps the navigation surfaces current.

Everything is plain markdown. Raw sources remain the ground truth. The wiki is the maintained working map.

Based on [Andrej Karpathy's LLM Wiki gist](https://gist.github.com/karpathy/1dd0294ef9567971c1e4348a90d69285): use an LLM as a writer and maintainer, not as a stateless search box.

[Quick Start](#quick-start) · [Basic Loop](#basic-loop) · [Why Not RAG](#why-not-rag) · [Commands](#commands) · [What You Get](#what-you-get) · [Trust Model](#trust-model) · [Development](#development)

## Quick Start

Install the repo and command-line launchers:

```sh
curl -fsSL https://raw.githubusercontent.com/foundry-works/llm-wiki/main/install.sh | sh
```

Create a wiki:

```sh
llm-wiki-new ~/wikis/my-wiki --git
cd ~/wikis/my-wiki
llm-wiki-doctor .
```

Add source material and ingest it:

```sh
# Optional: PDF ingest support
python3 -m pip install -r requirements.txt

# Edit purpose.md, then add a source
cp ~/Downloads/paper.pdf raw/

# Start Claude Code and run the wiki skill
claude
/wiki-ingest raw/paper.pdf
```

The installer clones this repo to `~/.local/share/llm-wiki` and symlinks:

| Command | Target |
| --- | --- |
| `llm-wiki-new` | `scripts/new-wiki.sh` |
| `llm-wiki-doctor` | `scripts/wiki-doctor.sh` |

Override install paths with `LLM_WIKI_DIR` or `LLM_WIKI_BIN`. If you do not want to pipe the installer into a shell, clone the repo manually and run `scripts/new-wiki.sh` directly.

## Basic Loop

1. Edit `purpose.md` so the agent knows what you are trying to understand or build.
2. Put source documents in `raw/`.
3. Run `/wiki-ingest raw/<source>` from Claude Code.
4. Review `wiki/dashboard.md`, then the generated source summary, entity pages, concept pages, and synthesis updates.
5. Ask questions with `/wiki-query "<question>"`.
6. Run `/wiki-lint` or `llm-wiki-doctor .` to check structure, links, freshness, and provenance.

The loop is human-reviewed. The agent can do the upkeep, but the wiki gets better when you correct it.

## Why Not RAG?

Document chat and RAG tools answer the current prompt. LLM Wiki maintains the compiled knowledge base that future prompts should start from.

| Need | RAG or document chat | Notes app | LLM Wiki |
| --- | --- | --- | --- |
| Persistent synthesis | Re-derived per question | Human-maintained | Updated as sources are ingested |
| Cross-source contradictions | Often hidden | Human must notice | Surfaced in pages and `wiki/debates.md` |
| Provenance | Chunk citations vary by answer | Depends on author | Claims are typed and linked to source summaries |
| Reusable answers | Usually trapped in chat | Manual copy/paste | Filed into wiki pages or `wiki/queries/` |
| Maintenance burden | Low, but stateless | High | Agent-maintained, human-reviewed |
| Portability | Tool-specific | Usually portable | Plain markdown and git-friendly |

The bet is compilation over retrieval. The expensive work is not finding one quote; it is integrating new evidence into the map you will use next month.

## Commands

Run these inside Claude Code from a generated wiki.

| Command | Use it for |
| --- | --- |
| `/wiki-ingest raw/<source>` | Ingest a paper, report, transcript, note, or other source. |
| `/wiki-ingest --audit-only <source>` | Re-audit an existing ingest without extracting again. |
| `/wiki-query "<question>"` | Answer from the wiki and optionally file reusable answers. |
| `/wiki-lint` | Run deterministic validation plus conceptual health checks. |
| `/wiki-lint --briefing` | Print a compact session-start summary. |
| `/wiki-repair <scope>` | Make a narrow, source-grounded correction to existing pages. |
| `/wiki-purpose` | Review or refine the human-owned research direction. |

Useful shell commands:

| Command | Use it for |
| --- | --- |
| `llm-wiki-new <dir> [--git]` | Create a new wiki from `wiki-base/`. |
| `llm-wiki-new <dir> --into` | Add missing scaffold files to an existing directory without overwriting files. |
| `llm-wiki-doctor <dir>` | Check structure, lint status, optional tools, PDF support, and briefing output. |
| `python3 scripts/wiki-ops.py stage-source <path>` | Copy or convert a source into the ingest-ready `raw/` shape. |
| `python3 scripts/wiki-ops.py source-status <raw-path>` | Classify a raw source as new, matching, drifted, or ambiguous. |
| `python3 scripts/wiki-ops.py affected-pages <source-summary>` | List source-citing knowledge pages and meta pages for audit or refresh scope. |
| `python3 scripts/wiki-ops.py append-audit <source-summary> <audit-report-or-stdin>` | Append or replace the source-summary extraction coverage callout. |
| `python3 scripts/wiki-ops.py manifest new <raw-path>` | Create a local JSON operation manifest under `wiki/.ops/`. |
| `python3 scripts/wiki-ops.py manifest show <manifest-path>` | Print a local operation manifest without mutating it. |
| `python3 scripts/wiki-lint.py --briefing` | Print page counts, recent activity, gaps, stale hubs, hash drift, and dashboard freshness. |
| `python3 scripts/wiki-lint.py --rebuild-index` | Rebuild `wiki/index.md` from page frontmatter and TLDRs. |

## What You Get

A generated wiki starts with a set of human-readable surfaces, not just a schema.

| Path | Purpose |
| --- | --- |
| `purpose.md` | Human-owned research direction. The agent reads it but does not edit it. |
| `AGENTS.md` | Codex entrypoint; points to `CLAUDE.md` as the canonical wiki schema. |
| `raw/` | Immutable source material. |
| `wiki/dashboard.md` | Session-start front door: current answer, recent activity, gaps, debates, stale areas, and reading routes. |
| `wiki/synthesis.md` | Current integrated view across sources. |
| `wiki/index.md` | Generated catalog of entities, concepts, sources, and comparisons. |
| `wiki/debates.md` | Contradictions, source disagreements, and unresolved tensions. |
| `wiki/queries/query-hub.md` | Durable answers to recurring questions. |
| `wiki/backlog.md` | Open questions, important gaps, and unverified claims. |
| `wiki/handoff.md` | Cross-session state: what was last worked on, deferred, or blocked. |
| `wiki/decisions.md` | Structural decisions and rationale. |
| `wiki/.ops/` | Local JSON operation manifests from `wiki-ops`; ignored by git and outside the knowledge graph. |
| `wiki/entities/` | People, organizations, tools, systems, datasets, products, projects. |
| `wiki/concepts/` | Ideas, methods, metrics, mechanisms, definitions, recurring patterns. |
| `wiki/sources/` | One source summary per raw source. |
| `wiki/comparisons/` | Cross-source comparisons and trade-off analyses. |

After ingest, one source may update several pages. That is the point: the source gets connected to what the wiki already knows.

## Reading Path

Use the wiki like an iceberg:

| Layer | Start here | What it answers |
| --- | --- | --- |
| Surface | `wiki/dashboard.md` or `--briefing` | What changed? What needs attention? Where should I start? |
| Skim | `wiki/index.md`, `wiki/debates.md`, `wiki/queries/query-hub.md`, `wiki/backlog.md` | What exists? What disagrees? What questions recur? |
| Read | Entity, concept, source, comparison, and synthesis pages | What does the wiki currently believe, and why? |
| Dive | Source summaries, claim callouts, extraction audits, `raw_hash`, decisions, git history | What evidence supports this, and what changed over time? |

## Trust Model

The wiki preserves the difference between evidence, interpretation, uncertainty, and missing information.

Claims use Obsidian-style callouts:

| Callout | Meaning |
| --- | --- |
| `[!source]` | A claim stated by a cited source. Must link to a source summary. |
| `[!analysis]` | An inference by the agent. Reasoning should be shown. |
| `[!unverified]` | Useful but not yet backed by an authoritative source. |
| `[!gap]` | Explicitly missing information. Never fill with a guess. |

The deterministic linter checks:

- frontmatter shape and ISO dates
- TLDR placement
- filename rules
- wikilink resolution
- generated index consistency
- source-summary citation invariants
- raw source hash drift
- candidate bare claims outside typed callouts
- briefing signals such as stale hubs, missing extraction audits, hash drift, and dashboard freshness

## Requirements

Required:

- Claude Code
- Python 3
- A POSIX-like shell

Optional:

| Tool | What it adds |
| --- | --- |
| Obsidian | Graph view, backlinks, live wikilink navigation. |
| Obsidian CLI | Preferred graph/search interface for the agent when available. |
| `pymupdf4llm` | PDF-to-markdown ingest support. Installed from `requirements.txt`. |
| git | Reviewable history and easy rollback. |

`wiki-lint.py` runs with the Python standard library. PDF conversion is the only packaged Python dependency.

## Obsidian Support

Obsidian is optional.

The wiki is plain markdown. When Obsidian's command-line interface is available, the agent can use it for graph traversal, backlinks, link checks, and full-text search. Without it, the workflow falls back to direct file reads and text search.

If you stop using Obsidian, the wiki remains a directory of markdown files.

## Repository Layout

| Path | Description |
| --- | --- |
| `wiki-base/` | Scaffold copied by `llm-wiki-new` when creating a fresh wiki. |
| `wiki-base/AGENTS.md` | Codex-facing scaffold instructions for generated wikis. |
| `wiki-base/.agents/` | Codex-facing mirrors of the Claude Code agents and skills. |
| `scripts/new-wiki.sh` | Creates a new wiki from `wiki-base/`. |
| `scripts/wiki-doctor.sh` | Runs structure and health checks against a wiki. |
| `wiki-base/scripts/wiki-ops.py` | Deterministic source staging, status, scope, audit append, and manifest primitives copied into generated wikis. |
| `install.sh` | Installs or updates local launcher commands. |
| `plan.md` | Progressive-disclosure implementation plan. |
| `PHILOSOPHY.md` | Longer design rationale. |
| `CHANGELOG.md` | Design-phase change log. |
| `tests/` | Smoke tests and linter fixture tests. |

## Development

Run tests:

```sh
python3 -m unittest -q
```

Check a generated wiki:

```sh
llm-wiki-doctor .
python3 scripts/wiki-lint.py
python3 scripts/wiki-lint.py --briefing
```

The scaffold in `wiki-base/` intentionally contains `{{date}}` placeholders. `llm-wiki-new` substitutes them when creating a real vault, so generated wikis lint cleanly on day one.

## Design Notes

The human is editor-in-chief. The agent writes, links, audits, and maintains, but the human decides what matters and what to trust.

For deeper rationale, read `PHILOSOPHY.md`. For operational rules, read `wiki-base/CLAUDE.md` and the skill docs under `wiki-base/.claude/skills/`.
