# wiki-ingest

Use when ingesting a new source or re-auditing an existing ingest.
Compose deterministic `wiki-ops` primitives with human review,
extraction, and independent audit. Common flows are examples, not a
mandatory pipeline.

## Primitives

```bash
python3 scripts/wiki-ops.py stage-source <path>
python3 scripts/wiki-ops.py source-status <raw-path>
python3 scripts/wiki-ops.py affected-pages <source-summary>
python3 scripts/wiki-ops.py append-audit <source-summary> <audit-report-or-stdin>
python3 scripts/wiki-ops.py manifest new <raw-path>
python3 scripts/wiki-ops.py manifest show <manifest-path>
```

## Flow Examples

- New source: stage source, classify status, optionally create a
  manifest, precheck with the human, extract after approval, audit
  independently, append audit, summarize.
- Unchanged source: stage source, confirm `match`, skip extraction,
  discover affected pages, audit, append audit, summarize.
- Drifted source: stage source, confirm `drift`, discover affected
  pages for review, stop and ask whether to refresh or treat as new.
- Ambiguous source: surface claiming source-summary paths and stop for
  human resolution.
- Audit-only: resolve the source-summary, verify `source-status` is
  `match`, use `affected-pages` `knowledge_pages` as audit scope, then
  append the audit report.

## Boundaries

- Do not auto-commit.
- Do not run lint as part of ingest unless the user asks.
- Do not repair audit findings inline; route repairs to `wiki-repair`.
- Preserve the distinction between sourced claims, analysis,
  unverified claims, and gaps.
