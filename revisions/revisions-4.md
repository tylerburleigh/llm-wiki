# Revisions (Round 4)

Changes to `implementation-proposal.md`, `plan.md`, and `plan-checklist.md` based on a full comparative review of all planning documents against `llm-wiki.md`, `PHILOSOPHY.md`, `intermediate/`, `synthesis/`, `obsidian-cli/`, and the Round 1-3 revisions.

Key themes of this revision:
1. **Formalize the human review flywheel.** Production reports and the critical synthesis converge on a training period as the mechanism that makes the schema co-evolve. The plan has the pieces (Phase 2 review, Phase 4 verification) but doesn't name the principle.
2. **Verify untested CLI assumptions.** The plan assumes `obsidian search` can filter by directory. The CLI reference doesn't confirm a folder-scoping parameter for search. Test it or document the fallback.
3. **Tighten a data contract that tooling depends on.** Index entry conciseness determines whether the index fits in Claude Code's context window. The ~100 entry split threshold from Round 2 is necessary but not sufficient -- verbose entries can exhaust context well before 100.
4. **Fill a gap in source handling guidance.** Sources with images and attachments have no documented workflow, though llm-wiki.md mentions attachment handling and the raw/assets directory exists.
5. **Set realistic expectations for the ingestion gap.** The Round 2 note acknowledges the gap but doesn't give the builder a concrete threshold for when to start trusting wiki answers.
6. **Keep revisions lean.** Rationale and diffs only. Top-level files are the source of truth.

### Philosophy check

Two candidate changes were withdrawn during review for PHILOSOPHY violations:

- **Source hash tracking** was rated Tier 1 by the critical synthesis, but adding it now violates Principle 6 ("Start simple, add infrastructure when earned"). At 4-10 sources, a human knows when a file has changed. The proposal's decision to defer to the scaling plan is the philosophically correct call.
- **Promoting diff-before-commit to Phase 2** was tempting given the ETH Zurich findings, but mandating a procedural step on every write violates Principle 2 ("Agent as writer, not pipeline") and the "flexible workflows" aspect of Principle 3. The current plan's approach -- guidance to "prefer targeted updates" + Phase 4 review question -- trusts agent judgment and lets the convention emerge from use.

Both remain correctly positioned in the existing plan (scaling plan and Phase 4.3 review question, respectively).

---

## Change 1: Formalize the training period

**Problem:** The critical synthesis (`05_critical_synthesis.md`) rates a human training period as Tier 2, and multiple production reports confirm it as the mechanism that bootstraps the schema flywheel. The plan has Phase 2 (review first ingest) and Phase 4 (verify 3-5 sources), but there's no explicit principle that the human should review *every* write during early operation. Without it, the builder may spot-check Phase 2, approve, then disengage -- missing the corrections that should feed Wiki Conventions.

PHILOSOPHY alignment: Principle 5 ("Human thinks, LLM does bookkeeping") positions the human as editor-in-chief. Principle 6 ("Schema co-evolves") says corrections get recorded so they persist. A training period is how both principles become operational. It's not infrastructure -- it's a human practice.

**Files changed:** `implementation-proposal.md` (the CLAUDE.md content within it), `plan.md`

**Change in `implementation-proposal.md`:** Add to the CLAUDE.md Guidance section, after the Ingest principles:

```markdown
### Training Period

For the first ~10 ingests, the human should review every created and
updated page -- not just spot-check. Corrections get filed to Wiki
Conventions immediately. This is what bootstraps the schema flywheel:
each correction makes the next ingest better, and the conventions
accumulate domain-specific patterns that no upfront design can
anticipate. As the Wiki Conventions section fills and corrections
become rare, the human can shift to periodic review.
```

**Change in `plan.md`:** Add a note to the Phase 2 introduction, after the existing text:

```markdown
**This is the start of the training period.** Review every page the
agent creates or updates -- not just the source summary. File
corrections to Wiki Conventions immediately. Continue this level of
review through Phase 4 (~10 ingests total). The conventions
accumulated during this period are the schema's most valuable content.
```

**Change in `plan-checklist.md`:** Add to Phase 2:

```markdown
  - [ ] Every created/updated page reviewed (not just spot-checked)
  - [ ] Corrections filed to Wiki Conventions
```

