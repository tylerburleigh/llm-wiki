# LLM Wiki

Analysis and implementation planning for an LLM-maintained personal knowledge wiki, based on [Karpathy's LLM Wiki gist](https://gist.github.com/karpathy/1dd0294ef9567971c1e4348a90d69285) and the ~387 community comments it received.

## What's here

### Source material

- **`llm-wiki.md`** — Karpathy's original gist. Describes the core pattern: an LLM incrementally builds and maintains a persistent wiki of interlinked markdown files, sitting between you and your raw source documents. Defines the three-layer architecture (raw sources, wiki, schema) and the three operations (ingest, query, lint).

- **`comments/`** — 387 individual comment files (`001.md` through `387.md`) extracted from the gist's comment thread. Each file is one comment: questions, implementations, critiques, tips, and discussion.

- **`obsidian-cli/`** — Reference documentation for the Obsidian CLI.
  - `cli-reference.md` — Full command reference for the Obsidian CLI (requires Obsidian 1.12.7+, desktop app running).
  - `headless-sync.md` — Documentation for Obsidian Headless Sync (npm package for syncing without the desktop app).

### Analysis (intermediate)

- **`intermediate/`** — Thematic syntheses of the comment thread, organized by comment type. These were the first analytical pass over the raw comments.
  - `01_questions.md` — Synthesis of questions raised in the thread, grouped by theme (error handling, scaling, structure, collaboration, comparisons to prior art, tooling).
  - `02_implementations.md` — Synthesis of 178 concrete implementations shared in the thread, grouped by architectural approach (filesystem, databases, provenance, agent skills, knowledge graphs, multi-agent, research, voice/mobile, local/offline, domain-specific).
  - `03_others.md` — Synthesis of 169 discussion comments: critiques, production experience reports, conceptual extensions, practical tips, prior art connections, and meta-discussion.

### Analysis (synthesis)

- **`synthesis/`** — Higher-order analysis that combines the intermediate syntheses into prioritized findings.
  - `04_intermediate_synthesis.md` — Consolidates questions, implementations, and discussion into a single document organized around the core pattern. Identifies gaps, opportunities, and concrete solutions for each theme (epistemic integrity, provenance, scaling, structure, human role, multi-agent, conceptual extensions).
  - `05_critical_synthesis.md` — Critical assessment of every proposed idea for plausibility, feasibility, effectiveness, and complexity. Identifies 6 core challenges ranked by severity, evaluates solutions in 3 tiers (implement first / implement when needed / defer or skip), and surfaces 3 underappreciated findings. Ends with a 4-phase priority stack.

### Design philosophy

- **`PHILOSOPHY.md`** — The principles behind the LLM Wiki design. Covers: compilation over retrieval, agent as writer (not pipeline), strict data contracts with flexible workflows, epistemic integrity via claim typing, human-as-editor-in-chief, schema co-evolution, and compounding value.

### Implementation

- **`implementation-proposal.md`** — Concrete proposal for implementing the LLM Wiki as a Claude Code skill backed by the Obsidian CLI (for search/graph) and direct file I/O (for reads/writes). Specifies: vault structure, 4 page templates with claim typing (Source/Analysis/Unverified/Gap), the full CLAUDE.md skill file with specifications/guidance split, and a scaling plan. Operations (ingest, query, lint) are described by goals and principles — the agent exercises judgment, not a fixed procedure. Deliverables: 1 skill file, 4 templates, 3 wiki scaffolds (index, log, synthesis).

- **`plan.md`** — Implementation plan in 5 phases: prerequisites, minimal setup, first ingest smoke test, query/lint smoke tests, and iteration with schema refinement. First real content appears in Phase 2. Includes a risk register and success criteria.

- **`plan-checklist.md`** — Trackable checklist version of the plan. Organized by phase, with verification steps for each deliverable.

### Revision history

- **`revisions/`** — Records of design revisions with rationale.
  - `revisions-1.md` — First revision round. Key changes: specifications/guidance split in CLAUDE.md, log.md restored, synthesis.md given operational workflow, shell scripts removed from V1, Obsidian CLI exclusivity relaxed, generative lint added, plan condensed from 9 phases to 5, token budget removed.

## Reading order

For understanding the analysis: `llm-wiki.md` -> `intermediate/` (01, 02, 03) -> `synthesis/` (04, 05)

For understanding the design: `PHILOSOPHY.md` -> `implementation-proposal.md`

For building the wiki: `implementation-proposal.md` -> `plan.md` -> `plan-checklist.md`
