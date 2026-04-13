# Revisions (Round 5)

Changes to `implementation-proposal.md`, `plan.md`, `plan-checklist.md`, `README.md`, and `CHANGELOG.md` based on a full comparative review of all planning documents against `llm-wiki.md`, `PHILOSOPHY.md`, `intermediate/`, `synthesis/`, `obsidian-cli/`, and Rounds 1-4 revisions.

Key themes of this revision:
1. **Test what you depend on — completely.** Lint's claim scanning and query's link traversal rely on CLI commands that are never verified. Same principle as Rounds 3-4: if you depend on it, test it early and document the fallback.
2. **Correct factual claims against the CLI reference.** The search `path=` parameter IS documented; the risk register should reflect this.
3. **Fix documentation accuracy.** README missing three revision rounds; CHANGELOG miscounts PHILOSOPHY principles.
4. **Keep revisions lean.** Rationale and diffs only. Top-level files are the source of truth.

---

## Change 1: Add callout search test to Phase 1.4

**Problem:** Lint depends on searching for claim-typed callouts:
```
obsidian search:context query="[!unverified]" path=wiki
obsidian search:context query="[!gap]" path=wiki
```

The brackets and exclamation marks in `[!unverified]` are characters that may be interpreted as search operators or fail to match literally. Phase 1.4 tests template creation, graph commands, and search directory scoping -- but never tests whether callout syntax is searchable. If it isn't, lint's claim-scanning capability silently falls back to grep with no documented alternative.

PHILOSOPHY alignment: Principle 3 ("Strict where it matters") -- callout search is the mechanism that makes claim typing auditable, which is the implementation of Principle 4 ("Epistemic integrity"). Same "test before you depend" logic as the lint graph command tests (R3) and search scoping test (R4).

**Files changed:** `plan.md`, `plan-checklist.md`

**Change in `plan.md`:** Add to Phase 1.4, after the search directory scoping test:

```markdown
Test callout search:

```bash
obsidian search:context query="[!source]" path=wiki
```

If the brackets or exclamation mark prevent literal matching, try
quoting or escaping. If callout syntax isn't searchable via the CLI,
the fallback is grep: `grep -r "\[!unverified\]" wiki/`. Document the
working approach in CLAUDE.md so lint operations use the correct tool.
```

**Change in `plan-checklist.md`:** Add to Phase 1.4:

```markdown
  - [ ] Callout search tested (`[!source]` findable via search) or fallback documented
```

**Change in `plan.md` risk register:** Add a row:

```
| Callout syntax (`[!source]`, `[!gap]`) not searchable via `obsidian search` | Medium | Medium | Test in Phase 1.4. Fallback: grep or direct file scanning. Document in CLAUDE.md. |
```

**Rationale:** Claim typing is the system's core epistemic safeguard. Lint's ability to scan for `[!unverified]` and `[!gap]` claims is what makes claim typing auditable rather than aspirational. If the search tool can't find callouts, the agent needs to know upfront and use the fallback consistently.

---

## Change 2: Note search `path=` is documented in CLI reference

**Problem:** The Round 4 rationale says "The CLI reference doesn't confirm a folder-scoping parameter for search." But `obsidian-cli/cli-reference.md` explicitly documents `path=<folder>` as "limit to folder" for both `search` and `search:context`. The risk register entry ("obsidian search has no directory scoping parameter") overstates the risk. Testing is still correct -- documentation and behavior can diverge -- but the risk entry should acknowledge what the docs say.

**Files changed:** `plan.md`

**Change:** Replace the risk register entry:

```markdown
# Before
| `obsidian search` has no directory scoping parameter | Medium | Low | Test in Phase 1.4. Fallback: search full vault and filter by path prefix, or use grep. Document in CLAUDE.md. |

# After
| `obsidian search path=` doesn't filter results as documented | Low | Low | CLI reference documents `path=<folder>` for search. Test in Phase 1.4 to confirm behavior matches docs. Fallback: filter by path prefix, or use grep. |
```

**Rationale:** Accuracy. The risk is "docs don't match behavior," not "parameter doesn't exist." Lowering likelihood from Medium to Low reflects that the parameter is documented; keeping the test reflects that documentation isn't a guarantee.

---

## Change 3: Test `backlinks` and `links` commands in Phase 1.4

**Problem:** Query operations use `obsidian backlinks file="<page>"` and `obsidian links file="<page>"` to follow connections and discover related content. These commands are listed in the proposal's Available Tools sections for both Query and Lint. Neither is tested in Phase 1.4. They're simpler than graph commands (they target a single file rather than scanning the vault), but the `file=` parameter's wikilink-style resolution could behave unexpectedly with Title Case filenames containing spaces.

