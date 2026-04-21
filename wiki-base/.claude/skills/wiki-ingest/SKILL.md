---
name: wiki-ingest
description: Ingest a source into the LLM wiki, or re-audit a past ingest. Use when the user asks to ingest a source ("ingest the source at raw/foo.pdf", "/wiki-ingest raw/foo.md", "add this paper to the wiki") or to audit a past ingest ("/wiki-ingest --audit-only <source>", "audit the Williamson ingest", "what did we miss in <source>?"). You compose six building blocks (stage, hash, precheck, extract, audit, append-audit) following the principles below. The agent decides the order; common compositions are listed. Does not commit to git; the human reviews first.
---

# wiki-ingest

You are integrating a new source into the wiki, or re-auditing a past ingest. The vault root has a `CLAUDE.md` that describes the schema; this skill describes *how to ingest*.

Three principles underlie the work:

- **Capabilities, not pipelines.** You compose building blocks based on what the source and the wiki state demand; a fixed sequence assumes every source is like every other one.
- **Epistemic integrity.** Every claim the extractor writes is typed (`[!source]`, `[!analysis]`, `[!unverified]`, `[!gap]`); promoting inference to sourced fact poisons everything built on it.
- **Human as editor-in-chief.** You propose; the human reviews and commits.

You have six building blocks. Compose them. The principles below describe *when and why* each applies; the common compositions describe the typical paths. The agent decides the order.

## Building blocks

**stage** — Ensure the source is in `raw/` and has a markdown form the extractor can read.

- If PDF: convert to markdown via `pymupdf4llm`. Store the converted `.md` alongside the original. The original PDF is the immutable artifact.
  ```bash
  python3 -c "import pymupdf4llm; open('raw/<name>.md','w').write(pymupdf4llm.to_markdown('raw/<name>.pdf'))"
  ```
- If already markdown: it should be at `raw/<name>.md`. If the user gave a path outside `raw/`, copy it in first. Never read from outside `raw/` for ingestion.
- Returns: `raw_path` (the original — PDF for PDFs, `.md` for markdown sources), `source_md_path` (the markdown form).

**hash** — Compute SHA256 of the original file and compare to any stored `raw_hash` on an existing source-summary.

```bash
shasum -a 256 <raw_path>
```

Status:

- **new** — no existing source-summary; proceed to full ingest.
- **match** — source unchanged since last ingest; skip extract, run audit against existing pages.
- **drift** — source has changed since last ingest; stop and ask the human whether to refresh affected pages or treat as a new source. Never silently overwrite.

**precheck** — Read `CLAUDE.md`, `purpose.md`, and the source end to end. If `purpose.md` is empty (placeholder only), note that — the extractor won't get research-direction steering. Search `wiki/` for entities and concepts that overlap (`obsidian search query="..." path=wiki` preferred; `grep -ri "..." wiki/` fallback). Present to the human, before any page writes:

1. **Citation** — author(s), year, title, venue.
2. **Key takeaways** — 4-8 substantive claims you'd extract.
3. **Planned new pages** — under `sources/`, `entities/`, `concepts/`, `comparisons/`. Filename in Title Case matching the wikilink; one line on what each covers.
4. **Existing pages to update** — each overlapping page and what you'd add.
5. **Potential contradictions** — source vs. wiki; internal source contradictions.

End with "Proceed?". Skip in batch mode (when the user has said "skip the pre-check from now on" or similar).

**extract** (subagent: `wiki-extractor`) — Invoke with `source_md_path`, `raw_path`, `raw_hash`, `today_iso`, `purpose_md` contents, and the approved plan (the pre-check structure, condensed). Wait for the structured report: `pages_created`, `pages_updated`, `index_entries_added`, `log_entry`, `synthesis_changed`, `surprises`, `unresolved_during_extraction`.

**audit** (subagent: `wiki-auditor`) — Invoke **independently**. Pass no extractor reasoning. The auditor reads the source fresh against the pages; that independence is the point.

Pass: `source_md_path`, `source_summary_path`, `pages_created` (paths), `pages_updated` (paths plus `what_changed` summary), `today_iso`. For audit-only, derive `pages_created` from frontmatter backlinks (see composition below).

**append-audit** — Edit the source-summary. Add or replace a `[!gap] Extraction coverage of this ingest (self-audit, <today_iso>)` callout with the auditor's findings. If a prior audit callout exists, replace it; do not stack stale audits. If the human wants history preserved, rename the prior one to `... — superseded` and append the new.

## Principles

**Stage before you read.** Sources come in many formats. The markdown form is what extract and audit read; the original is what hash fingerprints.

**Hash before you write.** Match means skip extract. Drift means stop and ask. A re-ingest that silently overwrites conflates "source updated" with "extraction refined."

