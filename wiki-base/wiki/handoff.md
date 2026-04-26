---
type: meta
sources: []
created: "{{date}}"
updated: "{{date}}"
status: current
tags: []
---

> [!tldr]
> Cross-session continuity. What was the last session working on, what's still in progress, what's blocked. Read at session start; append at session end.

The agent reads this file at the start of every session before any other work. It captures things `wiki/log.md` does not: the *current state of attention*, not just the history of operations.

## Format

Newest entry on top. Each entry is short — five to ten lines — and answers three questions:

1. **What did the session work on?** One or two lines.
2. **What was deferred or left in flight?** Anything a future session should pick up.
3. **What does the next session need to know?** Surprises, constraints, decisions made mid-session that future work depends on.

```
### [YYYY-MM-DD] short title
- Worked on: ...
- Deferred: ...
- Notes: ...
```

When a session resolves an item from "In Progress" or "Blocked," strike it from those sections and note the resolution in the Last Session entry.

## Last Session

<!-- Append entries above this line, newest on top. Empty until the first session. -->

*No sessions logged yet.*

## In Progress

<!-- Active items that span sessions. Remove when done. -->

*Nothing in progress.*

## Blocked

<!-- Items waiting on human input or external action. -->

*Nothing blocked.*

## Open Questions

<!-- Questions that came up mid-session and weren't resolved. -->

*No open questions.*