PHILOSOPHY alignment: Same as Changes 1 and the R3/R4 CLI tests. If you depend on it, verify it.

**Files changed:** `plan.md`, `plan-checklist.md`

**Change in `plan.md`:** Add to Phase 1.4, after the callout search test (Change 1 above):

```markdown
Test link traversal commands (used by query and lint):

```bash
obsidian backlinks file="Test Entity"
obsidian links file="Test Entity"
```

Run these against the test page created earlier (before cleanup).
Verify that `backlinks` returns files linking to the test page and
`links` returns outgoing links from it. If the `file=` parameter
doesn't resolve Title Case names with spaces, try `path=` instead.
Document the working syntax in CLAUDE.md.
```

**Change in `plan-checklist.md`:** Add to Phase 1.4:

```markdown
  - [ ] Link traversal commands tested (`backlinks`, `links`) or fallback documented
```

**Rationale:** Query's "follow links via backlinks and outgoing links to discover related content" is a core principle. If `backlinks` doesn't resolve filenames correctly, the agent falls back to grep for wikilinks -- functional but slower and less reliable. Testing with the Phase 1.4 test page (which has a Title Case name with a space) verifies the exact filename pattern the wiki will use.

---

## Change 4: Update README.md revisions section

**Problem:** The README's revisions section only mentions `revisions-1.md`:

> `revisions-1.md` -- First revision round. Key changes: specifications/guidance split...

Revisions 2, 3, and 4 exist and contain important design rationale (frontmatter compliance, data contract completions, training period formalization, CLI verification). Someone reading the README would not know these exist.

**Files changed:** `README.md`

**Change:** Replace the revisions section:

```markdown
### Revision history

- **`revisions/`** -- Records of design revisions with rationale.
  - `revisions-1.md` -- Round 1. Specifications/guidance split, log.md and synthesis.md restored, shell scripts removed, plan condensed from 9 to 5 phases, Obsidian CLI exclusivity relaxed.
  - `revisions-2.md` -- Round 2. Frontmatter compliance, claim typing for synthesis, index split threshold, dual output convention, ingestion gap acknowledged.
  - `revisions-3.md` -- Round 3. Page naming convention, lint CLI tests, source granularity guidance, bare-claims risk, page length guidance, log format H3.
  - `revisions-4.md` -- Round 4. Training period formalized, search scoping test, index entry conciseness, image handling, ingestion gap threshold strengthened. Includes philosophy check that withdrew two candidate changes.
  - `revisions-5.md` -- Round 5. Callout search test, link traversal test, risk register corrections, documentation fixes.
```

**Rationale:** Documentation accuracy. The revisions contain the "why" behind every change to the top-level files. Omitting them from the README means the most navigable entry point to the project doesn't acknowledge they exist.

---

## Change 5: Fix principle count in CHANGELOG

**Problem:** `CHANGELOG.md` (Revision 1 entry) says:

> Seven principles: compilation over retrieval, agent as writer, strict/flexible split, epistemic integrity, human as editor-in-chief, schema co-evolution, compounding value.

PHILOSOPHY.md has eight principles. The list omits "Start simple, add infrastructure when earned" -- which is arguably the principle most frequently cited in revision rationale (R1 removed shell scripts, R4 withdrew source hash tracking, the scaling plan defers all infrastructure).

**Files changed:** `CHANGELOG.md`

**Change:** Replace:

```markdown
# Before
Seven principles: compilation over retrieval, agent as writer, strict/flexible split, epistemic integrity, human as editor-in-chief, schema co-evolution, compounding value.

# After
Eight principles: compilation over retrieval, agent as writer, strict/flexible split, epistemic integrity, human as editor-in-chief, schema co-evolution, start simple, compounding value.
```

**Rationale:** Factual correction. The omitted principle is the one that justifies deferring infrastructure to the scaling plan -- the single most consequential design decision in the proposal.

---

## Summary

| # | Change | Files | Complexity |
|---|--------|-------|------------|
| 1 | Callout search test | plan, plan-checklist | One test block + one checklist item + one risk row |
| 2 | Search path= risk correction | plan | Replace one risk register row |
| 3 | Backlinks/links test | plan, plan-checklist | One test block + one checklist item |
| 4 | README revisions section | README | Replace one section |
| 5 | CHANGELOG principle count | CHANGELOG | One word + one phrase |

No architectural changes. No new deliverables. No removed features. Changes 1 and 3 are "test what you depend on" -- the same principle applied in R3 (lint graph commands) and R4 (search scoping). Change 2 corrects a factual claim against the CLI reference. Changes 4 and 5 fix documentation accuracy. All consistent with PHILOSOPHY: strict where tooling depends (1, 3), epistemic integrity even in planning documents (2, 5), and no added infrastructure or workflow changes.
