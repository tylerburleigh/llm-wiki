---
type: meta
sources: []
created: "{{date}}"
updated: "{{date}}"
status: current
tags: []
---

> [!tldr]
> Append-only log of structural decisions and the rationale behind them. Captures *why* a structural choice was made so it doesn't have to be re-derived later.

Conventions in `CLAUDE.md` and `wiki/conventions.md` say what the rule is. This file captures *why* — the rationale that gets lost between sessions.

## When to append

- A page was split, merged, or renamed for a non-obvious reason.
- A claim was classified as `[!analysis]` rather than `[!source]` (or vice versa) on a judgment call.
- A new convention was added — record the case that prompted it.
- A schema or template change landed — record what evidence motivated it.
- A hypothesis or comparison was scoped a particular way after weighing alternatives.

Skip this file for changes whose rationale is obvious from the diff. It's for the choices a future session would otherwise have to reconstruct.

## Format

Newest on top. One paragraph per entry. Reference affected pages with wikilinks.

```
### [YYYY-MM-DD] decision | one-line summary
Two to four sentences explaining the reasoning. Mention the alternatives that were considered and why they were rejected. Link affected pages: [[Page A]], [[Page B]].
```

Do not rewrite past entries. If a decision is later reversed, append a new entry referencing the original.

## Log

<!-- Append entries above this line, newest on top. -->

*No structural decisions logged yet.*
