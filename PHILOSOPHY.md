# LLM Wiki: Design Philosophy

The principles behind why the LLM Wiki is designed the way it is.

---

## The core bet: compilation over retrieval

Most systems that combine LLMs with documents treat the LLM as a search engine — retrieve relevant chunks at query time, generate an answer, discard everything. The knowledge is re-derived from scratch on every question. Nothing accumulates.

The LLM Wiki makes a different bet: that the LLM's most valuable work is **compilation**, not retrieval. When the LLM reads a source, it doesn't just index it for later — it extracts the knowledge, integrates it with what's already known, surfaces contradictions, and builds cross-references. The result is a persistent, compounding artifact. The synthesis has already been done. The connections are already there. The contradictions have already been flagged.

This is a bet that the upfront cost of compilation pays off over time through faster, richer, more reliable answers — and through the compounding value of a knowledge base that gets better with every source and every question.

---

## The agent is the writer, not a pipeline

The LLM is not executing a fixed procedure. It is a writer maintaining a knowledge base — one that exercises judgment about what a source means, how it connects to existing knowledge, what's missing, and what matters.

This means the system gives the agent **capabilities and constraints**, not step-by-step instructions. It has tools (search, graph traversal, file I/O). It has data contracts it must honor (frontmatter schemas, callout syntax, directory structure). It has principles that guide its work (track provenance, surface contradictions, distinguish facts from inferences). But how it accomplishes its goals — how it breaks down a source, what pages it creates, how it handles a contradiction, whether it asks the human or proceeds — that's the agent's judgment call.

The alternative — rigid workflows with numbered steps — produces compliance without understanding. The agent follows the checklist but doesn't think about what the source actually changes. The wiki gets pages but not insight.

---

## Strict where it matters, flexible where it doesn't

The system distinguishes between two kinds of structure:

**Data contracts are strict.** Frontmatter schemas, directory layout, callout syntax, wikilink format, index and log entry format — these are non-negotiable specifications. They exist because other things depend on them: Dataview queries, grep-based searches, Obsidian's graph view, backlink resolution, programmatic indexing, CLI search filters, unix tool parsing. An agent that invents its own frontmatter format or puts entity pages in the wrong directory breaks every downstream tool. These specifications are the foundation the rest of the system is built on.

**Workflows are flexible.** How the agent reads a source, what it emphasizes, how many pages it creates, when it talks to the human, how it handles contradictions — these depend on the specific source, the current state of the wiki, and the domain. A data table gets different treatment than a long-form essay. A source that rewrites the wiki's thesis needs more deliberation than one that adds a minor data point. The agent adapts.

The failure mode of too much rigidity is a system that produces consistent but shallow output — every ingest follows the same ten steps regardless of whether the source warrants it. The failure mode of too much flexibility is inconsistency that breaks tooling. The design aims for the middle: reliable data infrastructure supporting flexible intellectual work.

---

## Epistemic integrity is a first-class concern

The most dangerous thing an LLM-maintained wiki can do is present an inference as a fact. Once an unsourced claim gets written into a wiki page as if it were extracted from a source, it becomes part of the knowledge base's trusted foundation. Other pages build on it. Queries cite it. The provenance is lost, and the wiki asserts something with false confidence.

Claim typing — the `[!source]` / `[!analysis]` / `[!unverified]` / `[!gap]` system — exists specifically to prevent this. It forces the agent to be explicit about the epistemic status of every claim it writes. Is this from a source? Then cite it. Is this your inference? Then label it and show your reasoning. Are you uncertain? Then say so. Is something missing? Then mark the gap rather than filling it with a plausible guess.

This is more than a formatting convention. It's a discipline that changes how the agent thinks about what it writes. And because the callout types are parseable (grep, search, lint), the system can audit its own epistemic hygiene.

---

## The human thinks; the LLM does the bookkeeping

The tedious part of maintaining a knowledge base is not the reading or the thinking — it's the maintenance. Updating cross-references when a new source arrives. Keeping summaries current. Noting when new data contradicts old claims. Maintaining consistency across dozens of pages. Rebuilding the index. Humans abandon wikis because this burden grows faster than the value.

The LLM Wiki inverts this: the LLM handles all the maintenance, and the human focuses on what humans are good at — choosing what to read, asking the right questions, directing the analysis, deciding what matters. The human is the editor-in-chief; the LLM is the writer. The human never needs to update a cross-reference, rewrite a summary, or rebuild the index. That's the agent's job.

This division works because the costs are asymmetric. For the LLM, touching 15 files in one pass is trivial. For a human, it's the thing that makes them close the app and not come back. The wiki stays maintained because the cost of maintenance is near zero.

---

## The schema co-evolves

CLAUDE.md is not a fixed configuration file. It's a living document that the agent and the human maintain together.

The initial schema is a starting point — reasonable defaults for a wiki that hasn't ingested anything yet. As the wiki grows, the agent discovers what works for this specific domain: which page types are most useful, what conventions produce good results, what patterns keep emerging, what mistakes to avoid. These discoveries get recorded in the schema so they persist across sessions.

This is the difference between "accumulated corrections" (reactive error-fixing) and "wiki conventions" (proactive pattern-building). The agent doesn't just learn what not to do — it learns what works and codifies it. Over time, the schema becomes a sophisticated guide tuned to the specific domain, the specific human's preferences, and the specific wiki's needs.

---

## Start simple, add infrastructure when earned

The system starts with markdown files, Obsidian, git, and the LLM's native capabilities. No databases, no embedding stores, no search engines, no shell scripts, no build systems.

This isn't because those things aren't useful — it's because they aren't useful yet. At 10 sources and 30 pages, the LLM reading an index file is faster and more reliable than a vector search pipeline. At 100 sources, it might not be. The design defers infrastructure decisions until concrete bottlenecks appear, because:

1. You can't predict which bottlenecks will actually matter for your domain.
2. Premature infrastructure creates maintenance burden that competes with the wiki itself.
3. The simpler system is easier to understand, debug, and evolve.

The scaling plan exists — federated indexes, hash-based staleness, search engines, SQLite FTS5 — but it's a menu of options to reach for when specific problems arise, not a roadmap to follow blindly.

---

## Everything compounds

The central design goal is that every interaction with the wiki makes it more valuable.

An ingest doesn't just add a summary — it updates entity pages, revises concept pages, strengthens or challenges the synthesis, adds cross-references, and logs what happened. A query doesn't just produce an answer — it can file the answer as a new page, fix gaps it discovers, and update stale content. A lint pass doesn't just find broken links — it identifies conceptual gaps and suggests new lines of investigation.

Even the schema compounds. Every correction, every learned convention, every workflow refinement makes the next session more effective than the last.

This is the difference between a tool and a practice. A tool produces output. A practice builds on itself. The LLM Wiki is designed as a practice — one where the investment of attention pays increasing returns over time.
