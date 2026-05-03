---
name: wiki-ingest
description: Ingest a source into the LLM wiki, or re-audit a past ingest. Use when the user asks to ingest a source ("ingest the source at raw/foo.pdf", "/wiki-ingest raw/foo.md", "add this paper to the wiki") or to audit a past ingest ("/wiki-ingest --audit-only <source>", "audit the Williamson ingest", "what did we miss in <source>?"). You compose wiki-ops primitives plus precheck, extraction, and audit judgment. The agent decides the order; common compositions are examples. Does not commit to git; the human reviews first.
---

# wiki-ingest

You are integrating a new source into the wiki, or re-auditing a past ingest. The vault root has a `CLAUDE.md` that describes the schema; this skill describes *how to ingest*.

Three principles underlie the work:

- **Capabilities, not pipelines.** You compose building blocks based on what the source and the wiki state demand; a fixed sequence assumes every source is like every other one.
- **Epistemic integrity.** Every claim the extractor writes is typed (`[!source]`, `[!analysis]`, `[!unverified]`, `[!gap]`); promoting inference to sourced fact poisons everything built on it.
- **Human as editor-in-chief.** You propose; the human reviews and commits.

You have deterministic primitives plus judgment-heavy blocks. Compose them. The principles below describe *when and why* each applies; the common compositions describe typical paths, not a mandatory pipeline. The agent decides the order.

## Building blocks

**stage** — Ensure the source is in `raw/` and has a markdown form the extractor can read.

Use the capability command:

```bash
python3 scripts/wiki-ops.py stage-source <path>
```

Read the JSON. It returns `raw_path` (the original artifact), `source_md_path` (the markdown form), `source_kind`, `converted`, and `warnings`. If the source is already under `raw/`, it stays there. If the user gave a markdown or PDF path outside `raw/`, the command copies it into `raw/` without deleting or modifying the original. For PDFs, it writes a converted `.md` sibling when `pymupdf4llm` is installed; if conversion support is missing, stop and surface the command error.

**status** — Classify the staged raw source before write-heavy work.

```bash
python3 scripts/wiki-ops.py source-status <raw-path>
```

Read the JSON status:

- **new** — no existing source-summary; proceed to full ingest.
- **match** — source unchanged since last ingest; skip extract, run audit against existing pages.
- **drift** — source has changed since last ingest; stop and ask the human whether to refresh affected pages or treat as a new source. Never silently overwrite.
- **ambiguous** — multiple source summaries claim the same raw path; stop and ask the human which source-summary, if any, is authoritative.

**scope** — Find pages affected by a source-summary.

```bash
python3 scripts/wiki-ops.py affected-pages <source-summary>
```

The `<source-summary>` argument may be a path, page stem, or wikilink. Use `knowledge_pages` as the audit or refresh scope. `meta_pages` are reported separately; treat them as surfaces to update after content changes, not pages the auditor should score as source extraction.

**manifest** — Preserve operation state when it helps review or handoff.

```bash
python3 scripts/wiki-ops.py manifest new <raw-path>
python3 scripts/wiki-ops.py manifest show <manifest-path>
```

Use a manifest for non-trivial ingests, drift decisions, long sessions, or handoff-prone work. It is a reviewable record under `wiki/.ops/`, not a workflow engine. If you maintain it during the session, keep fields like `precheck_summary`, `planned_pages`, `touched_pages`, `auditor_report`, and `deferred_items` factual.

**precheck** — Read `CLAUDE.md`, `purpose.md`, `wiki/dashboard.md`, `wiki/handoff.md`, and the source end to end. If `purpose.md` is empty (placeholder only), note that — the extractor won't get research-direction steering. The dashboard and handoff tell you what the current entry points and active state are; they can change which overlaps matter. Search `wiki/` for entities and concepts that overlap (`obsidian search query="..." path=wiki` preferred; `grep -ri "..." wiki/` fallback). Present to the human, before any page writes:

