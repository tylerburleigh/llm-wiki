---
type: meta
sources: []
created: "{{date}}"
updated: "{{date}}"
status: current
tags: []
---

> [!tldr]
> Prioritized queue of open questions, unverified claims, and known gaps that need follow-up. Inline `[!gap]` and `[!unverified]` callouts surface specific holes; this file ranks and triages them.

Inline callouts mark a gap *where it lives* — useful for the page, but invisible at the wiki level. The backlog promotes the ones that matter into a single ranked queue with a `Review By` date so they get looked at on a cadence.

## How items get here

- `[!gap]` callouts on hub pages or pages central to `purpose.md`
- `[!unverified]` callouts where the unverified status blocks downstream work
- Open questions surfaced during `/wiki-query` that the session couldn't answer
- Conceptual gaps surfaced during `/wiki-lint` (entity-concept pairs that co-occur but aren't cross-linked, thinly-sourced hub pages)

Routine `[!gap]` callouts on leaf pages stay inline — the backlog is for items the agent (or human) actively wants to triage, not every gap in the wiki.

## How items leave

- The gap is filled, the unverified claim is sourced, or the question is answered → mark `resolved` and link to where the answer landed.
- The item turns out to not matter → mark `dropped` with a one-line reason. Don't silently delete; the dropped reason is itself information.

## Open

| # | Question or claim | Surfaced from | Priority | Review By | Status |
|---|-------------------|---------------|----------|-----------|--------|

<!-- Append rows above. Priority: high | medium | low. Review By: ISO 8601 date. Status: open | in-progress. -->

*No backlog items yet. Add rows as gaps and unverified claims accumulate.*

## Resolved

| # | Question or claim | Resolution | Resolved on |
|---|-------------------|------------|-------------|

<!-- Append rows above. Resolution: link to page or section where the answer landed. -->

*No resolved items yet.*

## Dropped

| # | Question or claim | Why dropped | Dropped on |
|---|-------------------|-------------|------------|

<!-- Append rows above. -->

*No dropped items yet.*