**Rationale:** The schema flywheel is the system's core compounding mechanism. Naming the training period explicitly ensures the builder understands *why* they're reviewing (to build conventions, not just to catch errors) and *when* they can reduce oversight (when corrections become rare, not after a fixed number).

---

## Change 2: Test search directory filtering in Phase 1.4

**Problem:** The plan uses `obsidian search` throughout ingest and query operations, often with the assumption that results can be scoped to a directory (e.g., searching only `wiki/entities/` to check for existing entity pages before creating one). The CLI reference (`obsidian-cli/cli-reference.md`) documents `search` with parameters `limit`, `format`, `total`, and `case` -- but no explicit `folder` or `path` parameter for scoping results. The plan's risk register notes the `folder=` vs `path=` uncertainty but doesn't test it.

PHILOSOPHY alignment: Principle 3 ("Strict where it matters") -- search scoping determines whether the agent can reliably check for duplicates, which is a core ingest requirement. This is a practical test, not added infrastructure.

**Files changed:** `plan.md`, `plan-checklist.md`

**Change in `plan.md`:** Add to Phase 1.4, after the lint graph command tests (added in Round 3):

```markdown
Test search directory scoping:

```bash
obsidian search query=test path=wiki/entities
obsidian search query=test folder=wiki/entities
```

If neither syntax filters results by directory, the fallback is:
search the full vault and filter results by path prefix in the
agent's output, or use grep directly. Document the working approach
in CLAUDE.md so the agent doesn't re-discover it each session.
```

**Change in `plan-checklist.md`:** Add to Phase 1.4:

```markdown
  - [ ] Search directory scoping tested (path= or folder=) or fallback documented
```

**Change in `plan.md` risk register:** Add a row:

```
| `obsidian search` has no directory scoping parameter | Medium | Low | Test in Phase 1.4. Fallback: search full vault and filter by path prefix, or use grep. Document in CLAUDE.md. |
```

**Rationale:** The ingest operation's "search before creating" discipline depends on being able to search within specific wiki directories. If scoping doesn't work, the agent gets vault-wide results including raw sources, templates, and scaffolds -- making duplicate detection unreliable. Testing early prevents a silent degradation of ingest quality.

---

## Change 3: Specify index entry conciseness

**Problem:** Round 2 added a ~100 entry index split threshold. But the threshold assumes entries are concise. A verbose index -- where each entry is 80+ words with multiple metadata fields -- could exhaust Claude Code's context budget at 40 entries. The spec says "one wikilink + one-line TLDR per page" but doesn't define what "one-line" means in practice. The critical synthesis's emphasis on index token budgets (L0 ~200 tokens) addresses the same concern at a different level.

PHILOSOPHY alignment: Principle 3 ("Strict where it matters, flexible where it doesn't") -- index format is a data contract. Context window management is the tooling that depends on it. A concise-enough constraint makes the ~100 entry threshold actually work.

**Files changed:** `implementation-proposal.md` (the CLAUDE.md content within it)

**Change:** In the CLAUDE.md Index Format section, replace:

```markdown
One wikilink + one-line TLDR per page, organized by category.
```

with:

```markdown
One wikilink + one-line TLDR per page, organized by category. Keep
each entry under ~30 words. The index must remain small enough to
read in full at the start of every query and ingest operation.
```

**Rationale:** 30 words is concrete enough to enforce, loose enough to adapt. At 30 words per entry and 100 entries, the full index is ~3,000 words -- comfortably within a single context read. This makes the Round 2 split threshold work as intended without requiring a separate token-counting mechanism.

---

## Change 4: Add image and attachment handling guidance

**Problem:** `llm-wiki.md` mentions Obsidian's "Attachment folder path" setting and the "Download attachments for current file" hotkey. The plan creates `raw/assets/` as a directory. But there's no guidance for how to handle sources that contain images, diagrams, or tables-as-images during ingest. The agent will encounter PDFs with figures, web articles with diagrams, and papers with charts. Without guidance, it will either ignore images (losing information) or handle them inconsistently.

PHILOSOPHY alignment: This is guidance, not a spec or infrastructure. Principle 6 ("Start simple") -- a brief note is zero-cost. Principle 2 ("Agent as writer") -- the agent benefits from a starting point without being constrained to a rigid procedure.

**Files changed:** `implementation-proposal.md` (the CLAUDE.md content within it)