**Pre-check before the human approves.** Page writes are expensive to unwind, so the pre-check is the human's only checkpoint before wiki state changes shape. Batch mode is the exception, calibrated after a history of reviewed ingests.

**Extract once, audit independently.** The auditor gets file paths and a date, nothing else. Independence is what lets the audit catch gaps the extractor would have rationalized.

**Never fix gaps inline.** The skill produces pages plus a gap callout. It does not produce fixed pages. Do not backfill missing pages, revise flagged `[!source]` claims, or edit existing pages in response to the gap list. Mixing extraction with repair obscures what was changed when, which makes root-cause analysis impossible on bad ingests. Lint fixes; subsequent ingests touching the same pages fix.

*Exception:* attribution-mismatch findings — actual misattributions (`[!source]` callouts the source doesn't support, overstated paraphrases, reconstructed figures mislabeled as `[!source]`) — surface prominently. The human decides whether to fix inline or file as known errors.

*Exception to the exception:* on a drift refresh, if the extractor is rewriting a block the prior audit flagged (scope-drift, attribution-mismatch), fix it as part of the rewrite. A block already in the edit path is the right moment to restore a missing scope qualifier or split a stitched quote. A gap "passively preserved" becomes a fresh extraction choice once the block is rewritten without addressing it.

**Don't commit, don't lint, don't chain ingests.** One source per invocation. The human reviews and commits — without the review gate, errors in one ingest propagate into the next via updated cross-references and a revised synthesis. Corrections file to the conventions files: domain-general patterns to `CLAUDE.md` "Wiki Conventions (Domain-General)", domain-specific patterns to `wiki/conventions.md`.

## Reading the invocation

The user's phrasing signals which composition applies:

- **"/wiki-ingest <path>"** or **"add this paper"** → new or unchanged source; hash decides which.
- **"/wiki-ingest --audit-only <X>"**, **"audit the X ingest"**, **"what did we miss in X?"** → audit-only.
- **Vague reference** (e.g., "the Williamson paper") → search `wiki/sources/` and confirm with the human before proceeding.

If no source path is given, ask. Do not invent.

## Common compositions

**New source.** stage → hash (new) → precheck → (human approves) → extract → (if surprises, pause and surface) → audit → append-audit → summarize.

**Unchanged source (re-ingest).** stage → hash (match) → tell the user why extract is skipped (source unchanged; re-extracting would duplicate work) → audit → append-audit → summarize.

**Drifted source.** stage → hash (drift) → stop. Ask the human: refresh affected pages (re-extract over the existing pages) or treat as a new source?

**Audit-only.** Locate the source-summary (search `wiki/sources/` on a vague reference; confirm with the user if multiple match). Verify the raw source still matches the stored `raw_hash` — a mismatch means the source has drifted; stop and recommend full re-ingest (do not audit; the gap list would conflate "we missed this" with "this didn't exist at ingest"). If the raw is a PDF, ensure the converted `.md` exists in `raw/`; regenerate via `pymupdf4llm` if missing. Find all linked pages via frontmatter:

```bash
grep -rl "\[\[<source-summary-stem>\]\]" wiki/
```

Pass that list as `pages_created` to the auditor, `pages_updated` = `[]`. The auditor doesn't care whether pages came from the original ingest or were added later. audit → append-audit → summarize.

**Extractor surprises.** Pause between extract and audit. Surface the surprises to the human (e.g., an entity already existed that the plan missed). Ask whether to proceed.

## What counts as done

A summary to the user:

- Source path and `raw_hash`.
- (Full ingest) Pages created, pages updated, index/log/synthesis updates confirmed.
- (Audit-only) Number of linked pages audited; whether this superseded a prior audit.
- Auditor's gap report inline, so the human can triage in place.
- (Full ingest) Extractor `surprises` and `unresolved_during_extraction` highlighted separately.
- A reminder to commit when ready. **Do not auto-commit.**

## Error handling

- **`pymupdf4llm` not installed.** Stop, tell the user to run `python3 -m pip install -r requirements.txt`.
- **Hash mismatch on audit-only.** Source has drifted since ingestion. Stop; recommend full re-ingest. Do not audit.
- **Attribution-mismatch anomalies.** Potential extraction errors, not extraction gaps. Surface prominently.

## What this skill does NOT do

- Commit to git. The human reviews and commits.
- Run `/wiki-lint`. Lint is a separate operation.
- Modify `CLAUDE.md`, `purpose.md`, `writing-style.md`, or anything in `raw/`.
- Bulk-ingest. One source per invocation. Long sources are split into chapters/sections by the user; each chunk is a separate invocation.
