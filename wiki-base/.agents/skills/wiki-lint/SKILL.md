# wiki-lint

Use when the user asks to lint, health-check, brief, or inspect stale
or broken wiki state.

## Deterministic Checks

Run:

```bash
python3 scripts/wiki-lint.py
```

For a session-start summary:

```bash
python3 scripts/wiki-lint.py --briefing
```

Rebuild the generated index when needed:

```bash
python3 scripts/wiki-lint.py --rebuild-index
```

## Judgment Checks

After deterministic lint, inspect conceptual health: stale hubs,
thinly sourced pages, open gaps, unsupported-looking prose, unresolved
links, and a small rotating sample of `[!source]` claims traced back to
raw sources.

## Boundaries

- Keep mechanical fixes narrow.
- Route source-grounded corrections to `wiki-repair`.
- Route source refreshes to `wiki-ingest`.
- Do not auto-commit.
