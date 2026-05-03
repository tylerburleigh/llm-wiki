# wiki-query

Use when answering a question from the wiki or filing a reusable answer.

## Workflow

- Read `AGENTS.md`, `CLAUDE.md`, `purpose.md`, `wiki/index.md`, and
  relevant pages.
- Follow wikilinks and source-summary references.
- Distinguish sourced claims from analysis and uncertainty.
- Cite specific wiki pages in the answer.
- If the answer should persist, write a suitable wiki page, update
  frontmatter, rebuild the index when needed, and append the log.

## Boundaries

- Do not ingest new sources inside query.
- Do not repair existing pages unless the user explicitly asks.
- Surface stale pages, gaps, and attribution concerns as observations
  and route them to repair, ingest, or lint.
