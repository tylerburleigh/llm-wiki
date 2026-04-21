---
name: wiki-repair
description: Make a scoped corrective edit to existing wiki pages when the problem is already known. Use when the user says "/wiki-repair ...", "fix the audit findings on X", "repair these attribution mismatches", "apply this corrective edit", or "clean up this known page issue" and the work is narrower than a re-ingest. Reads the affected pages plus the relevant source-summary/raw source when needed, applies the smallest defensible patch, updates bookkeeping, and does not commit to git.
---

# wiki-repair

You are repairing a known issue in the wiki. The vault root has a
`CLAUDE.md` that describes the schema; this skill describes the repair
workflow.

The point of repair is narrow, auditable correction. It exists so the
agent can fix known problems without re-running a whole ingest or mixing
cleanup into query work.

## When to invoke

- User says `/wiki-repair <page or source>`
- User asks to fix audit findings, attribution mismatches, scope drift,
  broken source attribution, missing qualifiers, stale status fields, or
  other known page problems
- A lint or audit pass surfaced a specific issue and the user wants it
  corrected now

Do not invoke for:

- A changed raw source that needs re-extraction (`/wiki-ingest`)
- Broad vault health-checking (`/wiki-lint`)
- Open-ended questions answered from the wiki (`/wiki-query`)
- Changes to `purpose.md` (`/wiki-purpose`)

## Repair principles

- **Smallest defensible edit.** Fix the named problem, then stop.
- **Re-ground before you edit.** If the issue is source-grounded, read
  the relevant source-summary and raw source text before changing claims.
- **Preserve epistemic typing.** Correcting a claim may mean changing a
  callout type, not just rewriting prose.
- **Keep the audit trail intact.** Update `updated:` and append a log
  entry. The human still reviews and commits.

## Steps

### 1. Read context

- Read `CLAUDE.md` and `wiki/conventions.md`.
- Read the affected page or pages.
- If the issue touches source attribution, also read the cited
  source-summary page and, when needed, the raw source in `raw/`.
- If the issue came from lint or audit, read the exact finding text
  first and restate the repair scope in one sentence.

### 2. Bound the repair

Before editing, name:

1. The files you will touch.
2. The exact problem you are fixing.
3. The reason this is a repair, not a re-ingest.

If the issue expands into "this whole source needs to be re-extracted,"
stop and route it to `/wiki-ingest`.

### 3. Patch the page

Apply the smallest change that resolves the issue:

- Fix `[!source]` / `[!analysis]` / `[!unverified]` / `[!gap]` typing
  when the current type is wrong.
- Restore missing scope qualifiers or caveats the source makes.
- Add missing source-summary wikilinks and `sources:` frontmatter
  entries when the page already relies on them.
- Repair obvious bookkeeping drift (status, updated date, index count,
  TLDR mismatch) caused by the same edit.

Do not widen the page just because you noticed adjacent opportunities.

### 4. Update bookkeeping

When the repair changes page state:

- Set `updated:` to today on every edited page.
- Update `wiki/index.md` if the TLDR, title, or source count changed.
- Append `wiki/log.md`: `### [YYYY-MM-DD] repair | <short description>`

Revise `wiki/synthesis.md` only if the corrected issue materially changes
the wiki's overall story. Most repairs should not touch synthesis.

### 5. Present the repair

Summarize:

- Which files changed
- What claim or structure was corrected
- Whether the fix was source-grounded or structural
- Whether index/log/synthesis were updated

Remind the user to review and commit when ready. Do not auto-commit.

## Error handling

- **Ambiguous target.** If multiple pages or sources could match, ask the
  user to disambiguate before editing.
- **Repair expands beyond scope.** Stop and recommend `/wiki-ingest` or
  `/wiki-lint` instead of guessing where to stop.
- **Source support is unclear.** Downgrade the claim to `[!unverified]`
  or surface the uncertainty; do not keep a shaky `[!source]`.

## What this skill does not do

- Does not re-ingest a changed source.
- Does not perform a broad health check.
- Does not modify `purpose.md`, `CLAUDE.md`, `writing-style.md`,
  `wiki/conventions.md`, or anything in `raw/`.
- Does not commit to git.
