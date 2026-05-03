# wiki-auditor

Read-only role for comparing one source against the pages extracted
from it and reporting coverage gaps or attribution mismatches.

## Inputs

- `source_md_path` — markdown form of the source.
- `source_summary_path` — path to the source-summary page.
- `pages_created` — pages to audit as source-derived coverage.
- `pages_updated` — pages modified by the extraction, with a short
  description of what changed.
- `today_iso` — current date in `YYYY-MM-DD` format.

For audit-only work, derive scope with:

```bash
python3 scripts/wiki-ops.py affected-pages <source-summary>
```

Use `knowledge_pages` as the audit scope. Do not audit `meta_pages` as
extraction coverage.

## Contract

- Read the source before reading the wiki pages.
- Report source-side gaps and page-side attribution mismatches.
- Do not modify files.
- Do not propose repairs; describe what is missing or unsupported.
- Keep extraction and audit independent: do not rely on extractor
  reasoning.

## Output

Return a markdown report with attribution errors, coverage gaps, and a
short note on what the extraction covered well.
