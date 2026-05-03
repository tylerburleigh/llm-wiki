# wiki-repair

Use when making a known, scoped correction to existing wiki pages.

## Workflow

- Read `CLAUDE.md`, the affected pages, and relevant source summaries
  or raw sources.
- Make the smallest defensible edit.
- Preserve claim typing and provenance.
- Update `updated:` on changed pages.
- Repair frontmatter `sources:` when body source links require it.
- Rebuild `wiki/index.md` if knowledge-page metadata or TLDRs changed.
- Append `wiki/log.md` when wiki state changes.

## Boundaries

- Do not re-ingest a changed source.
- Do not broaden beyond the named repair scope.
- Do not modify `purpose.md` or raw source files.
- Do not auto-commit.