1. **Citation** — author(s), year, title, venue.
2. **Key takeaways** — 4-8 substantive claims you'd extract.
3. **Planned new pages** — under `sources/`, `entities/`, `concepts/`, `comparisons/`. Filename in Title Case matching the wikilink; one line on what each covers.
4. **Existing pages to update** — each overlapping page and what you'd add.
5. **Potential contradictions** — source vs. wiki; internal source contradictions.

End with "Proceed?". Skip in batch mode (when the user has said "skip the pre-check from now on" or similar).

**extract** (subagent: `wiki-extractor`) — Invoke with `source_md_path`, `raw_path`, `raw_hash`, `today_iso`, `purpose_md` contents, and the approved plan (the pre-check structure, condensed). Wait for the structured report: `pages_created`, `pages_updated`, `index_rebuilt`, `log_entry`, `synthesis_changed`, `surprises`, `unresolved_during_extraction`.

**audit** (subagent: `wiki-auditor`) — Invoke **independently**. Pass no extractor reasoning. The auditor reads the source fresh against the pages; that independence is the point.

Pass: `source_md_path`, `source_summary_path`, `pages_created` (paths), `pages_updated` (paths plus `what_changed` summary), `today_iso`. For audit-only, derive `pages_created` from `affected-pages` `knowledge_pages` (see composition below).

**append-audit** — Safely append or replace the extraction coverage callout.

```bash
python3 scripts/wiki-ops.py append-audit <source-summary> <audit-report.md>
python3 scripts/wiki-ops.py append-audit <source-summary> -
```

The command adds or replaces the `[!gap] Extraction coverage of this ingest` callout, preserves surrounding non-audit content, and updates the source-summary `updated:` date. If the human wants old audit history preserved, copy the prior audit into a separate decision or handoff note before running the command; do not stack stale extraction coverage callouts on the source-summary.

## Principles

**Stage before you read.** Sources come in many formats. The markdown form is what extract and audit read; the original is what `source-status` fingerprints.

**Classify before you write.** Match means skip extract. Drift and ambiguous matches mean stop and ask. A re-ingest that silently overwrites conflates "source updated" with "extraction refined."

**Pre-check before the human approves.** Page writes are expensive to unwind, so the pre-check is the human's only checkpoint before wiki state changes shape. Batch mode is the exception, calibrated after a history of reviewed ingests.

**Extract once, audit independently.** The auditor gets file paths and a date, nothing else. Independence is what lets the audit catch gaps the extractor would have rationalized.

**Never fix gaps inline.** The skill produces pages plus a gap callout. It does not produce fixed pages. Do not backfill missing pages, revise flagged `[!source]` claims, or edit existing pages in response to the gap list. Mixing extraction with repair obscures what was changed when, which makes root-cause analysis impossible on bad ingests. Use `/wiki-repair` for scoped corrective follow-up; use later ingests when the source itself changed.

