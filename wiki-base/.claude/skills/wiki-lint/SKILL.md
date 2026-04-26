---
name: wiki-lint
description: Health-check the wiki's structure, provenance, and conceptual coverage. Use when the user says "/wiki-lint", "lint the wiki", "health-check the vault", "what's stale or broken?", or "audit the wiki for gaps". Runs `python3 scripts/wiki-lint.py` first, then performs the judgment-dependent lint passes described in CLAUDE.md. Does not commit to git.
---

# wiki-lint

You are auditing the health of the wiki. The vault root has a `CLAUDE.md`
that describes the schema; this skill describes the *workflow* for a lint
pass.

The point of lint is not just cleanup. It prevents structural drift from
compounding and highlights where the wiki is getting thin, stale, or
epistemically sloppy.

## When to invoke

- User says `/wiki-lint`
- User asks to audit, health-check, or clean up the wiki
- User asks what is stale, broken, thinly sourced, or unresolved
- After a batch of ingests, before a commit, or before relying on the wiki for heavy query work

Do not invoke for:

- A question that should be answered from the wiki (`/wiki-query`)
- A source that still needs ingesting (`/wiki-ingest`)
- A change to `purpose.md` (`/wiki-purpose`)

## Arguments

- No positional arguments required
- `--apply` — after presenting findings and getting explicit approval, apply the approved fixes in the same session

Do not combine discovery and apply without an intervening approval step unless the user explicitly asked for `--apply` *and* the fixes are mechanical and low-risk.

## Steps

### 1. Read context

- Read `CLAUDE.md` at the vault root, especially the Lint section and the "Wiki Conventions (Domain-General)" section.
- Read `wiki/conventions.md`.
- Read `wiki/index.md`.
- Read the tail of `wiki/log.md` to see recent ingests, queries, and prior lint passes.

### 2. Run deterministic validation first

Run:

```bash
python3 scripts/wiki-lint.py
```

Treat this as the first gate. Group the findings by category. If the script reports structural errors, lead with those; downstream conceptual review matters less if the schema is already broken.

### 3. Do the judgment-dependent passes

After the deterministic pass, perform the checks `wiki-lint.py` cannot do alone:

- **Bare-claim review.** Flag prose that looks like a factual or analytical claim but sits outside a typed callout. Report as candidates, not verdicts. `wiki/synthesis.md` is exempt; `type: meta` pages are exempt.
- **Sampled claim audit.** Select 2-3 `[!source]` claims, preferring claims not audited in recent lint log entries. Trace each claim back to the cited source-summary pages and verify support.
- **Conceptual review.** Call out:
  - thinly sourced pages (`sources:` length 1)
  - pages with `[!source]` claims but no `[!analysis]`
  - hub pages (5+ backlinks) with stale `updated` dates
  - unanswered `[!gap]` callouts that should be promoted to `wiki/backlog.md` (recurring across pages, blocking downstream work, or central to `purpose.md`)
  - entity/concept pairs that co-occur in source-summary pages but are not cross-linked
- **Backlog triage.** Read `wiki/backlog.md`. Flag rows with a `Review By` date in the past (overdue) and rows older than the `Review By` window without a status update. Surface, do not auto-resolve.
- **Handoff currency.** If `wiki/handoff.md` was last updated more than two weeks ago, note it — the wiki has been worked on without anyone updating the cross-session state. Not an error; an observation.

Name specific pages and the reason they were flagged. Avoid generic maintenance advice.

### 4. Present findings

Report findings in this order:

1. Deterministic schema / link / index findings
2. Attribution or provenance risks from sampled claim audit
3. Bare-claim candidates
4. Conceptual weak spots and stale areas

For each finding, include the file path and the minimum useful explanation. If a fix is obvious and low-risk, propose it. If a fix needs a judgment call, say what decision is required.

If there are no findings in a category, say so explicitly.

### 5. Apply only with approval

Without approval:

- Do not edit pages.
- Do append a log entry summarizing the lint pass and the audited claim references.

With approval or `--apply`:

- Apply only the approved fixes.
- Prefer mechanical, local fixes first: frontmatter corrections, link repairs, index updates, stale status flips with clear justification.
- Route source-grounded attribution or scope repairs to `/wiki-repair` unless the user explicitly asked to apply them here.
- Do not rewrite `purpose.md`, `writing-style.md`, or `raw/`.
- If a fix turns into source refresh work, stop and route that item to `/wiki-ingest`.

### 6. Close out

Summarize:

- Whether `python3 scripts/wiki-lint.py` passed
- Which claim references you audited
- Which fixes were applied vs. deferred
- Whether a log entry was appended
- Whether the wiki is safe to treat as "clean enough" for the next ingest or query

Remind the user to commit when ready. Do not auto-commit.

## Error handling

- **`python3` missing.** Stop and tell the user lint cannot run without Python 3.
- **`scripts/wiki-lint.py` missing.** Stop; the wiki scaffold is incomplete or was modified unexpectedly.
- **Validator findings are too numerous.** Prioritize by severity. Surface the highest-risk findings first instead of dumping an unranked wall of output.

## What this skill does not do

- Does not ingest new sources.
- Does not answer substantive research questions from the wiki.
- Does not modify `purpose.md`, `writing-style.md`, `CLAUDE.md`, `wiki/conventions.md`, or anything in `raw/` without explicit human approval.
- Does not commit to git.