**Change:** Add to the CLAUDE.md Ingest guidance section, after the source granularity guidance (added in Round 3):

```markdown
For sources with images or diagrams: ensure attachments are stored in
`raw/assets/`. Reference images in source-summary pages using standard
Obsidian image embeds (`![[image.png]]`). When an image contains
information relevant to the wiki (a diagram, chart, or table), describe
its content in text nearby so the information is searchable and
available to future queries.
```

**Rationale:** Images are a common source format that the plan doesn't address. The guidance is minimal -- store in assets, embed with Obsidian syntax, describe in text. No new infrastructure. The text-description convention ensures image content participates in search and cross-referencing, which are text-based operations.

---

## Change 5: Strengthen ingestion gap threshold

**Problem:** Round 2 added a note to Phase 4 acknowledging the ingestion gap: "A partially-built wiki can underperform no wiki at all." But the note doesn't give the builder a concrete sense of when the wiki crosses the reliability threshold. The research finding was specific: a wiki at 60% coverage performed 17% worse than a fully compiled one. Without a concrete threshold, the builder may start relying on wiki answers prematurely.

PHILOSOPHY alignment: Principle 7 ("Everything compounds") -- but compounding requires a minimum density of cross-references. Naming a concrete threshold helps the builder calibrate expectations without adding infrastructure.

**Files changed:** `plan.md`

**Change:** Replace the existing Phase 4 ingestion gap note (from Round 2) with:

```markdown
**Note:** A partially-built wiki can underperform no wiki at all --
incomplete cross-references and partial synthesis can mislead rather
than help. Until the wiki has 8-10+ sources with overlapping topics,
treat wiki answers as starting points, not authoritative. Cross-
references and synthesis only become reliable when multiple sources
cover the same entities and concepts. This phase is where the wiki
crosses that threshold.
```

**Rationale:** "8-10+ sources with overlapping topics" is a concrete-enough guideline derived from the research (the 60% coverage finding, combined with Phase 4's target of 4+ additional sources on top of Phase 2's initial ingest). It sets expectations without requiring measurement infrastructure. The key qualifier is "with overlapping topics" -- 10 sources on disjoint subjects won't cross the threshold.

---

## Change 6: Note diverse query output formats for future testing

**Problem:** The implementation-proposal says queries can produce various output formats: markdown pages, comparison tables, Marp slide decks, charts. Phase 3's query test only verifies basic wiki page creation with citations. This is correct for V1 -- testing the fundamentals first. But the capability isn't mentioned in the plan at all, which means it could be forgotten.

PHILOSOPHY alignment: No tension. This is a tracking note, not added infrastructure or a workflow change.

**Files changed:** `plan.md`

**Change:** Add a note to Phase 3.1 (Query Smoke Test), after the existing verification items:

```markdown
**Future:** Query output formats (comparison tables, Marp slides, etc.)
are supported but not tested in this phase. Exercise them once the
basic query workflow is validated.
```

**Rationale:** Keeps the Phase 3 test focused on fundamentals while ensuring the feature isn't lost. No checklist item needed -- this is a reminder, not a gate.

---

## Summary

| # | Change | Files | Complexity |
|---|--------|-------|------------|
| 1 | Training period | implementation-proposal (CLAUDE.md), plan, plan-checklist | One subsection + one note + two checklist items |
| 2 | Search directory scoping test | plan, plan-checklist | One test block + one checklist item + one risk row |
| 3 | Index entry conciseness (~30 words) | implementation-proposal (CLAUDE.md) | One sentence addition |
| 4 | Image/attachment handling | implementation-proposal (CLAUDE.md) | One paragraph |
| 5 | Ingestion gap threshold | plan | Replace one paragraph |
| 6 | Query output formats note | plan | One sentence |

No architectural changes. No new deliverables. No removed features. Change 1 formalizes a human practice that bootstraps the schema flywheel. Change 2 tests a CLI assumption that ingest quality depends on. Change 3 tightens a data contract for context window management. Change 4 fills a gap in source handling guidance. Change 5 gives the builder a concrete reliability threshold. Change 6 tracks a deferred capability. All consistent with PHILOSOPHY: human oversight for the compounding mechanism (1), test before you depend (2), strict where tooling depends (3), flexible guidance without added infrastructure (4), honest expectations for compounding (5), and no premature complexity (6).