*Exception:* attribution-mismatch findings — actual misattributions (`[!source]` callouts the source doesn't support, overstated paraphrases, reconstructed figures mislabeled as `[!source]`) — surface prominently. The human decides whether to fix them immediately via `/wiki-repair` or file them as known errors.

*Exception to the exception:* on a drift refresh, if the extractor is rewriting a block the prior audit flagged (scope-drift, attribution-mismatch), fix it as part of the rewrite. A block already in the edit path is the right moment to restore a missing scope qualifier or split a stitched quote. A gap "passively preserved" becomes a fresh extraction choice once the block is rewritten without addressing it.

**Don't commit, don't lint, don't chain ingests.** One source per invocation. The human reviews and commits — without the review gate, errors in one ingest propagate into the next via updated cross-references and a revised synthesis. Corrections file to the conventions files: domain-general patterns to `CLAUDE.md` "Wiki Conventions (Domain-General)", domain-specific patterns to `wiki/conventions.md`.

## Reading the invocation

The user's phrasing signals which composition applies:

- **"/wiki-ingest <path>"** or **"add this paper"** → new, unchanged, drifted, or ambiguous source; `source-status` decides which.
- **"/wiki-ingest --audit-only <X>"**, **"audit the X ingest"**, **"what did we miss in X?"** → audit-only.
- **Vague reference** (e.g., "the Williamson paper") → search `wiki/sources/` and confirm with the human before proceeding.

If no source path is given, ask. Do not invent.

## Common compositions

**New source.** stage-source → source-status (`new`) → optional manifest → precheck → (human approves) → extract → (if surprises, pause and surface) → audit → append-audit → summarize.

**Unchanged source (re-ingest).** stage-source → source-status (`match`) → tell the user why extract is skipped (source unchanged; re-extracting would duplicate work) → affected-pages → audit → append-audit → summarize.

**Drifted source.** stage-source → source-status (`drift`) → affected-pages for review scope → stop. Ask the human: refresh affected pages (re-extract over the existing pages) or treat as a new source?

**Ambiguous source status.** stage-source → source-status (`ambiguous`) → stop. Surface the claiming source-summary paths and ask the human which record is authoritative before extract, audit, or repair.

**Audit-only.** Locate the source-summary (search `wiki/sources/` on a vague reference; confirm with the user if multiple match). Read its `raw_path`, then run `source-status <raw_path>`. A status other than `match` means the source has drifted or the provenance record is ambiguous; stop and recommend full re-ingest or human resolution. Do not audit, because the gap list would conflate "we missed this" with "this didn't exist at ingest." If the raw is a PDF and the converted `.md` sibling is missing, run `stage-source <raw_path>` to regenerate it. Find all linked pages:

```bash
python3 scripts/wiki-ops.py affected-pages <source-summary>
```

Pass `knowledge_pages` as `pages_created` to the auditor, `pages_updated` = `[]`. The auditor doesn't care whether pages came from the original ingest or were added later. audit → append-audit → summarize.

**Extractor surprises.** Pause between extract and audit. Surface the surprises to the human (e.g., an entity already existed that the plan missed). Ask whether to proceed.

## What counts as done

A summary to the user:

- Source path and `raw_hash`.
- (Full ingest) Pages created, pages updated, index rebuild/log/synthesis updates confirmed.
- (Full ingest) Surface artifacts updated when relevant: `wiki/dashboard.md` for recent activity or priority routes, `wiki/debates.md` for disagreements, and `wiki/backlog.md` for gaps that deserve session-level triage.
- (Audit-only) Number of linked pages audited; whether this superseded a prior audit.
- Auditor's gap report inline, so the human can triage in place.
- (Full ingest) Extractor `surprises` and `unresolved_during_extraction` highlighted separately.
- A reminder to commit when ready. **Do not auto-commit.**

After the summary, append an entry to `wiki/handoff.md` capturing what
was ingested, anything left in flight (e.g., audit gaps the human will
triage later), and notes a future session needs. If the ingest forced
a non-obvious structural choice (page split, callout type chosen on a
judgment call, alias rules, scope decisions), append a one-paragraph
rationale to `wiki/decisions.md`. Skip both for trivial re-audits with
no findings.

## Error handling

- **`pymupdf4llm` not installed.** `stage-source` returns `pdf_conversion_unavailable`. Stop, tell the user to run `python3 -m pip install -r requirements.txt`.
- **Hash mismatch on audit-only.** Source has drifted since ingestion. Stop; recommend full re-ingest. Do not audit.
- **Attribution-mismatch anomalies.** Potential extraction errors, not extraction gaps. Surface prominently.

## What this skill does NOT do

- Commit to git. The human reviews and commits.
- Run `/wiki-lint`. Lint is a separate operation.
- Modify `CLAUDE.md`, `purpose.md`, `writing-style.md`, or anything in `raw/` except through `stage-source` staging/conversion.
- Bulk-ingest. One source per invocation. Long sources are split into chapters/sections by the user; each chunk is a separate invocation.
